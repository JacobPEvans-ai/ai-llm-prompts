---
type: LLM Prompt
title: Hermes assistant research
description: One queued personal research question per run with public sources.
resource: prompt://dryvist/auto-ai-agent/hermes-assistant-research
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
  variable: hermes_agent_assistant_research_prompt
---
Work through the Vikunja project titled "Donna research queue". Take the oldest
open item that asks a question and has no answer recorded yet, skipping any
that is technical.

Research it from public sources only. Write an answer of under 300 words that
states what is known, what is not, and the sources it rests on. Record the
answer on the item. Work one item per run. If you cannot finish it, stop
cleanly and leave a note on the item saying where you stopped.

After saving an answer, reply with the title of the item and a summary of
the answer in one sentence. If the queue is empty, or every open item is technical,
reply with exactly [SILENT] and nothing else. If you cannot read the queue at
all, say so in one line.

{{ hermes_agent_assistant_exclusion_clause }}
