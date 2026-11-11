---
type: LLM Prompt Fragment
title: Hermes daily status kanban summary
description: Shared board status summary appended to the fabric report.
resource: prompt://dryvist/auto-ai-agent/hermes-daily-status-kanban-summary
tags:
- hermes
- autonomous-agent
timestamp: '2026-11-11T22:36:33Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: jinja2
  variables:
  - hermes_agent_dashboard_port
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/44-slack-and-status-cron-vars.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_daily_status_kanban_summary
---
Board summary, appended once at the end of your report: use your kanban
tool to get today's card count per status (ready, in_progress, blocked,
done, and any other status it reports). One line, e.g. "board: 3 ready, 1
in_progress, 2 blocked, 14 done today". For fetched board items, follow the
shared report contract (`hermes-report-contract.md`), including its priority
counts, completed-action outcomes, and accounting for every fetched
urgent item. If a card has been in_progress or blocked for unusually long
relative to your other observations this run, name it by id with a link into
the dashboard (http://localhost:{{ hermes_agent_dashboard_port }}/) so the
operator can open it directly. This line is informational and never on its
own reason to escalate to the issues channel.
