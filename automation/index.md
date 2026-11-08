# Automation

Prompts and reusable fragments for repository automation, cloud routines, and retired workflow references.

The cloud-routine bodies and their shared fragments were retired on 2026-08-06 when the
Anthropic cloud-routine substrate they ran on was decommissioned. They are kept here as
history, not as runnable prompts. Each retired entry's `source_history` note records where
its content went — Hermes jobs under `auto-ai-agent/`, an existing skill, or nowhere because
a native feature already covered it.

`issue-solver` is the exception and is still active. It never ran on that substrate — it runs
in GitHub Actions on a GitHub App token — so it and the one fragment it includes stay live.

## Prompts

* [Policy Rubric Sources](policy-gate-src/index.md) - Shared gomplate template, rubric inputs, and render checks.
* [Docs Drift Render Template](ai-workflows-docs-drift.prompt.yml.tmpl) - Renders the workflow prompt from the canonical agent prompt.
* [Dependency Review Render Template](ai-workflows-dep-review.md.tmpl) - Renders the workflow prompt from the canonical agent prompt.
* [Policy Gate](ai-workflows-policy-gate.prompt.yml) - Structured pull-request policy checks.
* [Security Review](ai-workflows-security-review.prompt.yml) - Structured pull-request security review.
* [Semantic Review](ai-workflows-semantic-review.prompt.yml) - Structured pull-request semantic review.
* [Leak Review](ai-workflows-leak-review.prompt.yml) - Structured public-disclosure review.
* [Docs Drift](ai-workflows-docs-drift.prompt.yml) - Documentation drift analysis.
* [Repository Hygiene](ai-workflows-repo-hygiene.prompt.yml) - Repository hygiene analysis.
* [Thread Triage](ai-workflows-thread-triage.prompt.yml) - Pull-request review-thread triage.
* [Testing Agents](testing/index.md) - Portable instruction bodies for specialized browser and UI-testing agents.
* [CI Workbook](ci-workbook/index.md) - Known CI failure signatures with their class, match pattern and fix recipe.
* [DRY Enforcer Agent](ai-workflows-agent-dry-enforcer.md) - Dormant Copilot agent profile for code simplification and DRY enforcement.
* [Issue Analyst Agent](ai-workflows-agent-issue-analyst.md) - Dormant Copilot agent profile for issue-intent analysis.
* [Label Expert Agent](ai-workflows-agent-label-expert.md) - Dormant Copilot agent profile for canonical issue labeling.
* [Momentum Analyst Agent](ai-workflows-agent-momentum-analyst.md) - Dormant Copilot agent profile for development-momentum analysis.
* [Best Practices Recommender](ai-workflows-best-practices.md) - Weekly repository-practices audit prompt.
* [CI Failure Issue](ai-workflows-ci-fail-issue.md) - Dormant prompt for creating an issue from a main-branch CI failure.
* [CI Failure Auto-Fix](ai-workflows-ci-fix.md) - Prompt for diagnosing and minimally fixing CI failures.
* [Code Simplifier](ai-workflows-code-simplifier.md) - Behavior-preserving code simplification prompt.
* [Dependency Update Risk Review](ai-workflows-dep-review.md) - Advisory dependency-update risk review prompt.
* [DRY Principles](ai-workflows-dry-principles-fragment.md) - Reusable code-simplification and duplication rules.
* [Issue Analysis](ai-workflows-issue-analysis-fragment.md) - Reusable issue categorization and duplicate-detection rules.
* [Issue Backlog Sweep](ai-workflows-issue-backlog-sweep.md) - Read-only issue-backlog triage prompt.
* [Issue Hygiene](ai-workflows-issue-hygiene.md) - Issue duplicate and housekeeping analysis prompt.
* [Issue Linker](ai-workflows-issue-linker.md) - PR-to-issue association and lifecycle prompt.
* [Issue Auto-Resolver](ai-workflows-issue-resolver.md) - Prompt for implementing a minimal fix for one GitHub issue.
* [Issue Sweeper](ai-workflows-issue-sweeper.md) - Weekly issue status-analysis prompt.
* [Issue Triage](ai-workflows-issue-triage.md) - Issue categorization, deduplication, and labeling prompt.
* [Label Sync](ai-workflows-label-sync.md) - Canonical repository-label synchronization prompt.
* [Merge Momentum](ai-workflows-merge-momentum-fragment.md) - Reusable development-direction analysis rules.
* [Next Steps](ai-workflows-next-steps.md) - Development-momentum analysis prompt.
* [Docs Sync](ai-workflows-docs-sync.md) - Per-merge private-docs correction prompt, triggered once per merged pull request.
* [Post-Merge Docs Review](ai-workflows-post-merge-docs-review.md) - Post-merge documentation quality review prompt.
* [Post-Merge Test Coverage](ai-workflows-post-merge-tests.md) - Post-merge test-coverage improvement prompt.
* [PR Review Responder](ai-workflows-pr-review-responder.md) - Prompt for evaluating and resolving pull-request feedback.
* [AI Provenance Footer](ai-workflows-provenance-footer.md) - Canonical provenance footer fragment for AI-created pull requests.
* [Release Notes](ai-workflows-release-notes.md) - Release-highlight drafting prompt.
* [Repository Orchestrator](ai-workflows-repo-orchestrator.md) - Multi-repository workflow dispatch prompt.
* [CI Failure Doctor](ci-failure-doctor.md) - Investigates failed GitHub Actions runs and reports root causes and remediation.
* [Daily Malicious Code Scan](daily-malicious-code-scan.md) - Reviews recent code changes for malicious behavior and supply-chain compromise indicators.
* [Dependabot PR Bundler](dependabot-pr-bundler.md) - Bundles compatible dependency security updates into tested draft pull requests.
* [GitHub Agentic Workflows Reference Template](gh-aw-reference-template.md) - Historical, non-production example of the retired GH-AW workflow format.
* [Public Docs Updater](public-docs-updater.md) - Reviews recent public repository activity and prepares one safe documentation update.
* [Repository Health Audit](repo-health-audit.md) - Audits repository automation, security, and maintenance health and files structured findings.
* [Bot PR Merge](bot-pr-merge.md) - Retired 2026-08-06. Security triage and allowlisted bot pull-request merge routine prompt.
* [Deploy Routines Reference](deploy-reference.md) - Historical auto-deployment prompt retained from the broken RemoteTrigger workflow.
* [Documentation Polish](docs-polish.md) - Retired 2026-08-06. Documentation quality improvement routine prompt.
* [Documentation Sync](docs-sync.md) - Retired 2026-08-06. Cross-site documentation synchronization routine prompt.
* [Estate Briefing](estate-briefing.md) - Retired 2026-08-06. Read-only daily GitHub estate briefing routine prompt.
* [Estate Janitor](estate-janitor.md) - Retired 2026-08-06. GitHub estate maintenance routine prompt.
* [Bot PR Security Triage](fragment-bot-pr-security-triage.md) - Retired 2026-08-06. Phase A CodeQL/Dependabot triage and auto-label gate for bot-pr-merge.
* [Bot PR Merge Gates](fragment-bot-pr-merge-gates.md) - Retired 2026-08-06. Phase B allowlist and merge gates for bot-pr-merge.
* [Docs-Sync Draft PR Authoring](fragment-docs-sync-pr-authoring.md) - Retired 2026-08-06. Step 8 draft-PR authoring and provenance for docs-sync.
* [Attribution](fragment-attribution.md) - Retired 2026-08-06. Shared provenance and attribution rules for cloud routines.
* [Hard Rules](fragment-hard-rules.md) - Retired 2026-08-06. Shared load-bearing safety and mutation rules for cloud routines.
* [Connectivity Preflight](fragment-preflight.md) - Retired 2026-08-06. Shared authentication and egress preflight for cloud routines.
* [Issue Solver](issue-solver.md) - GitHub Actions task-driver prompt for resolving one Linear task.
* [Prerequisites](fragment-prerequisites.md) - Shared runtime tools and environment prerequisites; still consumed by issue-solver.
* [Redaction](fragment-redaction.md) - Retired 2026-08-06. Shared sensitive-data redaction rules for cloud routines.
* [Skip List](fragment-skip-list.md) - Retired 2026-08-06. Shared repository exclusions for cloud routines.
* [Slack Output](fragment-slack-output.md) - Retired 2026-08-06. Shared Slack output and sanitization rules for cloud routines.
* [State File](fragment-state-file.md) - Retired 2026-08-06. Shared durable cross-run state contract for cloud routines.
* [State Migration](fragment-state-migrate.md) - Retired 2026-08-06. Shared one-run state migration fragment for renamed routines.
* [Pre-Commit Bump](precommit-bump.md) - Retired 2026-08-06. Estate-wide pre-commit hook update routine prompt.
* [Repository Audit](repo-audit.md) - Retired 2026-08-06. Rotating estate-wide repository audit routine prompt.
* [Sub-Issue Closer](sub-issue-closer.md) - Recursively closes parent issues after every tracked sub-issue is complete.
