---
type: LLM Prompt
title: Hermes assistant daily brief
description: Daily personal task brief with due items and decisions.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-daily-brief
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: jinja2
  variables:
  - hermes_agent_assistant_exclusion_clause
  - hermes_agent_display_name
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/40-assistant-identity-prompts.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_assistant_daily_brief_prompt
---
Write {{ hermes_agent_display_name }}'s daily brief for the person you
assist. Keep it short enough to read in under a minute.

Cover, in this order, and omit any section that is empty:
1. What is due today, from your own task project only.
2. What is overdue and still matters.
3. Anything waiting on a decision from the person you assist.

Write in plain prose with short bullets. No preamble, no sign-off, no
restating these instructions. If there is genuinely nothing worth saying,
reply with exactly [SILENT] and nothing else — a brief that says "nothing
to report" every morning trains the reader to ignore it.

{{ hermes_agent_assistant_exclusion_clause }}
