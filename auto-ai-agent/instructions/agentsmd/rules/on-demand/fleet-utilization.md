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
  - repository: jpe-ai-agents/ai-llm-prompts
    path: "auto-ai-agent/instructions/agentsmd/rules/on-demand/fleet-utilization.md"
    note: New rule.
---

# Fleet utilization

Applies when one lead session coordinates several long-lived worker sessions. Doctrine and terms: the
`premium-agent-orchestration` skill in the `ai-delegation` plugin. A session is busy while a task or a background job
of its own is running; otherwise it is idle.

- **Roster.** The lead names the worker sessions and which one of them sweeps, and writes both at the top of
  the sweeper's report file.
- **Idle sweep.** Every 15 minutes the sweeper, never the lead, asks every session on the roster for one line:
  busy and on what, or idle and its next `QUEUE` item. It appends the answers to its report file.
- **Lead review.** Every 30 minutes the lead reads the sweeper's report file and reassigns work.
- **Productivity check.** Once an hour the sweeper appends one line to the same file: sessions busy out of the
  roster total, and idle minutes in the last hour.
- **`QUEUE` block.** Each worker keeps one at the top of its report file: ranked items, each with a check that
  answers yes or no.

All three loops follow `loop-cadence.md` (durable marker, minimum interval) and the Schedules rule in
`operating-core.md` for their minutes.
