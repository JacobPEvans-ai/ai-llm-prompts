---
type: LLM Prompt Fragment
title: "CI Workbook: Nix flake check"
description: "CI workbook entry: recipe handling for nix flake check failures."
resource: "prompt://dryvist/automation/ci-workbook/nix-flake-check"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"nix-flake-check","class":"recipe","match":{"log":"nix flake check|check flake|failed assertions|error: builder for"},"reproduce":"nix flake check --print-build-logs"}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/nix-flake-check.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Reproduce with the command above and read the first error, not the last. Fix the evaluation or build error at its source. Never add an option to silence an assertion.
