---
type: LLM Prompt Fragment
title: "CI Workbook: Markdownlint"
description: "CI workbook entry: deterministic handling for markdownlint failures."
resource: "prompt://dryvist/automation/ci-workbook/markdownlint"
tags: ["automation", "ci-workbook", "deterministic"]
timestamp: "2026-10-11T00:00:00Z"
status: staged
consumers: ["dryvist/nix-agent-sandbox"]
render: {engine: literal, variables: [], frontmatter: strip}
ci_workbook: '{"id":"markdownlint","class":"deterministic","match":{"log":"markdownlint|\\bmd(?:\\d{3}|n)/"},"fix":{"command":"git fetch -q origin HEAD && git diff --name-only --diff-filter=AM FETCH_HEAD...HEAD -- \u0027*.md\u0027 | xargs -r nix --extra-experimental-features \"nix-command flakes\" shell nixpkgs#markdownlint-cli2 -c markdownlint-cli2 --fix"},"reproduce":"markdownlint-cli2"}'
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/ci-workbook/markdownlint.md"
    note: "Seeded from a 90-day census of failed workflow runs."
---

Fix only Markdown files this branch added or modified. Use the repository's own markdownlint configuration. Never reformat unrelated files. If autofix leaves errors (usually MD013 line length), rewrap those lines by hand without changing meaning.
