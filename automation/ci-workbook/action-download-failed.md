---
type: LLM Prompt Fragment
title: "CI Workbook: Action archive download failed"
description: "CI workbook entry: transient handling for action archive download failed failures."
resource: "prompt://dryvist/automation/ci-workbook/action-download-failed"
tags: ["automation", "ci-workbook", "transient"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"action-download-failed","class":"transient","match":{"log":"failed to download action|unable to (?:download|resolve) action|an action could not be found"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/action-download-failed.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Downloading an action archive failed during job setup. Rerun once. If the action reference is genuinely missing, the next failure carries a different signature.
