---
type: LLM Prompt
title: Hermes pepper intake
description: Bounded issue intake with idempotent Kanban cards.
resource: prompt://dryvist/auto-ai-agent/hermes-pepper-intake
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
  - hermes_agent_pepper_card_prompt
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/40-assistant-identity-prompts.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_pepper_intake_prompt
---
Search only your authorized YouTrack issues with a page size of 10. Request
only issue keys, State and Priority; never request summaries, descriptions,
comments or any other issue text. Create at most 10 new Kanban cards
per run, one per issue, in order Critical, In Progress, Open, Waiting; within
each group preserve the returned key order. Use pepper-youtrack:<issue-key>
as the native kanban create --idempotency-key value. Check existing and completed cards before creating;
reuse the same key after interruption or retry, and never create a duplicate.
Each card runs in the default home and contains this instruction:
{{ hermes_agent_pepper_card_prompt }}
