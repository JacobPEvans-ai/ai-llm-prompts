#!/bin/sh
# promptfoo exec provider for the OpenCode Go lane: the prompt arrives as $1 and goes to opencode on stdin
# (a prompt that starts with "-" would otherwise parse as a flag); print only the model answer.
printf '%s' "$1" | exec opencode run -m opencode-go/go-kimi-k3 --pure 2>/dev/null
