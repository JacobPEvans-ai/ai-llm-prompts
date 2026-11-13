---
type: LLM Prompt Fragment
title: "Bot PR Security Triage"
description: "Phase A of bot-pr-merge: CodeQL/Dependabot alert enumeration, the high-severity auto-label gate, and escalation. Composed back into bot-pr-merge via include."
resource: "prompt://dryvist/automation/bot-pr-merge/security-triage"
tags:
  - "automation"
  - "routine"
  - "fragment"
timestamp: "2026-07-20T13:00:00-04:00"
status: retired
consumers: []
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/bot-pr-merge.md"
    note: "Extracted verbatim from bot-pr-merge Phase A to keep each catalog file under the 12KB file-size limit; recomposed via include, no content change."
---
### Phase A1 — Enumerate target repos

```bash
gh repo list "$GH_OWNER" --limit 100 \
  --json name,isArchived \
  | jq '[.[] | select(.isArchived==false) | .name]'
```

Apply the global skip-list:

<!-- include: fragment-skip-list.md -->

### Phase A2 — Fetch open CodeQL alerts (primary)

```bash
gh api "repos/$GH_OWNER/$REPO/code-scanning/alerts?state=open&per_page=100" \
  --jq '[.[] | {
    number,
    rule_id:.rule.id,
    severity_level:.rule.security_severity_level,
    severity:.rule.severity,
    age_days:((now - (.created_at | fromdate)) / 86400 | floor),
    instance_count:.instances_url,
    html_url
  }]' 2>/dev/null
```

404 → repo has no GHAS (or it's disabled). Skip silently.

### Phase A3 — Fetch open Dependabot alerts (secondary)

```bash
gh api "repos/$GH_OWNER/$REPO/dependabot/alerts?state=open&per_page=100" \
  --jq '[.[] | {
    number,
    package:.dependency.package.name,
    ecosystem:.dependency.package.ecosystem,
    severity:.security_advisory.severity,
    cve:.security_advisory.cve_id,
    ghsa:.security_advisory.ghsa_id,
    age_days:((now - (.created_at | fromdate)) / 86400 | floor),
    auto_dismissed_at,
    html_url
  }]' 2>/dev/null
```

404 → Dependabot alerts not enabled. Skip silently.

### Phase A4 — Fetch matching bot PRs

```bash
gh pr list --repo "$GH_OWNER/$REPO" --state open --limit 100 \
  --json number,title,author,labels,headRefName \
  --jq '[.[] | select(.author.login == "dependabot[bot]" or
                       .author.login == "renovate[bot]" or
                       .author.login == "github-actions[bot]" or
                       .author.login == "jacobpevans-github-actions[bot]")]'
```

For each Dependabot alert, cross-reference to its open PR by package name match (and by `auto_dismissed_at == null`). Renovate PRs that touch dependency manifests are also candidates even without a Dependabot alert backing them (Renovate ships proactive bumps).

### Phase A5 — Auto-label gate (high severity only)

For each candidate bot PR, run the full gate:

#### Gate 1 — Severity

Alert is `state == "open"` AND `severity_level == "high"` (Dependabot equivalent: `severity == "high"`). If `severity_level` is missing/null on the alert (or no alert backs the PR), **fail closed** — Slack-only.

Critical severity → never auto-label, always Slack with `<!here>`.

#### Gate 2 — Age

Alert age > 7 days. Filters transient findings.

#### Gate 3 — CodeQL ignore list

`rule.id` is NOT in `codeql_ignore[$repo]` (operator-curated list in the state file). If a rule has been historically determined to be a false positive for this repo, leave it alone.

#### Gate 4 — File-list allowlist (subset, NOT exact-set)

Fetch the PR file list once (reused by Gate 5):

```bash
FILES_JSON=$(gh api "repos/$GH_OWNER/$REPO/pulls/$PR_NUMBER/files")
FILES=$(echo "$FILES_JSON" | jq '[.[].filename]')
```

Every file in `$FILES` MUST be in the dependency-manifest allowlist:

```text
flake.lock
uv.lock
pyproject.toml
package.json
package-lock.json
Cargo.toml
Cargo.lock
requirements.txt
requirements-dev.txt
go.sum
go.mod
Gemfile
Gemfile.lock
poetry.lock
Pipfile
Pipfile.lock
```

Renovate's standard flows update manifest + lockfile together (e.g. `pyproject.toml` + `uv.lock`). Subset allowlist accepts these; exact-set would have rejected them.

#### Gate 5 — Diff-content (closes the one-byte source-edit bypass)

Re-use `$FILES_JSON` from Gate 4 (same payload includes the `patch` field) and verify every changed hunk line is a dependency-declaration line:

```bash
echo "$FILES_JSON" | jq '.[] | {filename, patch}'
```

Per-file regex for declaration lines (apply to the `+` and `-` lines of the patch, excluding the `+++` / `---` headers and `@@` hunk markers):

- `*.toml`: line matches `^[+-]\s*[A-Za-z0-9_-]+\s*=`
- `*.json`: line matches `^[+-]\s*"[^"]+":\s*("[^"]*"|true|false|null|[0-9.]+)\s*,?$`
- `*lock*` files: structured-data lines only (per-format heuristics; reject any free-form text additions)
- `*.txt` (requirements): line matches `^[+-]\s*[A-Za-z0-9_.-]+\s*(==|>=|<=|~=|>|<|@)`
- `go.mod`: line matches `^[+-]\s*[a-z0-9./_-]+\s+v[0-9]`

Any line outside these patterns (executable code, imports, etc.) → reject.

#### Gate 6 — Signed commits

All commits in the PR must be web-flow signed:

```bash
gh api "repos/$GH_OWNER/$REPO/pulls/$PR_NUMBER/commits" \
  --jq 'all(.[]; .commit.verification.verified == true)'
```

#### Gate 7 — Label provisioned

The `auto-merge-deps` label exists in the target repo:

```bash
gh label list --repo "$GH_OWNER/$REPO" --search auto-merge-deps --json name \
  --jq 'length'
```

If 0: skip the auto-label, escalate to Slack with `[label missing]` annotation. Operator decides whether to add via `JacobPEvans/.github` label-sync.

#### Gate 8 — Already labeled / cap

PR doesn't already have `auto-merge-deps`. Total labels added this run < 5.

### Phase A6 — Apply label

```bash
gh pr edit --repo "$GH_OWNER/$REPO" "$PR_NUMBER" --add-label "auto-merge-deps"
```

Append `label_added` to `run_log`.

### Phase A7 — Escalate high/critical

For each alert classified as high (failed auto-label gate for any reason except age) or critical:

- Check `escalation_cooldown[$repo:$alert_id]`. If less than 3 days since last escalation, skip.
- Compose Slack ping. `@here` for high, `<!here>` for critical. Include CVE/GHSA, severity level, repo, link.
- Update `escalation_cooldown` with today's date.

Escalations are collected into the combined Slack message (see Slack output) — not sent as separate messages.
