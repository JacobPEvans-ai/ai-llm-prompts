---
type: LLM Prompt
title: PR fix briefs
description: Router table a PR controller uses to pick the per-state fix brief for an unmergeable pull request, with detection fields and the attempt limit.
resource: prompt://dryvist/auto-ai-agent/pr-fix/index
tags:
- autonomous-agent
- pull-requests
- pr-fix
timestamp: '2026-11-12T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/claude-code-plugins
  path: github-workflows/skills
  note: briefs condensed from finalize-pr, resolve-pr-threads, rebase-pr, merge-pr, and gh-cli-patterns
---

These are the per-state fix briefs a PR controller hands to a sandboxed coding
agent when a pull request is not mergeable: one brief per state, one run per
head state. The controller fills the brief's `{...}` placeholders, runs the
agent with only that brief, and reads one line back.

| State | Detected from GitHub API fields | Brief | Attempt limit |
|---|---|---|---|
| Branch is behind base; update-branch failed or not allowed | `mergeStateStatus` = `BEHIND` | [behind.md](behind.md) | 3 |
| Merge conflict with base | `mergeable` = `CONFLICTING` or `mergeStateStatus` = `DIRTY`; label `merge-conflict` | [conflicted.md](conflicted.md) | 3 |
| One named check failing | a `statusCheckRollup` context for `{check_name}` reports failure | [red-check.md](red-check.md) | 3 |
| Open review feedback | `reviewThreads.isResolved` false or `reviewDecision` is `CHANGES_REQUESTED` | [review-threads](review-threads.md) | 3 |

Detection reads `mergeable`, `mergeStateStatus`, `reviewDecision`, and
`statusCheckRollup` from `gh pr view --json`; thread state is GraphQL-only
(`reviewThreads` is not a valid `--json` field). `mergeStateStatus` values that
are not ready: `BEHIND`, `BLOCKED`, `DIRTY`, `DRAFT`, `UNKNOWN`, `UNSTABLE`.

Every brief runs under the same contract: exactly one new commit on the pull
request branch (the base is merged into the branch, never the reverse), no
rebase, no force-push, no skipped or weakened checks, hooks, or tests, no
workflow edits unless the failing check is about that workflow file, no
auto-merge, and never merging. Each run ends with one line, `FIXED head=<new sha>`
or `STOP: <reason>`; a run that replies `STOP` counts as a spent attempt.

Attempt limit: three attempts per head state; a new head sha resets the count.
After three, the controller labels the pull request `needs-lead` and a human
session takes it.

Source: the maintained skills in dryvist/claude-code-plugins, directory
`github-workflows/skills/`; the briefs condense them and link to them by URL:
[finalize-pr][finalize-pr], [resolve-pr-threads][resolve-pr-threads],
[rebase-pr][rebase-pr], [merge-pr][merge-pr], [gh-cli-patterns][gh-cli-patterns].

[finalize-pr]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/finalize-pr/SKILL.md
[resolve-pr-threads]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/resolve-pr-threads/SKILL.md
[rebase-pr]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/rebase-pr/SKILL.md
[merge-pr]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/merge-pr/SKILL.md
[gh-cli-patterns]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/gh-cli-patterns/SKILL.md
