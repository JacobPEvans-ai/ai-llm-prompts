---
name: review-gate
description: First code review check for custom code and reuse.
type: LLM Prompt
title: "Review gate"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/review-gate"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-11T14:11:57Z"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history: []
---

# Review gate

Before any other review check, ask whether the change adds or edits custom code: a script, service unit, timer, scheduled job, or glue code. The last paragraph lists what is not custom code.

If it does, apply the tool-choice order in `AGENTS.md`. If a rung before writing code does the same, the verdict is CHANGES and the finding names it.

If none exists, the change must name the options checked, explain why each does not fit, and cite the repository owner's recorded approval. Without all three, the verdict is CHANGES.

Then ask: does the change add a second copy of a mechanism that already exists? If yes, the verdict is CHANGES.

Does anything hard-coded for one consumer need to be a parameter? If yes, the verdict is CHANGES.

These are not custom code: configuration of existing software, a maintained tool's own plugin or module, and a test case
that runs under the test framework the repository already uses. A new test runner, harness, or helper script is custom code.
