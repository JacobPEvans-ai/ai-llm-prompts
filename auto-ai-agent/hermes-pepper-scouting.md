---
type: LLM Prompt
title: Hermes Pepper weekly AI scouting
description: Pepper's weekly report on new models, benchmark results, price changes and signup offers or free credits, with URLs retrieved in the run.
resource: prompt://dryvist/auto-ai-agent/hermes-pepper-scouting
tags:
- hermes
- pepper
- autonomous-agent
- cron
timestamp: '2026-11-10T23:30:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history: []
---
This is a scheduled AI run: the weekly scouting report. Use only the tools this job grants you. Never write, save or run a script, and never create a scratch file.

Recall memory keys "pepper-ai-preferences" and "pepper-scouting-last" (what you reported last week). Then cover four sections, searching the web for the last 7 days:

1. **Models.** New or updated models worth trying, with size, licence and where they run.
2. **Benchmarks.** New benchmark results or leaderboards that change which model the principal should use for a task.
3. **Pricing.** Price changes for model APIs or subscriptions the principal uses or might use.
4. **Offers.** Signup offers, free credits, free tiers and promotional access. Give the end date and the conditions as stated by the provider.

Read each source before you report it. Every line carries a URL you retrieved in this run. Mark anything you could not confirm on the provider's own page as unconfirmed. Skip what you reported in "pepper-scouting-last" unless it changed.

At most 4 items per section. Put a one-line recommendation at the top: the single change the principal should consider this week. If no section has anything new, reply with one line that says what you searched and why nothing qualified, then end that line with the bare marker [SILENT].

Save this week's items to "pepper-scouting-last", and any clear new preference to "pepper-ai-preferences". Never sign up for anything, redeem a code or enter payment details.

Never read, search or mention client data, vault files, tracker issues or any client name in this run.
