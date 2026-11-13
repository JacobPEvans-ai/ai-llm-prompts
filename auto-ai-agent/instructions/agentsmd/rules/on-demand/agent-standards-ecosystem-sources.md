---
name: agent-standards-ecosystem-sources
description: Dated source attribution for Agent Skills, Google, LangChain and Langfuse standards.
type: LLM Prompt Fragment
title: "Agent ecosystem standards sources"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-ecosystem-sources"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-08T13:58:25Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: jpe-ai-agents/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-ecosystem-sources.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-06.
---

# Agent ecosystem standards sources

Use these source IDs with the [building standards](agent-standards.md).

| Title | Publisher | Date | URL |
| --- | --- | --- | --- |
| A15. Agent Skills specification | Agent Skills | Undated official page | [A15] |
| G1. Five rules for evaluating agent skills before they bloat your context window | Google Cloud | 2026-11-03 | [G1] |
| G2. Four evaluation engineering lessons learned from building agent plugins | Google Cloud | 2026-10-16 | [G2] |
| G3. ADK Python v2.14.0 release notes | Google | 2026-11-04 | [G3] |
| C1. Trajectories now in LangSmith: A readable view of every agent session | LangChain | 2026-09-24 | [C1] |
| C2. Context Engineering Starts with Retrieval | LangChain | 2026-10-23 | [C2] |
| C3. Building Evidence-Grounded Agent Memory with OpenWiki and Graphs | LangChain | 2026-10-28 | [C3] |
| F5. Skill Management in Langfuse | Langfuse | 2026-11-03 | [F5] |
| F6. See when token usage is missing | Langfuse | 2026-11-06 | [F6] |

[A15]: https://agentskills.io/specification
[G1]: https://cloud.google.com/blog/topics/developers-practitioners/evaluate-agent-skills-before-they-bloat-your-context-window
[G2]: https://cloud.google.com/blog/topics/developers-practitioners/four-eval-engineering-lessons
[G3]: https://github.com/google/adk-python/releases/tag/v2.14.0
[C1]: https://www.langchain.com/blog/langsmith-trajectories-tracing
[C2]: https://www.langchain.com/blog/context-engineering-starts-with-retrieval
[C3]: https://www.langchain.com/blog/building-agent-memory-openwiki-graphs
[F5]: https://langfuse.com/changelog/2026-11-03-skill-management
[F6]: https://langfuse.com/changelog/2026-11-06-retiring-tokenization
