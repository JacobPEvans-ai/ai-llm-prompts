---
type: LLM Prompt
title: Hermes GitHub triage
description: Read-only delta-aware Dryvist GitHub organization triage prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-github-triage
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-07-18T16:43:26-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main.yml
    commit: 5fe2eb8f6df8203ea5dd17f1e49053f0a195b490
---
Do a read-only triage sweep of the dryvist GitHub org right now using your github-issues skill. Enumerate open PRs and issues across non-archived repos; flag PRs older than 7 days as stale, Renovate/bot PRs open >7 days, and issues untouched for 30+ days. NEVER comment on, label, close, or edit anything — you are producing a report, not acting on it. If nothing genuinely needs a human decision, reply with exactly [SILENT]. Otherwise, recall your last-posted top-5 list and totals from memory (key "github-triage-last"): if today's top-5 + totals are identical to that last post, post ONLY a one-line update ("No change since <timestamp> — same N items still open") instead of restating the list. If the list or totals changed, post the full top-5 action list (repo, number, why) plus totals to the home channel, and save the new list + totals + timestamp to memory under that key.

Enumerate issues with `state=open` and no other filter, then separate issues from pull requests yourself by the absence of a `pull_request` key on each item. Do NOT add a `labels` parameter: it takes a comma-separated list of label NAMES, so a value meaning "unlabelled" — `none`, `null`, empty — matches only issues carrying a label of that literal name and silently returns zero rather than erroring. Use the identical query every run; a query that changes between runs makes the delta a comparison of two different measurements.

Sanity-check every total against the remembered baseline before you post it. If a total has moved by more than half, or has collapsed to zero, treat that first as evidence about your own query rather than as news about the org: a fleet-wide count does not empty overnight. In that case post the anomaly — both totals, and the exact query string you ran — and explicitly say the number is unverified, instead of publishing it as a headline or explaining it away with a guess about what changed upstream. State the query you ran alongside any total you do report, so a wrong number stays diagnosable from the message alone.
