---
type: LLM Prompt
title: Hermes assistant nudge
description: Personal task blockers and the decisions needed to advance them.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-nudge
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
  variable: hermes_agent_assistant_nudge_prompt
---
Find what is stalled specifically on the person you assist, and say so.

A thing qualifies only if THEY are the blocker: a question you asked that
they have not answered, an approval nobody can proceed without, a task
assigned to them that has not moved. Work that is merely unfinished does
NOT qualify — someone else is already carrying it.

Consult your memory before writing so you do not raise the same item twice
in a row. Escalate a genuinely repeated blocker rather than restating it:
say how long it has been waiting and what it is holding up.

One line per item, naming the item and the decision needed. If nothing is
actually blocked on them, reply with exactly [SILENT] and nothing else.

{{ hermes_agent_assistant_exclusion_clause }}
