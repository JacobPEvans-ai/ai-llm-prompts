---
type: LLM Prompt Fragment
title: "CI Workbook: Runner lost"
description: "CI workbook entry: transient handling for runner lost failures."
resource: "prompt://dryvist/automation/ci-workbook/infra-runner-lost"
tags: ["automation", "ci-workbook", "transient"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"infra-runner-lost","class":"transient","match":{"log":"lost communication with the server|runner has received a shutdown signal|job was not acquired by runner"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/infra-runner-lost.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

The runner disappeared mid-job. Rerun the failed jobs once, and only while a runner matching the job labels is online. A second loss on the same head is an infrastructure incident, not a code fix.
