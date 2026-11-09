---
type: LLM Prompt
title: Hermes digest: Splunk security lens
description: 6-hourly auto-delivered Splunk security-relevant pattern digest.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-splunk-security-lens
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
STRICT budget: EXACTLY ONE splunk tool call, never a second. Call mcp__splunk__splunk_run_query with exactly: search index=os OR index=network (failed OR denied OR unauthorized OR invalid) earliest=-6h | stats count by host, sourcetype | sort -count | head 12 . Issue that as a real tool call. Never write a tool call as text — any message containing "<function=" or "<parameter=" is delivered verbatim to Slack as garbage, so it must never appear in anything you write, on any turn. The moment the tool result comes back you are finished querying; if you want another query, report what the one result showed instead. Then produce your final response: a plain-text security digest UNDER 12 LINES containing the exact SPL you ran, the top counts, and ONE sentence on the most security-relevant pattern; if benign say exactly "no security-relevant anomalies". Your final response is automatically delivered to Slack - do not call any slack tool, do not output SILENT. If splunk errors or returns zero rows, your final response is that exact fact. Never invent data. Keep the entire response under 12 lines. End with one line naming the model id you used.
