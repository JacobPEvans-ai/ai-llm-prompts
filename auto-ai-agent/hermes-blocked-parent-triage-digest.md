---
type: LLM Prompt
title: Hermes blocked parent triage digest
description: Daily report of blocked parent cards and waiting children.
resource: prompt://dryvist/auto-ai-agent/hermes-blocked-parent-triage-digest
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
  path: roles/hermes_agent/defaults/main/45-recurring-catalog.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_blocked_parent_triage_digest_cron_prompt
---
Daily blocked-parent triage digest (a parent card stuck in blocked/needs_input status starves every child waiting on it, since recompute_ready only promotes a child once ALL its parents are done or archived). Use your kanban tool to list cards and their parent/child relations and current status. Recall memory key "blocked-parent-triage-last" (parent card ids you already flagged) and work the delta — do not re-flag a parent you already reported unless its status changed. Find every PARENT card that has been blocked or awaiting input for more than 7 days AND has at least one child card that is otherwise ready to run. For each, name the parent's id and age in days, the blocked reason if the card has one, and how many children it is starving. You can only observe and report — never mark a parent done, archived, or blocked yourself; that is the operator's call. If none are found, reply exactly [SILENT]. Save the flagged parent ids back to "blocked-parent-triage-last".