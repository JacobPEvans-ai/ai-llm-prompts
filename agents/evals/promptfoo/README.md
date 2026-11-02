# Promptfoo agent evaluation matrix

The test generator loads the three source suites directly. Run it from the repository root to check its case and
assertion counts:

```sh
python3 agents/evals/promptfoo/generate.py
```

Each suite's static prefix is its agent prompt, the declared tool list, fixed JSON instructions and the names (never the
values) of the outcome fields that suite scores. The prefix is byte-identical across the suite's cases; case data comes
last, in the user message. The shared prefix the agents name, `shared/homelab.md`, is absent, so it is skipped.

Every `vikunja-clerk` case with `expected_parse` also yields a `vikunja-clerk-parse` test. That test sends the raw caller
input to the Dify "Parse request" node prompt (`agents/dify/vikunja-clerk.dsl.yml`) and scores `expected-fields-match`
and `parse-json-schema-valid` (the checker in `agents/judges/parse-json-schema.py`).

## Providers

| Label | Candidate | Configuration |
| --- | --- | --- |
| `local` | an OpenAI-compatible endpoint | `EVAL_LOCAL_MODEL`, `OPENAI_BASE_URL`, `OPENAI_API_BASE_URL`, `OPENAI_API_KEY` |
| `luna` | Codex, through `scripts/promptfoo/luna.sh` | an operator-signed-in `codex` CLI |
| `go-kimi` | OpenCode Go, through `scripts/promptfoo/go-kimi.sh` | an operator-signed-in `opencode` CLI |

The behavior rubric is graded by `scripts/promptfoo/grader.sh`, which calls `EVAL_GRADER_BASE_URL` with
`EVAL_GRADER_MODEL`. Point it at a model that is not the candidate under test.

## Installation

Nothing is installed globally. The run command below takes Node.js 22, `yq` and Python 3 from nixpkgs for the one
command, and promptfoo 0.118.14 from npm. Node.js 22 is required: promptfoo 0.118 hits a native assertion under
Node.js 24. `PROMPTFOO_PYTHON` must name a Python that runs `agents/judges/parse-json-schema.py`.

## Usage

Run one provider at a time, from this directory, because the exec providers resolve their script paths relative to it:

```sh
cd agents/evals/promptfoo
PROMPTFOO_PYTHON=python3 nix --extra-experimental-features 'nix-command flakes' \
  shell nixpkgs#nodejs_22 nixpkgs#yq-go nixpkgs#python3 -c \
  npx -y promptfoo@0.118.14 eval -c promptfooconfig.yaml --filter-providers local \
  --no-cache --no-progress-bar -o /tmp/agent-evals-local.json
```

Promptfoo records per-assertion metric scores in each result's `namedScores`. Print suite/provider/metric counts and mean
scores with:

```sh
jq -r '
  .results.results
  | map(. as $result | (($result.namedScores // {}) | to_entries[]) | {
      suite: $result.vars.suite,
      provider: ($result.provider.label // $result.provider.id),
      metric: .key,
      score: .value
    })
  | group_by([.suite, .provider, .metric])[]
  | [.[0].suite, .[0].provider, .[0].metric, (length | tostring), (map(.score) | add / length | tostring)]
  | @tsv
' /tmp/agent-evals-local.json
```
