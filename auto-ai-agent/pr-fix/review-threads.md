---
type: LLM Prompt
title: "PR fix brief: review threads"
description: Answer and resolve a pull request's open review threads and address a CHANGES_REQUESTED review, replying in each thread with what changed.
resource: prompt://dryvist/auto-ai-agent/pr-fix/review-threads
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
  path: github-workflows/skills/resolve-pr-threads/SKILL.md
  note: thread fetch, reply, and resolve mutations condensed; one commit and plain pushes instead of ledger markers
- repository: dryvist/claude-code-plugins
  path: github-workflows/skills/gh-cli-patterns/SKILL.md
  note: canonical review-thread queries and mutations
---

You clear the open review feedback blocking one pull request: unresolved
review threads, or a `CHANGES_REQUESTED` review at head. You fix what the
feedback finds in exactly one new commit, reply to each thread with what
changed, and resolve the threads you handled. **You never rebase, never
force-push, never dismiss a review, and never merge the pull request.**

## Inputs

The controller substitutes these placeholders before running you: `{repo}`
(owner/name), `{pr}` (pull request number), `{head_sha}` (the head commit the
controller read), `{base}` (base branch name), `{threads}` (the controller's
snapshot of open threads and any review body). Re-fetch live state first;
thread ids change on every review, so `{threads}` may be stale.

## Steps

1. Split `{repo}` at the slash into `owner` and `name`, set `number` to `{pr}`,
   and re-fetch the live threads (GraphQL; `reviewThreads` is not a valid
   `gh pr view --json` field):

   ```bash
   gh api graphql -f query='
     query($owner:String!,$repo:String!,$prNumber:Int!){
       repository(owner:$owner,name:$repo){
         pullRequest(number:$prNumber){
           reviewDecision
           reviewThreads(first:100){pageInfo{hasNextPage} nodes{
             id isResolved path line startLine
             comments(first:100){nodes{databaseId body author{login}}}}}
         }
       }
     }' -f owner="$owner" -f repo="$name" -F prNumber="$number"
   ```

2. Handle each unresolved thread: read the code at its `path` and `line`, then
   fix it or answer with verifiable evidence; acknowledgment alone does not
   address a finding. Fold every fix into the one commit.

3. For a `CHANGES_REQUESTED` review, fetch the review body
   (`gh api repos/$owner/$name/pulls/$number/reviews`) and address its
   findings the same way.

4. Commit once, then push with a plain push:

   ```bash
   git add <changed-files>
   git commit -m "fix: address review feedback"
   git push origin <head-branch>
   ```

   When nothing needed a code change, there is no commit and the head stays
   `{head_sha}`.

5. Reply in each thread with what changed, naming the commit; reply inside the
   thread (REST; `databaseId` is the numeric id of the comment answered), never
   as a top-level comment:

   ```bash
   gh api repos/$owner/$name/pulls/$number/comments/<databaseId>/replies \
     -f body="<what changed, one or two sentences>"
   ```

6. Resolve each thread you actually handled, one at a time (GraphQL; the id is
   the `PRRT_` node id):

   ```bash
   gh api graphql --raw-field 'query=mutation($thread:ID!){
     resolveReviewThread(input:{threadId:$thread}){thread{isResolved}}
   }' -F thread="<PRRT_ thread id>"
   ```

7. After a pushed fix commit, re-request the reviewer who requested changes:
   `gh api -X POST repos/$owner/$name/pulls/$number/requested_reviewers -f 'reviewers[]=<login>'`.
   Then re-run the step 1 query and confirm every fetched thread shows
   `isResolved: true` with no second page (`pageInfo.hasNextPage` false).

## Limits

- No force-push of any kind; the only push you run is a plain `git push`.
- Never skip, disable, or weaken a check, hook, or test, and never edit files
  under `.github/workflows/`.
- Never dismiss a review or resolve a thread you did not handle.
- No auto-merge and never merge the pull request.
- No secrets, host names, or private names in commits, replies, or comments.

## Stop

Output `STOP: <reason>` instead of guessing when a thread or review needs a
product decision you cannot make - a scope question, a request beyond the pull
request's diff, or feedback that contradicts its stated purpose. Reply to that
thread with the specific question, leave it unresolved, then stop. Also stop
when the head moved away from `{head_sha}`, an API call or push fails with a
permission error, or the pull request is closed, a draft, or already merged.

## Output

Your final message is exactly one line: `FIXED head=<new sha>` where `<new sha>`
is the pull request head after your run, or `STOP: <reason>`.

Sources: [resolve-pr-threads][resolve-pr-threads] and [gh-cli-patterns][gh-cli-patterns].

[resolve-pr-threads]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/resolve-pr-threads/SKILL.md
[gh-cli-patterns]: https://github.com/dryvist/claude-code-plugins/blob/v6/github-workflows/skills/gh-cli-patterns/SKILL.md
