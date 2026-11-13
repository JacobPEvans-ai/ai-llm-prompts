---
type: LLM Prompt Fragment
title: "CI Workbook: Workflow script path missing"
description: "CI workbook entry: human handling for workflow script path missing failures."
resource: "prompt://dryvist/automation/ci-workbook/script-path-missing"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"script-path-missing","class":"human","match":{"log":"\\.ai-workflows/\\S+: no such file"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/script-path-missing.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A reusable workflow could not find one of its own scripts, so its checkout ref is wrong. Fix the reusable workflow, not the calling repository. Escalate.
