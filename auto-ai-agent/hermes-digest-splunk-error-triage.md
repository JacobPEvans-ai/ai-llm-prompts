---
type: LLM Prompt
title: Hermes digest: Splunk error triage
description: Hourly auto-delivered Splunk error/failure triage digest.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-splunk-error-triage
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

STRICT budget: EXACTLY ONE splunk tool call, never a second. Call mcp__splunk__splunk_run_query with exactly: search index=os OR index=network (error OR failed OR critical) earliest=-1h | stats count by host, sourcetype | sort -count | head 12 . The moment that tool result comes back you are finished querying: your very next message is the finished report itself, written as plain prose for a human. Never write a tool call as text — a message containing "<function=" or "<parameter=" is delivered verbatim to Slack as garbage. If you want another query, report what the one result showed instead. Final response UNDER 12 LINES: the exact SPL, the top counts, and ONE sentence on the most recurring error nobody alerts on; if benign say exactly 'no recurring errors'. Auto-delivered to Slack - no slack tool, no SILENT. On splunk error or zero rows, respond with that exact fact. Never invent data. End with the model id.
