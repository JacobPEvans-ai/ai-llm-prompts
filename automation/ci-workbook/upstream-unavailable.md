---
type: LLM Prompt Fragment
title: "CI Workbook: Upstream service unavailable"
description: "CI workbook entry: transient handling for upstream service unavailable failures."
resource: "prompt://dryvist/automation/ci-workbook/upstream-unavailable"
tags: ["automation", "ci-workbook", "transient"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"upstream-unavailable","class":"transient","match":{"log":"service unavailable|bad gateway|gateway time-?out|connection (?:refused|reset by peer)|econnreset"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/upstream-unavailable.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A dependency answered with a gateway or availability error. Rerun once; a repeat on the same head goes to the incident queue.
