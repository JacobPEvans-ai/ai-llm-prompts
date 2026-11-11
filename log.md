# Change Log

## 2026-11-11

* **Feat (rules)**: Add the on-demand `fleet-utilization.md` rule — worker-fleet cadences, the `QUEUE` block and the
  two hourly numbers — indexed in `rule-tiers.md` and referenced from the delegation routing paragraph.

## 2026-11-10

* **Fix (auto-ai-agent)**: Donna no longer opens a thread to the person she works for about her own setup. A failed job,
  a wrong target or a missing permission goes to failure reporting, and she mentions it only when asked. She still
  answers questions about her configuration and delivery, and still asks once about choices only that person can make.

## 2026-11-09

* **Fix (agents)**: The JSON-fence judge accepts compliant overlay parse nodes — it still requires every listed parse
  node to route through the shared fence stripper, and it now allows unlisted nodes from DSLs outside this repo's roster
  (agent definitions that do not extend a profile in `agents/profiles/`), with judge tests covering a synthetic overlay
  DSL, an unlisted roster node, and a public DSL that loses the stripper call.

* **Feat (agents)**: Accept an overlay roster's prefix, manifest, and parse suites — the judges require each
  definition's `shared_prefix` to equal the prefix declared by a profile in its `extends` chain, additional
  `agents/dify/manifest.<roster>.json` manifests that together name every roster DSL and cover every rendered DSL
  exactly once, and `<agent>-parse` suites derived from every eval suite's unskipped `expected_parse` cases.
* **Fix (auto-ai-agent)**: The Hermes surface gains one cron tool rule — a cron run never runs an inline `-c`/`-e`
  script (write a per-run script file or use a native tool) and reads a file in full before overwriting it, preferring
  per-run scratch file names — and judge tests reject any Hermes prompt that instructs an inline script or restates the
  rule outside the surface.
* **Feat (agents)**: The Dify rotation driver's app name is a render input — `make render-dify` takes it
  from the `ROTATION_DRIVER_NAME` make variable (default `tier2-rotation`), so an overlay can render its
  own driver beside the public one.

* **Feat (agents)**: Add `youtrack-clerk`, a connector for scoped issue reads, creates, comments, updates and
  evidence-backed resolution, with readback evals and rendered catalog entries.

* **Fix (agents)**: The shared Dify report-envelope helper states unexpected reply properties as a count in its rejection
  reason, so no reason ever repeats key names or values a reply can choose, and the judge suite plants a unique marker in
  an otherwise valid reply to assert no returned reason echoes it.

* **Feat (rules)**: Status posts put one component and one metric on each line, each led by a green, yellow or red status.

* **Feat (agents)**: Run action-extractor, commit-grouper, plain-rewriter, style-gate and tag-suggester on the small
  role.
* **Fix (evals)**: The shared promptfoo output instruction now forbids claiming a readback, receipt, dedup result, or
  write unless its result is in the input.

* **Fix (agents)**: Give the vikunja-clerk classifier an open-only filter rule — it sets `done` to false.

* **Fix (agents)**: State model-scout's fail-closed outcome for a missing, ambiguous, or stale release date — the run
  returns `stop` with a null result.

* **Fix (agents)**: Name openbao-clerk's policy-change refusal reason — `policy_change_forbidden` — instead of leaving
  "their respective refusal reasons" unnamed.

* **Fix (agents)**: Make the zammad-triage lead decision explicit — a rank item is emitted only for a blocked ticket or
  one with an explicit priority — and give oversized or unavailable input an output shape of `{"actions": []}`.

## 2026-11-08

* **Add (auto-ai-agent)**: `hermes-reporting/status-levels.md` defines the shared green, yellow and red status
  levels for Hermes report and alert headlines once, with a machine-readable block a role can load.

* **Update (auto-ai-agent)**: The direct-cron reporting footers carry the green, yellow and red status markers inline
  in one HEADLINE LEVEL line, because the cron runtime appends only the footer body to the job prompt and the model
  never reads the referenced shared file; the service pulse chooses its level from those footer markers and turns red
  only on two consecutive failed probes; judge tests rebuild the expected footer line from the machine-readable block
  in `hermes-reporting/status-levels.md` so the footers cannot drift from it, and that file stays the canonical
  machine-readable source.

* **Update (instructions)**: `AGENTS.md` picks the qualifier subscription dynamically — each quota is looked up at
  decision time and the most headroom against its period pace wins, with no hard-coded pause — and after the
  local-first step a failed local call gets a subagent to find what went wrong and what to improve, and at least one
  medium leg accepts the local model's native maximum context.

* **Update (instructions)**: `AGENTS.md` delegation routing gains a first rung — small, quick, checkable tasks go to
  the router local default or medium capability before any subscription, escalating only after a checked failure — and
  other subscriptions such as OpenCode Go are used only while at or under their pace for the billing period.

* **Update (instructions)**: `AGENTS.md` routes delegation by sensitivity — ZCode and Codex Luna are equal first
  choices, other subscriptions fit where they can, and Haiku `xhigh` stays the explicit last resort — and states that
  the lead never does delegable work and fans subagents out in parallel; `model-delegation.md` points at that one order.

* **Update (standards)**: Add rules to set subagent and forked side-job effort explicitly for the job and to run a
  subagent's long shell commands in the background so the prompt cache does not expire; refresh the Anthropic source
  table with the Claude Code v2.1.316 and v2.1.318 releases and advance the research cutoff to 2026-11-08.

* **Update (auto-ai-agent)**: `hermes-service-pulse.md` starts its headline with a green, yellow or red status emoji
  chosen by fixed criteria.

* **Update (standards)**: Split agent-authoring source records into publisher files while preserving source IDs and links.

* **Update (agents)**: Render and judge MCP servers that expose individual tools: a dotted tool whose prefix is a declared
  server becomes one tool node per tool, while subcommand-form entries must share a single tool prefix.

* **Add (repo)**: Add a root `.gitattributes` applying the built-in union merge driver to the root change log, so
  concurrent entries from parallel pull requests are kept instead of conflicted.

* **Update (standards)**: Add rules for stopped subagents, temporary credential-refresh failures, tool-argument
  comparison modes in evals, and list-form LiteLLM fallback targets.

* **Update (standards)**: Add rules for skill-script arguments, fresh approval at managed command checkpoints, turn and
  tool attribution in traces, and a shared MCP server request cap.

* **Fix (agents)**: Name the reader and acted signal of vikunja-triage, zammad-triage and doc-contradiction-finder, and
  require both for every agent that an event, rotation or anchor starts.

* **Update (agents)**: Stop on incomplete or unavailable required input and reserve refusals for out-of-scope events; add
  credential and out-of-sandbox edit evaluation cases.

* **Fix (agents)**: Give code-simplifier a handback decision for requests outside its mandated pull request, and name its
  refusal and handback eval cases by that decision.

* **Fix (agents)**: Return stop, not refused, when the Dify trigger gate receives a malformed or oversized event.

* **Update (agents)**: Make the report envelope decidable: every role returns it unless the prompt opts out by name, name
  each envelope result's fields, and count records supplied in the input as available sources.

* **Update (standards)**: Add an eval rule to use provider-reported token usage for agent-cost evaluations.

* **Fix (instructions)**: Float first-party shared workflow refs on each repository's current major tag.

* **Add (automation)**: Catalog the OpenHands Vikunja ticket-to-pull-request prompt with literal rendering and webhook-task safety rules.

* **Update (agents)**: Return stop for incomplete Langfuse comparisons and ambiguous Slack targets, keep refusals for
  unverified callers and out-of-policy channels, and scope the shared ambiguous status to unclear requests.

* **Update (agents)**: Define the report envelope statuses once in the shared prefix: stop for malformed, ambiguous,
  incomplete, oversized, or unavailable-source input; refused only for out-of-mandate or unsafe requests; ok otherwise.

* **Update (standards)**: Add hook-failure, verifier-isolation, memory-comparison and MCP auth-forwarding rules to the agent
  standards, and move their source attribution into the source tables.
* **Update (agents)**: Add shadow proposal cases with readback for the Slack and Semaphore connectors, share connector
  transport fixtures per principal, and define the OpenBao metadata result schema with a deterministic eval check.

## 2026-11-07

* **Update (agents)**: Limit GitHub review agents to forwarded event evidence and fixed refusals for missing inputs.

* **Update (automation)**: Render dependency review inspection and risk criteria from the shared agent prompt.

* **Update (automation)**: Compose the documentation-drift workflow prompt from canonical agent rules while preserving consumer inputs and outputs.

* **Update (automation)**: Render the dependency review prompt from its canonical agent prompt and retain its envsubst inputs.

* **Update (automation)**: Render the docs-drift workflow prompt from its canonical agent prompt and check it for drift.

* **Add (agents)**: Add dep-review as a shadow GitHub agent with a canonical prompt and regression cases.
* **Add (agents)**: Add docs-drift as a shadow GitHub agent with a canonical prompt and regression cases.
* **Update (standards)**: Prefer one agent with progressively disclosed skills, and limit optional subagents to measured needs.
* **Update (agents)**: Add read-only Langfuse score access and deterministic promotion review inputs and cases.

* **Add (agents)**: Add the OpenBao connector definition, prompt, and shadow evaluation for metadata reads and secret-value refusals.

* **Add (agents)**: Add the Proxmox connector definition, prompt, and shadow evaluation for scoped read-only resource state.

* **Add (agents)**: Add the Semaphore connector definition, prompt, and shadow evaluation for allowlisted template runs.

* **Add (agents)**: Add the Splunk connector definition, prompt, and shadow evaluation for bounded read-only searches.

* **Add (agents)**: Add the Slack connector definition, prompt, and shadow evaluation for policy-approved channel posts.

* **Update (auto-ai-agent)**: Render the daily summary's project allowlist from one input.

* **Add (auto-ai-agent)**: Catalog three Hermes operating-profile addenda with source provenance and literal rendering.

* **Update (instructions)**: Add evidence and status fields, authorized rule correction, and single-writer shared memory requirements.

* **Add (applications)**: Catalog the Open WebUI Docling VLM page-parsing prompt with source provenance and literal rendering.

* **Add (automation)**: Catalog the tier-2 load-test request with its request-id placeholder and source provenance.

* **Update (automation)**: Render four workflow review rubrics with one gomplate template and include prompt drift checks in `make check-dify`.

* **Add (automation)**: Catalog seven workflow prompts in the actions/ai-inference YAML prompt-file format.

* **Update (instructions)**: Extend dated agent authoring standards for delivery reconciliation, skill selection,
  measured revision gains, evaluation fidelity, judge calibration, and skill tracing.

* **Update (auto-ai-agent)**: Group the Hermes catalog indexes and compose the hourly stats prompt from three ordered fragments.

* **Add (auto-ai-agent)**: Catalog Hermes assistant, coordination, recurring-job, and shared-fragment prompts with source provenance.

* **Update (auto-ai-agent)**: Zammad review uses the current bounded lifecycle and weekly metrics prompt.

* **Update (agents)**: Every prompt reference to another roster agent declares a gateway peer and call tool.

* **Update (agents)**: Clerk and shipping handoffs declare gateway peers and call tools; judges validate outbound prompt handoffs.

* **Update (agents)**: Native minute rotation schedules omit quarter-hour starts and preserve minimum intervals.

* **Update (agents)**: Weekly Splunk readers inherit privacy, connector, tool, and trigger settings from one profile.

* **Update (agents)**: Task advisory agents inherit connector, tool, and privacy settings from one profile.

* **Update (prompts)**: Refresh OKF timestamps for the shared context and revised documentation, simplification, and task prompts.

* **Update (agents)**: Consolidated definitions describe trigger scenarios and link to worked invocation examples in their prompts.

* **Update (evals)**: Model dossier fixtures supply dated source snapshots, immutable references, matched measurements, and URLs.

* **Update (evals)**: GitHub proposal cases include transport identity, a scoped mandate, payload, and an unverified-caller refusal.

* **Update (evals)**: Model scouting and benchmarking reference one shared malformed-candidate case.

* **Update (agents)**: Generic trigger workflows pass bounded, redacted event envelopes through native branch aggregation.

## 2026-11-06

* **Update (agents)**: Fold deferred task intake, documentation stewardship, and simplification review into existing
  agents; evaluation instructions follow each canonical output contract.

* **Add (agents)**: Add merge, shipping, reconciliation, session closure, promotion review, and metadata advisory procedures.

* **Add (agents)**: Add GitHub and Zammad connector definitions with shared mandate and receipt policies and shadow evals.

* **Add (agents)**: Consolidate operations into alert triage, deep dives, agent audit, PR upkeep, repository maintenance,
  release promotion, and voice learning; retain standalone patch-grader fixtures.

* **Add (agents)**: Add AI news, model scouting and dossiers, and release digests with shared evaluation boundaries.

* **Add (agents)**: Add the Donna briefs, weekly review, research, and innovation agents with shared report contracts,
  evaluation cases, and generated runtime exports and catalogs.

* **Update (instructions)**: Reference the canonical delegate brief rules by their cross-package prompt resource identifier.

* **Add (auto-ai-agent)**: Add Pepper's project manager persona with one-issue evidence review and bounded comment authority.

* **Update (instructions)**: Agent standards link to the canonical delegate brief rules for verification and evidence reporting.

* **Update (agents)**: Dify workflows render through 1 shared gomplate template from agent YAML and canonical prompts.
  CI compares the generated output set, and the import guide covers Dify 1.18, difyctl, and published-version exports.

* **Update (instructions)**: Organize agent standards into linked authoring rules, platform rules, and dated source tables.

* **Add (applications)**: Add the YouTrack issue specialist with sole tracker ownership, bounded issue and comment
  operations, and verification of every write by readback.

* **Update (instructions)**: Agent standards require secret-free exports and records of omitted resource dependencies.
* **Update (claude-code)**: Delegate briefs state runtime authority, independent sandbox and approval choices, proportional checks, and delivery evidence.
* **Creation (instructions)**: Add source-cited agent and skill building standards with dated attribution and rules for briefs and platform integrations.
* **Creation (agents)**: Add an agent catalog index linking authoring standards and validation guides.

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
