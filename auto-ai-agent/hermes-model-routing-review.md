---
type: LLM Prompt
title: Hermes model routing review
description: Read-only review of tracked public model routing resources.
resource: prompt://dryvist/auto-ai-agent/hermes-model-routing-review
tags:
- hermes
- autonomous-agent
- cron
timestamp: 2026-11-08T19:00:00Z
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/46-recurring-catalog-model-routing-review.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_model_routing_review_cron_prompt
---
You are reviewing two model routing resources that the operator asked you to track: (1) awesome-model-routing (https://github.com/yenanjing/awesome-model-routing), an auto-refreshing curated list across 8 categories (routers, gateways, proxies, inference engines, orchestration, API management, cost optimization, research) — ignore its daily bot star-count refreshes, see Baseline method below; (2) claude-code-router (https://github.com/musistudio/claude-code-router), a local model gateway/control plane for coding agents supporting Claude Code, Codex, Grok CLI, Kimi CLI, Kilo Code, OpenCode, Pi, ZCode, and WorkBuddy, with provider management, model routing with conditions/retries/fallbacks, tool extensions, observability, and an AgentClaw relay.

Baseline method (do this, don't trust any numbers already in this prompt): 1) recall memory key "model-routing-review-last" (last run's reported baseline line: repo count + CCR stars + latest release tag); if absent this is your first run, so just save a baseline and reply exactly [SILENT]. 2) Fetch the README at today's HEAD and at the commit from roughly 7 days ago; diff the repo slugs extracted from the github.com links in both versions — additions/removals are real changes, star-count deltas are not. 3) List claude-code-router releases newer than the recorded latest tag. 4) End your report with the updated baseline line: baseline: N repos | CCR stars | CCR latest tag+date. Save it back to "model-routing-review-last".

Task: check both repos for changes since the last review. Report any new repos added to awesome-model-routing (with stars), any new releases or major changes to claude-code-router, and any notable new projects in the routing space worth flagging. If nothing changed, reply with exactly [SILENT]. If there are changes, highlight the top 2-3 most interesting ones and why they matter.

HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from auto-ai-agent/hermes-reporting/status-levels.md: green (healthy, no action), yellow (degraded, unverified, flapping or above baseline; look when convenient), red (failing or down; act now) - pick the worst level that applies, and use no other status emoji.

ABSOLUTE SCOPE LIMIT: this is a tracking/reminder job, not an engineering task. Do not attempt to deploy, configure, or modify any of these tools — only report what changed and whether it is worth the operator's attention.