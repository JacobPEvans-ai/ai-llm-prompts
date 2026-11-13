---
type: LLM Prompt Fragment
title: "Bot PR Merge Gates"
description: "Phase B of bot-pr-merge: author/title allowlists, workflow-edit and release file-allowlist exceptions, signed-commit and age gates, and the cross-repo merge batcher. Composed back via include."
resource: "prompt://dryvist/automation/bot-pr-merge/gates"
tags:
  - "automation"
  - "routine"
  - "fragment"
timestamp: "2026-07-20T13:00:00-04:00"
status: retired
consumers: []
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "automation/bot-pr-merge.md"
    note: "Extracted verbatim from bot-pr-merge Phase B to keep each catalog file under the 12KB file-size limit; recomposed via include, no content change."
---
### Bot author allowlist (corrected against 200-PR sample)

A PR is eligible for consideration only if `author.login` is one of:

- `renovate[bot]`
- `dependabot[bot]`
- `github-actions[bot]`
- `jacobpevans-github-actions[bot]`

Any other login → skip. Dropped from the prior version: `release-please[bot]` (unused — this estate's release-please runs as `github-actions[bot]`), `app/renovate`, `app/dependabot` (App slugs never match `author.login`).

### Title-pattern allowlist (corrected against 200-PR sample)

After the author check, the PR title must match at least one (case-sensitive prefix unless noted):

- `chore(deps):` — Renovate base prefix (36/200 in sample).
- `chore(deps-dev):` — Renovate dev deps (defensive).
- `chore(main): release` — actual release-please-action format (44/200) — **subject to release file-allowlist below**.
- `fix(deps):` — jacobpevans-github-actions action-pin refreshes.
- `build(deps):` — Dependabot.
- `ci(deps):` / `ci(deps)(deps):` — Dependabot.
- `chore(workflow): regenerate locks` — gh-aw-sync-upstream workflow.

Dropped (never matched in sample): `chore(release):`, `chore: release`, `chore(gh-aw): refresh action pins`.

#### Title rejection: emoji and conventional-commit prefix (absorbs the prior `soul` rule for the bot-PR pipeline)

Reject if title contains Unicode emoji (`\x{1F300}-\x{1FFFF}` or `[\x{2600}-\x{27BF}]`) — bot-generated titles should never contain emoji. Scope note: this covers `soul` ONLY for bot PRs this routine sees; estate-wide enforcement on human commits is not provided here (baseline today is clean — zero violations in the 100-commit sample dated 2026-05-15 to 2026-05-25; file a follow-up issue if the baseline degrades).

### Workflow-edits exception

Workflow file edits are permitted ONLY when all of:

- Title starts with `fix(deps):` AND
- Title contains `[aw:gh-aw-pin-refresh]` AND
- Author is `jacobpevans-github-actions[bot]`.

Any other PR touching `.github/workflows/*.yml` → skip with reason `workflow_files_blocked`.

### Release PR file-allowlist

For `chore(main): release` PRs from `github-actions[bot]`, the changed file set MUST be a subset of:

```text
CHANGELOG.md
.release-please-manifest.json
package.json
Cargo.toml
pyproject.toml
uv.lock
flake.lock
VERSION
```

Plus any per-repo additions from `release_allowlist_extensions[$repo]` in `state/bot-pr-merge.json` (operator-managed).

```bash
FILES=$(gh api "repos/$GH_OWNER/$REPO/pulls/$PR_NUMBER/files" \
  --jq '[.[].filename]')
```

If any file is outside the union of (default allowlist + per-repo extensions) → escalate to Slack, do not merge.

### Signed-commit verification

```bash
ALL_VERIFIED=$(gh api "repos/$GH_OWNER/$REPO/pulls/$PR_NUMBER/commits" \
  --jq 'all(.[]; .commit.verification.verified == true)')
```

If `false` → escalate to Slack, do not merge.

### Minimum PR age

```bash
PR_CREATED=$(gh pr view "$PR_NUMBER" --repo "$GH_OWNER/$REPO" --json createdAt --jq '.createdAt')
AGE_HOURS=$(( ($(date +%s) - $(date -d "$PR_CREATED" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$PR_CREATED" +%s)) / 3600 ))
[ "$AGE_HOURS" -lt 4 ] && skip
```

PRs younger than 4 hours → defer to the next run.

### Blocking-label guard (one-line, in case labels are provisioned later)

```bash
HAS_BLOCK=$(gh pr view "$PR_NUMBER" --repo "$GH_OWNER/$REPO" --json labels \
  --jq '[.labels[].name] | any(. as $l | ["do-not-merge","wip","blocked","hold","on-hold"] | index($l))')
```

If `true` → skip with reason `blocked_label`.

### Merge eligibility (ALL conditions required after the gates above)

```bash
gh pr view "$PR_NUMBER" --repo "$GH_OWNER/$REPO" \
  --json state,isDraft,mergeable,mergeStateStatus,reviewDecision,labels,headRefName,headRefOid \
  --jq '{state,isDraft,mergeable,mergeStateStatus,reviewDecision,labels:[.labels[].name],headSha:.headRefOid}'
```

- `state == "OPEN"`
- `isDraft == false`
- `mergeable == "MERGEABLE"`
- `mergeStateStatus` is `CLEAN` or `HAS_HOOKS`
- `reviewDecision` is `APPROVED` or `null` (not `REVIEW_REQUIRED` / `CHANGES_REQUESTED`)
- All required status checks are `SUCCESS` (no pending, no failing)

CI check:

```bash
gh api "repos/$GH_OWNER/$REPO/commits/$HEAD_SHA/check-runs" \
  --jq '[.check_runs[] | select(.status=="completed") | .conclusion] | all(. == "success" or . == "skipped" or . == "neutral")'
```

### Phase B1 — Enumerate active repos

```bash
gh repo list "$GH_OWNER" --limit 100 \
  --json name,isArchived \
  | jq '[.[] | select(.isArchived==false) | .name]'
```

Apply the skip-list (mirrors, abandoned, profile/meta — same set as Phase A).

### Phase B2 — Fetch bot PRs (one org-wide search, not per-repo)

Use `gh search prs` to enumerate all open bot PRs in `$GH_OWNER` in a single call. Avoids the per-repo `gh pr list` loop (saves ~one API request per repo per run, ~100 calls/run at current estate size). If this `gh search` returns HTTP 502 (the Search API flakes through the proxy), fall back to the per-repo `gh pr list --state open` loop it replaces:

```bash
gh search prs --owner "$GH_OWNER" --state open --limit 200 \
  --json repository,number,title,author,isDraft,createdAt \
  --jq '[.[] | select(.author.login as $a |
                       ["renovate[bot]","dependabot[bot]",
                        "github-actions[bot]","jacobpevans-github-actions[bot]"]
                       | index($a))]' > /tmp/bot-prs.json
```

Then enrich each candidate with the mergeability + CI fields via a per-PR `gh pr view` (these can't be returned from `search prs`):

```bash
jq -c '.[]' /tmp/bot-prs.json | while read -r PR; do
  REPO=$(echo "$PR" | jq -r '.repository.nameWithOwner')
  NUM=$(echo "$PR" | jq -r '.number')
  gh pr view "$NUM" --repo "$REPO" \
    --json number,mergeable,mergeStateStatus,reviewDecision,labels,headRefOid
done
```

Skip the skip-list when iterating.

### Phase B3 — Apply the gates in order

For each candidate PR, run gates sequentially and stop at the first failure:

- Bot author allowlist
- Title-pattern allowlist (incl. emoji rejection)
- Minimum PR age (≥4h)
- Workflow-edits exception (skip if touches workflows without the exception)
- Release file-allowlist (only for `chore(main): release` titles)
- Signed-commit verification
- Blocking-label guard
- Merge eligibility + CI

If all gates pass: merge.

```bash
gh pr merge "$PR_NUMBER" --squash --repo "$GH_OWNER/$REPO"
```

Record each outcome (merged/skipped + reason) in `run_log`. Stop after 20 successful merges.

