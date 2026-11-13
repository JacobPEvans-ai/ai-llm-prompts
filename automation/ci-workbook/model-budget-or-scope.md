---
type: LLM Prompt Fragment
title: "CI Workbook: Model budget or key scope"
description: "CI workbook entry: human handling for model budget or key scope failures."
resource: "prompt://dryvist/automation/ci-workbook/model-budget-or-scope"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"model-budget-or-scope","class":"human","match":{"log":"budget has been exceeded|key not allowed to access model"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/model-budget-or-scope.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

The model router refused the request on budget or key scope. Configuration must change; no commit on the branch fixes it. Escalate.
