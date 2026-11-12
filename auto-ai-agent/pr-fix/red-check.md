---
type: LLM Prompt
title: "PR fix brief: failing check"
description: Fix one failing named check on a pull request as one new commit, from the check name and log lines the controller passes.
resource: prompt://dryvist/auto-ai-agent/pr-fix/red-check
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
  note: CI failure handling from Phase 2.3 (fetch logs, fix locally, validate, one push), condensed
- repository: dryvist/claude-code-plugins
  path: github-workflows/skills/gh-cli-patterns/SKILL.md
  note: canonical status-check rollup shapes and placeholder convention
---

You fix one pull request whose check `{check_name}` fails at head. The
controller passes the check name and the failing log lines. The fix is exactly
one new commit on the pull request branch that makes `{check_name}` pass.
**You never rebase, never force-push, and never merge the pull request.**

## Inputs

The controller substitutes these placeholders before running you: `{repo}`
(owner/name), `{pr}` (pull request number), `{head_sha}` (the head commit the
controller read), `{base}` (base branch name), `{check_name}` (the failing
check), `{log_lines}` (the failure excerpt). Re-read live state first; checks
re-run on every push.

## Steps

1. Confirm the failure is still current at `{head_sha}`:

   ```bash
   gh pr view {pr} --repo {repo} --json statusCheckRollup \
     --jq '.statusCheckRollup[] | [(.name // .context), (.conclusion // .state)] | join(" ")'
   ```

2. Reproduce locally: check out the head branch at `{head_sha}`, read the
   workflow that defines `{check_name}`, run the same command the check runs,
   and confirm it fails the same way `{log_lines}` shows.

3. Fix the cause. Fix only what the pull request's diff controls; the smallest
   correct change wins. Never change the check itself - no skipping,
   disabling, weakening, or retitling a check, hook, or test.

4. Validate locally with the touched repo's own lint and test entry points,
   then land exactly one commit and push with a plain push:

   ```bash
   git add <changed-files>
   git commit -m "fix: make {check_name} pass"
   git push origin <head-branch>
   ```

5. Workflow exception: you may edit a file under `.github/workflows/` only
   when `{check_name}` is about that file itself - workflow lint, actionlint,
   or a check that validates workflow files. Never in any other case.

## Limits

- No force-push of any kind; the only push you run is a plain `git push`.
- Never skip, disable, or weaken a check, hook, or test, including the failing
  one; fixing means the check passes as written.
- Outside step 5's exception, never edit files under `.github/workflows/`.
- No auto-merge and never merge the pull request.
- No secrets, host names, or private names in the commit message or any comment.

## Stop

Output `STOP: <reason>` instead of guessing when `{log_lines}` or your local
reproduction shows the failure outside the pull request's diff - the failing
code or configuration is untouched by it, so the base is red or the check is
flaky. Also stop when the check needs a secret or permission the pull request
cannot grant, the head moved away from `{head_sha}`, an API call or push fails
with a permission error, or the pull request is closed, a draft, or already
merged.

## Output

Your final message is exactly one line: `FIXED head=<new sha>` where `<new sha>`
is your fix commit sha, or `STOP: <reason>`.

Sources: [finalize-pr][finalize-pr] and [gh-cli-patterns][gh-cli-patterns].

[finalize-pr]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/finalize-pr/SKILL.md
[gh-cli-patterns]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/gh-cli-patterns/SKILL.md
