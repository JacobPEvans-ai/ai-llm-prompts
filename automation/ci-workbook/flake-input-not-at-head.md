---
type: LLM Prompt Fragment
title: "CI Workbook: Flake input behind its branch head"
description: "CI workbook entry: recipe handling for flake input behind its branch head failures."
resource: "prompt://dryvist/automation/ci-workbook/flake-input-not-at-head"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"flake-input-not-at-head","class":"recipe","match":{"log":"owned inputs are at branch head|not at (?:the )?branch head"},"reproduce":"nix flake metadata"}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/flake-input-not-at-head.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A pinned flake input lags its branch head. Run nix flake update for each input the log names, and commit only flake.lock.
