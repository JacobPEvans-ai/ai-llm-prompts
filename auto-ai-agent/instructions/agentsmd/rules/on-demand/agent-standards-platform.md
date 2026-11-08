---
name: agent-standards-platform
description: Rules for building Dify workflows and configuring LiteLLM routing.
type: LLM Prompt Fragment
title: "Platform integration building standards"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-platform"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-08T09:27:32Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-platform.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# Platform integration building standards

Apply the [agent and skill building standards](agent-standards.md) with these platform rules.
Source IDs resolve to the dated [authoring sources](agent-standards-sources.md) and [platform sources](agent-standards-platform-sources.md).
Local policy is identified separately from upstream requirements.

## f. Dify agent and workflow construction

- Use workflows for repeatable steps and to own schedules, branches, checks, approvals, and failure handling. Use an agent for bounded
  recurring work with a clear, evaluable outcome when context must guide selection among approved actions; keep it to the variable
  step in a mostly fixed process. [D13]
- Reuse `difyctl` and its official skill; discover commands supported by the installed client/server pair. [D1] [D2] [D7]
- Pin application and sandbox contracts together. Preserve build snapshots and skill versions for reproducibility. [D5] [D7]
- Render platform files from the canonical agent definitions and one standard template (local policy); test compatibility paths for newer formats. [D7]
- Export the intended published version explicitly; account for workflow, Agent, and skill exports containing saved draft changes. [D9] [D11]
- Exclude secret values from exported artifacts. Record dependencies that exports omit: credentials, linked knowledge bases,
  trigger subscriptions, and relevant runtime files. [D9]
- Test routing, failure branches, pause/resume, unavailable tools, and output contracts before publication; name a rollback version. [D10] [D12] [A3]
- Prefer supported integration triggers, then webhooks. Test activation and verify published subscriptions. [D8]
- Define exhaustive Agent routes, an otherwise route, and failure handling for invalid results. [D12]
- Verify bindings and traces before promotion. Check generation, import, execution, and trace receipt separately. [D9] [F2]

## g. LiteLLM routing and configuration

- Expose stable model-group names with centrally configured deployments. Bound timeouts, retries, and fallback chains; test workload behavior. [L2]
- Start with `simple-shuffle` unless measurements justify another strategy; share routing state and rate-limit counters through Redis across instances. [L1]
- Assign scoped application keys to teams; define model access, budgets, reset periods, and rate limits. [L4] [L5]
- Set a server-level `rpm` on each MCP Gateway server so all its callers share one request cap. [L8]
- Enable tag filtering explicitly. Test plain-tag OR, required-tag AND, exclusions, untagged requests, and unknown tags. [L3]
- Separate attribution tags from routing intent; migrate callers deliberately when adopting routing prefixes. [L3]
- Enforce hard routing boundaries independently of fail-open tag exclusions; test fallbacks against the same constraints. [L3]
- Verify delivered traces, costs, model selection, and attribution; test dependency failures and budget exhaustion. [L1] [L6] [L5]

[D3]: agent-standards-platform-sources.md
[D1]: agent-standards-platform-sources.md
[D2]: agent-standards-platform-sources.md
[D7]: agent-standards-platform-sources.md
[D5]: agent-standards-platform-sources.md
[D9]: agent-standards-platform-sources.md
[D11]: agent-standards-platform-sources.md
[D10]: agent-standards-platform-sources.md
[D12]: agent-standards-platform-sources.md
[D13]: agent-standards-platform-sources.md
[A3]: agent-standards-sources.md
[D8]: agent-standards-platform-sources.md
[F2]: agent-standards-platform-sources.md
[L2]: agent-standards-platform-sources.md
[L1]: agent-standards-platform-sources.md
[L4]: agent-standards-platform-sources.md
[L5]: agent-standards-platform-sources.md
[L3]: agent-standards-platform-sources.md
[L6]: agent-standards-platform-sources.md
[L8]: agent-standards-platform-sources.md
