---
type: LLM Prompt Fragment
title: "CI Workbook: Privileged VPN download test"
description: "CI workbook entry: never_retry handling for privileged vpn download test failures."
resource: "prompt://dryvist/automation/ci-workbook/never-retry-download-vpn"
tags: ["automation", "ci-workbook", "never_retry"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"never-retry-download-vpn","class":"never_retry","match":{"log":"download_vpn"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/never-retry-download-vpn.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

This test knocks shared runners offline. Never rerun it automatically.
