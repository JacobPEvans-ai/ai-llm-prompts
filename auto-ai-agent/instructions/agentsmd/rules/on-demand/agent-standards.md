---
name: agent-standards
description: Standards for building agents, skills, tools, evaluations, briefs, Dify workflows, and LiteLLM routing.
type: LLM Prompt Fragment
title: "Agent and skill building standards"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-06T20:00:00Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# Agent and skill building standards

Apply these rules when building or revising agents, skills, tools, evaluations, coding-agent briefs, Dify workflows, or LiteLLM configuration.
Treat them as authoring requirements; verify implementation and delivery separately.

## Sources

Research cutoff: **2026-11-06**. Titles, publishers, dates, and URLs retain the R2 source table's attribution.
An undated official page does not establish publication within July–November 2026. D4–D7 release years remain **UNVERIFIED**.
Source IDs in the rules resolve to the URLs below. Local policy is identified separately from upstream requirements.

| Title | Publisher | Date | URL |
| --- | --- | --- | --- |
| A1. The new rules of context engineering for Claude 5 generation models | Anthropic engineering | 2026-07-24 | [A1] |
| A2. Building effective agent automations | Anthropic engineering | 2026-10-08 | [A2] |
| A3. Automating eval design and hillclimbing with Claude | Anthropic engineering | 2026-09-28 | [A3] |
| A4. Best practices for Claude Code | Anthropic | Undated official page | [A4] |
| A5. Create custom subagents | Anthropic | Undated official page | [A5] |
| A6. Extend Claude with skills | Anthropic | Undated official page | [A6] |
| A7. Hooks reference | Anthropic | Undated official page | [A7] |
| A8. Plugins overview / Install and manage plugins | Anthropic | Undated official pages | [Overview][A8], [installation][A9] |
| A10. Settings files and precedence | Anthropic | Undated official page | [A10] |
| A11. How Claude remembers your project | Anthropic | Undated official page | [A11] |
| A12. Skill authoring best practices | Anthropic | Undated official page | [A12] |
| A13. Define tools | Anthropic | Undated official page | [A13] |
| A14. Define success criteria and build evaluations | Anthropic | Undated official page | [A14] |
| A15. Agent Skills specification | Agent Skills | Undated official page | [A15] |
| A16. skill-creator | Anthropic | Undated official source page | [A16] |
| A17. Plugin Development Toolkit | Anthropic | Undated official source page | [A17] |
| A18. mcp-builder | Anthropic | Undated official source page | [A18] |
| A19. Anthropic Skills installation | Anthropic | Undated official source page | [A19] |
| O1. Rethinking skills and prompts for GPT-6 Astra | OpenAI | 2026-09-11 | [O1] |
| O2. Custom instructions with AGENTS.md | OpenAI | Undated official page | [O2] |
| O3. Build skills | OpenAI | Undated official page | [O3] |
| O4. Agent approvals & security / Configuration Reference | OpenAI | Undated official pages | [Security][O4], [configuration][O5] |
| O6. Using GPT-6: prompting best practices | OpenAI | Undated official page | [O6] |
| O7. Prompting | OpenAI | Undated official page | [O7] |
| D1. Dify’s Official CLI: difyctl Ships | Dify | 2026-07-09 | [D1] |
| D2. How to Let Your Agent Call Dify Workflows Directly | Dify | 2026-07-22 | [D2] |
| D3. Why We Redesigned Dify’s Agent? | Dify | 2026-08-27 | [D3] |
| D4. Dify 1.16.0 release | Dify | Undated official release page; header shows 17 Jul without year | [D4] |
| D5. Dify 1.17.0 release | Dify | Undated official release page; header shows 25 Aug without year | [D5] |
| D6. Dify 1.17.1 release | Dify | Undated official release page; header shows 10 Sep without year | [D6] |
| D7. Dify 1.18.0 release | Dify | Undated official release page; header shows 23 Oct without year | [D7] |
| D8. Trigger | Dify | Updated 2026-08-25 | [D8] |
| D9. Export and Import Apps | Dify | Updated 2026-11-04 | [D9] |
| D10. Version Control | Dify | Updated 2026-10-23 | [D10] |
| D11. Skills | Dify | Updated 2026-10-26 | [D11] |
| D12. Agent node | Dify | Updated 2026-10-28 | [D12] |
| L1. Production Best Practices | LiteLLM | Undated official page | [L1] |
| L2. Router — Load Balancing | LiteLLM | Undated official page | [L2] |
| L3. Tag Based Routing | LiteLLM | Undated official page | [L3] |
| L4. Virtual Keys / Setting Team Budgets | LiteLLM | Undated official pages | [Keys][L4], [teams][L5] |
| L6. Logging | LiteLLM | Undated official page | [L6] |
| F1. Prompt Version Control | Langfuse | Undated official page | [F1] |
| F2. Evaluate with Datasets | Langfuse | Undated official page | [F2] |
| F3. LLM-as-a-Judge | Langfuse | Undated official page | [F3] |
| F4. Langfuse Skills | Langfuse | Undated official source page | [F4] |

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

## f. Dify agent and workflow construction

- Put flexible execution in agents; coordinate schedules, branches, approvals, and failures in workflows. Validate recurring behavior. [D3]
- Reuse `difyctl` and its official skill; discover commands supported by the installed client/server pair. [D1] [D2] [D7]
- Pin application and sandbox contracts together. Preserve build snapshots and skill versions for reproducibility. [D5] [D7]
- Render platform files from the canonical agent definitions and one standard template (local policy); test compatibility paths for newer formats. [D7]
- Export the intended published version explicitly; account for workflow, Agent, and skill exports containing saved draft changes. [D9] [D11]
- Test routing, failure branches, pause/resume, unavailable tools, and output contracts before publication; name a rollback version. [D10] [D12] [A3]
- Prefer supported integration triggers, then webhooks. Test activation and verify published subscriptions. [D8]
- Define exhaustive Agent routes, an otherwise route, and failure handling for invalid results. [D12]
- Verify bindings and traces before promotion. Check generation, import, execution, and trace receipt separately. [D9] [F2]

## g. LiteLLM routing and configuration

- Expose stable model-group names with centrally configured deployments. Bound timeouts, retries, and fallback chains; test workload behavior. [L2]
- Start with `simple-shuffle` unless measurements justify another strategy; share routing state and rate-limit counters through Redis across instances. [L1]
- Assign scoped application keys to teams; define model access, budgets, reset periods, and rate limits. [L4] [L5]
- Enable tag filtering explicitly. Test plain-tag OR, required-tag AND, exclusions, untagged requests, and unknown tags. [L3]
- Separate attribution tags from routing intent; migrate callers deliberately when adopting routing prefixes. [L3]
- Enforce hard routing boundaries independently of fail-open tag exclusions; test fallbacks against the same constraints. [L3]
- Verify delivered traces, costs, model selection, and attribution; test dependency failures and budget exhaustion. [L1] [L6] [L5]

[A1]: https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/
[A2]: https://claude.dev/blog/building-effective-agent-automations/
[A3]: https://claude.dev/blog/automating-eval-design-and-hillclimbing/
[A4]: https://code.claude.com/docs/en/best-practices
[A5]: https://code.claude.com/docs/en/sub-agents
[A6]: https://code.claude.com/docs/en/skills
[A7]: https://code.claude.com/docs/en/hooks
[A8]: https://code.claude.com/docs/en/plugins
[A9]: https://code.claude.com/docs/en/discover-plugins
[A10]: https://code.claude.com/docs/en/settings
[A11]: https://code.claude.com/docs/en/memory
[A12]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[A13]: https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
[A14]: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
[A15]: https://agentskills.io/specification
[A16]: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
[A17]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev
[A18]: https://github.com/anthropics/skills/blob/main/skills/mcp-builder/SKILL.md
[A19]: https://github.com/anthropics/skills
[O1]: https://learn.chatgpt.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
[O2]: https://learn.chatgpt.com/docs/agent-configuration/agents-md
[O3]: https://learn.chatgpt.com/docs/build-skills
[O4]: https://learn.chatgpt.com/docs/agent-approvals-security
[O5]: https://learn.chatgpt.com/docs/config-file/config-reference
[O6]: https://developers.openai.com/api/docs/guides/latest-model
[O7]: https://learn.chatgpt.com/docs/prompting
[D1]: https://dify.ai/blog/dify-s-official-cli-difyctl-ships
[D2]: https://dify.ai/blog/how-to-let-your-agent-call-dify-workflows-directly
[D3]: https://dify.ai/blog/why-we-redesigned-dify-agent
[D4]: https://github.com/langgenius/dify/releases/tag/1.16.0
[D5]: https://github.com/langgenius/dify/releases/tag/1.17.0
[D6]: https://github.com/langgenius/dify/releases/tag/1.17.1
[D7]: https://github.com/langgenius/dify/releases/tag/1.18.0
[D8]: https://docs.dify.ai/en/self-host/use-dify/nodes/trigger/overview
[D9]: https://docs.dify.ai/en/self-host/use-dify/workspace/export-import-apps
[D10]: https://docs.dify.ai/en/self-host/use-dify/build/version-control
[D11]: https://docs.dify.ai/en/self-host/use-dify/build/skills
[D12]: https://docs.dify.ai/en/cloud/use-dify/nodes/agent
[L1]: https://docs.litellm.ai/docs/proxy/prod
[L2]: https://docs.litellm.ai/docs/routing
[L3]: https://docs.litellm.ai/docs/proxy/tag_routing
[L4]: https://docs.litellm.ai/docs/proxy/virtual_keys
[L5]: https://docs.litellm.ai/docs/proxy/team_budgets
[L6]: https://docs.litellm.ai/docs/proxy/logging
[F1]: https://langfuse.com/docs/prompt-management/features/prompt-version-control
[F2]: https://langfuse.com/docs/evaluation/get-started/offline
[F3]: https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
[F4]: https://github.com/langfuse/skills
