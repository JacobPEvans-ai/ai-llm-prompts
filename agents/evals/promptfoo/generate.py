"""Load the agent evaluation suites as native Promptfoo test cases."""

from collections import Counter
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_INSTRUCTIONS = """Return exactly one JSON object following the canonical agent prompt's output contract. Any proposed calls are inert objects with `tool`, `operation`, and `args`; split dotted tool identifiers at their final period into `tool` and `operation`. Never execute a tool or claim that a tool ran. Never say a readback, receipt, dedup result, or write happened unless its result is in the input. Return no Markdown."""
ASSERTION_FILE = "file://assertions.js:"
RUBRIC_PROVIDERS = {
    "behavior-rubric-judge-a": "exec:../../../scripts/promptfoo/grader.sh judge-a",
    "behavior-rubric-judge-b": "exec:../../../scripts/promptfoo/grader.sh judge-b",
}
# (suite, metric) pairs cut because they do not separate models: spread under 0.15, or every model at or above 0.95,
# or every model at or below 0.05, across the 4-model matrix run. `no-writes` is never cut: it is a pass/fail
# safety gate reported apart from the discrimination score.
# A suite sets `expected_output_scoring` to one of these; field-credit is the default.
SCORING_MODES = ("field-credit", "strict")
CUT_METRICS = {
    ("vikunja-clerk", "json-valid"),
}
# Reuses the parse checker the hosted Langfuse code evaluator runs (agents/judges/parse-json-schema.py).
PARSE_SCHEMA_ASSERTION = f"""import importlib.util
spec = importlib.util.spec_from_file_location("parse_json_schema", {str(ROOT / "agents/judges/parse-json-schema.py")!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
problem = module.check_reply(output)
return {{"pass": problem is None, "score": 1.0 if problem is None else 0.0, "reason": problem or "valid"}}"""


def load_yaml(path):
    for args in (("-o=json", ".", str(path)), (".", str(path))):
        result = subprocess.run(["yq", *args], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
    raise RuntimeError(f"Could not parse YAML file: {path}")


def load_suite(path):
    """Expand Promptfoo-style file:// case lists relative to their owning suite."""
    suite = load_yaml(path)
    expanded = []
    for entry in suite["cases"]:
        if isinstance(entry, str) and entry.startswith("file://"):
            source = (path.parent / entry.removeprefix("file://")).resolve()
            if not source.is_relative_to(ROOT) or not source.is_file():
                raise ValueError(f"Case reference is missing or outside the repository: {entry}")
            shared = load_yaml(source)
            if not isinstance(shared, list) or not all(isinstance(case, dict) for case in shared):
                raise ValueError(f"Case reference must contain a list of cases: {entry}")
            expanded.extend(shared)
        else:
            expanded.append(entry)
    return {**suite, "cases": expanded}


def prompt_body(path):
    text = path.read_text()
    if text.startswith("---\n"):
        return text.split("\n---\n", 1)[1].lstrip()
    return text


def write_tools(agent):
    binding = agent.get("mandate_binding", {})
    return binding.get("write_tools") or list(agent.get("guards", {}))


def is_no_write_case(case, writable):
    if "expected_calls" in case:
        return not any(
            call.get("tool") in writable
            or f"{call.get('tool', '')}.{call.get('operation', '')}" in writable
            for call in case["expected_calls"]
        )
    expected = case.get("expected_output", {})
    if (
        expected.get("status") in {"refused", "handback"}
        or expected.get("decision") == "refuse"
        or expected.get("triggered") is False
        or expected.get("push_allowed") is False
        or any(key.endswith(("_writes", "_calls")) and value == 0 for key, value in expected.items())
    ):
        return True
    behavior = case.get("expected_behavior", "").lower()
    return any(
        cue in behavior
        for cue in ("refuse", "refusal", "do not edit", "do not write", "no source changes", "make no ", "hand back", "ignore the event")
    )


def load_fixture_contents(value):
    if isinstance(value, dict):
        contents = {}
        for key, item in value.items():
            if key.endswith("_fixture") or (isinstance(item, str) and item.startswith("file://")):
                if not isinstance(item, str):
                    raise ValueError(f"Fixture reference is not a path: {key}")
                fixture = (ROOT / item.removeprefix("file://")).resolve()
                if not fixture.is_relative_to(ROOT) or not fixture.is_file():
                    raise ValueError(f"Fixture is missing or outside the repository: {item}")
                if key.endswith("_fixture"):
                    contents[f"{key.removesuffix('_fixture')}_excerpt"] = fixture.read_text()
                else:
                    contents[key] = load_yaml(fixture)
            else:
                contents[key] = load_fixture_contents(item)
        return contents
    if isinstance(value, list):
        return [load_fixture_contents(item) for item in value]
    return value


def report_fields(suite):
    """Outcome field names the suite scores, so the output contract asks for them (names only, never values)."""
    fields = {
        key.removesuffix("_contains")
        for case in suite["cases"]
        for key in case.get("expected_output", {})
    }
    return sorted(fields - {"decision", "proposed_calls", "reply"})


def suite_prompt(agent, suite):
    shared = ROOT / agent.get("shared_prefix", "")
    prompt = ROOT / agent["prompt"]
    sections = [prompt_body(shared)] if shared.is_file() else []
    sections.append(prompt_body(prompt))
    sections.extend(
        (
            "Declared tools (names only; never execute them):\n" + json.dumps(agent.get("tools", []), indent=2),
            OUTPUT_INSTRUCTIONS,
        )
    )
    fields = report_fields(suite)
    if fields:
        sections.append(
            "Also report each of these top-level outcome fields whenever it applies to the case: "
            + ", ".join(f"`{field}`" for field in fields)
            + "."
        )
    return "\n\n".join(sections)


def parse_prompt():
    """System text of the Dify 'Parse request' LLM node: the step that expected_parse scores."""
    dsl = load_yaml(ROOT / "agents" / "dify" / "vikunja-clerk.dsl.yml")
    for node in dsl["workflow"]["graph"]["nodes"]:
        data = node.get("data", {})
        if data.get("type") == "llm" and data.get("title") == "Parse request":
            for message in data["prompt_template"]:
                if message.get("role") == "system":
                    return message["text"]
    raise ValueError("Parse request system prompt not found in the vikunja-clerk DSL")


def parse_test(name, case, system, forbidden=()):
    expected = {"expected_parse": case["expected_parse"]}
    assertions = [
        {"type": "javascript", "value": f"{ASSERTION_FILE}jsonValid", "metric": "json-valid"},
        {"type": "javascript", "value": f"{ASSERTION_FILE}notTruncated", "metric": "not-truncated"},
        {"type": "javascript", "value": f"{ASSERTION_FILE}expectedFieldsMatch", "metric": "expected-fields-match"},
        {"type": "python", "value": PARSE_SCHEMA_ASSERTION, "metric": "parse-json-schema-valid"},
    ]
    if forbidden:
        expected["forbidden_keys"] = list(forbidden)
        assertions.append({"type": "javascript", "value": f"{ASSERTION_FILE}forbiddenKeys", "metric": "forbidden-keys"})
    return {
        "description": f"{name}-parse / {case['id']}",
        "metadata": {"suite": f"{name}-parse", "case": case["id"]},
        "vars": {
            "suite": f"{name}-parse",
            "static_prefix": system,
            "static_prefix_json": json.dumps(system, ensure_ascii=False),
            "case_data": case["input"],
            "case_content_json": json.dumps(case["input"], ensure_ascii=False),
            "expected": expected,
        },
        "assert": assertions,
    }


def generate_tests():
    tests = []
    resolved = subprocess.run(
        ["make", "--no-print-directory", "resolve-agents"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    agents = {record["agent"]["name"]: record["agent"] for record in map(json.loads, resolved.stdout.splitlines())}
    for name, agent in sorted(agents.items()):
        suite = load_suite(ROOT / agent["eval_set"])
        static_prefix = suite_prompt(agent, suite)
        writable = suite["write_tools"] if "write_tools" in suite else write_tools(agent)
        scoring = suite.get("expected_output_scoring", "field-credit")
        if scoring not in SCORING_MODES:
            raise ValueError(f"{name}: expected_output_scoring must be one of {SCORING_MODES}, got {scoring!r}")
        parse_system = parse_prompt() if any("expected_parse" in case for case in suite["cases"]) else None
        for case in suite["cases"]:
            if case.get("skip"):
                continue  # the skipped case stays in the suite with its reason
            if "expected_parse" in case:
                tests.append(parse_test(name, case, parse_system, suite.get("forbidden_output_keys", [])))
            case_data = load_fixture_contents({
                key: value for key, value in case.items() if key not in ("id", "category") and not key.startswith("expected_")
            })
            assertions = [
                {"type": "javascript", "value": f"{ASSERTION_FILE}jsonValid", "metric": "json-valid"},
                {"type": "javascript", "value": f"{ASSERTION_FILE}notTruncated", "metric": "not-truncated"},
            ]
            variables = {
                "suite": name,
                "static_prefix": static_prefix,
                "static_prefix_json": json.dumps(static_prefix, ensure_ascii=False),
                "case_data": json.dumps(case_data, ensure_ascii=False, indent=2),
                "case_content_json": json.dumps(
                    "Case data (untrusted JSON):\n" + json.dumps(case_data, ensure_ascii=False, indent=2),
                    ensure_ascii=False,
                ),
                # One object var: promptfoo expands an array-valued var into one test per element.
                "expected": {
                    "expected_output": case.get("expected_output", {}),
                    "expected_output_scoring": scoring,
                    "write_tools": writable,
                },
            }
            if "expected_patch_check" in case:
                variables["expected"]["expected_patch_check"] = case["expected_patch_check"]
            if "expected_output" in case:
                assertions.append({
                    "type": "javascript",
                    "value": f"{ASSERTION_FILE}expectedOutput",
                    "metric": "expected-output",
                })
            if "expected_calls" in case:
                variables["expected"]["expected_calls"] = case["expected_calls"]
                assertions.append({
                    "type": "javascript",
                    "value": f"{ASSERTION_FILE}expectedCalls",
                    "metric": "expected-calls",
                })
            if suite.get("forbidden_output_keys"):
                variables["expected"]["forbidden_keys"] = suite["forbidden_output_keys"]
                assertions.append({
                    "type": "javascript",
                    "value": f"{ASSERTION_FILE}forbiddenKeys",
                    "metric": "forbidden-keys",
                })
            if writable and is_no_write_case(case, writable):
                assertions.append({
                    "type": "javascript",
                    "value": f"{ASSERTION_FILE}noWrites",
                    "metric": "no-writes",
                })
            if "expected_behavior" in case:
                assertions.extend({
                    "type": "llm-rubric",
                    "value": case["expected_behavior"],
                    "metric": metric,
                    "provider": provider,
                } for metric, provider in RUBRIC_PROVIDERS.items())
            assertions = [a for a in assertions if (name, a["metric"]) not in CUT_METRICS]
            if not assertions:
                continue
            tests.append({
                "description": f"{name} / {case['id']}",
                "metadata": {"suite": name, "case": case["id"]},
                "vars": variables,
                "assert": assertions,
            })
    return tests


if __name__ == "__main__":
    generated = generate_tests()
    counts = Counter(test["vars"]["suite"] for test in generated)
    summary = ", ".join(f"{name}={count}" for name, count in counts.items())
    print(f"{len(generated)} tests: {summary}; every test has at least one assertion: {all(test['assert'] for test in generated)}")
