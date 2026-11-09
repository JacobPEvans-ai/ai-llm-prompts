---
type: LLM Prompt
title: Hermes Splunk digest
description: Hourly delta-aware Splunk status digest prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-splunk-digest
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-07-18T16:43:26-04:00
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
Gather the current normal (top indexes/sourcetypes by volume and freshness) and any anomalies still open. Recall your last-posted digest state from memory (key "splunk-digest-last": fingerprint, first-seen timestamp, post date). If nothing has materially changed since that post AND today's UTC hour is not 00 (the daily anchor hour), post ONLY a one-line update: "No change — still <one-line state>, Day N since <first-seen date>, see <wiki/memory reference>." If something changed OR it is the 00:52 UTC anchor post, post the FULL digest — what you looked at, the current normal, open anomalies, and any splunk-auto-* checks added or removed — and save the new fingerprint (resetting first-seen if the state actually changed) to memory under that key. Bounded queries only. This job ALWAYS posts something and NEVER replies [SILENT] — the one-line update satisfies that contract just as the full digest does; [SILENT] is only for the anomaly sweeps.
