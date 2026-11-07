# Hermes coordination prompts

* [Hermes bot PR triage](../hermes-bot-pr-triage.md) - Delta-aware bot-PR security triage plus a once-daily stale-open-PR report; never merges.
* [Hermes docs sync](../hermes-docs-sync.md) - Retired 2026-09-05. Bounded pass that routed doc-worthy changes to public or private docs via draft PRs.
* [Hermes GitHub triage](../hermes-github-triage.md) - Read-only delta-aware Dryvist GitHub organization triage prompt.
* [Hermes inbound webhook relay](../hermes-inbound-webhook.md) - Prompt template for relaying the raw inbound webhook payload.
* [Hermes nightly wiki health](../hermes-nightly-wiki-health.md) - Nightly wiki lint and health-check prompt.
* [Hermes repo scorecard](../hermes-repo-scorecard.md) - Weekly weighted 0-100 repo-health scorecard with week-over-week deltas.
* [Hermes promotion drift](../hermes-promotion-drift.md) - Daily read-only sweep that reports git-flow repos with develop ahead of main and no promotion PR.
* [Hermes PR shepherd sweep](../hermes-pr-shepherd-sweep.md) - Hourly sweep that updates BEHIND agent PRs and leaves eligible merges to the org workflow.
* [Hermes release watch](../hermes-release-watch.md) - Daily digest of recent releases for tracked dependencies.
* [Hermes self-audit](../hermes-self-audit.md) - Scheduled self-correction loop: own Slack output critique, own Splunk errors,
  subsystem health, correction cards.
* [Hermes secrets policy audit](../hermes-secrets-policy-audit.md) - Issue-only scan for credential and private-topology leaks, never a pull request.
* [Hermes zammad review](../hermes-zammad-review.md) - Bounded open-incident lifecycle sweep across all Zammad queues.
* [Hermes github maint review](../hermes-github-maint-review.md) - Read-only repository maintenance review and delta digest.
* [Hermes reviewer](../hermes-reviewer.md) - Eight-hour self-review of Kanban activity and follow-up cards.
* [Hermes anomaly hunt](../hermes-anomaly-hunt.md) - Bounded anomaly investigation with confirming evidence and follow-up cards.
* [Hermes docs study](../hermes-docs-study.md) - Daily public documentation drift review with bounded follow-up cards.
* [Hermes ai news](../hermes-ai-news.md) - Interest-guided news scouting with retrieved sources and deduplicated suggestions.
* [Hermes ai news interests](../hermes-ai-news-interests.md) - Shared interest seed for the news scouting profile.
* [Hermes daily innovation](../hermes-daily-innovation.md) - Evidence-based improvement proposals recorded in Kanban and the proposal log.
* [Hermes app seeding](../hermes-app-seeding.md) - Bounded application setup with verified completion markers.
* [Hermes pricing diff](../hermes-pricing-diff.md) - Weekly public model pricing changes against a saved baseline.
* [Hermes backlog sweep](../hermes-backlog-sweep.md) - One-incident evidence review with a proposed next step.
* [Hermes model routing review](../hermes-model-routing-review.md) - Read-only review of tracked public model routing resources.
* [Hermes github route](../hermes-github-route.md) - Pull request review request populated from a webhook event.
* [Hermes repo crawl](../hermes-repo-crawl.md) - Triage of new repository crawl findings with scoped pull request updates.
