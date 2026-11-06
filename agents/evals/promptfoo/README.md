# Promptfoo agent evaluation matrix

The test generator loads the five source suites directly; the other suites, such as `agents/evals/docs-updater.yaml`,
are not part of this matrix. Run it from the repository root to check its case and
assertion counts:

```sh
python3 agents/evals/promptfoo/generate.py
```

Suite `cases` lists may include `file://` references to shared YAML case lists, relative to the suite file.
The generator and authoring judges expand these references through the same loader. Text-agent boundary cases live
in `agents/evals/shared/text-boundaries.yaml`.

Each suite's static prefix contains its declared shared prefix when that file exists, its canonical prompt, the declared
tool list, fixed JSON instructions and the names (never the values) of the outcome fields that suite scores. The prefix
is byte-identical across the suite's cases; case data comes last, in the user message. The generator includes
`shared/homelab.md` because the agent definitions declare that existing file.

Every `vikunja-clerk` case with `expected_parse` also yields a `vikunja-clerk-parse` test. That test sends the raw caller
input to the Dify "Parse request" node prompt (`agents/dify/vikunja-clerk.dsl.yml`), now composed from the shared prefix
and canonical `agents/prompts/vikunja-clerk.md` prompt, including its "Parse request (classifier step)" section. It
scores `expected-fields-match` and `parse-json-schema-valid` (the checker in `agents/judges/parse-json-schema.py`).

A suite's top-level `expected_output_scoring` sets how `expected-output` scores: `field-credit` (the default) is the
share of expected keys that match, and `strict` is 1 only when every key matches. `vikunja-clerk` is `strict`.

## Providers

| Label | Candidate | Configuration |
| --- | --- | --- |
| `local` | an OpenAI-compatible endpoint | `EVAL_LOCAL_MODEL`, `OPENAI_BASE_URL`, `OPENAI_API_BASE_URL`, `OPENAI_API_KEY` |
| `luna` | Codex, through `scripts/promptfoo/luna.sh` | an operator-signed-in `codex` CLI |
| `go-kimi` | OpenCode Go, through `scripts/promptfoo/go-kimi.sh` | an operator-signed-in `opencode` CLI |

Only the four `code-simplifier` behavior-rubric cases use two graders: `behavior-rubric-judge-a` reads
`EVAL_JUDGE_A_BASE_URL` and `EVAL_JUDGE_A_MODEL`, and `behavior-rubric-judge-b` reads
`EVAL_JUDGE_B_BASE_URL` and `EVAL_JUDGE_B_MODEL`. A judge that needs a key sets `EVAL_JUDGE_A_API_KEY` or
`EVAL_JUDGE_B_API_KEY`; the grader sends it as a bearer header and never puts it on a command line. Keys come from the
runtime secret store, never from this repository. Both judges must be models outside the candidate set. Rubric scores
count only for cases where `not-truncated` passes.

## Installation

Nothing is installed globally. The run command below takes Node.js 22, `yq`, gomplate, and Python 3 from nixpkgs for the one
command, and promptfoo 0.118.14 from npm. The generator resolves profiles through `make resolve-agents`, the same
gomplate merge used by Dify rendering and the pytest judges. Node.js 22 is required: promptfoo 0.118 hits a native assertion under
Node.js 24. `PROMPTFOO_PYTHON` must name a Python that runs `agents/judges/parse-json-schema.py`.

## Usage

Run one provider at a time, from this directory, because the exec providers resolve their script paths relative to it:

```sh
cd agents/evals/promptfoo
PROMPTFOO_PYTHON=python3 nix --extra-experimental-features 'nix-command flakes' \
  shell nixpkgs#nodejs_22 nixpkgs#yq-go nixpkgs#gomplate nixpkgs#python3 -c \
  npx -y promptfoo@0.118.14 eval -c promptfooconfig.yaml --filter-providers local \
  --no-cache --no-progress-bar -o /tmp/agent-evals-local.json
```

Promptfoo records per-assertion metric scores in each result's `namedScores`. Print suite/provider/metric counts and mean
scores with (rubric scores are included only when `not-truncated` scored 1):

```sh
jq -r '
  .results.results
  | map(. as $result | (($result.namedScores // {}) | to_entries[]) | {
      suite: $result.vars.suite,
      provider: ($result.provider.label // $result.provider.id),
      metric: .key,
      score: .value
    } | select((.metric | startswith("behavior-rubric-") | not) or $result.namedScores["not-truncated"] == 1))
  | group_by([.suite, .provider, .metric])[]
  | [.[0].suite, .[0].provider, .[0].metric, (length | tostring), (map(.score) | add / length | tostring)]
  | @tsv
' /tmp/agent-evals-local.json
```

Print the share of result cases where both judges' pass values agree:

```sh
jq -r '
  [.results.results[]
   | [(.gradingResult.componentResults // [])[] | select(.assertion.metric == "behavior-rubric-judge-a") | .pass] as $judge_a
   | [(.gradingResult.componentResults // [])[] | select(.assertion.metric == "behavior-rubric-judge-b") | .pass] as $judge_b
   | select(($judge_a | length) > 0 and ($judge_b | length) > 0)
   | ($judge_a[0] == $judge_b[0])]
  | if length == 0 then "no paired judge results"
    else "agreement=\((map(select(.)) | length) / length)"
    end
' /tmp/agent-evals-local.json
```
