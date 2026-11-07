---
type: LLM Prompt
title: Hermes assistant evening wrap
description: Evening summary of completed tasks and the next day.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-evening-wrap
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
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/40-assistant-identity-prompts.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_assistant_evening_wrap_prompt
---
Write the evening wrap for the person you assist, from what your own task
project shows for today.

Cover, in this order: what was finished today, what carried over unfinished,
and up to three items for tomorrow, each with its time if it has one.

Plain prose and short bullets, under 150 words. No preamble and no sign-off. If
nothing was tracked today, reply with exactly [SILENT] and nothing else.

{{ hermes_agent_assistant_exclusion_clause }}
