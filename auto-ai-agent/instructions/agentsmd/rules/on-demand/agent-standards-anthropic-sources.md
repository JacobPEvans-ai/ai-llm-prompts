---
name: agent-standards-anthropic-sources
description: Dated source attribution for Anthropic agent, skill, tool and evaluation standards.
type: LLM Prompt Fragment
title: "Anthropic agent authoring standards sources"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-anthropic-sources"
tags: [shared-instructions, agent-standards, skill-authoring]
timestamp: "2026-11-08T17:05:00Z"
status: active
consumers: [dryvist/nix-ai, dryvist/nix-claude-code]
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-llm-prompts
    path: auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards-anthropic-sources.md
    note: Standards synthesized from R2-practices sections 1-2, research cutoff 2026-11-08.
---

# Anthropic agent authoring standards sources

Use these source IDs with the [building standards](agent-standards.md).

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
| A16. skill-creator | Anthropic | Undated official source page | [A16] |
| A17. Plugin Development Toolkit | Anthropic | Undated official source page | [A17] |
| A18. mcp-builder | Anthropic | Undated official source page | [A18] |
| A19. Anthropic Skills installation | Anthropic | Undated official source page | [A19] |
| A20. The components of agent memory | Anthropic | 2026-11-06 | [A20] |
| A21. Building agents: When to fold subagents into your main agent loop | Anthropic | 2026-10-22 | [A21] |
| A22. Claude Code v2.1.317 release notes | Anthropic | 2026-11-03 | [A22] |
| A23. Claude Code 2.1.319 | Anthropic | 2026-11-06 | [A23] |
| A24. Claude Code v2.1.316 release notes | Anthropic | 2026-10-31 | [A24] |
| A25. Claude Code v2.1.318 release notes | Anthropic | 2026-11-04 | [A25] |

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
[A16]: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
[A17]: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev
[A18]: https://github.com/anthropics/skills/blob/main/skills/mcp-builder/SKILL.md
[A19]: https://github.com/anthropics/skills
[A20]: https://www.anthropic.com/research/components-of-agent-memory
[A21]: https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop
[A22]: https://github.com/anthropics/claude-code/releases/tag/v2.1.317
[A23]: https://code.claude.com/docs/en/changelog#2-1-319
[A24]: https://github.com/anthropics/claude-code/releases/tag/v2.1.316
[A25]: https://github.com/anthropics/claude-code/releases/tag/v2.1.318
