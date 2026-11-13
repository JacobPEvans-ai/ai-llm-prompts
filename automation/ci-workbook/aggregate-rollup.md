---
type: LLM Prompt Fragment
title: "CI Workbook: Aggregate result job"
description: "CI workbook entry: aggregate handling for aggregate result job failures."
resource: "prompt://dryvist/automation/ci-workbook/aggregate-rollup"
tags: ["automation", "ci-workbook", "aggregate"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"aggregate-rollup","class":"aggregate","match":{"log":"some of the required to succeed jobs failed|aggregate results|check all results|verify workflow results"}}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/aggregate-rollup.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

A roll-up job failed only because another job in the same run failed. Never fix or rerun it. Classify the underlying failed job instead; when it is green, the roll-up turns green on the next run.
