---
type: LLM Prompt
title: Hermes digest: GitHub org triage
description: Daily auto-delivered dryvist org PR/issue triage.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-github-org-triage
tags: [hermes, cron, autonomous-agent, digest]
timestamp: 2026-11-08T19:00:00Z
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main.yml
    commit: 3b0c332623d5d2ee2fd283f9ab265cf6d5a7911b
---
HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from auto-ai-agent/hermes-reporting/status-levels.md: green (healthy, no action), yellow (degraded, unverified, flapping or above baseline; look when convenient), red (failing or down; act now) - pick the worst level that applies, and use no other status emoji.

STRICT budget: at most 3 tool calls via the github skill. Sweep the dryvist org for open PRs and stale open issues. Final response UNDER 12 LINES: count of open PRs, any with failing/red CI, and the oldest-untouched issue. Auto-delivered - no slack tool, no SILENT. If the tool errors, respond with the exact error. Never invent repo data. End with the model id.
