---
type: LLM Prompt
title: Hermes github route
description: Pull request review request populated from a webhook event.
resource: prompt://dryvist/auto-ai-agent/hermes-github-route
tags:
- hermes
- autonomous-agent
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
  path: roles/hermes_agent/defaults/main/51-github-webhook-route.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_github_route_prompt
---
Review pull request #{pull_request.number} in {repository.full_name} at head commit {pull_request.head.sha}.