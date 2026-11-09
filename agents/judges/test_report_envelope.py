"""Every agent prompt declares exactly one report-envelope contract, the eval agrees with it, and the shared
envelope helper never echoes a reply's own content into a rejection reason."""

import importlib.util
import json

import pytest
import yaml

from definitions import ROOT, definitions

_SOURCE = ROOT / "agents" / "evals" / "promptfoo" / "generate.py"
_SPEC = importlib.util.spec_from_file_location("promptfoo_envelope_cases", _SOURCE)
assert _SPEC is not None and _SPEC.loader is not None
generate = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(generate)

def envelope_namespace():
    """Compose the helper exactly as the rendered node code does: import json, then json_fence, then envelope."""
    namespace = {"__name__": "envelope_helper"}
    exec("import json", namespace)
    for name in ("json_fence", "envelope"):
        source = (ROOT / "agents" / "dify-src" / "helpers" / f"{name}.py").read_text()
        exec(compile(source, str(ROOT / "agents" / "dify-src" / "helpers" / f"{name}.py"), "exec"), namespace)
    return namespace

ENVELOPE = "Return the report envelope"
OPT_OUT = "Do not use the report envelope"

MARKER = "envelope-reason-echo-probe-9q4x7"

ENVELOPE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "reason", "result"],
    "properties": {
        "status": {"type": "string", "enum": ["ok", "stop"]},
        "reason": {"type": "string"},
        "result": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"count": {"type": "integer"}},
        },
    },
}

_VALID = {"status": "ok", "reason": "", "result": {"count": 1}}

MARKED_REPLIES = [
    ({**_VALID, MARKER: "unused"}, "extra key name"),
    ({**_VALID, "result": {"count": 1, MARKER: "unused"}}, "nested extra key name"),
    ({**_VALID, "extra": MARKER}, "extra property value"),
    ({**_VALID, "status": MARKER}, "enum-missing status value"),
    ({**_VALID, "result": MARKER}, "wrong-typed result value"),
]


def prompt_contracts():
    """Yield (name, whitespace-normalized prompt body, expanded suite) for every agent."""
    for _, agent in definitions():
        text = (ROOT / agent["prompt"]).read_text()
        if text.startswith("---\n"):
            text = text.split("\n---\n", 1)[1]
        suite = generate.load_suite(ROOT / agent["eval_set"])
        yield agent["name"], " ".join(text.split()), suite


def status_cases(suite):
    return [case["id"] for case in suite["cases"] if "status" in case.get("expected_output", {})]


def test_every_agent_prompt_declares_exactly_one_envelope_contract():
    offenders = [name for name, body, _ in prompt_contracts()
                 if (ENVELOPE in body) == (OPT_OUT in body)]
    assert offenders == [], f"prompts must state exactly one of the report-envelope contracts: {offenders}"


def test_opt_out_agent_evals_never_expect_status():
    offenders = {name: status_cases(suite) for name, body, suite in prompt_contracts()
                 if OPT_OUT in body and status_cases(suite)}
    assert offenders == {}, f"opt-out agents' evals must never expect status: {offenders}"


def test_agents_whose_evals_expect_status_return_the_envelope():
    offenders = [name for name, body, suite in prompt_contracts()
                 if status_cases(suite) and ENVELOPE not in body]
    assert offenders == [], f"agents whose evals expect status must return the report envelope: {offenders}"


@pytest.mark.parametrize(("reply", "planting"), MARKED_REPLIES, ids=[planting for _, planting in MARKED_REPLIES])
def test_helper_reasons_never_echo_a_marker_planted_in_the_reply(reply, planting):
    parsed, problem = envelope_namespace()["check_envelope"](json.dumps(reply), ENVELOPE_SCHEMA)
    assert parsed is None and problem, f"{planting} must be rejected"
    assert MARKER not in problem, f"reason echoes the {planting}: {problem}"


def _envelope_nodes():
    for path in sorted((ROOT / "agents" / "dify").glob("*.dsl.yml")):
        dsl = yaml.safe_load(path.read_text())
        for node in dsl["workflow"]["graph"]["nodes"]:
            code = node.get("data", {}).get("code", "")
            if isinstance(code, str) and "def check_envelope" in code:
                yield path.name, node["data"]["title"], code


_NODES = list(_envelope_nodes())


def test_rendered_dsls_embed_the_envelope_helper():
    assert len({(file, title) for file, title, _ in _NODES}) >= 2, "expected embedded copies in the rendered DSLs"


@pytest.mark.parametrize(("file", "title", "code"), _NODES, ids=[f"{f}:{t}" for f, t, _ in _NODES])
def test_rendered_helper_reasons_never_echo_a_marker_planted_in_the_reply(file, title, code):
    namespace = {}
    exec(compile(code, f"{file}:{title}", "exec"), namespace)  # defines the node's functions only
    for reply, _ in MARKED_REPLIES:
        _, problem = namespace["check_envelope"](json.dumps(reply), ENVELOPE_SCHEMA)
        assert problem and MARKER not in problem
