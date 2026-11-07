<!-- Generated from agent definitions. Run make render-index. -->
# Agent catalog

## Authoring

* [Agent and skill building standards](../auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards.md) - Agent and skill authoring rules.

## Validation

* [Agent evaluations](evals/promptfoo/README.md) - Executable evaluation suites and output contracts.
* [Dify import](dify/IMPORT.md) - Generated application imports and acceptance checks.

## Roster

### [action-extractor](action-extractor.yaml)

* Tier: 0
* Trigger: call: caller

### [agent-audit](agent-audit.yaml)

* Tier: 2
* Trigger: rotation: 12h
* Reader: Vikunja via vikunja-clerk
* Acted signal: task closed

### [ai-news](ai-news.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: donna-morning-brief
* Acted signal: cited news item

### [alert-triage](alert-triage.yaml)

* Tier: 1
* Trigger: event: splunk.alert
* Trigger: event: grafana.alert
* Reader: Zammad via zammad-clerk
* Acted signal: ticket updated

### [code-simplifier](code-simplifier.yaml)

* Tier: 1
* Trigger: event: github.pull_request

### [commit-grouper](commit-grouper.yaml)

* Tier: 0
* Trigger: call: caller

### [daily-innovation](daily-innovation.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: operator
* Acted signal: One proposed task is accepted or done.

### [doc-contradiction-finder](doc-contradiction-finder.yaml)

* Tier: 1
* Trigger: event: github.pull_request

### [docs-updater](docs-updater.yaml)

* Tier: 1
* Trigger: event: github.pull_request

### [donna-evening-wrap](donna-evening-wrap.yaml)

* Tier: 2
* Trigger: anchor: 23:11 UTC
* Reader: operator
* Acted signal: A listed item is moved or done.

### [donna-morning-brief](donna-morning-brief.yaml)

* Tier: 2
* Trigger: anchor: 12:37 UTC
* Reader: operator
* Acted signal: A listed item changes within 24 hours.

### [donna-research](donna-research.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: operator
* Acted signal: The associated Vikunja item is closed or commented on.

### [donna-weekly-review](donna-weekly-review.yaml)

* Tier: 2
* Trigger: anchor: 15:31 UTC (Sun)
* Reader: operator
* Acted signal: A proposed move is applied.

### [model-benchmarker](model-benchmarker.yaml)

* Tier: 2
* Trigger: call: model-scout
* Reader: catalog PR
* Acted signal: dossier merged

### [model-scout](model-scout.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: model-benchmarker
* Acted signal: catalog PR via github-clerk

### [plain-rewriter](plain-rewriter.yaml)

* Tier: 0
* Trigger: call: caller

### [pr-keeper](pr-keeper.yaml)

* Tier: 1
* Trigger: event: github.pull_request
* Trigger: event: github.check_run
* Trigger: event: github.pull_request_review
* Trigger: event: github.pull_request_review_comment
* Trigger: event: github.issue_comment
* Trigger: rotation: 15m
* Reader: pull requests via github-clerk
* Acted signal: required checks green on current head

### [release-digest](release-digest.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: donna-morning-brief
* Acted signal: upgrade task via vikunja-clerk

### [release-promoter](release-promoter.yaml)

* Tier: 1
* Trigger: event: github.push
* Reader: promotion pull request via github-clerk
* Acted signal: promotion PR merged

### [repo-janitor](repo-janitor.yaml)

* Tier: 2
* Trigger: rotation: 7d
* Trigger: event: agent-sandbox.finding
* Reader: agent-sandbox jobs
* Acted signal: fix PR merged

### [splunk-deepdive](splunk-deepdive.yaml)

* Tier: 2
* Trigger: rotation: 7d
* Reader: private documentation page
* Acted signal: page PR merged

### [style-gate](style-gate.yaml)

* Tier: 0
* Trigger: call: caller

### [tag-suggester](tag-suggester.yaml)

* Tier: 0
* Trigger: call: caller

### [vikunja-clerk](vikunja-clerk.yaml)

* Tier: 0
* Trigger: call: caller

### [vikunja-triage](vikunja-triage.yaml)

* Tier: 2
* Trigger: event: vikunja
* Trigger: rotation: 1d

### [voice-learn](voice-learn.yaml)

* Tier: 2
* Trigger: rotation: 7d
* Reader: style-gate and plain-rewriter prompts
* Acted signal: draft PR merged

### [zammad-triage](zammad-triage.yaml)

* Tier: 2
* Trigger: event: zammad
* Trigger: rotation: 1d
