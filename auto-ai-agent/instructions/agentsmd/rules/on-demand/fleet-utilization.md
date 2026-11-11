---
name: fleet-utilization
description: Estate cadences, QUEUE block and hourly numbers for keeping orchestrated worker sessions busy. Doctrine lives in a skill.
type: LLM Prompt
title: "Fleet utilization"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/fleet-utilization"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-11T02:34:00Z"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: "auto-ai-agent/instructions/agentsmd/rules/on-demand/fleet-utilization.md"
    note: New rule.
---

# Fleet utilization

For the doctrine, follow the `premium-agent-orchestration` skill in the `ai-delegation` plugin.

- The idle sweep runs on the cheapest session that can do it, never on the lead.
- The idle sweep runs every 15 minutes and the lead review every 30 minutes. Keep both off :00, :15, :30 and :45
  (see Schedules in `operating-core.md`).
- The productivity check runs at :50 each hour. The hourly report carries two numbers: sessions busy out of total,
  and idle minutes in the last hour.
- Each worker keeps a `QUEUE` block at the top of its report file: ranked items, each with a yes/no check.
