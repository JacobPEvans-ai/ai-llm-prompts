---
type: LLM Prompt Fragment
title: Hermes ai news interests
description: Shared interest seed for the news scouting profile.
resource: prompt://dryvist/auto-ai-agent/hermes-ai-news-interests
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
  path: roles/hermes_agent/defaults/main/140-work-supply-cards-b.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_ai_news_interests
---
INTEREST SEED (static floor — the interests note starts from this and grows):
- Infrastructure as code: Proxmox VE, OpenTofu/Terraform, Terrakube,
  Ansible, UniFi networking
- Secrets and identity: OpenBao/Vault, ephemeral credentials, SSH
  certificate authorities
- Observability and SIEM: Splunk, Cribl Edge/Stream, OpenTelemetry, syslog
  pipelines
- Local LLM serving: MLX on Apple Silicon, quantization, llama.cpp, LiteLLM
  routing, open-weight model releases (DeepSeek, Qwen, Hermes, Llama)
- AI agents and tooling: agent frameworks, MCP, Claude Code, Codex, Gemini
  CLI, multi-agent orchestration, agent memory systems
- Nix: nix-darwin, home-manager, flakes, reproducible dev environments
- Self-hosted services this estate runs: Traefik, Authelia, Technitium DNS,
  Vikunja, Zammad, Nautobot, Qdrant, PostgreSQL, Plex and the *arr stack
- Security advisories (CVEs, supply-chain compromises) affecting anything
  above
- GitHub automation: Actions, Renovate, release-please