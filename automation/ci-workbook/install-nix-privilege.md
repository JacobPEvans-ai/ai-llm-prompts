---
type: LLM Prompt Fragment
title: "CI Workbook: Nix install needs privilege"
description: "CI workbook entry: human handling for nix install needs privilege failures."
resource: "prompt://dryvist/automation/ci-workbook/install-nix-privilege"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"install-nix-privilege","class":"human","match":{"log":"sudo: a (?:password|terminal) is required|install nix[\\s\\S]*sudo"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/install-nix-privilege.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Installing Nix on the runner needs privileges the runner lacks. This is runner configuration. Escalate.
