---
type: LLM Prompt Fragment
title: "Repository Audit — Rule Definitions"
description: "Detection, scope, and action steps for the repo-audit rule rotation."
resource: "prompt://dryvist/automation/repo-audit-rules"
tags:
  - "automation"
  - "routine"
timestamp: "2026-07-18T16:40:00-04:00"
status: retired
consumers: []
render:
  engine: include
  variables: []
  frontmatter: strip
source_history:
  - repository: "dryvist/claude-code-routines"
    path: "routines/repo-audit.prompt.md"
    commit: "11a75537a6ec52bdf60f37b06c8a5ebd51562a4d"
---

Companion to [repo-audit](repo-audit.md) — the full definition of each rule in its rotation.

## Rule 0 — `claude-md-staleness`

**Scope**: `CLAUDE.md`, `AGENTS.md`, and any `**/SKILL.md` in each repo.

**Detection**: extract referenced relative paths from each file, check existence via Contents API.

```bash
# Fetch content (use cache if hash matches)
BODY=$(gh api "repos/$GH_OWNER/$REPO/contents/CLAUDE.md" --jq '.content' 2>/dev/null | base64 -d)
HASH=$(printf "%s" "$BODY" | sha256sum | cut -d' ' -f1)
CACHED_HASH=$(jq -r --arg k "$GH_OWNER/$REPO:CLAUDE.md" '.content_hashes[$k] // ""' /tmp/state.json)
if [ "$HASH" = "$CACHED_HASH" ]; then
  # No change since last scan — skip
  continue
fi
```

**Filters** (skip during path extraction):

- Strings containing placeholders: `<...>`, `${...}`, `%s`, `{{...}}`, `<repo>`, `<basename>`.
- Globs (any `*` in the path).
- URLs (`http://`, `https://`, `mailto:`, `tel:`).
- Absolute paths outside the repo (start with `/nix/store/`, `/Users/`, `/tmp/`, `/var/`).
- Skip-list filenames: `CLAUDE.local.md`, `*.local.md`, `.envrc`, `.envrc.local`.

**Path existence check** (use `resolved_paths` cache):

```bash
gh api "repos/$GH_OWNER/$REPO/contents/$PATH" --jq '.type' 2>/dev/null
```

Flag paths that return 404 AND aren't in the filter list.

**Action**: open ONE review-ready PR removing or correcting the stale references in a single file. Maximum-impact selection: the repo with the most flagged paths in one file.

**Redaction**: every flagged path written into the PR body MUST pass through the Hard Rules redaction set. The Provenance "Why" line describes the rule, never quotes the offending string.

## Rule 1 — `secrets-policy`

**Scope** (scan only):

- `src/**`, `lib/**`, `terraform/**`, `ansible/roles/**`, `.github/workflows/**`.

**Hard skip** (do not scan):

- `SECURITY.md`, `README.md`, `CHANGELOG.md`, `LICENSE`, `*resume*`, `*cover-letter*`.
- Entire repos: private note vaults, career-document repos, personal-site repos, config-dump repos, and the `${PRIVATE_DOCS_REPO}` env var if set.
- `tests/**`, `fixtures/**`, `examples/**`, `*.example`, `*.test.*`, `*.spec.*`.
- Vendor manifests where author email is intentional: `package.json`, `Cargo.toml`, `pyproject.toml`, `Gemfile`.

**Patterns** (each anchored to limit false positives):

- AWS account IDs: `\b\d{12}\b` within 100 chars of the case-insensitive token `account`.
- GitHub tokens: `gh[ps]_[A-Za-z0-9]{30,}`.
- Anthropic API keys: `sk-ant-[A-Za-z0-9_-]{20,}`.
- Private hostnames in source files (NOT in docs/comments): `\b[a-z0-9-]+\.(internal|lan|home|corp)\b`.
- IP literals in non-comment lines of source files (regex omitted; high false-positive risk — only enable after first 30 days of run data shows it's tractable).

**Action**: file ONE ISSUE in the affected repo titled `[routine:repo-audit] Possible secret leak in <file>`. The issue body:

- Identifies the file and line range (NOT the literal value).
- Recommends rotation as the first step, then expunge from history.
- Links to the rule definition.
- Applies `cloud-routine` label.

**NEVER open a PR for `secrets-policy`.** Operator judgment is required (rotate first, then expunge — this routine cannot rotate).

## Rule 2 — `no-scripts`

**Scope**: `.github/workflows/*.yml` (NOT underscore-prefixed reusables like `_ai-merge-gate.yml`).

**Detection**: parse each workflow with a YAML parser, walk `jobs.*.steps[*].run`:

- Multi-line `run:` block containing keywords `if`, `for`, `while`, `case` outside string literals.
- Multi-line `run:` block with 4+ non-blank lines.
- Single-line interpreters: `python -c`, `node -e`, `perl -e`, `ruby -e`, multi-line `bash -c`.

**Hard relax of the "no workflow edits" guard** — for THIS rule only, this routine MAY edit `.github/workflows/*.yml` files, subject to all of:

- The PR is DRAFT (`gh pr create --draft`).
- The edit extracts inline logic to `.github/scripts/<name>.js` invoked via `actions/github-script` (the estate convention from `JacobPEvans/.github-ai` AGENTS.md) — NEVER to a `.sh` file; shell wrapper scripts are banned estate-wide.
- No semantic change to what the workflow does (refactor only).
- Post-edit YAML parse passes:

```bash
python3 -c "import yaml,sys; yaml.safe_load(sys.stdin)" < /tmp/repo-audit-new-workflow.yml
```

If parse fails: ABORT this PR, log to state file, do not commit. Never commit broken YAML.

**Maximum-impact selection**: the workflow file with the largest extractable run-block.

**Action**: open ONE DRAFT PR adding the new `.github/scripts/<name>.js` file AND updating the workflow to invoke it via `actions/github-script`. Operator flips draft → ready after manual review.
