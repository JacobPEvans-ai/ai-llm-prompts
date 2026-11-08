---
name: agent-standards
description: Standards for building agents, skills, tools, evaluations, briefs, and platform integrations.
type: LLM Prompt Fragment
title: "Agent and skill building standards"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-08T03:49:34Z"
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
Memory guidance: Anthropic, *The components of agent memory*, published 2026-11-06. [A20]
Subagent guidance: Anthropic, *Building agents: When to fold subagents into your main agent loop*, published 2026-10-22. [A21]

## a. Agent definitions and prompts

- State the job, inputs, output schema, tools, completion criterion, and authority boundary. Separate project guidance from task instructions. [A4] [A5] [O7]
- Name the native workflow enforcing the [scheduling, branching, approval, and recovery boundary](agent-standards-platform.md#f-dify-agent-and-workflow-construction). [D3]
- Encode local conventions and costly gotchas; remove discoverable structure and default behavior. Re-evaluate instructions when changing models. [A1] [O1]
- Define focused roles with explicit tools, Model Context Protocol (MCP) servers, and essential startup skills. [A5]
- Prefer one agent with progressively disclosed skills and tools for related domain work. Keep an optional subagent only for measured context bloat, fresh-context parallelism, tool-selection or instruction conflicts, or modular permission boundaries. Connector-agent boundaries stay mandatory and are not optional subagents. [A21]
- Keep `CLAUDE.md` concise, scope specialized rules to files, and store learned context in memory. [A11]
- Give each learned or stored rule an evidence reference and a confirmed or unconfirmed status. Define who is authorized to correct or retire a wrong rule and how they check it against its source. [A20]
- Name one writer per source record in shared memory. Preserve key facts exactly: numbers, names, dates, and links. Concurrent writers append to their own records and never rewrite a shared summary (local write policy). [A20]
- Treat retrieval and writable memory as instruction inputs. Enforce source, destination, and network limits at runtime; keep preferences read-only. [A2]
- Retain per-source bookmarks and a delivery ledger. Preserve bookmarks after failed reads; report unavailable sources. [A2]
- Reconcile with the destination before retrying delivery. Record ambiguous delivery separately; advance bookmarks and ledger only after confirmed receipt. [A2]

## b. Skills: structure, descriptions, disclosure, scripts, tests

- Package YAML-frontmatter `SKILL.md` with optional `references/`, `scripts/`, and `assets/`; distribute the complete directory. [A15] [O3]
- Describe the task and exact triggers. Front-load distinguishing words and include exclusions that prevent false activation. [O1] [O3]
- Check description overlap with neighboring skills before paid execution trials; measure intended selection and sibling hijacking in the deployed catalog. [G1]
- Limit descriptions to 1,024 characters. Apply the separate local portability budget of 1,024 bytes and approximately 250-character soft target. [A15]
- Keep the body below the recommended 500 lines. Link references directly from `SKILL.md`; add navigation to long references. [A12]
- Keep prerequisites, authority limits, and stop conditions available when loaded alone; disclose optional detail progressively (local policy). [A12]
- Prefer instructions and existing native tools. Include executable resources only for warranted deterministic work; document dependencies and errors. [O3] [A12]
- Set invocation policy per harness: Claude `disable-model-invocation` and Codex `agents/openai.yaml`. Verify both behaviors. [A6] [O3]
- Test triggering and execution separately with positive and negative prompts. Compare outputs against no skill or the previous version. [O3] [A16]
- Reject revisions with no measured gain over the previous version; consider skills with no measured gain over no skill for retirement (local acceptance policy). [G1] [A3]
- Test the actual permitted target models and environments. Measure instruction changes for each target. [A12] [O1]

## c. Tool and MCP design

- Use consistent, discoverable action names, constrained input schemas, and structured outputs where supported. [A18]
- Describe purpose, applicability, parameters, results, and limitations in tool definitions; remove repeated system-prompt instructions. [A13] [A1]
- Filter and paginate results; return actionable errors. For retrieval, offload large payloads behind pointers, preserve source URLs
  and dates with the results, and test that claims cite and match the retrieved material. [A18] [C2]
- Match tool granularity to client workflows; preserve composability and evaluate convenience tools on realistic tasks. [A18]
- Annotate read-only, destructive, idempotent, and open-world behavior accurately. Enforce access through permissions and scoped credentials. [A18] [A2]
- For action-gating hooks, make a failed callback block the protected action where the harness supports it, and test that failure path. [A22]
- When upgrading the model router to a release that changes MCP credential forwarding, test auth forwarding and team-key tool visibility explicitly before rollout. [L7]
- Test with an MCP client or Inspector, then evaluate realistic agent tasks through the interface. [A18]

## d. Evals

- Define measurable acceptance thresholds for correctness, privacy, latency, cost, and consequential failures before optimization. [A14]
- Sample production tasks and hard cases: malformed, ambiguous, oversized, unavailable-source, and negative-trigger inputs. [A14] [A3]
- Explain each hard case's intrinsic difficulty independently of current model failures; diagnose saturation, universal failures, and permitted model/effort scaling. [A3]
- Pair plan-only cases with authorized disposable sandbox execution; grade actual tool arguments, artifacts, and unauthorized effects separately. [G2]
- Keep fixtures, grading scripts and answer keys outside the agent's reachable workspace during trials, and let a separate verifier inspect artifacts after the agent exits. Efficiency never offsets a failed correctness or security check. [G1]
- Before adding compiled or persistent memory, compare it with retrieval alone on the same simple-lookup and cross-source tasks. Report accuracy, citation consistency, latency and the full cost of creating and updating the memory. [C3]
- Preserve assistant-turn boundaries, parallel call batches, and instruction-injection timing; detect actions dispatched before loaded guidance arrives. [G2]
- Evaluate complete multi-turn sessions across handoffs; deduplicate repeated messages in ordered trajectories and retain the underlying traces. [C1]
- Check constrained outputs deterministically. Calibrate rubric judges against human-reviewed examples; keep judges distinct from candidates and blind to candidate identity. [A3] [F3]
- Randomize candidate/baseline order and check position bias; regrade identical outputs and report verdict disagreement. [A3]
- Repeat trials in clean environments. Separate model failures from timeouts, truncation, grader inconsistency, and stale state. [A3]
- Replay shared fixtures through existing direct-tool, controlled-loop, and installed-harness runners; locate guidance/tool-availability differences before editing instructions. [O8]
- Compare baselines and report uncertainty. Hold test cases outside optimizer context; reject gains within noise. [A3]
- Record dataset and prompt versions, model and evaluator configurations, and trace-linked results. Gate promotion on regression checks. [F1] [F2]
- Trace available skills, exact loaded versions, and loaded resource paths; link observations to the canonical skill revision without creating another source of truth. [F5]
- Continue sampled production evaluation; feed reviewed failures into datasets while protecting held-out answers. [F2] [F3] [A3]

## e. Coding-agent briefs

Follow `prompt://dryvist/auto-ai-agent/claude-code/rules/brief-delegates` for scope, authority, stops, verification, and evidence reporting.

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
[D3]: agent-standards-platform-sources.md
[G1]: agent-standards-sources.md
[G2]: agent-standards-sources.md
[C1]: agent-standards-sources.md
[C2]: agent-standards-sources.md
[O8]: agent-standards-sources.md
[F5]: agent-standards-sources.md
[A20]: https://www.anthropic.com/research/components-of-agent-memory
[A21]: https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop
[A22]: https://github.com/anthropics/claude-code/releases/tag/v2.1.317
[C3]: https://www.langchain.com/blog/building-agent-memory-openwiki-graphs
[L7]: https://github.com/BerriAI/litellm/releases/tag/v1.109.0-rc.1
