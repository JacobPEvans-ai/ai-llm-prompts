---
type: LLM Prompt Fragment
title: "CI Workbook: Dependency review found a vulnerability"
description: "CI workbook entry: human handling for dependency review found a vulnerability failures."
resource: "prompt://dryvist/automation/ci-workbook/dependency-review-vulnerable"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"dependency-review-vulnerable","class":"human","match":{"log":"dependency review detected vulnerable|vulnerable packages?"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/dependency-review-vulnerable.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A dependency update introduces a known vulnerability. This needs a review decision, not a code fix. Escalate.
