---
type: LLM Prompt
title: Hermes secrets policy audit
description: Issue-only scan for credential and private-topology leaks in dryvist org source, never a pull request.
resource: prompt://dryvist/auto-ai-agent/hermes-secrets-policy-audit
tags: [hermes, cron, autonomous-agent, security]
timestamp: 2026-08-06T00:00:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ai-llm-prompts
    path: automation/repo-audit.md
    note: "Salvaged from the retired repo-audit rule rotation. Only the secrets-policy rule survives — it files an issue and never a PR, which is what makes it Hermes-legal. The no-scripts and claude-md-staleness rules are dropped as already covered by the script-guards:native-first and claude-md-management:claude-md-improver skills."
---
Run a secrets-policy audit across the dryvist GitHub org right now using your `github-issues` skill.

You need a token carrying `contents:read` across the org to read source files. **If that token is absent you cannot scan — reply with exactly [SILENT].** Do not attempt a partial scan from repo metadata alone; a scan that cannot read files finds nothing and would report a clean estate that was never examined.

**You file issues only. Never open a pull request for a finding here, and never edit or delete the offending line.** Remediation order is rotate first, then expunge from history, and you can do neither — a PR that removes the literal leaves the credential live and its history intact while making it look handled.

## Scope

Scan only: `src/**`, `lib/**`, `terraform/**`, `ansible/roles/**`, `.github/workflows/**`.

Hard skip, no exceptions:

- `SECURITY.md`, `README.md`, `CHANGELOG.md`, `LICENSE`, and any path matching `*resume*` or `*cover-letter*`.
- Entire repos: private note vaults, career-document repos, personal-site repos, config-dump repos, plus your operator skip-list.
- `tests/**`, `fixtures/**`, `examples/**`, `*.example`, `*.test.*`, `*.spec.*`.
- Vendor manifests where an author email is intentional: `package.json`, `Cargo.toml`, `pyproject.toml`, `Gemfile`.

## Patterns

Each is anchored to keep false positives tractable:

- GitHub tokens: `gh[ps]_[A-Za-z0-9]{30,}`.
- Anthropic API keys: `sk-ant-[A-Za-z0-9_-]{20,}`.
- AWS account ids: a bare 12-digit number within 100 characters of the case-insensitive token `account`.
- Private hostnames in source files, not in docs or comments: `\b[a-z0-9-]+\.(internal|lan|home|corp)\b`.

Do not scan for bare IP literals. The false-positive rate makes the output unusable and buries real findings.

## Report

Recall memory key `secrets-policy-last` — the findings you already filed, keyed by repo, file path, and line range. A finding you have already filed an open issue for is not new: do not file it again. If nothing new is found, save the run timestamp and reply with exactly [SILENT].

For each genuinely new finding, file ONE issue in the affected repo:

- Title it `[hermes-secrets-policy] Possible credential leak in <file>`.
- **Name the file and line range only. Never put the matched value, or any fragment of it, in the issue body, the title, or Slack.** The issue is public; restating the secret is the leak.
- State the remediation order explicitly: rotate the credential first, then expunge it from git history.
- Say which pattern matched, so a false positive can be dismissed without re-running the scan.

Anything that looks like a live, currently-valid credential is an operational problem needing human action now — alert the operator directly rather than waiting for the digest, and open a Zammad ticket to track it to resolution. A leaked credential is an incident, not a code-quality finding.

Save the run timestamp and the filed findings back to `secrets-policy-last`. Post a one-line summary to the home channel naming the count of new issues filed and the repos involved — never the file contents. End every delivered message with one line naming the model id(s) you used.
