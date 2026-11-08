---
type: LLM Prompt
title: Hermes router capacity digest
description: Daily router capacity metrics and changes against a recalled baseline.
resource: prompt://dryvist/auto-ai-agent/hermes-router-capacity-digest
tags:
- hermes
- autonomous-agent
- cron
timestamp: 2026-11-08T19:00:00Z
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/45-recurring-catalog.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_router_capacity_digest_cron_prompt
---
HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from auto-ai-agent/hermes-reporting/status-levels.md: green (healthy, no action), yellow (degraded, unverified, flapping or above baseline; look when convenient), red (failing or down; act now) - pick the worst level that applies, and use no other status emoji.

Daily router-capacity digest. The router already emits ONE metric event per day under syslog identifier "llm-serving-share", carrying `requests`, `local_share`, `overflow_share`, `caller_429_rate`, `window` and `computed_at` — read it from the log platform (never the host). Recall memory key "router-capacity-digest-last" (yesterday's `caller_429_rate` and `requests`) so the report is a genuine day-over-day comparison, not an isolated number. Report today's requests, the 429 rate and how it moved versus yesterday, and the overflow share. If the 429 rate genuinely regressed (meaningfully worse, not day-to-day noise) or requests dropped to near zero (a silent metric-emission gap, not low real traffic), say so plainly as the headline; otherwise lead with "capacity nominal". If no event landed in the log platform for today at all, report that as the finding — a missing event is a pipeline defect, never silence. Save today's numbers back to "router-capacity-digest-last".