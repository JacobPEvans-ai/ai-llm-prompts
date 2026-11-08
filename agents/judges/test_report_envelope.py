"""Every agent prompt declares exactly one report-envelope contract, and the eval agrees with it."""

import importlib.util

from definitions import ROOT, definitions

_SOURCE = ROOT / "agents" / "evals" / "promptfoo" / "generate.py"
_SPEC = importlib.util.spec_from_file_location("promptfoo_envelope_cases", _SOURCE)
assert _SPEC is not None and _SPEC.loader is not None
generate = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(generate)

ENVELOPE = "Return the report envelope"
OPT_OUT = "Do not use the report envelope"


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
