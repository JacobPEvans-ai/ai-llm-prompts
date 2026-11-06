# Agent prompts

* [zammad-review](zammad-review.md) - Canonical Hermes cron task.
* [self-audit](self-audit.md) - Canonical Hermes cron task.
* [voice-learn](voice-learn.md) - Canonical Hermes cron task.
* [assistant-pulse](assistant-pulse.md) - Canonical Hermes cron task.
* [assistant-inbox-groom](assistant-inbox-groom.md) - Canonical Hermes cron task.
* [assistant-daily-brief](assistant-daily-brief.md) - Canonical Hermes cron task.
* [assistant-decision-nudge](assistant-decision-nudge.md) - Canonical Hermes cron task.
* [assistant-evening-wrap](assistant-evening-wrap.md) - Canonical Hermes cron task.
* [assistant-nightly-research](assistant-nightly-research.md) - Canonical Hermes cron task.
* [assistant-task-triage](assistant-task-triage.md) - Canonical Hermes cron task.
* [assistant-weekly-review](assistant-weekly-review.md) - Canonical Hermes cron task.
* [splunk-security-lens-v2](splunk-security-lens-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [splunk-error-triage-v2](splunk-error-triage-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [splunk-parsing-quality-v2](splunk-parsing-quality-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [anomaly-hunt-v2](anomaly-hunt-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [homelab-ai-fabric-status-v2](homelab-ai-fabric-status-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [zammad-incident-review-v2](zammad-incident-review-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [github-org-triage-v2](github-org-triage-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [daily-operator-summary-v2](daily-operator-summary-v2.md) - Canonical Hermes cron task, with its schedule disabled.
* [splunk-hourly-digest-v3](splunk-hourly-digest-v3.md) - Canonical Hermes cron task, with its schedule disabled.
* [homelab-ai-fabric-status](homelab-ai-fabric-status.md) - Canonical Hermes cron task.
* [hermes-nightly-wiki](hermes-nightly-wiki.md) - Canonical Hermes cron task, with its schedule disabled.
* [daily-summary](daily-summary.md) - Canonical Hermes cron task.
* [splunk-triage](splunk-triage.md) - Canonical Hermes cron task, with its schedule disabled.
* [splunk-security](splunk-security.md) - Canonical Hermes cron task, with its schedule disabled.
* [splunk-parsing](splunk-parsing.md) - Canonical Hermes cron task.
* [splunk-deepdive](splunk-deepdive.md) - Canonical Hermes cron task.
* [github-triage](github-triage.md) - Canonical Hermes cron task.
* [bot-pr-triage](bot-pr-triage.md) - Canonical Hermes cron task.
* [github-maint-review](github-maint-review.md) - Canonical Hermes cron task.
* [release-watch](release-watch.md) - Canonical Hermes cron task.
* [review](review.md) - Canonical Hermes cron task, with its schedule disabled.
* [anomaly-hunt](anomaly-hunt.md) - Canonical Hermes cron task, with its schedule disabled.
* [docs-study](docs-study.md) - Canonical Hermes cron task.
* [fleet-health](fleet-health.md) - Canonical Hermes cron task.
* [docs-sync](docs-sync.md) - Canonical Hermes cron task, with its schedule disabled.
* [repo-scorecard](repo-scorecard.md) - Canonical Hermes cron task, with its schedule disabled.
* [secrets-policy-audit](secrets-policy-audit.md) - Canonical Hermes cron task.
* [pricing-diff](pricing-diff.md) - Canonical Hermes cron task, with its schedule disabled.
* [blocked-parent-triage-digest](blocked-parent-triage-digest.md) - Canonical Hermes cron task.
* [router-capacity-digest](router-capacity-digest.md) - Canonical Hermes cron task.
* [backlog-sweep](backlog-sweep.md) - Canonical Hermes cron task, with its schedule disabled.
* [github-cache-stats](github-cache-stats.md) - Canonical Hermes cron task.
* [ai-news](ai-news.md) - Canonical Hermes cron task, with its schedule disabled.
* [daily-innovation](daily-innovation.md) - Canonical Hermes cron task, with its schedule disabled.
* [app-seeding](app-seeding.md) - Canonical Hermes cron task, with its schedule disabled.
* [model-routing-review](model-routing-review.md) - Canonical Hermes cron task.
* [promotion-drift](promotion-drift.md) - Canonical Hermes cron task.
* [service-pulse](service-pulse.md) - Canonical Hermes cron task.
* [splunk-health](splunk-health.md) - Canonical Hermes cron task.
* [llm-stats-hourly](llm-stats-hourly.md) - Canonical Hermes cron task.
* [repo-crawl](repo-crawl.md) - Canonical Hermes cron task, with its schedule disabled.

* [Donna](donna.md) - Interactive personal assistant and operator-managed interest ranking.
* [AI news brief](ai-news-brief.md) - Daily verified news for configured interests.
* [Slack digest](slack-digest.md) - Decisions and asks from explicitly allowed channels.
* [Memory consolidation](memory-consolidation.md) - Proposed dated Donna-bank summary.
* [Vikunja backlog review](vikunja-backlog-review.md) - Weekly read-only task review.
* [Model watch](model-watch.md) - Parameterized upstream release scouting.
* [Benchmark tracker](benchmark-tracker.md) - Dated, task-matched leaderboard changes.
* [Trending quants](trending-quants.md) - Revision-pinned quant provenance scouting.
* [AI news digest](ai-news-digest.md) - Dated model-catalog announcements.
* [Model benchmarker](model-benchmarker.md) - Complete dated model, artifact, runtime, and benchmark dossiers.

* [Action extractor](action-extractor.md) - Summarize notes or a conversation and extract its action items.
* [CI fixer](ci-fixer.md) - Repair one eligible code defect exposed by a failed check.
* [Code simplifier](code-simplifier.md) - Review eligible changes for concrete, behavior-preserving simplifications.
* [Commit grouper](commit-grouper.md) - Group changed paths into topical commits with caller-supplied message prefixes.
* [Doc contradiction finder](doc-contradiction-finder.md) - Report contradictions between documentation pages after a merged pull request.
* [Docs updater](docs-updater.md) - Propose safe private-documentation edits from merged pull requests or operator-decided findings.
* [Plain rewriter](plain-rewriter.md) - Rewrite one draft in plain language and keep every fact.
* [Shared homelab context](shared/homelab.md) - Static safety and routing context composed into canonical Dify prompts
  and loaded before Promptfoo agent prompts.
* [Style gate](style-gate.md) - Check one draft against the style rules and list every violation.
* [Tag suggester](tag-suggester.md) - Pick tags for one note from a caller-supplied allowed list.
* [Vikunja Clerk](vikunja-clerk.md) - Read, file, and update tasks within an explicit project mandate.
* [Vikunja Triage](vikunja-triage.md) - Rank eligible tasks and propose verified comments or completion updates.
* [Zammad Triage](zammad-triage.md) - Rank authorized tickets and return guarded triage proposals.
