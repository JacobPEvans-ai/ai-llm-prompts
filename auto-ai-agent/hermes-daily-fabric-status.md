---
type: LLM Prompt
title: Hermes daily fabric status
description: Hourly AI-fabric status and delta-reporting prompt.
resource: prompt://dryvist/auto-ai-agent/hermes-daily-fabric-status
tags: [hermes, cron, autonomous-agent]
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
    commit: 5fe2eb8f6df8203ea5dd17f1e49053f0a195b490
---
HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from auto-ai-agent/hermes-reporting/status-levels.md: green (healthy, no action), yellow (degraded, unverified, flapping or above baseline; look when convenient), red (failing or down; act now) - pick the worst level that applies, and use no other status emoji.

Check the homelab AI-fabric status: LLM router health, Hermes gateway health, Hindsight memory-pool health, and any merge-ready PRs. Recall your last posted fingerprint and its timestamp from memory (key "fabric-status-last"). If today's status is unchanged from that fingerprint AND it has been under 24h since the fingerprint's timestamp, post ONLY a one-line update: "No change since <timestamp> — still <short status>." and save nothing new. Otherwise post the full one-paragraph heartbeat as before, and save today's fingerprint + timestamp to memory under that key. A few sentences is plenty when you do post the full version — this runs hourly, so keep it short either way.
