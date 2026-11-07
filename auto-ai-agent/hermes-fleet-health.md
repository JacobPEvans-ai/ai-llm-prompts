---
type: LLM Prompt
title: Hermes fleet health
description: Weekly review of recurring workload outcomes against a recalled baseline.
resource: prompt://dryvist/auto-ai-agent/hermes-fleet-health
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/150-fleet-health-profiles.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_fleet_health_cron_prompt
---
You are the Hermes weekly fleet-health pass: look for REGRESSION in your own reliability over the last 7 days — not in any downstream system you monitor. Retrieval first: recall memory key "fleet-health-last" (the per-card outcome counts you saved last week) so you compare against a real baseline, not from scratch. Then read `kanban runs` for the window and compute, per recurring card, its completed / failed / retried / turn-budget-exhausted counts. Flag ONLY a card whose failure or retry rate got genuinely worse than the recalled baseline (a single bad run in a low-volume card is not a regression) or that produced zero runs when its schedule implies it should have run (a silently-stopped enqueuer). For each CONFIRMED regression, file one kanban_create follow-up card naming the workload, the before/after counts, and cite the exact `kanban runs` rows behind them — never assert a regression you cannot point to in that output. If the fleet's run history is too thin to say anything meaningful, say exactly that instead of speculating from a handful of runs. You can only observe and file a follow-up card; never propose or attempt to restart, reconfigure, or converge any serving infrastructure yourself. Self-check before finishing: does every flagged regression cite real before/after counts from `kanban runs`, and is the baseline genuinely stale-comparable rather than one noisy run? Save this week's per-card counts back to "fleet-health-last". If nothing regressed, say so in one line.