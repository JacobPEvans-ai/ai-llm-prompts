---
type: LLM Prompt
title: Hermes Splunk parsing sweep
description: Bounded Splunk data-quality monitoring prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-splunk-parsing
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-08-05T00:45:00-04:00
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
Retrieval first: recall memory key "splunk-parsing-last" (the sourcetypes and parsing-defect signatures you already reported) so a defect that is still open is not re-reported every run — an unfixed problem is not a new finding.

Sweep Splunk with a data-quality lens this run — timestamp-extraction failures, events dated far in the past/future, line-merge anomalies, new or unknown sourcetypes, mis-sized or unparsed events, splunkd parsing warnings — all bounded.

Self-check before reporting: is each defect genuinely absent from "splunk-parsing-last"? Drop the ones that are not, and say in one line how many you suppressed as already-known rather than listing them again. Save the updated sourcetype/signature fingerprint back to "splunk-parsing-last".

Reply exactly [SILENT] if clean; otherwise one concise, numbers-backed alert.
