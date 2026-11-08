---
name: agent-standards-sources
description: Dated source attribution for agent, skill, tool, evaluation, and brief standards.
type: LLM Prompt Fragment
title: "Agent authoring standards sources"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-sources"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-08T09:27:32Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-sources.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# Agent authoring standards sources

Research cutoff: **2026-11-07**. Titles, publishers, dates, and URLs retain primary-source attribution.
An undated official page does not establish publication within July–November 2026.

Use these source IDs with the [building standards](agent-standards.md). See the [platform sources](agent-standards-platform-sources.md)
for Dify, LiteLLM, and Langfuse attribution.

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
| A20. The components of agent memory | Anthropic | 2026-11-06 | [A20] |
| A21. Building agents: When to fold subagents into your main agent loop | Anthropic | 2026-10-22 | [A21] |
| A22. Claude Code v2.1.317 release notes | Anthropic | 2026-11-03 | [A22] |
| O1. Rethinking skills and prompts for GPT-6 Astra | OpenAI | 2026-09-11 | [O1] |
| O2. Custom instructions with AGENTS.md | OpenAI | Undated official page | [O2] |
| O3. Build skills | OpenAI | Undated official page | [O3] |
| O4. Agent approvals & security / Configuration Reference | OpenAI | Undated official pages | [Security][O4], [configuration][O5] |
| O6. Using GPT-6: prompting best practices | OpenAI | Undated official page | [O6] |
| O7. Prompting | OpenAI | Undated official page | [O7] |
| O8. Harness-aware evaluation of plugins | OpenAI | 2026-09-23 | [O8] |
| O9. Codex CLI 0.166.0 release notes | OpenAI | 2026-10-29 | [O9] |
| O10. Codex CLI 0.167.0 release notes | OpenAI | 2026-11-06 | [O10] |
| G1. Five rules for evaluating agent skills before they bloat your context window | Google Cloud | 2026-11-03 | [G1] |
| G2. Four evaluation engineering lessons learned from building agent plugins | Google Cloud | 2026-10-16 | [G2] |
| G3. ADK Python v2.14.0 release notes | Google | 2026-11-04 | [G3] |
| C1. Trajectories now in LangSmith: A readable view of every agent session | LangChain | 2026-09-24 | [C1] |
| C2. Context Engineering Starts with Retrieval | LangChain | 2026-10-23 | [C2] |
| C3. Building Evidence-Grounded Agent Memory with OpenWiki and Graphs | LangChain | 2026-10-28 | [C3] |
| F5. Skill Management in Langfuse | Langfuse | 2026-11-03 | [F5] |
| F6. See when token usage is missing | Langfuse | 2026-11-06 | [F6] |

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
[A20]: https://www.anthropic.com/research/components-of-agent-memory
[A21]: https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop
[A22]: https://github.com/anthropics/claude-code/releases/tag/v2.1.317
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
[G1]: https://cloud.google.com/blog/topics/developers-practitioners/evaluate-agent-skills-before-they-bloat-your-context-window
[G2]: https://cloud.google.com/blog/topics/developers-practitioners/four-eval-engineering-lessons
[G3]: https://github.com/google/adk-python/releases/tag/v2.14.0
[C1]: https://www.langchain.com/blog/langsmith-trajectories-tracing
[C2]: https://www.langchain.com/blog/context-engineering-starts-with-retrieval
[C3]: https://www.langchain.com/blog/building-agent-memory-openwiki-graphs
[F5]: https://langfuse.com/changelog/2026-11-03-skill-management
[F6]: https://langfuse.com/changelog/2026-11-06-retiring-tokenization
