---
type: LLM Prompt
title: Hermes Splunk triage
description: Broad bounded Splunk anomaly-sweep prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-splunk-triage
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-08-01T00:00:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main.yml
    commit: 5fe2eb8f6df8203ea5dd17f1e49053f0a195b490
---
Do a broad, self-directed anomaly sweep of Splunk right now using only bounded queries. Recall your known baselines first, confirm anything surprising with follow-up bounded queries, and record notable findings and updated baselines to memory. Before you alert, also recall your own last-posted findings from memory (key "splunk-triage-last"): this job is for NEW or ESCALATING findings only, not a restatement of what you already sent. If your top finding is already covered there and has not gotten worse, do not re-derive or re-alert it — reply with exactly [SILENT]. If nothing is genuinely off, also reply with exactly [SILENT]. Otherwise send one concise, numbers-backed alert covering only what is new or escalating, and save the updated findings back to "splunk-triage-last".
