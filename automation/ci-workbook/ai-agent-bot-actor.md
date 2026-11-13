---
type: LLM Prompt Fragment
title: "CI Workbook: AI agent refused a bot actor"
description: "CI workbook entry: human handling for ai agent refused a bot actor failures."
resource: "prompt://dryvist/automation/ci-workbook/ai-agent-bot-actor"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"ai-agent-bot-actor","class":"human","match":{"log":"initiated by non-human actor"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/ai-agent-bot-actor.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

An AI workflow refused to run for a bot-triggered event. The caller configuration decides this. Escalate.
