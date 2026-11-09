---
type: LLM Prompt
title: Hermes self-audit
description: Scheduled self-correction loop — read your own Slack output back, sweep Splunk for your own errors, prove memory/cron/kanban healthy, file correction cards.
resource: prompt://dryvist/auto-ai-agent/hermes-self-audit
tags: [hermes, cron, autonomous-agent, observability]
timestamp: 2026-08-23T00:00:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/nix-hermes
    path: data/skills/dryvist/self-audit/SKILL.md
    note: companion skill carrying the full procedures; this prompt sets the run's posture
---
Run a complete audit of your own operation right now using the dryvist/self-audit skill. First recall memory key "self-audit-last" — it is your fingerprint from the previous run (per-channel Slack cursors, discovered Splunk trace coordinates, known error signatures, per-subsystem consecutive-down counts, cards already filed); on the very first run it will be empty, which is valid. Then work only the delta since that fingerprint: read your own recent Slack posts back and critique them for repetition, broken [SILENT] discipline, garbled output, wrong routing, and unkept follow-up promises; sweep Splunk with strictly bounded queries for your own new or escalating error signatures; and prove memory/hindsight, the cron fleet, kanban, and both transport paths healthy with concrete evidence per probe. File one kanban card per deduped defect; escalate to Zammad only when a subsystem has been down two consecutive runs or the finding is security-shaped. Save the updated fingerprint back to "self-audit-last". If every probe passed and nothing new was found, reply with exactly [SILENT]. Otherwise end with one concise digest of what you checked, what you found, and what you filed.
