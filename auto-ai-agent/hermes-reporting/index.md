# Hermes reporting prompts

* [Hermes reporting status levels](status-levels.md) - Shared green, yellow and red status levels for Hermes report and alert headlines.
* [Hermes daily fabric status](../hermes-daily-fabric-status.md) - Hourly AI-fabric status and delta-reporting prompt.
* [Hermes daily summary](../hermes-daily-summary.md) - Once-daily delta-only operator rollup for the home channel.
* [Hermes digest: anomaly hunt](../hermes-digest-anomaly-hunt.md) - Twice-daily auto-delivered unmonitored-pattern anomaly hunt.
* [Hermes digest: daily operator summary](../hermes-digest-daily-operator-summary.md) - Daily auto-delivered ingest-volume operator summary.
* [Hermes digest: GitHub org triage](../hermes-digest-github-org-triage.md) - Daily auto-delivered dryvist org PR/issue triage.
* [Hermes digest: homelab AI fabric status](../hermes-digest-homelab-ai-fabric-status.md) - 6-hourly auto-delivered AI fabric component health probe.
* [Hermes digest: Zammad incident review](../hermes-digest-zammad-incident-review.md) - Daily auto-delivered open Zammad incident review.
* [Hermes service pulse](../hermes-service-pulse.md) - Hourly service pulse that keeps compact baselines and a flaky list in the available memory.
* [Hermes fleet health](../hermes-fleet-health.md) - Weekly review of recurring workload outcomes against a recalled baseline.
* [Hermes daily status kanban summary](../hermes-daily-status-kanban-summary.md) - Shared board status summary appended to the fabric report.
* [Hermes blocked parent triage digest](../hermes-blocked-parent-triage-digest.md) - Daily report of blocked parent cards and waiting children.
* [Hermes router capacity digest](../hermes-router-capacity-digest.md) - Daily router capacity metrics and changes against a recalled baseline.
* [Hermes github cache stats](../hermes-github-cache-stats.md) - Read-only repository cache usage and churn threshold report.

## Hourly stats assembly order

Strip each part's YAML frontmatter, then concatenate the literal bodies in this order with no trimming or added separators:

1. [Delivery, metrics, and query limits](../hermes-llm-stats-hourly-part1.md).
2. [Seed queries and row interpretation](../hermes-llm-stats-hourly-part2.md).
3. [Memory, tools, feedback, and format](../hermes-llm-stats-hourly-part3.md).

The assembled body retains resource identifier `prompt://dryvist/auto-ai-agent/hermes-llm-stats-hourly`.
