---
type: LLM Prompt
title: Hermes PR shepherd sweep
description: "Hourly sweep updates BEHIND agent PRs and reports unresolved PRs; the org workflow arms eligible PRs, and the sweep never merges directly."
resource: prompt://dryvist/auto-ai-agent/hermes-pr-shepherd-sweep
tags: [hermes, cron, autonomous-agent, pull-requests]
timestamp: 2026-11-04T10:10:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: jpe-ai-agents/ai-llm-prompts
    path: auto-ai-agent/claude-code/agents/pr-shepherd.md
    note: "Durable counterpart of the in-session shepherd; limited to branch updates and one report comment; the org workflow handles eligible merges."
---
Run a PR follow-through sweep across the dryvist GitHub org right now. You keep agent-authored PRs moving. **You never commit, push, dismiss a review, or merge directly. Your only writes are `gh pr update-branch` and one comment per head commit. The org workflow arms eligible PRs, not you.**

Use your `github-issues` skill with your per-repo write token. If a token is missing, skip that repo and name it in the report.

## Enumerate

- List open, non-draft PRs older than 2 hours in non-archived repos whose author is `app/jacobpevans-claude`. Apply your operator skip-list.
- For each PR read `mergeStateStatus`, `reviewDecision`, labels, the check rollup, all review threads, and every issue comment, review body and inline comment.

## Act, in order, first match wins

1. A PR waiting for a person stays a draft. Leave `release:in-progress` PRs and `develop` to `main` promotions alone.
2. `BEHIND`: run `gh pr update-branch`.
3. `DIRTY`, a failed check, or a required check that never reported: post one comment marked `<!-- hermes-pr-shepherd:<head-sha> -->` naming the conflict or the check names. Skip the PR if that marker is already present for this head.
4. `reviewDecision` of `CHANGES_REQUESTED`, any unresolved thread, or any comment, review body or inline comment from someone other than the PR author, the release apps or PR-agent that the author has not answered: leave it for an agent session and include it in the report.
5. A PR-agent finding counts as open feedback unless a reply carries `<!-- addressed: agent-finding-` for it. Treat a PR-agent "not included because of the token budget" list as open feedback too.
6. Otherwise, with `CLEAN` or `UNSTABLE` and every check successful: leave auto-merge to the org workflow.

## Report

If you changed nothing and no PR has waited more than 24 hours, reply with exactly [SILENT]. Otherwise post one message to the home channel. Include updated branches, eligible PRs left to the org workflow, and PRs waiting over 24 hours with their URLs and holding rules. End with one line naming the model id(s) you used.
