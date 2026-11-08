---
type: LLM Prompt
title: Hermes digest: Splunk parsing quality
description: Daily auto-delivered Splunk per-sourcetype parsing-quality digest.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-splunk-parsing-quality
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

STRICT budget: at most 2 splunk tool calls. Call mcp__splunk__splunk_run_query with exactly: search index=os OR index=network earliest=-24h | stats count by sourcetype | sort -count | head 15 . Final response UNDER 12 LINES: the exact SPL, the per-sourcetype counts, and ONE sentence flagging any sourcetype that looks mis-parsed or unexpectedly low/high. Auto-delivered - no slack tool, no SILENT. On error or zero rows, respond with that exact fact. Never invent data. End with the model id.
