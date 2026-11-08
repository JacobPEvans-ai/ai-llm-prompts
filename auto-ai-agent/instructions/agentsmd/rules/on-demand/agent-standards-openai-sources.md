---
name: agent-standards-openai-sources
description: Dated source attribution for OpenAI agent, skill, prompting and evaluation standards.
type: LLM Prompt Fragment
title: "OpenAI agent authoring standards sources"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-openai-sources"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-08T13:58:25Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-openai-sources.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# OpenAI agent authoring standards sources

Use these source IDs with the [building standards](agent-standards.md).

| Title | Publisher | Date | URL |
| --- | --- | --- | --- |
| O1. Rethinking skills and prompts for GPT-6 Astra | OpenAI | 2026-09-11 | [O1] |
| O2. Custom instructions with AGENTS.md | OpenAI | Undated official page | [O2] |
| O3. Build skills | OpenAI | Undated official page | [O3] |
| O4. Agent approvals & security / Configuration Reference | OpenAI | Undated official pages | [Security][O4], [configuration][O5] |
| O6. Using GPT-6: prompting best practices | OpenAI | Undated official page | [O6] |
| O7. Prompting | OpenAI | Undated official page | [O7] |
| O8. Harness-aware evaluation of plugins | OpenAI | 2026-09-23 | [O8] |
| O9. Codex CLI 0.166.0 release notes | OpenAI | 2026-10-29 | [O9] |
| O10. Codex CLI 0.167.0 release notes | OpenAI | 2026-11-06 | [O10] |

[O1]: https://learn.chatgpt.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
[O2]: https://learn.chatgpt.com/docs/agent-configuration/agents-md
[O3]: https://learn.chatgpt.com/docs/build-skills
[O4]: https://learn.chatgpt.com/docs/agent-approvals-security
[O5]: https://learn.chatgpt.com/docs/config-file/config-reference
[O6]: https://developers.openai.com/api/docs/guides/latest-model
[O7]: https://learn.chatgpt.com/docs/prompting
[O8]: https://developers.openai.com/cookbook/examples/partners/harness_aware_plugin_evals/harness_aware_plugin_evals
[O9]: https://github.com/openai/codex/releases/tag/rust-v0.166.0
[O10]: https://github.com/openai/codex/releases/tag/rust-v0.167.0
