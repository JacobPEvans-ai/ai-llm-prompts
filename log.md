# Change Log

## 2026-11-06

* **Add (agents)**: Define the complete Hermes cron prompt roster, retaining disabled schedules, source replacements,
  read-only connector access, and sandbox handoffs for repository work.

* **Add (agents)**: Define Donna, scheduled news, Slack, memory and backlog tasks, and five local scouting tasks with
  private routing, connector proposals, dated model dossiers, and Promptfoo suites.

## 2026-11-04

* **Update (auto-ai-agent)**: The Splunk deep dive bounds its utilization pass to one search per signal over an 8-day
  window, grouped into rolling 24-hour buckets, caps each result at 20 rows, and allows 3 utilization searches and 12
  Splunk searches per run.

* **Update (agents)**: Make the major-release rule human-only in the always-loaded operating core, with no operator-approval
  path, and point the git-flow rule's major-version line at it.

* **Remove (evals)**: Drop the GitHub capability case whose only subject was the hold label.
* **Update (automation)**: The Dependabot bundler holds a waiting pull request as a draft; the hold-label option is
  removed.
* **Update (agents)**: The Hermes PR sweep treats a draft as the only agent-side hold and no longer leaves hold-label
  PRs alone.
* **Update (agents)**: The PR shepherd keeps a pull request draft to hold it; the automerge step no longer names a
  hold label.
* **Update (instructions)**: The session coordination claim step holds work with a draft alone.
* **Update (instructions)**: The git-flow merging step says the org workflow arms eligible pull requests and a
  draft holds one.
* **Update (instructions)**: The projects brief holds work with a draft alone; the automerge and merge bullets no
  longer name a hold label.
* **Update (instructions)**: The zcode-job sandbox delegation step hands back a ready pull request with no hold
  label; the leak-scan and no-auto-merge rules stay.

## 2026-11-03

* **Update (instructions)**: Add privileged-run rules to `infrastructure-conventions`: narrowest selector, full
  reconciles only in a maintenance window, plan before apply, and one owner per privileged chain. Add token
  accessor capture and EXIT-trap revocation to `secrets-separation`. Add hourly batching of operator approvals to
  `delegation-trust`.

## 2026-11-02

* **Fix (agents)**: The Vikunja triage guard accepts a done action only for a merged linked PR or a closed linked issue;
  a closed PR that was never merged is not done.
* **Fix (agents)**: Vikunja triage proposes a done action only for a merged linked PR or a closed linked issue; an open
  linked PR or issue is not done.
* **Fix (agents)**: Redact finder quotes with one shared rule before the verbatim check, and mark a finding whose quote needed
  redaction as a security finding that is never asked in Slack.
* **Fix (agents)**: Route an accepted docs-updater operator decision to the model node, with its cited statements and pages
  as context and no pull request reads. Pull request routing is unchanged.
* **Add (agents)**: Add the shadow-only doc-contradiction-finder for documentation pages after merged pull requests. It
  reads changed and related pages, returns a JSON findings object, and has no write, Slack, or memory tools.
* **Update (agents)**: Give docs-updater a second mandate shape, {repo, finding_ref, operator_decision}, for an operator
  decision on a reported contradiction. The Dify gate admits it without pull request reads and keeps live writes off.
* **Add (agents)**: Add the shadow-only docs-updater for merged pull requests, with safe private-documentation proposals
  and a read-only GitHub set.
* **Fix (agents)**: Compose Vikunja Clerk's `Parse request` classifier from its shared prefix and canonical prompt;
  clarify shared-prefix inclusion in Promptfoo generation docs.
* **Fix (agents)**: Generate Dify app names, model roles, schedules, mode defaults, and Vikunja MCP contracts from
  agent YAML; make the DSL drift check byte-exact, enforce unique per-agent scopes and key refs, and give Vikunja
  triage its own memory and key references. Update import guides to use the renderer.
* **Update (agents)**: Render Dify workflow system prompts from their source templates and canonical prompts, with a
  declared Vikunja Clerk parser exception and a drift check in `agent-tests`.
* **Add (agents)**: Add one shared homelab context prefix and point the five agent definitions at it. Validate roster
  fields and Dify prompt copies; accept opened or ready-for-review pull requests in the code simplifier.
* **Creation (agents)**: Add a scheduled, guarded Zammad triage Workflow with group-scoped reads, local-only model routing, and shadow output.

## 2026-11-01

* **Creation (agents)**: Add a scheduled, guarded Vikunja triage Workflow with shadow output, policy-scoped reads, evidence checks, and regression cases.

## 2026-10-31

* **Creation (applications)**: Add a platform-neutral Vikunja task specialist prompt with a
  request/result contract, duplicate-safe writes, readback verification, role-based escalation, and a
  single-owner handoff boundary.
* **Add (auto-ai-agent)**: Add a platform-neutral GitHub specialist prompt with tiered authority, idempotent write
  handling, evidence-based result statuses, and declarative acceptance examples.
* **Add (auto-ai-agent)**: staged Slack Interactor contract permits one authorized fresh send without a key or record
  when trusted native context establishes no prior attempt; runtime binding remains pending.
* **Update (auto-ai-agent/instructions)**: `AGENTS.md` states the one delegation routing order: Codex, zcode-job sandbox,
  Z.ai GLM, OpenCode Go, then Haiku `xhigh`. `model-delegation.md` keeps CLI procedure and links to it.

## 2026-10-30

* **Update (auto-ai-agent)**: Service-pulse and Splunk-health prompts use the active memory provider and configured probes.
* **Update (auto-ai-agent/instructions)**: `model-delegation.md` uses configured Herdr for agent work and declares
  remote targeting, explicit harness fallback, and unchanged routing and authority gates.

## 2026-10-29

* **Update (auto-ai-agent/instructions)**: `git-flow.md` states the Main Source Gate allow-list for merges into `main`.

## 2026-10-26

* **Update (auto-ai-agent/instructions)**: `AGENTS.md` starts branches with `git town hack` instead of `/refresh-repo`.

## 2026-10-25

* **Update (auto-ai-agent/instructions)**: Branch names start with their Conventional Commits type (`feat/`, `fix/`, …) on
  trunk and git-flow repos alike; `feature/` is retired.

## 2026-10-24

* **Update (auto-ai-agent/instructions)**: `git-flow.md` starts and syncs branches with Git Town by rebase and drops git-flow-next.
* **Update (auto-ai-agent/instructions)**: Centralize the Codex call contract in `model-delegation.md`, align delegate
  output expectations, and point routing references to the canonical rule.

## 2026-10-23

* **Add (auto-ai-agent/instructions)**: `task-tracking.md` starts program-scale work with a tracker pass
  (inventory, dedupe and close, retarget, file epics) and keeps epics current at each milestone.

## 2026-10-18

* **Change (auto-ai-agent/instructions)**: Route incidents and follow-ups by role and add a public example role map.
* **Add (auto-ai-agent/instructions)**: Generic infrastructure, workspace, secrets, dependency, and observability guidance.
* **Fix (auto-ai-agent)**: Correct the PR shepherd executor source reference.

* **Add (auto-ai-agent/instructions)**: Migrate the shared global instruction files, preserving Claude-native
  frontmatter and source bodies; deliver the original layout through the `instructions` package with OKF
  metadata stripped.

* **Change (auto-ai-agent/claude-code)**: Replace the model-specific executor definitions with one model-neutral
  `executor` agent; the router selects the backend and effort per spawn.

## 2026-10-14

* **Add (developer-tools)**: `public-disclosure-judge.md`, a fail-closed one-token classifier for actual public disclosures.
  It allows WHAT-only descriptions of code behavior.

## 2026-10-12

* **Add (auto-ai-agent)**: `claude-code/agents/pr-shepherd.md`, a subagent that drives named pull requests to merged
  and promotes a git-flow repo afterward. `hermes-promotion-drift.md` opens a draft promotion PR for each git-flow
  repo whose develop is ahead of main. `hermes-pr-shepherd-sweep.md` updates BEHIND agent PRs and enables auto-merge on
  clean ones.
* **Change (auto-ai-agent)**: `hermes-bot-pr-triage.md` no longer labels release-please PRs; they auto-merge without a
  label.
* **Update (auto-ai-agent)**: `autonomous-base.md` and `hermes.md` trim shared and Hermes guidance while preserving their behavior contracts.
* **Update (CI)**: Add ordered prompt token limits and enable the shared token-budget check.

## 2026-10-11

* **Change (auto-ai-agent)**: `hermes-bot-pr-triage.md` gains a manual-repo risk lane. In repos whose `automerge`
  property is `manual`, it labels low-risk Renovate and release-please PRs once CI is green, and drops the label when
  the head commit changes.

* **Add (automation)**: `ci-workbook/`, 26 seed entries describing recurring CI failure signatures. Each entry's
  `ci_workbook` frontmatter field holds its class, a match pattern for the normalized failure text and, where one
  exists, a fix or reproduce command. The body is the fix recipe.

## 2026-10-10

* **Add (auto-ai-agent/claude-code)**: the two model-named executor agent definitions, the Claude Code subagent
  roster migrated from the instruction repository. Defaults are xhigh effort for Haiku (never below high) and medium
  for Opus; models are the family aliases, never a version. `rules/brief-delegates.md`, an always-loaded rule that
  makes the parent state goal, scope, constraints, success check, output contract, stop conditions and difficulty in
  every subagent brief.
* **Update (auto-ai-agent)**: `model-delegation.md` gains a worked bad/good brief; `autonomous-base.md` gains one
  sentence on briefing a delegate.

## 2026-10-09

* **Add (auto-ai-agent)**: `hermes-splunk-health.md`, a two-hourly open-ended review of Splunk's own health: admin
  messages, health report, splunkd internal errors, license, scheduler, ingest pipeline and storage. License findings
  are one lens among these.

## 2026-10-08

* **Fix (auto-ai-agent)**: `hermes-service-pulse.md` reports the router readiness fields returned by its probe and uses the configured open-incident baseline.

## 2026-10-05

* **Update (applications)**: compose the LangGraph homelab assistant's generated system prompt from the canonical
  monitoring rule and skill sources.

## 2026-10-03

* **Add (auto-ai-agent)**: `hermes-release-watch.md`, a daily prompt that reads Renovate tracking and pinned public
  versions and reports matching release notes from the previous 24 hours.
* **Fix (auto-ai-agent)**: `hermes-release-watch.md` returns only `[SILENT]` when no release qualifies, so no-news runs
  produce no post.
* **Fix (auto-ai-agent)**: add the required `source_history` metadata to four existing Hermes prompts.

## 2026-09-25

* **Add (automation/testing)**: portable, staged instruction bodies for the `ui-smoke`,
  `spec-author`, `healer`, `perf-debug`, and `explorer` agents. The catalog records one
  immutable prompt resource for each role; consumers supply tool wiring and execution policy.
* **Fix (automation)**: `fragment-issue-solver-phases-1-4.md`, `fragment-issue-solver-phases-5-8.md`,
  and `repo-audit-rules.md` were missing the `render` and `source_history` OKF fields. The catalog's
  recursive-directory OKF check now covers nested paths and caught the pre-existing gap; both
  fragments now mirror `issue-solver.md`'s `source_history`, and the rule file mirrors
  `repo-audit.md`'s.

## 2026-09-24

* **Add (automation)**: `ai-workflows-docs-sync.md`, an event-driven docs-sync
  prompt consumed by a reusable CI workflow. It reviews merged pull requests
  for documentation changes and drafts matching updates. Its source history
  records earlier catalog entries for the same workflow.

## 2026-09-12

* **Update (auto-ai-agent)**: `hermes-bot-pr-triage` gains a once-per-calendar-day
  stale-open-PR report (top 10 open PRs across the org, oldest first, full PR
  URLs, all authors — not limited to bot PRs) alongside its existing security
  triage. Delta-aware via a new memory key
  (`bot-pr-triage-stale-last-date`) so the 3x/day cron does not repeat the
  same report; the `[SILENT]` condition now also requires the report to have
  already fired today.

## 2026-09-11

* **Update (auto-ai-agent)**: `hermes`'s `Model fabric:` paragraph stops telling the
  agent to send physical model ids to the router. The router now publishes a fixed
  role vocabulary (`lead`, `subagent`, `cheap`, among others) that resolves to a
  physical model without the caller naming one, so the stale `no generic ai-default
  alias, so send real model ids` claim and the OpenBao brain-value detail it needed
  are dropped in favor of naming a role. `Tier by job` and `Escalation (OpenRouter)`
  are reworded onto the same roles; the escalation paragraph keeps naming physical
  OpenRouter ids by design, since that tier is a deliberate paid per-call pick no
  role covers. The `Attribution:` example drops its hardcoded physical model id in
  favor of a role name. Line anchors `Model fabric:` and `Escalation routing:` are
  unchanged.

## 2026-09-05

* **Retire (auto-ai-agent)**: `hermes-docs-sync` moves to `status: retired` with
  `consumers` cleared. Public documentation is now produced by the docs publish
  workflow, which projects the pages marked publishable in the private docs
  source, opens the pull request as a dedicated publisher identity, and merges on
  the target branch's required status checks. Every step the routine performed has
  a native owner: selection is a frontmatter flag defaulting to unpublished,
  authoring is a deterministic transform rather than a per-concept judgement, and
  the merge gate is the required checks rather than an agent polling a check and
  renaming the pull request to flag a human. The body is kept as history and its
  `source_history` records the successor. The version-drift check has no successor
  and the retired body says so.

## 2026-08-06 (later)

* **Fix (automation)**: restore `issue-solver` as `automation/issue-solver.md`,
  `status: active`, and un-retire the `fragment-prerequisites` it includes. Both
  were swept up in the cloud-routine retirement, and that was wrong: issue-solver
  never ran on the cloud substrate. It runs in GitHub Actions on a GitHub App
  token, has succeeded twice daily throughout the five weeks the cloud routines
  were dead, and is the one routine still live. The removal left the body of a
  working job existing only at its consumer's pinned submodule commit and on no
  main branch anywhere, so any repin would have silently broken it. The earlier
  entry below saying the consumer renders nothing from this directory is
  corrected by this one: it renders `issue-solver`, and only `issue-solver`.

## 2026-08-06

* **Retire (automation)**: the seven cloud-routine bodies and their twelve shared
  fragments moved to `status: retired`. The Anthropic cloud-routine substrate they
  ran on has produced nothing since 2026-07-01 — every repo-scoped call returns a
  session/repo binding 403, the deploy path has been unusable since 2026-05-19, and
  no state file has been written in five weeks. The bodies stay here as history;
  each one's `source_history` note now records where its content went, so the
  catalog answers "where did this go" rather than only "this used to exist".
  `consumers` is cleared on all of them, `dryvist/claude-code-routines` no longer
  renders any prompt from this directory.

* **Add (auto-ai-agent)**: `hermes-repo-scorecard` and `hermes-secrets-policy-audit`
  salvage the two pieces of the retired routines that were neither duplicated
  elsewhere nor blocked by Hermes doctrine. The scorecard keeps the weighted 0-100
  rubric and week-over-week deltas from `estate-briefing`, with history in a Hermes
  memory key instead of the routine state repo. The secrets audit keeps the one
  `repo-audit` rule that files an issue and never a pull request — which is exactly
  what makes it Hermes-legal — and gates on the `contents:read` token so it fails
  visibly instead of reporting a clean estate it never read.

* **Promote (auto-ai-agent)**: `hermes-docs-sync` and `hermes-bot-pr-triage` move
  from `staged` to `active`. Draft-only commits to the two docs repos are the single
  code-commit carve-out Hermes has, so docs-sync transfers intact; bot-PR work
  transfers as its triage half only, because Hermes never merges and the org Renovate
  preset already merges bot PRs directly via API.

## 2026-08-05

* **Update (auto-ai-agent)**: `hermes-splunk-parsing` gained a named dedup
  baseline. It previously said only "Record findings and baselines to memory" —
  no key name — so there was nothing deterministic to recall, and a parsing
  defect that stayed unfixed was re-reported on every run. It now recalls
  `splunk-parsing-last` first, filters against it, states how many findings it
  suppressed as already-known instead of relisting them, and saves the updated
  fingerprint back. This is the same four-element pattern the other Hermes
  surfaces already use, and it is the one prompt of its family whose card is
  currently unpaused, so it was the only one repeating in a live channel.

## 2026-08-04

* **Update (auto-ai-agent)**: the `hermes` surface gained an output contract.
  Channel routing is now stated as a rule the agent can apply — real findings to
  the all channel, self-breakage to issues (one post per problem, not per
  occurrence), everything FYI or repeated to noise — because an audit of three
  days of live output found one recurring alert template filling 38% of the
  issues channel and routine sweeps repeating three to five times a day in the
  all channel. A 24-hour no-repeat rule now covers the core channels, with only
  an active unhandled P1 exempt. The format rules ask for a status emoji and one
  bold takeaway first, so a reader can triage a message at a glance. A new
  triage rule ends alert-and-stop behavior: a confirmed problem now also gets a
  deduped ticket and a bounded follow-up investigation. Model guidance gained a
  tiering line so the small fast model stays a deliberate choice for quick or
  bulk work rather than becoming the default.

* **Fix (auto-ai-agent)**: the `hermes` surface mandated routine status be
  delivered to a default home channel "every run, never suppressed", while the
  consumer's job enqueuer separately tells each job to deliver to the
  destination its own card names. Both are obeyable at once because they name
  different destinations, so routine status reports were delivered twice,
  minutes apart. The standing rule now names a single destination — the one the
  asking job names — and drops the never-suppress clause, which also
  contradicted the output-format rule directly below it ("do not re-dump
  unchanged or already-known-benign status every run").

Entries through 2026-08-07: [log-archive.md](log-archive.md).
