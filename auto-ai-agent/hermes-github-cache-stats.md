---
type: LLM Prompt
title: Hermes github cache stats
description: Read-only repository cache usage and churn threshold report.
resource: prompt://dryvist/auto-ai-agent/hermes-github-cache-stats
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/45-recurring-catalog.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_github_cache_stats_cron_prompt
---
Daily GitHub Actions cache health check for the dryvist organization, read-only. Your GitHub credential cannot write: only GET requests, sending header "Authorization: token $GH_PAT_WRITE_PROJECT_ISSUES" (this profile's key holds the read-only token) — never open, comment on, label, close, or change anything. List every non-archived repository in the org (GET https://api.github.com/orgs/dryvist/repos?per_page=100, following the Link header until exhausted). For each repo, call GET https://api.github.com/repos/dryvist/<repo>/actions/cache/usage and GET https://api.github.com/repos/dryvist/<repo>/actions/caches?per_page=100 (same Link-header pagination). Flag a repo on either condition: (1) active_caches_size_in_bytes exceeds 80% of the 10 GiB (10737418240 byte) default per-repository Actions cache limit — if you find solid evidence the repo's actual configured limit differs from 10 GiB, use that instead and say so; (2) grouping the caches array by key PREFIX (the key with its trailing content-hash/version segment stripped — e.g. "ansible-galaxy-" from "ansible-galaxy-Linux-<hash>") any one prefix has more than 3 entries whose created_at falls within the last 24 hours, meaning that cache is being evicted and rebuilt (churn) rather than reused. Report ONLY the repos and prefixes that actually breach one of the two conditions, each with its measured number against the threshold. If nothing breaches, reply exactly [SILENT]. Never propose or attempt to raise a repo's cache size limit yourself — that is a human/coder decision; you only observe and report.