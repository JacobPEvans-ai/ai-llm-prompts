# Continuous AI Agents

Prompts for continuously running local agents, shared autonomous behavior, monitoring, and scheduled jobs.

## Prompts

* [Autonomous Agent Base](autonomous-base.md) - Shared behavioral base for autonomous engineering agents.
* [Donna Surface](donna.md) - Donna identity and operating tone: executive-assistant archetype, response shapes, and interaction boundaries.
* [Pepper Surface](pepper.md) - Project manager identity, issue-scoped evidence review, and interaction boundaries.
* [GitHub specialist](github-specialist.md) - Platform-neutral GitHub operations prompt with tiered authority and verified results.
* [Hermes direct-cron reporting footer](hermes-direct-cron-footer.md) - Evidence and report-shape contract appended to every direct-cron prompt.
* [Hermes direct-cron footer, quiet when healthy](hermes-direct-cron-footer-quiet.md) - Same contract for a job whose all-clear goes to a quiet channel.
* [Hermes daily status kanban summary](hermes-daily-status-kanban-summary.md) - Daily board status counts and long-running card links.
* [Hermes scheduled report contract](hermes-report-contract.md) - Exact priority counts, action outcomes, urgent-item accounting, and report authority.
* [Hermes Surface](hermes.md) - Canonical Hermes identity, tools, investigation discipline, escalation routing, homelab constraints, and model fabric.
* [Large-Tier Surface](large-tier.md) - Deep-reasoning and synthesis delta for a staged large-model serving tier.
* [Maintenance Windows](maintenance-windows.md) - Shared homelab hands-off state as Vikunja tasks, checked before touching live infrastructure.
* [Model Delegation](model-delegation.md) - Offloading bounded subtasks to a shared model router at the cheapest capable tier, with router-enforced budgets.
* [Monitor Agent Discipline](monitor-agent-discipline.md) - Bounded-query, durable-state, and alerting discipline for always-on monitoring agents.
* [Open WebUI Surface](open-webui.md) - Interactive chat-surface delta for Open WebUI.
* [Slack Interactor](slack-interactor.md) - Staged single Slack-tool role and bounded request/result contract.

## Hermes prompt groups

* [Assistant](hermes-assistant/index.md) - Assistant task routines and project coordination prompts.
* [Coordination](hermes-coordination/index.md) - Repository, review, research, and recurring maintenance prompts.
* [Curriculum](hermes-curriculum/index.md) - Orientation, investigation, and self-improvement prompts.
* [Profiles](hermes-profiles/index.md) - Operating-profile addenda for Hermes roles.
* [Reporting](hermes-reporting/index.md) - Status digests, capacity reports, and ordered hourly stats fragments.
* [Splunk](hermes-splunk/index.md) - Health, parsing, security, and investigation prompts.

## Claude Code

* [Claude Code subagents](claude-code/agents/index.md) - Subagent definitions delivered into every Claude Code session.
* [Claude Code rules](claude-code/rules/index.md) - Always-loaded rules delivered into every Claude Code session.

## Shared Global Instructions

* [Shared global instructions](instructions/index.md) - Shared agent instructions delivered to machines through the `instructions` package.
