---
type: LLM Prompt
title: Hermes repo scorecard
description: Weekly weighted 0-100 repo-health scorecard for the dryvist org with week-over-week deltas.
resource: prompt://dryvist/auto-ai-agent/hermes-repo-scorecard
tags: [hermes, cron, autonomous-agent, github]
timestamp: 2026-08-07T20:00:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ai-llm-prompts
    path: automation/estate-briefing.md
    note: "Salvaged from the retired estate-briefing Phase 2. The daily briefing half is dropped as duplicate of hermes-github-triage and hermes-daily-summary; only the weighted scorecard and its week-over-week deltas survive. Scorecard history moves from the routine state repo to Hermes memory, and the Mintlify docs-coverage line is dropped because hermes-nightly-wiki-health already covers docs reachability."
---
Produce the weekly repo-health scorecard for the dryvist GitHub org right now using your `github-issues` skill. This is **read-only** — never comment, label, close, edit, commit, or merge anything. You are scoring, not fixing.

## Scope

List non-archived repos in the org and apply your operator skip-list. If more repos remain than you can score in one bounded pass, score the 25 most recently pushed and say plainly in the output how many you skipped — never let a truncated pass read as full coverage.

## Score each repo 0-100

Seven weighted factors:

- **README exists and has content — 25.** 0 if missing, 15 if present, 25 if it has multiple sections.
- **Last commit recency — 20.** 20 under 7 days, 15 under 30, 10 under 90, 5 under 180, 0 beyond.
- **Open issues reasonable — 15.** 15 under 5, 10 under 10, 5 under 20, 0 at 20 or more.
- **CI passing — 15.** 15 passing, 5 no CI configured, 0 failing.
- **Has releases — 10.** 10 if a release landed within 90 days, 5 for any release, 0 for none.
- **Description filled — 10.** 10 yes, 0 no.
- **License present — 5.** 5 yes, 0 no.

A repo with no CI scores 5 on that factor, not 0 — absent is not the same as broken, and conflating them makes every young repo look unhealthy.

## Deltas

Recall the previous run from memory key `repo-scorecard-last` — the run date plus each repo's score and factor breakdown. Compute each repo's delta against today. Save today's scores and date back to that key after you post, keeping the history entries so future runs can compare. Memory is the state store for this job; do not read or write any GitHub state repo.

On the first run there is no prior entry — report absolute scores, say it is the first run, and skip the delta section entirely rather than printing every repo as a fresh gain.

## Report

If every repo's score is unchanged since the last run, post only a one-line update naming the run date it matches, and save the new timestamp. Otherwise post to the home channel:

- The estate median score and its delta.
- The five lowest scorers with their score, delta, and the single factor costing each the most points.
- Any repo that moved by 10 points or more in either direction, with the factor that moved.
- The count of repos scored and the count skipped, if any.

Slack does not render Markdown tables — put the columnar parts in a fenced code block so the numbers stay aligned. Lead with what changed. Do not re-dump the full repo list every week.

If a finding needs human action beyond reporting — a repo whose CI has been failing for multiple runs, say — file it as a Vikunja task (`vikunja_tasks`) rather than only mentioning it in Slack. Never open a GitHub issue. If the finding is incident-shaped (e.g. a live security exposure), open a Zammad ticket instead. End every delivered message with one line naming the model id(s) you used.
