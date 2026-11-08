---
type: LLM Prompt
title: Hermes digest: Zammad incident review
description: Daily auto-delivered open Zammad incident review.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-zammad-incident-review
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

STRICT budget: at most 2 tool calls via the zammad skill. List OPEN Zammad tickets. Final response UNDER 12 LINES: total open, a count by priority, and the 3 oldest still-open ticket numbers+titles, plus ONE sentence on what most needs attention. Auto-delivered - no slack tool, no SILENT. If the tool errors, respond with the exact error. Never invent ticket data. End with the model id.
