---
name: review-gate
description: First code review check for custom code and reuse.
type: LLM Prompt
title: "Review gate"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/review-gate"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-11T14:29:27Z"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history: []
---

# Review gate

Before any other review check, ask whether the change adds or edits custom code: a script, a hand-written service unit, timer or scheduled job, or glue code. The last paragraph lists what is not custom code.

If it does, apply the tool-choice order in `AGENTS.md`. If a rung before writing code does the same, the verdict is CHANGES and the finding names it.

If none does, the change must show what that rule requires, each rung named with why it failed, and cite the repository owner's recorded approval. Otherwise the verdict is CHANGES.

Then apply the DRY principle of the code review instructions to mechanisms as well as code. A second copy of a mechanism that
already exists, or a value hard-coded for one consumer that should be a parameter, is CHANGES.

These are not custom code: configuration of existing software, including a unit or schedule that a maintained package ships, a maintained tool's own plugin or module, and a test case
that runs under the test framework the repository already uses. A new test runner, harness, or helper script is custom code.

## Who launches the review

The review that feeds a merge gate is launched by a seat that did not author the head. Its verdict file carries
`model:`, `call_id:`, `head:` and a last line `VERDICT: MERGE` or `VERDICT: CHANGES`. A launch is one read-only
review call with the standard brief, starting with the check above.

Fixed pairs launch for each other: deputy and models, infra and bench, build and ops. The co-lead takes host
repositories and overflow.
