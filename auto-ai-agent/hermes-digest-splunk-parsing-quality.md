---
type: LLM Prompt
title: Hermes digest: Splunk parsing quality
description: Daily auto-delivered Splunk per-sourcetype parsing-quality digest.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-splunk-parsing-quality
tags: [hermes, cron, autonomous-agent, digest]
timestamp: 2026-07-24T00:00:00-04:00
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
STRICT budget: at most 2 splunk tool calls. Call mcp__splunk__splunk_run_query with exactly: search index=os OR index=network earliest=-24h | stats count by sourcetype | sort -count | head 15 . Final response UNDER 12 LINES: the exact SPL, the per-sourcetype counts, and ONE sentence flagging any sourcetype that looks mis-parsed or unexpectedly low/high. Auto-delivered - no slack tool, no SILENT. On error or zero rows, respond with that exact fact. Never invent data. End with the model id.
