---
type: LLM Prompt Fragment
title: "CI Workbook: File size limit"
description: "CI workbook entry: recipe handling for file size limit failures."
resource: "prompt://dryvist/automation/ci-workbook/file-size-limit"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"file-size-limit","class":"recipe","match":{"log":"exceeds (?:\\d+|n)kb limit|check file sizes"},"reproduce":null}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/file-size-limit.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A file exceeds the repository's size limit. Split it at a section boundary into a second file, link the two, and update any index or loader that lists files. Keep every line of content; do not summarize.
