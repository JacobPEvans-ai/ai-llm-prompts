---
type: LLM Prompt
title: Hermes assistant task triage
description: Read-only personal task project review and proposed dispositions.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-task-triage
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
  variable: hermes_agent_assistant_task_triage_prompt
---
Review your own task project and keep it honest.

Look for: items overdue by enough to be misleading, items with no due date
that have sat untouched long enough to be stale, duplicates, and anything
finished in practice but still open. Propose a specific disposition for each
— reschedule to a named date, close, merge into another item, or drop — and
ask for confirmation on anything you are not confident about.

Change nothing without being asked. Read and recommend only.

Group by disposition rather than listing everything flatly. If the project
is in good shape, reply with exactly [SILENT] and nothing else.

{{ hermes_agent_assistant_exclusion_clause }}
