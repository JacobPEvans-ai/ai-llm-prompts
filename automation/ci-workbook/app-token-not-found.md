---
type: LLM Prompt Fragment
title: "CI Workbook: App token installation not found"
description: "CI workbook entry: human handling for app token installation not found failures."
resource: "prompt://dryvist/automation/ci-workbook/app-token-not-found"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"app-token-not-found","class":"human","match":{"log":"create-github-app-token[\\s\\S]*\\bnot found\\b|generate github app token\\W*not found"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/app-token-not-found.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

The GitHub App is not installed on the repository, or the App id secret is wrong. Escalate.
