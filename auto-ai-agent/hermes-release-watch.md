---
type: LLM Prompt
title: Hermes release watch
description: Daily digest of recent releases for tracked dependencies.
resource: prompt://dryvist/auto-ai-agent/hermes-release-watch
tags: [hermes, cron, releases, dependencies]
timestamp: 2026-10-04T01:46:15Z
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main/43-direct-cron-jobs-core.yml
    commit: 504d1cac163715ae3adfce491fe7897751c2ad67
---
Build this run's inventory only from open Renovate Dependency Dashboard issues and pinned versions in the public
repositories of the configured GitHub organization. Use the existing GitHub read tools available to this job; do not
create or maintain a separate inventory.

Find releases published in the last 24 hours (UTC), read their release notes, and confirm the currently pinned version
for each candidate. Include tracked releases about local LLM serving (MLX, llama.cpp, or llama-swap); LLM routers
(LiteLLM); agent command-line tools or agent frameworks; Proxmox; OpenBao; Cribl; Splunk; Grafana or VictoriaMetrics;
or Authelia. Include any security fix for a tracked project, regardless of category. Report only releases whose old and
new versions can be verified. Use release notes as the source of truth; do not infer extra impact.

Post at most 10 bullets, prioritizing security fixes and changes with clear operator impact. Use exactly this form for
each bullet:

`Tool old→new: why it matters — <release URL>`

Keep each reason concise and factual, and include the direct release URL. If no release qualifies, output only the bare
marker `[SILENT]`.
