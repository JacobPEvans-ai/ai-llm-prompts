#!/bin/sh
# promptfoo exec provider for the behavior-rubric grader. The run sets EVAL_GRADER_BASE_URL and
# EVAL_GRADER_MODEL to a local model that is NOT the candidate under test, so no model grades itself.
# The grading prompt arrives as $1: a JSON chat array, or plain text.
set -eu
jq -n --arg p "$1" --arg m "$EVAL_GRADER_MODEL" '{
  model: $m,
  temperature: 0,
  messages: (($p | fromjson? | select(type == "array")) // [{role: "user", content: $p}])
}' | curl -sf -m 600 "${EVAL_GRADER_BASE_URL%/}/chat/completions" \
  -H 'Content-Type: application/json' --data-binary @- \
  | jq -r '.choices[0].message.content'
