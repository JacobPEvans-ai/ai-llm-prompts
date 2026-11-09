---
type: LLM Prompt
title: Hermes digest: anomaly hunt
description: Twice-daily auto-delivered unmonitored-pattern anomaly hunt.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-anomaly-hunt
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
STRICT budget: EXACTLY ONE splunk tool call, never a second. Call mcp__splunk__splunk_run_query with exactly: search index=* earliest=-6h | stats count by index, sourcetype | sort -count | head 15 . Issue that as a real tool call. Never write a tool call as text — any message containing "<function=" or "<parameter=" is delivered verbatim to Slack as garbage, so it must never appear in anything you write, on any turn. The moment the tool result comes back you are finished querying; if you want another query, report what the one result showed instead. Final response UNDER 12 LINES: the exact SPL, the top index/sourcetype counts, and ONE sentence naming the single most unusual pattern nobody monitors and why. Auto-delivered - no slack tool, no SILENT. On error or zero rows, respond with that exact fact. Never invent data. End with the model id.
