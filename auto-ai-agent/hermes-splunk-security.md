---
type: LLM Prompt
title: Hermes Splunk security sweep
description: Bounded Splunk security-lens monitoring prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-splunk-security
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
Sweep Splunk with a security lens this run — firewall-drop spikes, auth-failure spikes, honeypot index hits, unexpected source IPs — all as bounded stats, compared against your remembered baselines. You are not limited to these; flag anything that looks like a threat. Record findings to memory. Reply exactly [SILENT] if clean; otherwise one concise, numbers-backed alert.
