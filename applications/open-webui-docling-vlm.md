---
type: LLM Prompt
title: Open WebUI Docling VLM
description: Page-parsing prompt for Open WebUI document conversion through Docling.
resource: prompt://dryvist/applications/open-webui-docling-vlm
tags: [open-webui, docling, ocr]
timestamp: 2026-11-07T11:31:54Z
status: staged
consumers:
  - dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/open_webui/defaults/main.yml
    commit: 810e5a1a0a9545515cfb669b48944457f3ab1530
    note: Exact open_webui_docling_vlm_config.model_spec.prompt value.
---

document parsing.
