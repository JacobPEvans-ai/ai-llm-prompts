---
type: LLM Prompt
title: Hermes repo crawl
description: Triage of new repository crawl findings with scoped pull request updates.
resource: prompt://dryvist/auto-ai-agent/hermes-repo-crawl
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: jinja2
  variables:
  - hermes_agent_hermes_home
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/94-repo-crawl.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_repo_crawl_cron_prompt
---
New repo-crawl findings are in {{ hermes_agent_hermes_home }}/data/repo-crawl/findings.json (this run's new, previously-unseen findings only — already-seen ones are pre-filtered by hash). Use the repo-crawl skill to triage them and open or update a pull request per actionable finding. Before any `gh` call that creates or modifies a pull request, export HERMES_GH_TOKEN_SET=author first. Skip a finding you cannot act on safely and say why.