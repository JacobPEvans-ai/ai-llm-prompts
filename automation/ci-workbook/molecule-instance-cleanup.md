---
type: LLM Prompt Fragment
title: "CI Workbook: Molecule instance cleanup"
description: "CI workbook entry: transient handling for molecule instance cleanup failures."
resource: "prompt://dryvist/automation/ci-workbook/molecule-instance-cleanup"
tags: ["automation", "ci-workbook", "transient"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"molecule-instance-cleanup","class":"transient","match":{"log":"paramiko|wait for instance\\(s\\) deletion"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/molecule-instance-cleanup.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Molecule could not reach or delete its test instance. This is test infrastructure, not the role under test. Rerun once.
