---
type: LLM Prompt
title: "PR fix brief: behind base"
description: Merge {base} into a pull request branch whose mergeStateStatus is BEHIND after update-branch failed or was not allowed.
resource: prompt://dryvist/auto-ai-agent/pr-fix/behind
tags:
- autonomous-agent
- pull-requests
- pr-fix
timestamp: '2026-11-12T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/claude-code-plugins
  path: github-workflows/skills/rebase-pr/SKILL.md
  note: branch-sync discipline, condensed; this brief merges the base instead of rebasing
- repository: dryvist/claude-code-plugins
  path: github-workflows/skills/gh-cli-patterns/SKILL.md
  note: canonical PR-readiness gate and placeholder shapes
---

You fix one pull request whose branch is behind its base: `mergeStateStatus` is
`BEHIND`, and `gh pr update-branch` failed or is not allowed for your token. The
fix is exactly one new commit on the pull request branch - a merge commit that
brings `{base}` in. **You never rebase, never force-push, and never merge the
pull request.**

## Inputs

The controller substitutes these placeholders before running you: `{repo}`
(owner/name), `{pr}` (pull request number), `{head_sha}` (the head commit the
controller read), `{base}` (base branch name). Re-read live state first; the
branch may have moved since the controller read it.

## Steps

1. Confirm the state and the head sha:

   ```bash
   gh pr view {pr} --repo {repo} --json headRefName,headRefOid,mergeStateStatus \
     --jq '.headRefName + " " + .headRefOid + " " + .mergeStateStatus'
   ```

   If `headRefOid` is not `{head_sha}`, output `STOP: head moved`. If
   `mergeStateStatus` is no longer `BEHIND`, output `STOP: not behind`. Never
   push on top of a head you did not verify.

2. Update the branch - API first, local merge as the fallback; both land one
   merge commit:

   ```bash
   gh pr update-branch {pr} --repo {repo}
   ```

   If that fails, merge locally and push with a plain push:

   ```bash
   git fetch origin {base} <head-branch>
   git switch <head-branch>
   git merge --no-ff origin/{base} -m "chore: merge {base} into pull request branch"
   git push origin <head-branch>
   ```

   `--no-ff` guarantees one merge commit even when the branch has no commits of
   its own. If the merge stops with conflicts, do not resolve them: that is the
   conflicted state and the controller routes it to its own brief.

3. Confirm the state cleared (`UNKNOWN` is fine; GitHub is recomputing):

   ```bash
   gh pr view {pr} --repo {repo} --json mergeStateStatus --jq .mergeStateStatus
   ```

## Limits

- No force-push of any kind; the only push you run is a plain `git push`.
- Never skip, disable, or weaken a check, hook, or test, and never edit a file
  under `.github/workflows/`; this state never justifies it.
- No auto-merge and never merge the pull request; clearing `BEHIND` is the
  whole job.
- No secrets, host names, or private names in the commit message or any comment.

## Stop

Output `STOP: <reason>` instead of guessing when the merge reports conflicts,
the head moved away from `{head_sha}`, an API call or push fails with a
permission error, or the pull request is closed, a draft, or already merged.

## Output

Your final message is exactly one line: `FIXED head=<new sha>` where `<new sha>`
is the merge commit sha, or `STOP: <reason>`.

Sources: [rebase-pr][rebase-pr] and [gh-cli-patterns][gh-cli-patterns].

[rebase-pr]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/rebase-pr/SKILL.md
[gh-cli-patterns]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/gh-cli-patterns/SKILL.md
