---
type: LLM Prompt
title: Hermes pricing diff
description: Weekly public model pricing changes against a saved baseline.
resource: prompt://dryvist/auto-ai-agent/hermes-pricing-diff
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
  variable: hermes_agent_pricing_diff_cron_prompt
---
Weekly OpenRouter pricing-diff sweep. Recall memory key "pricing-diff-last" (the model id -> prompt/completion price map you saved last run); if it is absent this is your first run, so just save a baseline and reply exactly [SILENT]. GET https://openrouter.ai/api/v1/models (public, no key) and build the same map from its current contents. Compare only the models this estate actually serves through — cross-reference ids against the router registry conversationally if you have Docs MCP access to it; otherwise compare every id in both maps. Report ONLY a model whose prompt or completion price changed since last run, with the old price, the new price, and the percent change. If nothing changed, reply exactly [SILENT]. Never propose or attempt to edit the router registry yourself — you can only observe and report; a registry change is a human/coder decision at the file `llm-models.d/` owns (AGENTS.md's hard rule). Save this run's full map back to "pricing-diff-last" regardless of whether anything changed.