---
type: LLM Prompt Fragment
title: "CI Workbook: Required secret missing"
description: "CI workbook entry: human handling for required secret missing failures."
resource: "prompt://dryvist/automation/ci-workbook/missing-secret"
tags: ["automation", "ci-workbook", "human"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"missing-secret","class":"human","match":{"log":"copilot_github_token|base_url is empty|router base url secret|illegal header value|private_key is not set|no claude bot app token|either anthropic_api_key"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/missing-secret.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A workflow secret did not reach the job. Secrets are configured outside the repository. Escalate.
