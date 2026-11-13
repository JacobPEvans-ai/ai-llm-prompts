---
type: LLM Prompt
title: "Tool role map example"
description: "Example product mappings for shared agent roles; the operator's real map stays private."
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/docs/tool-role-map.example"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-10-18T12:18:06-04:00"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: jpe-ai-agents/ai-llm-prompts
    path: "auto-ai-agent/instructions/agentsmd/docs/tool-role-map.example.md"
    note: New public example.
---
# Tool role map example

These are EXAMPLE products only; the operator's real role map is private and loaded every session.

| Role | Purpose | Example product |
| --- | --- | --- |
| incident tracker | Records incidents and security findings | ServiceNow |
| task tracker | Tracks follow-ups and deferred work | Jira |
| private docs site | Stores private operational documentation | Confluence |
| secret store | Stores and serves secrets | AWS Secrets Manager |
| credential delivery | Delivers credentials to tools and sessions | 1Password CLI |
| notification target | Delivers notifications | Microsoft Teams |
