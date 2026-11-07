---
type: LLM Prompt
title: Tier-2 Load-Test Request
description: Requests a count from 1 to 128 with a per-request identifier.
resource: prompt://dryvist/automation/testing/tier-2-load-test-request
tags: [automation, testing, load, tier-2]
timestamp: 2026-11-07T10:47:55Z
status: staged
consumers:
  - dryvist/ansible-proxmox-ai
render:
  engine: application
  variables: [id]
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: tests/load/tier2-burst.js
    commit: e55c2d147261fedb83cf801179a901cdb6c65b06
    note: Exact request content template literal with its request-id placeholder preserved.
---

Request ${id}. Count from 1 to 128.
