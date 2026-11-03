#!/bin/sh
# Promptfoo 0.118.14 appends prompt, options JSON, and context JSON after fixed exec-provider arguments.
# The judge name is $1 and the grading prompt is $2: a JSON chat array, or plain text.
set -eu
judge=${1:?judge name required}
prompt=${2:?grading prompt required}
case "$judge" in
  judge-a)
    model=${EVAL_JUDGE_A_MODEL:?EVAL_JUDGE_A_MODEL is required}
    base_url=${EVAL_JUDGE_A_BASE_URL:?EVAL_JUDGE_A_BASE_URL is required}
    key=${EVAL_JUDGE_A_API_KEY:-}
    ;;
  judge-b)
    model=${EVAL_JUDGE_B_MODEL:?EVAL_JUDGE_B_MODEL is required}
    base_url=${EVAL_JUDGE_B_BASE_URL:?EVAL_JUDGE_B_BASE_URL is required}
    key=${EVAL_JUDGE_B_API_KEY:-}
    ;;
  *)
    echo "unknown judge: $judge" >&2
    exit 2
    ;;
esac
# The bearer header lives in a private temp file, so the key never appears in a process argument list.
auth_header=$(mktemp)
trap 'rm -f "$auth_header"' EXIT
if [ -n "$key" ]; then
  printf 'Authorization: Bearer %s\n' "$key" > "$auth_header"
fi
jq -n --arg p "$prompt" --arg m "$model" '{
  model: $m,
  temperature: 0,
  messages: (($p | fromjson? | select(type == "array")) // [{role: "user", content: $p}])
}' | curl -sf -m 600 "${base_url%/}/chat/completions" \
  -H 'Content-Type: application/json' -H @"$auth_header" --data-binary @- \
  | jq -r '.choices[0].message.content'
