<!-- Generated from agent definitions. Run make render-index. -->
# Agent catalog

## Authoring

* [Agent and skill building standards](../auto-ai-agent/instructions/agentsmd/rules/on-demand/agent-standards.md) - Agent and skill authoring rules.

## Validation

* [Agent evaluations](evals/promptfoo/README.md) - Executable evaluation suites and output contracts.
* [Dify import](dify/IMPORT.md) - Generated application imports and acceptance checks.

## Roster

| Agent | Tier | Trigger | Reader | Acted signal |
| --- | --- | --- | --- | --- |
| [action-extractor](action-extractor.yaml) | 0 | call: caller | — | — |
| [ci-fixer](ci-fixer.yaml) | 1 | event: github.check_run | — | — |
| [code-simplifier](code-simplifier.yaml) | 1 | event: github.pull_request | — | — |
| [commit-grouper](commit-grouper.yaml) | 0 | call: caller | — | — |
| [daily-innovation](daily-innovation.yaml) | 2 | rotation: 1d | operator | One proposed task is accepted or done. |
| [doc-contradiction-finder](doc-contradiction-finder.yaml) | 1 | event: github.pull_request | — | — |
| [docs-updater](docs-updater.yaml) | 1 | event: github.pull_request | — | — |
| [donna-evening-wrap](donna-evening-wrap.yaml) | 2 | anchor: 23:11 UTC | operator | A listed item is moved or done. |
| [donna-morning-brief](donna-morning-brief.yaml) | 2 | anchor: 12:37 UTC | operator | A listed item changes within 24 hours. |
| [donna-research](donna-research.yaml) | 2 | rotation: 1d | operator | The associated Vikunja item is closed or commented on. |
| [donna-weekly-review](donna-weekly-review.yaml) | 2 | anchor: 15:31 UTC (Sun) | operator | A proposed move is applied. |
| [plain-rewriter](plain-rewriter.yaml) | 0 | call: caller | — | — |
| [style-gate](style-gate.yaml) | 0 | call: caller | — | — |
| [tag-suggester](tag-suggester.yaml) | 0 | call: caller | — | — |
| [vikunja-clerk](vikunja-clerk.yaml) | 0 | call: caller | — | — |
| [vikunja-triage](vikunja-triage.yaml) | 2 | event: vikunja; rotation: 1d | — | — |
| [zammad-triage](zammad-triage.yaml) | 2 | event: zammad; rotation: 1d | — | — |
