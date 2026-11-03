"""Tests for parse-json-schema.py. Run: uv run --with pytest pytest agents/judges"""

import importlib.util
from pathlib import Path

import pytest
import yaml

_SOURCE = Path(__file__).with_name("parse-json-schema.py")
_spec = importlib.util.spec_from_file_location("parse_json_schema", _SOURCE)
schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(schema)


@pytest.mark.parametrize(
    "reply",
    [
        '{"route": "vikunja", "operation": "list", "project_named": false, "done": false}',
        '{"route": "vikunja", "operation": "create", "project_named": true, "title": "Update the guide", "priority": 2}',
        '{"route": "zammad", "operation": null, "category": "security-finding"}',
        {"route": "vikunja", "operation": "delete", "task_id": "task-example-a"},
    ],
)
def test_valid_replies_pass(reply):
    assert schema.check_reply(reply) is None


@pytest.mark.parametrize(
    "reply, problem",
    [
        ("not json", "reply is not JSON"),
        ("[1, 2]", "reply is not a JSON object"),
        ('{"route": "vikunja", "bogus": 1}', "unexpected keys"),
        ('{"route": "vikunja", "project_id": "101"}', "project_id must not appear"),
        ('{"route": "slack"}', "route must be vikunja or zammad"),
        ('{"route": "vikunja", "title": 7}', "title must be a string or null"),
        (
            '{"route": "vikunja", "project_named": "yes"}',
            "project_named must be a boolean or null",
        ),
        ('{"route": "vikunja", "done": 1}', "done must be a boolean or null"),
        ('{"route": "vikunja", "priority": true}', "priority must be a number or null"),
    ],
)
def test_invalid_replies_name_the_problem(reply, problem):
    assert problem in schema.check_reply(reply)


def test_evaluate_returns_one_boolean_score():
    ctx = schema.EvaluationContext(
        observation=schema.ObservationContext(output='{"route": "vikunja"}')
    )
    result = schema.evaluate(ctx)
    assert len(result.scores) == 1
    assert result.scores[0].name == "parse-json-schema-valid"
    assert result.scores[0].value is True
    assert result.scores[0].data_type == "BOOLEAN"


def test_vikunja_expected_parse_fields_are_allowed_by_parse_schema():
    eval_set = Path(__file__).parents[1] / "evals" / "vikunja-clerk.yaml"
    cases = yaml.safe_load(eval_set.read_text(encoding="utf-8"))["cases"]
    unexpected = {
        key
        for case in cases
        for key in case.get("expected_parse", {})
        if key not in schema.ALLOWED_KEYS
    }

    assert not unexpected
