---
name: agent-standards-platform-sources
description: Dated source attribution for Dify, LiteLLM, and Langfuse standards.
type: LLM Prompt Fragment
title: "Platform integration standards sources"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-platform-sources"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-07T23:08:31Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-platform-sources.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# Platform integration standards sources

Retain the [research cutoff and date conventions](agent-standards-sources.md). D4–D7 release years remain **UNVERIFIED**.
Use these source IDs with the [building standards](agent-standards.md) and [platform rules](agent-standards-platform.md).

| Title | Publisher | Date | URL |
| --- | --- | --- | --- |
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
| D13. AI Agent or Workflow? How to Choose the Right Approach | Dify | 2026-10-16 | [D13] |
| L1. Production Best Practices | LiteLLM | Undated official page | [L1] |
| L2. Router — Load Balancing | LiteLLM | Undated official page | [L2] |
| L3. Tag Based Routing | LiteLLM | Undated official page | [L3] |
| L4. Virtual Keys / Setting Team Budgets | LiteLLM | Undated official pages | [Keys][L4], [teams][L5] |
| L6. Logging | LiteLLM | Undated official page | [L6] |
| F1. Prompt Version Control | Langfuse | Undated official page | [F1] |
| F2. Evaluate with Datasets | Langfuse | Undated official page | [F2] |
| F3. LLM-as-a-Judge | Langfuse | Undated official page | [F3] |
| F4. Langfuse Skills | Langfuse | Undated official source page | [F4] |

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
[D13]: https://www.dify.ai/de/blog/ai-agent-or-workflow-how-to-choose-the-right-approach
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
