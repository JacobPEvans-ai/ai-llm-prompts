---
type: LLM Prompt
title: Hermes digest: homelab AI fabric status
description: 6-hourly auto-delivered AI fabric component health probe.
resource: prompt://dryvist/auto-ai-agent/hermes-digest-homelab-ai-fabric-status
tags: [hermes, cron, autonomous-agent, digest]
timestamp: 2026-07-24T00:00:00-04:00
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: envsubst
  variables: [PROXMOX_SUBDOMAIN]
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main.yml
    commit: 3b0c332623d5d2ee2fd283f9ab265cf6d5a7911b
---
STRICT budget: at most 4 terminal calls, curl only. Probe each FQDN health endpoint with: curl -sS -m 8 -o /dev/null -w '%{http_code}' <url> . URLs: https://llm.${PROXMOX_SUBDOMAIN}/v1/models ; https://hermes.${PROXMOX_SUBDOMAIN}/ ; https://qdrant.${PROXMOX_SUBDOMAIN}/ ; https://agentgateway.${PROXMOX_SUBDOMAIN}/ . Final response UNDER 12 LINES: a plain-text component/status list with the ACTUAL http code per component (2xx/3xx=up, else down). Auto-delivered - no slack tool, no SILENT. Report exactly what curl returned. Never invent status. End with the model id.
