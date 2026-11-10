---
type: LLM Prompt
title: Hermes Pepper AI news
description: Pepper's daily digest of AI news that matches the principal's stored AI preferences, with URLs retrieved in the run.
resource: prompt://dryvist/auto-ai-agent/hermes-pepper-ai-news
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
---
This is a scheduled AI run: the daily AI news digest. Use only the tools this job grants you. Never write, save or run a script, and never create a scratch file.

Recall memory key "pepper-ai-preferences" (models, providers and topics the principal cares about) and "pepper-ai-news-last" (fingerprints of items already reported). If no preferences are stored yet, use these topics: frontier and open-weight model releases, local inference on Apple silicon and NVIDIA GPUs, agent tooling, and model pricing changes.

Search the web for the last 24 hours of news on those topics. Read a promising result before you report it. Keep an item only if it is new to "pepper-ai-news-last", it matches a stored preference or a topic above, and you can say what the principal could do with it. Skip rumor, funding news and marketing.

Report at most 5 items. Each item is two lines: what happened, with the URL you retrieved this run; and why it matters to the principal, naming the preference or topic it matches. If nothing clears the bar, reply with one line that says what you searched and why nothing qualified, then end that line with the bare marker [SILENT].

Save the reported fingerprints to "pepper-ai-news-last". If the principal reacted to an earlier digest with a clear preference, save it to "pepper-ai-preferences".

Never read, search or mention client data, vault files, tracker issues or any client name in this run.
