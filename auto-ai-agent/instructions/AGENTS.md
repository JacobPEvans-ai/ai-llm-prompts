---
type: LLM Prompt
title: "AI Agents Configuration"
description: "Shared global agent instructions for AI Agents Configuration."
resource: "prompt://dryvist/auto-ai-agent/instructions/AGENTS"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-08T18:00:00Z"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-assistant-instructions
    path: "AGENTS.md"
    note: Migrated from the instruction repository.
---
# AI Agents Configuration

## Coding behavior

Identity and posture: `soul.md`. Use evidence, make reasonable assumptions, proceed, and surface only
assumptions/tradeoffs that affect action. Ship the simplest surgical fix matching existing style; define
verifiable success criteria, use the narrowest proof, and report exactly what passed/failed. Fix every
warning, error and lint finding for real; never silence, skip or bypass the check that raised it.

Tool choice — **no new custom scripts**. Stop at the first rung that works:
(1) existing flags, config, or an installed skill, command, plugin or MCP server; (2) a native platform or tool
feature; (3) a maintained third-party tool; (4) community content (collections, modules, presets,
hooks, Actions); (5) prior art: `/github-code-search` (thousands of hits is idiomatic, three is a
mistake), context7, registries; (6) a standardized public repo. Only then write code, naming why each rung failed;
delete or replace an existing script before editing it.

Git workflow: never edit on the default branch — start a worktree with `git town hack`. `develop` default branch →
[git-flow](agentsmd/rules/on-demand/git-flow.md): PRs target `develop` (squash-merge), `develop` → `main` by
merge commit only. Otherwise trunk flow. Always **atomic commits**, one fix/feature/section per commit. Load
the on-demand rule for the activity — `rule-tiers.md` is the index. Instruction-behavior changes are `feat:`/`fix:`,
never `docs:`.

Writing voice: prose a person will read follows `~/.agents/voice.md` when that file exists.

Knowledge base: documentation follows [Open Knowledge Format](agentsmd/rules/on-demand/okf.md) — search before
editing, capture new knowledge after a change.

## Where things get written (routing law, no exceptions)

Once questions are resolved and the plan approved, execute end to end in one shot, routed per this table.
GitHub is public, **pull requests only**; a PR body states WHAT the code does — never why, what was
broken, or what's still weak.

| Content | Destination |
| --- | --- |
| Incidents, outages, security findings, weaknesses | the incident tracker |
| Private documentation, especially secret management | the private docs site |
| Everything else, including side quests and follow-ups | the task tracker — **never a GitHub issue** |

The operator's role map names each product ([example](agentsmd/docs/tool-role-map.example.md)).

Never put an incident narrative, security finding, credential/secret detail, unprovisioned identity, internal
topology, host name, or outage timeline in a GitHub issue, PR, comment, or commit message — "side quest" is
not an exemption.

Repo boundaries: `dryvist/ai-llm-prompts` `auto-ai-agent/instructions` (rules, `AGENTS.md`, workflows),
`dryvist/nix-claude-code` `data/permissions` (tool permissions), `dryvist/claude-code-plugins` (commands,
skills, agents, hooks).

**Delegation routing (binding, the only routing statement).** The lead never does delegable work itself: it plans,
judges results, and merges, fanning every independent task out to subagents in parallel. Route each task to the first
rung that qualifies; check `codex-quota` first (exit 0 means more than 5% left).

1. **ZCode or Codex Luna, equal first choices split by sensitivity.** ZCode (latest GLM Flash, `zcode-job` sandbox):
   obvious, definitely non-sensitive work in public repos; the output is a ready PR — leak-scan before merge, never
   auto-merge. Codex Luna: anything even remotely sensitive, or any private repo; `xhigh` default, `max` as needed.
   Never Terra.
2. **Other subscriptions where they fit** (for example OpenCode Go via `zcode-job --tool opencode`); public work only.
3. **Haiku `xhigh`, the last resort** — only after rungs 1 and 2 are exhausted or do not qualify, and still before the
   lead works solo.

Never Sonnet, Opus, or Fable subagents. Never send secrets, credentials, inventory, or incident content to any executor.
Antigravity (`agy`, Gemini 3.8 Flash) is a second-opinion reviewer, not an executor. Use it on high-risk diffs in public or
trusted repos; its call is in the `jpe-ai-delegation` plugin's `delegation-ladder` skill. The Codex CLI procedure is in
[model-delegation.md](agentsmd/rules/on-demand/model-delegation.md). That plugin's skill and hook implement this order.
