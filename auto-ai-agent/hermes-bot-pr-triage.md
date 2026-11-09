---
type: LLM Prompt
title: Hermes bot PR triage
description: Delta-aware bot-PR security triage that labels and escalates dependency PRs but never merges, plus a once-daily stale-open-PR report.
resource: prompt://dryvist/auto-ai-agent/hermes-bot-pr-triage
tags: [hermes, cron, autonomous-agent, security]
timestamp: 2026-10-11T00:00:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ai-llm-prompts
    path: automation/fragment-bot-pr-security-triage.md
    note: "Distilled from the retired bot-pr-merge Phase A for a scheduled Hermes job. State-file references adapted to Hermes memory keys; the merge phase removed because Hermes labels and escalates only."
---
Run a bot-PR security triage sweep across the dryvist GitHub org right now. You **label and escalate only — you never merge or push.** Merging a labeled PR is owned by deterministic CI, not by you.

Use your `github-issues` skill plus a security-alert read token (`security_events:read` + `contents:read` + `pull_requests:read`/`write`). If that token is absent you cannot read alerts — reply with exactly [SILENT].

## Enumerate

- List non-archived repos in the org. Apply your operator skip-list.
- For each repo, fetch open CodeQL alerts (`code-scanning/alerts?state=open`) and open Dependabot alerts (`dependabot/alerts?state=open`). A 404 means the feature is disabled — skip that repo silently.
- Fetch open bot PRs (authors `dependabot[bot]`, `renovate[bot]`, `github-actions[bot]`, `jacobpevans-github-actions[bot]`). Cross-reference each Dependabot alert to its PR by package name. Renovate manifest bumps are candidates even with no backing alert.

## Auto-label gate (apply mechanically — do NOT reason around a failed gate)

Label a candidate PR `auto-merge-deps` only if it clears every gate. These are deterministic pass/fail checks, not judgment calls.

1. **Severity** — a backing alert is `open` and `high`. Missing or null severity, or no backing alert, fails closed (Slack only). Critical severity is never labeled — always Slack with `<!here>`.
2. **Age** — the alert is older than 7 days. Filters transient findings.
3. **Ignore list** — the alert `rule.id` is not in your operator CodeQL ignore list (memory key `bot-pr-triage-codeql-ignore`).
4. **File allowlist** — every changed file is a dependency manifest or lockfile (flake.lock, uv.lock, pyproject.toml, package.json, package-lock.json, Cargo.toml/lock, requirements*.txt, go.mod/sum, Gemfile/lock, poetry.lock, Pipfile/lock). Subset match, so a manifest plus its lockfile passes.
5. **Diff content** — every added or removed line is a dependency-declaration line for its file type (a `key = value`, a quoted JSON pair, a version-pinned requirement, a `go.mod` require). Any executable code, import, or free-form text rejects the PR. This closes the one-byte source-edit bypass. If a changed line is genuinely ambiguous, escalate that single judgment to Codex rather than guessing.
6. **Signed commits** — every commit in the PR is verified.
7. **Label provisioned** — the `auto-merge-deps` label exists in the repo. If it does not, skip the label and Slack `[label missing]`.
8. **Bump size** — every version the PR changes keeps its major and minor (a patch bump). A digest-only change with no version passes. A minor or major bump fails. A `nixpkgs*` input move fails. A version you cannot read from the title, body, or diff fails closed (Slack only).
9. **Not a release PR** — a release-please PR (head branch `release-please--*` or title `chore(main): release …`) is never labeled. It auto-merges on its own and needs no label.
10. **Cap** — the PR is not already labeled, and you have added fewer than 5 labels this run.

## Manual-repo risk lane

A repo whose GitHub custom property `automerge` is `manual` merges a bot PR only after you label it. Read the property
for each repo; never infer it from the name. In those repos, also judge open PRs by `renovate[bot]` with these gates
instead of gates 1–5 and 8 above:

1. **CI green** — every check on the current head commit has completed successfully. Pending, failed, cancelled,
   skipped-only or unreadable fails; retry on a later run.
2. **Change type** — a digest, patch or minor update of a `dryvist` upstream; or every changed file is under
   `.github/`.
3. **Upstream evidence** — the upstream changelog and diff show no breaking change, removed input or changed default
   that this repo uses. Missing or ambiguous evidence fails.
4. Gates 6, 7, 9 and 10 above still apply.

On a full pass, add `auto-merge-deps` and save the head SHA under memory key `bot-pr-triage-labeled-heads`. If the head
SHA of a labeled PR changes, remove the label first, then judge the new head. When unsure, do not label: leave one
short comment per head SHA, marked `<!-- hermes-bot-pr-triage:<head-sha> -->`, that says why. Report these labels and
comments in the same message as the triage.

## Stale open PR report (once per calendar day, all authors)

Separate from the security triage above and not limited to bot PRs. Recall
memory key `bot-pr-triage-stale-last-date`. If it already matches today's
UTC date, skip this whole section for this run — the cron fires more than
once a day and the report is not.

Otherwise: list every open PR across the org's non-archived repos (apply
your operator skip-list), sort oldest-first by days open, and take the top
10. For each, report the repo, PR number, title, days open, and author. A
bare PR number is not acceptable — always give the full PR URL so the
report is one click, not a lookup. Save today's UTC date to
`bot-pr-triage-stale-last-date`.

## Act

- On a full pass, add `auto-merge-deps`. That is the whole action — CI merges from there. You never call merge.
- Escalate every high (failed the gate for any reason except age) and every critical alert to Slack: `@here` for high, `<!here>` for critical, with CVE/GHSA, severity, repo, and link. Dedupe with memory key `bot-pr-triage-cooldown` — skip an alert already escalated in the last 3 days. Collect escalations into one combined message.
- Cap labels at 5 per run; escalations are uncapped.
- Include the stale-PR report (if not skipped above) in the same message as its own section, even when the security triage found nothing.

If nothing cleared a gate, nothing needs escalation, and the stale-PR report was skipped (already reported today), reply with exactly [SILENT]. Otherwise post the combined Slack message (labels added, escalations, stale-PR report) to the home channel and save updated cooldowns to memory. End every delivered message with one line naming the model id(s) you used.
