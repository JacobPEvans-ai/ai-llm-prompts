---
type: LLM Prompt Fragment
title: "CI Workbook: Link check"
description: "CI workbook entry: recipe handling for link check failures."
resource: "prompt://dryvist/automation/ci-workbook/link-check"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"link-check","class":"recipe","match":{"log":"rejected status code|lychee|broken links?"},"reproduce":"lychee --no-progress ."}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/link-check.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A 429 or 5xx from a large site is transient: rerun once. A 404 is real: point the link at the moved target or remove it. Never add an exclusion to make the check pass.
