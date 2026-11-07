---
type: LLM Prompt
title: Hermes assistant inbox groom
description: Inbox sorting with next steps and bounded due-date updates.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-inbox-groom
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
  variable: hermes_agent_assistant_inbox_groom_prompt
---
Groom the Vikunja project titled "Inbox". It holds the items the person you
assist added without sorting them.

For each unsorted item, either move it or leave it. If its intent is obvious
from its text, move it to the project it belongs to, add a next step to its
description, and set a due date only if the text names one. If its intent is
not obvious, leave it where it is and list it under "Needs you" with the single
question that would place it.

Delete nothing. Do not change an item that is already in a project.

Reply with the groomed items grouped by project, then the "Needs you" list. If
the inbox is empty, reply with exactly [SILENT] and nothing else.

{{ hermes_agent_assistant_exclusion_clause }}
