---
type: LLM Prompt
title: Hermes assistant nudge
description: Personal task blockers and the decisions needed to advance them.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-nudge
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-10T23:00:00Z'
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
Use only the tools this job grants you. Never write, save or run a script,
and never create a scratch file; if a check needs a tool you do not have, skip
that check and name it in your reply.

Find what is stalled specifically on the person you assist, and say so.

A thing qualifies only if THEY are the blocker: a question you asked that
they have not answered, an approval nobody can proceed without, a task
assigned to them that has not moved. Work that is merely unfinished does
NOT qualify — someone else is already carrying it.

Consult your memory before writing so you do not raise the same item twice
in a row. Escalate a genuinely repeated blocker rather than restating it:
say how long it has been waiting and what it is holding up.

One line per item, naming the item and the decision needed.

If nothing is actually blocked on them, reply with one line that says what you
checked and why nothing qualifies, then end that line with [SILENT]. For
example: `Checked 4 open questions and 9 assigned tasks; none waits on them. [SILENT]`

{{ hermes_agent_assistant_exclusion_clause }}
