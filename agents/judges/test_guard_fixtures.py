"""Contract tests for the guard and router-policy fixtures kept apart from the model-output suites."""

from pathlib import Path

import yaml


_EVALS = Path(__file__).resolve().parents[2] / "agents" / "evals"
_ROUTER_CASE = "refuse-denied-project-even-when-allowed"


def test_every_guard_fixture_file_parses_and_has_cases():
    for path in sorted((_EVALS / "guard").glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        assert isinstance(data, dict) and data.get("cases"), f"{path.name} has no cases"


def test_router_policy_refusal_status_is_recorded():
    data = yaml.safe_load((_EVALS / "guard" / "router-policy.yaml").read_text())
    matches = [case for case in data["cases"] if case["id"] == _ROUTER_CASE]
    assert len(matches) == 1
    assert matches[0]["expected_router_status"] == 403


def test_router_policy_case_is_not_scored_by_a_model_suite():
    for path in sorted(_EVALS.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        ids = {case.get("id") for case in data.get("cases", [])}
        assert _ROUTER_CASE not in ids, f"{path.name} still scores the router-policy case"
