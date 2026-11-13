---
type: LLM Prompt Fragment
title: "CI Workbook: AI agent execution failed"
description: "CI workbook entry: human handling for ai agent execution failed failures."
resource: "prompt://dryvist/automation/ci-workbook/ai-agent-exec-failed"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"ai-agent-exec-failed","class":"human","match":{"log":"claude execution failed|codex exited with code|openai_api_key is required|pr-agent review failed|github copilot cli|release highlights (?:agent|job) (?:did not|failed)"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/ai-agent-exec-failed.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

An AI agent step exited without a usable result. Its credentials or provider configuration are wrong, or the model failed. A code change on the branch does not help. Never send an AI workflow failure to a fixing agent. Escalate.
