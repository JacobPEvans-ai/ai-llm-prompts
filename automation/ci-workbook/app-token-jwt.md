---
type: LLM Prompt Fragment
title: "CI Workbook: App private key invalid"
description: "CI workbook entry: human handling for app private key invalid failures."
resource: "prompt://dryvist/automation/ci-workbook/app-token-jwt"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"app-token-jwt","class":"human","match":{"log":"json web token could not be decoded"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/app-token-jwt.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

The GitHub App private key secret is malformed or belongs to a different App. Escalate.
