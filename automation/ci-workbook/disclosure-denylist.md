---
type: LLM Prompt Fragment
title: "CI Workbook: Disclosure denylist hit"
description: "CI workbook entry: human handling for disclosure denylist hit failures."
resource: "prompt://dryvist/automation/ci-workbook/disclosure-denylist"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"disclosure-denylist","class":"human","match":{"log":"disclosure denylist"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/disclosure-denylist.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

The disclosure scan matched restricted text in the diff, title or body. A person decides how to reword it. Never retry.
