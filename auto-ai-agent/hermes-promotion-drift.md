---
type: LLM Prompt
title: Hermes promotion drift
description: Daily read-only org sweep that reports each git-flow repo whose develop branch is ahead of main with no promotion PR open; opens no PRs.
resource: prompt://dryvist/auto-ai-agent/hermes-promotion-drift
tags: [hermes, cron, autonomous-agent, git-flow]
timestamp: 2026-10-17T01:30:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/hermes-bot-pr-triage.md
    note: "Same enumerate-then-report shape and delivery rules."
---
Run a promotion-drift sweep across the dryvist GitHub org right now. You **read only — you never open, label, update, push, or merge anything.** A ready promotion PR freezes `develop`, so a person or agent opens and finishes each promotion with the promote-release flow; your job is to make the drift visible.

Use your `github-issues` skill with a read token. If a repo's token is missing, skip that repo and name it in the report.

## Enumerate

- List non-archived repos in the org whose default branch is `develop`. Apply your operator skip-list.
- For each, read `gh api repos/<owner>/<repo>/compare/main...develop` and take `ahead_by`. A 404 or `ahead_by` of 0 means in sync: skip silently.
- List open PRs with base `main` and head `develop`. If one exists, skip the repo; if it has been open more than 7 days, record its URL and age for the report.

## Record

- For each drifting repo with no open promotion PR, record the repo, `ahead_by`, up to 5 of the first lines of the unpromoted commit messages, and the oldest unpromoted commit date (UTC).

## Report

If no repo drifts and no promotion PR is older than 7 days, reply with exactly [SILENT]. Otherwise post one message to the home channel listing each drifting repo (full repo URL, commits ahead, oldest unpromoted commit date, the commit lines), each stale promotion PR (full URL, days open), and each skipped repo with its reason. End the message with one line naming the model id(s) you used.
