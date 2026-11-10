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
* Reader: pull request author
* Acted signal: reviewed simplification suggestion

### [commit-grouper](commit-grouper.yaml)

* Tier: 0
* Trigger: call: caller

### [credential-steward](credential-steward.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: credential owner
* Acted signal: The owner schedules or resolves a rotation planning task.

### [daily-innovation](daily-innovation.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: operator
* Acted signal: One proposed task is accepted or done.

### [dep-review](dep-review.yaml)

* Tier: 1
* Trigger: event: github.pull_request
* Reader: dependency pull request maintainer
* Acted signal: dependency pull request merged or closed after advisory review

### [doc-contradiction-finder](doc-contradiction-finder.yaml)

* Tier: 1
* Trigger: event: github.pull_request
* Reader: documentation maintainer
* Acted signal: contradiction fix merged

### [docs-drift](docs-drift.yaml)

* Tier: 1
* Trigger: event: github.pull_request
* Reader: documentation maintainer
* Acted signal: documentation correction pull request merged

### [docs-updater](docs-updater.yaml)

* Tier: 1
* Trigger: event: github.pull_request
* Reader: documentation maintainer
* Acted signal: reviewed documentation proposal

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

### [github-clerk](github-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized caller
* Acted signal: verified receipt or actionable blocked result

### [langfuse-clerk](langfuse-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: verified gateway caller
* Acted signal: verified score report or actionable blocked result

### [merge-steward](merge-steward.yaml)

* Tier: 0
* Trigger: call: implementation-lead
* Reader: implementation lead
* Acted signal: Authorized pull requests are merged or their blockers are addressed.

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

### [openbao-clerk](openbao-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized secret administrator
* Acted signal: verified metadata supports an access or rotation review decision

### [plain-rewriter](plain-rewriter.yaml)

* Tier: 0
* Trigger: call: caller

### [plan-reconciler](plan-reconciler.yaml)

* Tier: 0
* Trigger: call: planning-lead
* Trigger: event: github.pull_request
* Reader: planning lead
* Acted signal: The lead acts on the reconciled plan and blockers.

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

### [promotion-review](promotion-review.yaml)

* Tier: 2
* Trigger: rotation: 1d
* Reader: supervising lead
* Acted signal: The lead reviews a mode-change pull request or resolves an evidence blocker.

### [proxmox-clerk](proxmox-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized virtualization operator
* Acted signal: verified resource state supports the caller's maintenance or capacity decision

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

### [semaphore-clerk](semaphore-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized workflow operator
* Acted signal: verified run receipt or actionable blocked result for an approved template

### [session-closer](session-closer.yaml)

* Tier: 0
* Trigger: call: operator-or-lead
* Reader: operator
* Acted signal: The operator uses the handoff or resolves a reported blocker.

### [ship-runner](ship-runner.yaml)

* Tier: 0
* Trigger: call: implementation-lead
* Reader: implementation lead
* Acted signal: The lead receives a confirmed pull request handoff.

### [slack-clerk](slack-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized Slack channel operator
* Acted signal: verified receipt for a message in an approved channel or an actionable blocked result

### [splunk-clerk](splunk-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized monitoring analyst
* Acted signal: verified search results support an authorized alert or investigation decision

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
* Reader: requesting operator
* Acted signal: verified task receipt or actionable blocked result

### [vikunja-triage](vikunja-triage.yaml)

* Tier: 2
* Trigger: event: vikunja
* Trigger: rotation: 1d
* Reader: Vikunja via vikunja-clerk
* Acted signal: proposed task move applied

### [voice-learn](voice-learn.yaml)

* Tier: 2
* Trigger: rotation: 7d
* Reader: style-gate and plain-rewriter prompts
* Acted signal: draft PR merged

### [zammad-clerk](zammad-clerk.yaml)

* Tier: 0
* Trigger: call: caller
* Reader: authorized incident operator
* Acted signal: verified ticket receipt or actionable blocked result

### [zammad-triage](zammad-triage.yaml)

* Tier: 2
* Trigger: event: zammad
* Trigger: rotation: 1d
* Reader: Zammad via zammad-clerk
* Acted signal: ticket state changes
