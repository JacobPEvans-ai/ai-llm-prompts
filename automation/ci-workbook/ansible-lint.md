---
type: LLM Prompt Fragment
title: "CI Workbook: Ansible-lint"
description: "CI workbook entry: recipe handling for ansible-lint failures."
resource: "prompt://dryvist/automation/ci-workbook/ansible-lint"
tags: ["automation", "ci-workbook", "recipe"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"ansible-lint","class":"recipe","match":{"log":"jinja templates should only be at the end of .name.|name\\[template\\]|ansible-lint@|ansible-lint .*violation"},"reproduce":"ansible-lint"}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/ansible-lint.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Reproduce, then fix only the reported rules on the reported lines. For name[template], move every Jinja expression to the end of the task name. For yamllint line-length, wrap with YAML folding, never a noqa or skip_list entry.
