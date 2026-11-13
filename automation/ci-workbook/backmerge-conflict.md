---
type: LLM Prompt Fragment
title: "CI Workbook: Back-merge conflict"
description: "CI workbook entry: human handling for back-merge conflict failures."
resource: "prompt://dryvist/automation/ci-workbook/backmerge-conflict"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"backmerge-conflict","class":"human","match":{"log":"back-?merge|merge conflict"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/backmerge-conflict.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A release back-merge has conflicts. A person resolves them. Escalate.
