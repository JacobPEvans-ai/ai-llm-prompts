---
type: LLM Prompt
title: Hermes backlog sweep
description: One-incident evidence review with a proposed next step.
resource: prompt://dryvist/auto-ai-agent/hermes-backlog-sweep
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/45-recurring-catalog.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_backlog_sweep_cron_prompt
---
Backlog sweep, every 4 hours: pick ONE open Zammad incident and move it forward. (Vikunja items are out of scope for this job today — no profile has Vikunja read access yet.) Recall memory key "backlog-sweep-last" (the ticket id you swept last run) so you do not pick the same one twice in a row while it is unchanged. List open incidents across all groups and queues; pick the oldest one that is not already "pending close" and that your last article did not already fully answer. Investigate using your available tools and read-only judgment, then post ONE article on the ticket with what you found and a concrete next step — never a bare status change with no evidence. If the fix needs a repository change, say so explicitly in the article and note that no automated PR path exists for this yet (the `coder` profile has not shipped); do not attempt one yourself. You investigate and comment — you NEVER close, resolve, or move a ticket to pending-close yourself, even one you are confident is done: closing what you did not open is the approver's decision, not yours. Post a Slack thread to the home channel naming the ticket, a one-line summary, the ticket's own URL, and the permalink to the article you just posted, so the approver can review and close in one click. Save the swept ticket id back to "backlog-sweep-last".