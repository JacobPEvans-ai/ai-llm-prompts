---
type: LLM Prompt Fragment
title: "CI Workbook: Token limit"
description: "CI workbook entry: recipe handling for token limit failures."
resource: "prompt://dryvist/automation/ci-workbook/token-limit"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"token-limit","class":"recipe","match":{"log":"exceeds n\\b.{0,40}token|token.{0,40}exceeds n\\b|check token limits"},"reproduce":null}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/token-limit.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

An always-loaded instruction file exceeds its token budget. Move detail into an on-demand file and leave a one-line pointer. Do not delete rules.
