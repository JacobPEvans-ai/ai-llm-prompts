---
type: LLM Prompt
title: Hermes Splunk deep dive
description: Quiet Splunk index or sourcetype characterization prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-splunk-deepdive
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-11-04T20:33:43-05:00
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
Pick ONE index or sourcetype you have not yet characterized well (check your wiki/memory for gaps). Using only bounded queries, learn its normal shape, volume and purpose, then write or update a page in the `splunk` area of your wiki plus a memory baseline. This is a quiet research run — no alert needed.

Give utilization its turn in that rotation: network throughput per host and per link, and the other saturation signals you can reach (CPU, memory, disk space and I/O, interface errors and drops). Characterize these across time, not at an instant. Compare the last 24 hours against a 7-day daily baseline, because a level that looks unremarkable now is a finding when it has been climbing. Keep the pass small:
- Run one `timechart span=1d` or `tstats` search per signal over `earliest=-8d@d latest=now`, with `head 8` on the output. Do not run a sub-daily series across several days.
- Keep every result to a summary: `stats` or `timechart` output of at most 20 rows. Never table raw events in this pass.
- Run at most 3 utilization searches per run. Choose the signals with the widest spread across hosts, and name the signals you did not reach.
- Stop after 12 Splunk searches in a run, whatever the topic, and write up what you have.
- Run queries only with the Splunk tools. Do not try scripts or shell commands for queries.

Report what changed, over what window, and against which baseline. A flat trend is a valid result and is worth one line, not a page.
