# Continuous AI Agents

Prompts for continuously running local agents, shared autonomous behavior, monitoring, and scheduled jobs.

## Prompts

* [Autonomous Agent Base](autonomous-base.md) - Shared behavioral base for autonomous engineering agents.
* [Donna Surface](donna.md) - Donna identity and operating tone: executive-assistant archetype, response shapes, and interaction boundaries.
* [Hermes bot PR triage](hermes-bot-pr-triage.md) - Delta-aware bot-PR security triage plus a once-daily stale-open-PR report; never merges.
* [Hermes curriculum application fleet health](hermes-curriculum-apps.md) - Fleet-health and repository cross-reference curriculum job.
* [Hermes curriculum self-improvement](hermes-curriculum-improve.md) - Bounded evidence-based self-improvement curriculum job.
* [Hermes curriculum orientation](hermes-curriculum-orient.md) - Verified self-orientation curriculum job.
* [Hermes curriculum repository sweep](hermes-curriculum-reposweep.md) - Read-only GitHub triage curriculum job.
* [Hermes curriculum Splunk investigation](hermes-curriculum-splunk.md) - Evidence-driven Splunk investigation curriculum job.
* [GitHub specialist](github-specialist.md) - Platform-neutral GitHub operations prompt with tiered authority and verified results.
* [Hermes daily fabric status](hermes-daily-fabric-status.md) - Hourly AI-fabric status and delta-reporting prompt.
* [Hermes daily summary](hermes-daily-summary.md) - Once-daily delta-only operator rollup for the home channel.
* [Hermes digest: anomaly hunt](hermes-digest-anomaly-hunt.md) - Twice-daily auto-delivered unmonitored-pattern anomaly hunt.
* [Hermes digest: daily operator summary](hermes-digest-daily-operator-summary.md) - Daily auto-delivered ingest-volume operator summary.
* [Hermes digest: GitHub org triage](hermes-digest-github-org-triage.md) - Daily auto-delivered dryvist org PR/issue triage.
* [Hermes digest: homelab AI fabric status](hermes-digest-homelab-ai-fabric-status.md) - 6-hourly auto-delivered AI fabric component health probe.
* [Hermes digest: Splunk error triage](hermes-digest-splunk-error-triage.md) - Hourly auto-delivered Splunk error/failure triage digest.
* [Hermes digest: Splunk parsing quality](hermes-digest-splunk-parsing-quality.md) - Daily auto-delivered Splunk per-sourcetype parsing-quality digest.
* [Hermes digest: Splunk security lens](hermes-digest-splunk-security-lens.md) - 6-hourly auto-delivered Splunk security-relevant pattern digest.
* [Hermes digest: Zammad incident review](hermes-digest-zammad-incident-review.md) - Daily auto-delivered open Zammad incident review.
* [Hermes docs sync](hermes-docs-sync.md) - Retired 2026-09-05. Bounded pass that routed doc-worthy changes to public or private docs via draft PRs.
* [Hermes GitHub triage](hermes-github-triage.md) - Read-only delta-aware Dryvist GitHub organization triage prompt.
* [Hermes inbound webhook relay](hermes-inbound-webhook.md) - Prompt template for relaying the raw inbound webhook payload.
* [Hermes nightly wiki health](hermes-nightly-wiki-health.md) - Nightly wiki lint and health-check prompt.
* [Hermes repo scorecard](hermes-repo-scorecard.md) - Weekly weighted 0-100 repo-health scorecard with week-over-week deltas.
* [Hermes promotion drift](hermes-promotion-drift.md) - Daily read-only sweep that reports git-flow repos with develop ahead of main and no promotion PR.
* [Hermes PR shepherd sweep](hermes-pr-shepherd-sweep.md) - Hourly sweep that updates BEHIND agent PRs and leaves eligible merges to the org workflow.
* [Hermes release watch](hermes-release-watch.md) - Daily digest of recent releases for tracked dependencies.
* [Hermes self-audit](hermes-self-audit.md) - Scheduled self-correction loop: own Slack output critique, own Splunk errors, subsystem health, correction cards.
* [Hermes secrets policy audit](hermes-secrets-policy-audit.md) - Issue-only scan for credential and private-topology leaks, never a pull request.
* [Hermes direct-cron reporting footer](hermes-direct-cron-footer.md) - Evidence and report-shape contract appended to every direct-cron prompt.
* [Hermes direct-cron footer, quiet when healthy](hermes-direct-cron-footer-quiet.md) - Same contract for a job whose all-clear goes to a quiet channel.
* [Hermes service pulse](hermes-service-pulse.md) - Hourly service pulse that keeps compact baselines and a flaky list in the available memory.
* [Hermes Splunk deep dive](hermes-splunk-deepdive.md) - Quiet Splunk index or sourcetype characterization prompt.
* [Hermes Splunk digest](hermes-splunk-digest.md) - Hourly delta-aware Splunk status digest prompt.
* [Hermes Splunk license audit](hermes-splunk-license.md) - Two-hourly Splunk audit of system messages, health report and license usage, learning in Hindsight.
* [Hermes Splunk parsing sweep](hermes-splunk-parsing.md) - Bounded Splunk data-quality monitoring prompt.
* [Hermes Splunk platform health](hermes-splunk-health.md) - Two-hourly Splunk health review with compact memory baselines.
* [Hermes Splunk security sweep](hermes-splunk-security.md) - Bounded Splunk security-lens monitoring prompt.
* [Hermes Zammad review](hermes-zammad-review.md) - Proactive open-incident lifecycle sweep across all Zammad queues.
* [Hermes Splunk triage](hermes-splunk-triage.md) - Broad bounded Splunk anomaly-sweep prompt.
* [Hermes Surface](hermes.md) - Canonical Hermes identity, tools, investigation discipline, escalation routing, homelab constraints, and model fabric.
* [Large-Tier Surface](large-tier.md) - Deep-reasoning and synthesis delta for a staged large-model serving tier.
* [Maintenance Windows](maintenance-windows.md) - Shared homelab hands-off state as Vikunja tasks, checked before touching live infrastructure.
* [Model Delegation](model-delegation.md) - Offloading bounded subtasks to a shared model router at the cheapest capable tier, with router-enforced budgets.
* [Monitor Agent Discipline](monitor-agent-discipline.md) - Bounded-query, durable-state, and alerting discipline for always-on monitoring agents.
* [Open WebUI Surface](open-webui.md) - Interactive chat-surface delta for Open WebUI.
* [Slack Interactor](slack-interactor.md) - Staged single Slack-tool role and bounded request/result contract.

## Claude Code

* [Claude Code subagents](claude-code/agents/index.md) - Subagent definitions delivered into every Claude Code session.
* [Claude Code rules](claude-code/rules/index.md) - Always-loaded rules delivered into every Claude Code session.

## Shared Global Instructions

* [Shared global instructions](instructions/index.md) - Shared agent instructions delivered to machines through the `instructions` package.
