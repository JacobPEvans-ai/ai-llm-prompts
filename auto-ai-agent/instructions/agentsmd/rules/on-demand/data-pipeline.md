---
name: data-pipeline
description: Observability and data-feed guidance for hub-first pipelines, fan-out, and dashboards. Read when changing telemetry sources, routes, or dashboards.
type: LLM Prompt
title: "Data pipeline"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/data-pipeline"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-10-18T12:18:06-04:00"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: jpe-ai-agents/ai-llm-prompts
    path: "auto-ai-agent/instructions/agentsmd/rules/on-demand/data-pipeline.md"
    note: New public rule.
---
# Data pipeline

## Hub-first

Route observability data through a shared hub. Use sources and native transforms
already available there before adding another collector.

## Fan-out

Send each source to every destination that supports its format. Avoid
source-specific destinations; use a single-destination route only when a
documented constraint requires it. Preserve duplicate feeds so destinations
can be compared; repair a failing route instead of removing it.

## Dashboards

Build dashboard entity sets from configuration, not returned series. Show a
missing series as stale with its age, then as no data since its last value; never
hide it.
