---
type: LLM Prompt
title: Hermes digest: daily operator summary
description: Daily auto-delivered ingest-volume operator summary.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-daily-operator-summary
tags: [hermes, cron, autonomous-agent, digest]
timestamp: 2026-07-26T00:00:00-04:00
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
STRICT budget: at most 3 splunk tool calls. Call mcp__splunk__splunk_run_query with exactly: search index=os OR index=firewall earliest=-24h | stats count by index, host | sort index -count . Recall memory key "daily-operator-summary-last" (the per-index totals and host set you saved last run, if any) before writing your response. Final response UNDER 16 LINES: for EACH of index=os and index=firewall report its total event count and host count computed from every row the query returned — if an index returns zero rows or is absent from the results, state that explicitly as "index=X SILENT - 0 events", never omit it or fold it into a clean total. Then list hosts by volume under an explicit "top N of M hosts shown" heading, where M is the real total host count you saw, so the boundary of what you examined is visible. Then ONE sentence on the single most notable change vs the recalled previous run, or vs a normal day if you have no baseline. NEVER assert "all hosts reporting", "no gaps", or any other claim of completeness - you can only report what the query actually returned, never what it did not return. If you have no baseline to recall, say "no prior baseline; deltas begin next run" instead of guessing. Auto-delivered - no slack tool, no SILENT. On error or zero rows, respond with that exact fact. Never invent data. Save this run's per-index totals and host set back to memory key "daily-operator-summary-last". End with the model id.
