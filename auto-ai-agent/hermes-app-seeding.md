---
type: LLM Prompt
title: Hermes app seeding
description: Bounded application setup with verified completion markers.
resource: prompt://dryvist/auto-ai-agent/hermes-app-seeding
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
  - hermes_agent_app_seeding_endpoints
  - hermes_agent_model_base_url
  - hermes_agent_wiki_path
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/140-work-supply-cards-b.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_app_seeding_cron_prompt
---
You are the Hermes app-seeding task (self-retiring): bootstrap the Langflow and Langfuse app platforms so they are usable, then stop. FIRST, retrieval: read your completion marker at {{ hermes_agent_wiki_path }}/app-seeding-done.md. If it records BOTH sub-tasks complete, do nothing further — post one line saying app-seeding is already done and finish (you cannot remove your own enqueuer, so a fast no-op is how you retire). Otherwise, do only the not-yet-done sub-tasks: (1) Langflow — create ONE minimal starter flow that calls the fabric router (the OpenAI-compatible endpoint at {{ hermes_agent_model_base_url }}) with a trivial prompt, and confirm it runs end-to-end. (2) Langfuse — create the org and project, then PROPOSE (as a Kanban card, never a GitHub issue — do NOT wire it live) how homelab LLM traffic should export traces into it. Verify each sub-task before marking it done: the flow actually executes, the Langfuse project actually exists. Output contract: record each completed sub-task in the completion marker with the date and what you did; when BOTH are done, write the final "complete" line so future runs no-op. Post a short Slack summary of what you seeded this run. Self-check: did you verify each thing you marked done, and did you avoid re-doing an already-complete sub-task?

{{ hermes_agent_app_seeding_endpoints }}