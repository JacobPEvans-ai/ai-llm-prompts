# Review verdict — pull request #439

- Repository: JacobPEvans-ai/ai-llm-prompts
- Reviewed head: `b3881b4f8936b1a19794084bab2bcb2cd39a9398` (branch `feat/pepper-ai-assistant-role`, base `main`)
- Files touched: `auto-ai-agent/pepper.md`, `auto-ai-agent/hermes-pepper-ai-news.md` (new), `auto-ai-agent/hermes-pepper-scouting.md` (new), `auto-ai-agent/hermes-assistant/index.md`
- All file:line references below are at the reviewed head.

## Scope of the change

The PR extends the Pepper persona with an AI-side technical assistant role (`auto-ai-agent/pepper.md:47-63`) and adds two scheduled prompts for it: a daily AI news digest (`auto-ai-agent/hermes-pepper-ai-news.md`) and a weekly models/benchmarks/pricing/offers scouting report (`auto-ai-agent/hermes-pepper-scouting.md`), plus index entries (`auto-ai-agent/hermes-assistant/index.md:15-16`). The two new prompts agree with each other: both use the memory key `pepper-ai-preferences` (`auto-ai-agent/hermes-pepper-ai-news.md:23,29`; `auto-ai-agent/hermes-pepper-scouting.md:23,34`), the same per-run URL evidence rule, the same client-data separation closing line (`auto-ai-agent/hermes-pepper-ai-news.md:31`; `auto-ai-agent/hermes-pepper-scouting.md:36`), and matching frontmatter shapes. OKF required fields are present and the role section is consistent with both prompts' schedules and scopes.

## (a) Second copy of an existing mechanism — YES

1. The no-scripts + reasoned-quiet-line reporting contract is copied into both new prompts, although the repository defines cron tool discipline once and pins the no-script variant to exactly two prompts:
   - The shared rule lives on the Hermes surface: `auto-ai-agent/hermes.md:37` ("Cron tool discipline: ..."), and the judge module states the intent in its docstring, "Hermes cron tool discipline is defined once, in the shared Hermes surface" (`agents/judges/test_hermes_cron_tool_discipline.py:1`).
   - The no-scripts-at-all variant is deliberately scoped: "The assistant's attention jobs run with no scripts at all, and a quiet run logs one line of reason before its [SILENT] marker" with `NO_SCRIPT_PROMPTS = ("hermes-assistant-pulse.md", "hermes-assistant-nudge.md")` (`agents/judges/test_hermes_cron_tool_discipline.py:69-71`).
   - The new prompts copy that mechanism near-verbatim: "Use only the tools this job grants you. Never write, save or run a script, and never create a scratch file." (`auto-ai-agent/hermes-pepper-ai-news.md:21`; `auto-ai-agent/hermes-pepper-scouting.md:21`) versus the source wording at `auto-ai-agent/hermes-assistant-pulse.md:25-27`, and the one-line reasoned `[SILENT]` quiet-run contract (`auto-ai-agent/hermes-pepper-ai-news.md:27`; `auto-ai-agent/hermes-pepper-scouting.md:32`) versus `auto-ai-agent/hermes-assistant-pulse.md:39-41` and the pinned clause list at `agents/judges/test_hermes_cron_tool_discipline.py:78-86`.
   - The judge's `NO_SCRIPT_PROMPTS` tuple (`agents/judges/test_hermes_cron_tool_discipline.py:71`) does not include the new files, so a discipline the repo treats as defined once and enforced now exists in four prompt files with only two under test.

2. A second AI-news scout for the same consumer already exists. `auto-ai-agent/hermes-ai-news.md:26` (status active, same consumer `dryvist/ansible-proxmox-ai` at `auto-ai-agent/hermes-ai-news.md:13` = `auto-ai-agent/hermes-pepper-ai-news.md:14`) implements interest-guided AI news scouting with: a stored interests profile, fingerprint dedup via memory key `ai-news-last`, a this-run-URL evidence rule, the same selection bar ("skip rumor, marketing, funding news"), a bounded item count, and save-state at the end. `auto-ai-agent/hermes-pepper-ai-news.md:23-29` re-implements each of those steps with parallel memory keys (`pepper-ai-news-last`) instead of extending or composing the existing prompt. The estate's own boundary fragment states the policy this defeats: "Another agent owns all of that and is already reporting on it — repeating any of it is duplicated work and a mistake" (`auto-ai-agent/hermes-assistant-exclusion-clause.md:28-29`).

## (b) Hard-coded single-consumer values — YES (the interest/topic seed)

- The fallback topic seed is inlined as prompt text: "If no preferences are stored yet, use these topics: frontier and open-weight model releases, local inference on Apple silicon and NVIDIA GPUs, agent tooling, and model pricing changes" (`auto-ai-agent/hermes-pepper-ai-news.md:23`), with the prompt declaring no render inputs (`render: engine: literal, variables: []` at `auto-ai-agent/hermes-pepper-ai-news.md:15-17`).
- The same principal-scope list is restated in two more places with no single source feeding them: the role scope bullet (`auto-ai-agent/pepper.md:52-53`) and the scouting report's four sections (`auto-ai-agent/hermes-pepper-scouting.md:25-28`). Changing the principal's AI scope requires coordinated edits to three files.
- The repository already has the mechanism the question describes for exactly this value: `auto-ai-agent/hermes-ai-news.md:15-19` declares the render inputs `hermes_agent_ai_news_interests` and `hermes_agent_wiki_path`, injects the interest list at `auto-ai-agent/hermes-ai-news.md:28`, and keeps the list itself in one shared fragment, `auto-ai-agent/hermes-ai-news-interests.md:23` ("INTEREST SEED (static floor ...)"). The new prompts should declare the seed as a render input with a default (or share the existing fragment) rather than inlining it.
- Not findings, because they match existing sibling conventions: inline memory key names (cf. `auto-ai-agent/hermes-pricing-diff.md:24`), item limits ("at most 5 items" / "at most 4 items per section"), and 24h/7d windows are hard-coded in current prompts as well (`auto-ai-agent/hermes-ai-news.md:26`); the `dryvist/ansible-proxmox-ai` consumer declaration matches every sibling `hermes-pepper-*` prompt.

## Other checks

- Judge suite at the reviewed head: `test_hermes_cron_tool_discipline.py` and `test_hermes_status_levels.py` pass. The 10 failures in `test_catalog_render.py` / `test_authoring_standards.py` are environmental (no `make` in the review container) and are identical at merge base `6eaf7d4`, so they are not introduced by this PR. The new prompts also do not trip the inline-script or restatement judges (`agents/judges/test_hermes_cron_tool_discipline.py:37-50`).
- The branch is based on release 1.100.2 while `main` is at release 1.104.0; no commit in between touches the files this PR changes, so there are no textual conflicts.
- Root `log.md` is not updated. The workspace AGENTS.md requires a newest-first `log.md` entry for every meaningful catalog change, and comparable merged prompt changes did update it (PRs #440, #442).
- `auto-ai-agent/index.md:9` still carries the pre-PR Pepper description ("Project manager identity, issue-scoped evidence review, and interaction boundaries") while the PR rewrites that description at `auto-ai-agent/pepper.md:4`.
- Naming: the new titles capitalize Pepper ("Hermes Pepper AI news" at `auto-ai-agent/hermes-pepper-ai-news.md:3`; "Hermes Pepper weekly AI scouting" at `auto-ai-agent/hermes-pepper-scouting.md:3`) while the sibling prompts use lowercase ("Hermes pepper card", "Hermes pepper digest", "Hermes pepper intake", e.g. `auto-ai-agent/hermes-pepper-digest.md:3`).
- `source_history: []` (`auto-ai-agent/hermes-pepper-ai-news.md:19`; `auto-ai-agent/hermes-pepper-scouting.md:19`) omits the consumer-side variable pointer that every sibling `hermes-pepper-*`/`hermes-assistant-*` prompt records (e.g. `auto-ai-agent/hermes-pepper-digest.md:18-22`). An empty array has precedent (`auto-ai-agent/github-specialist.md:14`), so this is minor.

## Verdict

Findings (a) and (b) are both confirmed against existing mechanisms in the repository: the pinned no-script/quiet-line reporting contract is duplicated into two new unpinned files, a second AI-news scouting mechanism is added beside the existing one for the same consumer, and the principal's interest seed is hard-coded in three places instead of being one declared, default-parameterized list. The remainder of the change (role definition, OKF metadata, inter-prompt agreement, index entries) is consistent.

VERDICT: REQUEST_CHANGES
