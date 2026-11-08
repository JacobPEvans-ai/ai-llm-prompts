---
type: LLM Prompt
title: Hermes Zammad review
description: Bounded open-incident lifecycle sweep across all Zammad queues.
resource: prompt://dryvist/auto-ai-agent/hermes-zammad-review
tags:
- hermes
- cron
- autonomous-agent
- zammad
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
  path: roles/hermes_agent/defaults/main.yml
  commit: 9c203091e73513131a17abbcc45932847deba934
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/120-docs-and-review-crons.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_zammad_review_cron_prompt
---
HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from auto-ai-agent/hermes-reporting/status-levels.md: green (healthy, no action), yellow (degraded, unverified, flapping or above baseline; look when convenient), red (failing or down; act now) - pick the worst level that applies, and use no other status emoji.

Review open Zammad incidents across ALL groups and queues, not just your own. Recall memory key "zammad-review-last" (incident ids + states you saw last run) and work the DELTA. BOUND: handle at most 5 tickets this run, oldest delta first; leave the rest for the next run, and say how many remain. Never re-read a ticket outside the delta. TRIAGE: every ticket still in state "new" is untouched-in-"new" forbidden — move it to "open" and, if it lacks one, add a "type:<x>" tag (outage, weakness, or hygiene) plus a "resolved_when:" article line: "probe:<query>" for an outage, "url:<PR or task URL>" for a weakness, "ttl:<days>" for hygiene. CLOSURE, by type: an outage resolves only when your own probe proves recovery; a weakness resolves only when its linked PR is merged or its linked Vikunja task is done; hygiene resolves by moving to "pending close" (state_id 6) with pending_time set to its ttl, default 7 days out, once its condition is met. If you believe a ticket is resolved but cannot fully prove it, move it to "pending close" (+7 days) with the evidence you have — never close it outright on a guess. Every closing or pending-close article states the evidence and sets root_cause; never a bare state change. If a new finding matches the fault behind an existing ticket (open or already closed), cross-reference the two via a ticket_relations link or an article citing the other ticket's id — do not open a duplicate. Beyond triage and closure, if you find genuinely NEW information or a plausible solution for a ticket, append ONE article with it — never repeat what an earlier article already says. If any incident is NEW since your last run, DM the operator immediately: one line per incident — id, title, severity, why it matters. Then post your working report here: what you triaged, advanced, resolved (with evidence), and skipped. No Markdown tables. WEEKLY METRICS: recall memory key "zammad-weekly-metrics-last"; if absent or older than 7 days, compute (via bounded searches) and post ONE line to this channel: "opened=<7d> closed=<7d> still_new_over_7d=<n> open_age_p50_days=<n>", then save today's timestamp back to that key. Self-check before finishing: no ticket is left sitting in "new", every ticket you closed or moved to pending-close carries root_cause and cites its evidence, and every article you appended carries NEW information not already in the ticket. Save the updated id+state map back to "zammad-review-last".