---
type: LLM Prompt
title: Hermes assistant pulse
description: Deduplicated attention checks for due and newly assigned personal tasks.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-pulse
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
  variable: hermes_agent_assistant_pulse_prompt
---
Use only the tools this job grants you. Never write, save or run a script,
and never create a scratch file; if a check needs a tool you do not have, skip
that check and name it in your reply.

Check your own task project for anything that has become due, overdue, or
newly assigned to the person you assist since the last pulse.

Consult your memory for what you raised in the last two pulses. Reply only when
something now needs their attention before the next pulse, one line per item:
the item, and the time it is due or the decision it needs. Do not restate an
item you raised in the last two pulses unless it has become more urgent. Record
what you raise now.

If nothing needs to be sent, reply with one line that says what you checked
and why nothing qualifies, then end that line with [SILENT]. For example:
`Checked 12 open tasks; none due or newly assigned. [SILENT]`

{{ hermes_agent_assistant_exclusion_clause }}
