---
name: agent-standards
description: Standards for building agents, skills, tools, evaluations, briefs, and platform integrations.
type: LLM Prompt Fragment
title: "Agent and skill building standards"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-06T22:25:00Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# Agent and skill building standards

Apply these rules when building or revising agents, skills, tools, evaluations, or coding-agent briefs.
When building Dify workflows or configuring LiteLLM, also apply the [platform rules f–g](agent-standards-platform.md).
Treat the rules as authoring requirements; verify implementation and delivery separately.

## Sources

Resolve source IDs through the dated [authoring source table](agent-standards-sources.md) and
[platform source table](agent-standards-platform-sources.md). Local policy is identified separately from upstream requirements.

## a. Agent definitions and prompts

- State the job, inputs, output schema, tools, completion criterion, and authority boundary. Separate project guidance from task instructions. [A4] [A5] [O7]
- Encode local conventions and costly gotchas; remove discoverable structure and default behavior. Re-evaluate instructions when changing models. [A1] [O1]
- Define focused roles with explicit tools, Model Context Protocol (MCP) servers, and essential startup skills. [A5]
- Keep `CLAUDE.md` concise, scope specialized rules to files, and store learned context in memory. [A11]
- Treat retrieval and writable memory as instruction inputs. Enforce source, destination, and network limits at runtime; keep preferences read-only. [A2]
- Retain per-source bookmarks and a delivery ledger. Preserve bookmarks after failed reads; report unavailable sources; advance only after receipt. [A2]

## b. Skills: structure, descriptions, disclosure, scripts, tests

- Package YAML-frontmatter `SKILL.md` with optional `references/`, `scripts/`, and `assets/`; distribute the complete directory. [A15] [O3]
- Describe the task and exact triggers. Front-load distinguishing words and include exclusions that prevent false activation. [O1] [O3]
- Limit descriptions to 1,024 characters. Apply the separate local portability budget of 1,024 bytes and approximately 250-character soft target. [A15]
- Keep the body below the recommended 500 lines. Link references directly from `SKILL.md`; add navigation to long references. [A12]
- Keep prerequisites, authority limits, and stop conditions available when loaded alone; disclose optional detail progressively (local policy). [A12]
- Prefer instructions and existing native tools. Include executable resources only for warranted deterministic work; document dependencies and errors. [O3] [A12]
- Set invocation policy per harness: Claude `disable-model-invocation` and Codex `agents/openai.yaml`. Verify both behaviors. [A6] [O3]
- Test triggering and execution separately with positive and negative prompts. Compare outputs against no skill or the previous version. [O3] [A16]
- Test the actual permitted target models and environments. Measure instruction changes for each target. [A12] [O1]

## c. Tool and MCP design

- Use consistent, discoverable action names, constrained input schemas, and structured outputs where supported. [A18]
- Describe purpose, applicability, parameters, results, and limitations in tool definitions; remove repeated system-prompt instructions. [A13] [A1]
- Filter and paginate results. Return actionable errors that support correction or identify blockers. [A18]
- Match tool granularity to client workflows; preserve composability and evaluate convenience tools on realistic tasks. [A18]
- Annotate read-only, destructive, idempotent, and open-world behavior accurately. Enforce access through permissions and scoped credentials. [A18] [A2]
- Test with an MCP client or Inspector, then evaluate realistic agent tasks through the interface. [A18]

## d. Evals

- Define measurable acceptance thresholds for correctness, privacy, latency, cost, and consequential failures before optimization. [A14]
- Sample production tasks and hard cases: malformed, ambiguous, oversized, unavailable-source, and negative-trigger inputs. [A14] [A3]
- Check constrained outputs deterministically. Calibrate rubric judges against human-reviewed examples; keep judges distinct from candidates. [A3] [F3]
- Repeat trials in clean environments. Separate model failures from timeouts, truncation, grader inconsistency, and stale state. [A3]
- Compare baselines and report uncertainty. Hold test cases outside optimizer context; reject gains within noise. [A3]
- Record dataset and prompt versions, model and evaluator configurations, and trace-linked results. Gate promotion on regression checks. [F1] [F2]
- Continue sampled production evaluation; feed reviewed failures into datasets while protecting held-out answers. [F2] [F3] [A3]

## e. Coding-agent briefs

- Use [Brief Delegates Completely](../../../../claude-code/rules/brief-delegates.md) for scope, authority, stops, verification, and evidence reporting.
- Specify edit, create, network, internal-service, dependency-install, commit, push, and publication authority; enforce boundaries at runtime. [O4] [O5] [O7]
- Select sandbox and approvals independently. Confine research to read-only; replace unsupported `untrusted` and migrate deprecated `on-failure`. [O4] [O5]
- Allow routine assumptions; stop on missing authority, unmet prerequisites, ambiguous scope, or the named failure threshold. [O6]
- Supply the smallest relevant examples and references; require whole-repository reading only when the task needs it. [O1]
- Run required checks and the narrowest additional proof. Broaden only for new failures, changes, or unresolved concerns. [O6]
- Report changed artifacts, passed checks, failed or unrun checks, blockers, and delivery status. Separate local proof from external acceptance. [A4] [D9] [F2]

[A4]: agent-standards-sources.md
[A5]: agent-standards-sources.md
[O7]: agent-standards-sources.md
[A1]: agent-standards-sources.md
[O1]: agent-standards-sources.md
[A11]: agent-standards-sources.md
[A2]: agent-standards-sources.md
[A15]: agent-standards-sources.md
[O3]: agent-standards-sources.md
[A12]: agent-standards-sources.md
[A6]: agent-standards-sources.md
[A16]: agent-standards-sources.md
[A18]: agent-standards-sources.md
[A13]: agent-standards-sources.md
[A14]: agent-standards-sources.md
[A3]: agent-standards-sources.md
[F3]: agent-standards-platform-sources.md
[F1]: agent-standards-platform-sources.md
[F2]: agent-standards-platform-sources.md
[O4]: agent-standards-sources.md
[O5]: agent-standards-sources.md
[O6]: agent-standards-sources.md
[D9]: agent-standards-platform-sources.md
