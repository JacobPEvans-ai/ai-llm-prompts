---
type: LLM Prompt Fragment
title: "CI Workbook: Home Manager conflicting definition"
description: "CI workbook entry: recipe handling for home manager conflicting definition failures."
resource: "prompt://dryvist/automation/ci-workbook/hm-conflicting-definition"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"hm-conflicting-definition","class":"recipe","match":{"log":"conflicting definition values|is defined multiple times"},"reproduce":null}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/hm-conflicting-definition.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Two modules set the same option. Find both definitions the log names. Keep the one owned by the module the branch changed, and remove or merge the other with lib.mkDefault or lib.mkForce only where ownership is clear.
