#!/bin/sh
# promptfoo exec provider for the Luna lane: the prompt arrives as $1 and goes to codex on stdin
# (a prompt that starts with "-" would otherwise parse as a flag); print only the model answer.
printf '%s' "$1" | exec codex exec -m gpt-6-luna -c model_reasoning_effort=medium -c otel.trace_exporter=none \
  --ephemeral --skip-git-repo-check -s read-only - 2>/dev/null
