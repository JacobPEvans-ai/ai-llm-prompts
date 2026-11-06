---
type: LLM Prompt Fragment
title: "Brief Delegates Completely"
description: "Always-loaded rule: every delegate brief states scope, runtime authority, checks, evidence, stops, and difficulty."
resource: "prompt://dryvist/auto-ai-agent/claude-code/rules/brief-delegates"
tags:
  - "claude-code"
  - "delegation"
  - "briefing"
timestamp: "2026-11-06T20:10:00Z"
status: active
consumers:
  - "dryvist/nix-ai"
render:
  engine: literal
  variables: []
  frontmatter: include
source_history:
  - repository: "dryvist/ai-llm-prompts"
    path: "auto-ai-agent/claude-code/rules/brief-delegates.md"
    note: "Authored net-new. Delivered as an always-loaded Claude Code rule; no hook checks briefs."
---

**Brief delegates completely.** A subagent knows only its prompt: nothing of this conversation, the files you read,
the user's preferences or what already failed. What the brief leaves out, the delegate guesses or skips, and the
parent owns that outcome. A vague brief is the parent's failure, never the delegate's. Every brief states:

1. the goal and the intent behind it;
2. the exact scope (repo, absolute paths, branch or worktree), allowed paths, and what must not be touched;
3. constraints, patterns to follow (`file:line`) and decisions already made, pasted rather than referred to;
4. the success criterion: required checks, the expected result, and the narrowest additional proof justified by the change;
5. the output contract: final message one line or schema, with the evidence states below; report file only for write-capable delegates;
6. where to stop and report instead of guessing: missing authority, an unmet prerequisite, a gate, a refusal,
   ambiguous scope, or the named failure threshold (a second failure by default);
7. difficulty and risk in plain words, never a model name. Routing picks the cheapest tier the brief justifies, so
   a thin brief buys the weakest executor.

## Runtime authority

State explicitly whether the delegate may edit, create files, access the network, contact internal services, install
dependencies, commit, push, or publish. Name permitted destinations and write paths. Enforce those boundaries through
the runtime's permissions, sandbox, and approval configuration; prose does not grant authority.

For Codex, select `sandbox_mode` independently from `approval_policy`. Use `read-only` for research; use
`workspace-write` only for authorized write paths. Select `on-request` approvals for interactive work or `never`
for noninteractive work within its preauthorized scope. Replace unsupported `untrusted` approvals and migrate
deprecated `on-failure` according to the current configuration reference. Stop when the selected runtime cannot
enforce the brief's boundaries or required authority is missing.

## Verification and evidence

Supply the smallest relevant examples, tests, and references. Require whole-repository reading only when the task
needs it. Allow reasonable assumptions for routine choices within the stated scope. Run required checks and the
narrowest additional proof; broaden verification only for new failures, changes, or unresolved concerns.

Require the final output to identify:

- changed artifacts, with exact paths;
- checks passed, with commands and results;
- checks failed or not run, with commands and reasons;
- remaining blockers;
- delivery status: local changes, commits, push, draft PR, deployment, or external acceptance, as applicable.

Keep local validation, source generation, import, execution, and confirmed external receipt as separate evidence
states. Claim only the states verified in the run. Apply the [agent and skill building standards][standards]
for source attribution: A4, O1, O4, O5, O6, O7, D9, and F2.

## Brief check

Test: could a capable contractor with no access to this conversation finish from the brief alone? If not, rewrite
it. Never write "as discussed", "the bug we found", "look into X" or "based on your findings, implement it": handing
off understanding is not handing off work. Worked example: `prompt://dryvist/auto-ai-agent/model-delegation`.

[standards]: ../../instructions/agentsmd/rules/on-demand/agent-standards.md#e-coding-agent-briefs
