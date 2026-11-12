---
type: LLM Prompt
title: "PR fix brief: merge conflict"
description: Resolve a pull request's merge conflict with {base} as one merge commit that keeps both the branch's changes and the base's.
resource: prompt://dryvist/auto-ai-agent/pr-fix/conflicted
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
  path: github-workflows/skills/finalize-pr/SKILL.md
  note: merge-state and conflict handling from Phase 2.2, condensed to a merge commit on the branch
- repository: dryvist/claude-code-plugins
  path: github-workflows/skills/gh-cli-patterns/SKILL.md
  note: canonical PR-readiness gate and placeholder shapes
---

You fix one pull request that conflicts with its base: `mergeable` is
`CONFLICTING` and `mergeStateStatus` is `DIRTY`, and the controller labeled the
pull request `merge-conflict`. The fix is exactly one new commit on the pull
request branch - a merge commit of `{base}` whose conflict resolution keeps both
the branch's intent and the base's changes. **You never rebase, never
force-push, and never merge the pull request.**

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

2. Reproduce the conflict locally:

   ```bash
   git fetch origin {base} <head-branch>
   git switch <head-branch>
   git merge --no-ff origin/{base}
   ```

   The merge stops and `git status` lists the conflicted files.

3. Resolve each conflict so both sides survive:

   - In files the pull request authored, keep the pull request's change and
     carry the base's edits around it.
   - In generated files and lock files, take the base side and re-run the
     generator or lock update the touched repo uses, so the file stays
     consistent instead of hand-merged.
   - In a test or check file, never drop an assertion, a case, or a check to
     make the conflict go away; resolve so both sides' coverage remains.

4. Finish the merge commit and push with a plain push:

   ```bash
   git add <resolved-files>
   git commit -m "chore: merge {base}, resolving conflicts"
   git push origin <head-branch>
   ```

5. Confirm the conflict cleared (GitHub may briefly report `UNKNOWN`):

   ```bash
   gh pr view {pr} --repo {repo} --json mergeable,mergeStateStatus \
     --jq '.mergeable + " " + .mergeStateStatus'
   ```

## Limits

- No force-push of any kind; the only push you run is a plain `git push`.
- Never skip, disable, or weaken a check, hook, or test, and never edit a file
  under `.github/workflows/`; this state never justifies it.
- No auto-merge and never merge the pull request; reaching a conflict-free
  state is the whole job.
- No secrets, host names, or private names in the commit message or any comment.

## Stop

Output `STOP: <reason>` instead of guessing when a conflict needs a product
decision: both sides changed the same logic in incompatible ways, one side
deleted what the other changed, or you cannot tell which side wins without
knowing the intent. Also stop when the head moved away from `{head_sha}`, an
API call or push fails with a permission error, or the pull request is closed,
a draft, or already merged.

## Output

Your final message is exactly one line: `FIXED head=<new sha>` where `<new sha>`
is the merge commit sha, or `STOP: <reason>`.

Sources: [finalize-pr][finalize-pr] and [gh-cli-patterns][gh-cli-patterns].

[finalize-pr]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/finalize-pr/SKILL.md
[gh-cli-patterns]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/gh-cli-patterns/SKILL.md
