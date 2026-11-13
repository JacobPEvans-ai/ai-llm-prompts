---
type: LLM Prompt Fragment
title: "CI Workbook: Zizmor workflow audit"
description: "CI workbook entry: recipe handling for zizmor workflow audit failures."
resource: "prompt://dryvist/automation/ci-workbook/zizmor"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"zizmor","class":"recipe","match":{"log":"zizmor"},"reproduce":"zizmor .github/workflows"}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/zizmor.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Zizmor flagged a workflow. Workflow edits are outside what an automated fix may publish, so this usually escalates. A fix outside .github/workflows, such as a composite action, follows zizmor's own remediation text.
