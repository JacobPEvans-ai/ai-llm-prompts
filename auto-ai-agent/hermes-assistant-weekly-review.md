---
type: LLM Prompt
title: Hermes assistant weekly review
description: Weekly personal task review with upcoming decisions.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-weekly-review
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
  variable: hermes_agent_assistant_weekly_review_prompt
---
Write the weekly review for the person you assist, covering the last seven
days in your own task project.

Cover what was finished, what slipped and why as far as the items show, and
the decisions the coming week needs. List at most three decisions, each as one
line naming the decision and the date it is needed by.

Under 250 words. Plain prose and short bullets. No preamble and no sign-off.

{{ hermes_agent_assistant_exclusion_clause }}
