---
name: agent-notifications
description: When an unattended agent notifies a human vs stays quiet.
type: LLM Prompt
title: "Agent Notifications"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/agent-notifications"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-09T16:11:00Z"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-assistant-instructions
    path: "agentsmd/rules/agent-notifications.md"
    note: Migrated from the instruction repository.
---

# Agent Notifications

Covers **autonomous, unattended agents** (chat gateways, scheduled jobs, alert-triggered runs), not an
interactive session. A human's attention is the scarcest resource; every channel that can page one competes
for the same budget.

## When to notify, and tone

- **Page**: something broke that needs action now (failed deploy, security alert, service down). Use the most
  interruptive channel for the severity.
- **Inform**: worth knowing, not worth interrupting (daily status, a completed long job). Home/status channel,
  not a DM; never tighter cadence than the event changes — see [[loop-cadence]] for the rate-limit pattern.
- **Log only**: routine, expected, reversible — log pipeline, not chat. Most activity belongs here; silence is
  the default. Never send a "just checking in" or heartbeat message with no actionable content.
- **Tone**: actionable fact first, no preamble, no filler acknowledgments, no restating the question, no "I've
  gone ahead and...". See [[soul]] for the interactive-session equivalent. Match urgency to severity; follow
  [[technical-writing]] for prose.
- **Status lines**: in any multi-facet status (KPI bumps, reports, digests), put one component and one metric on each line, and start each line with 🟢 on target, 🟡 behind, or 🔴 failing or unmeasured.

Gateway-to-channel mapping is environment-specific, in the operator's own local files.
