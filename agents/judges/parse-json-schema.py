"""Deterministic check for one Vikunja intake parse reply.

The reply must be one JSON object. Its keys must come from the allowed set.
Each value must have the type the parse prompt asks for. No project_id key is allowed.
"""

import json
from dataclasses import dataclass, field
from typing import Any

# Contract shapes, as the Langfuse code evaluator runtime documents them.


@dataclass
class ToolCall:
    id: str = ""
    name: str = ""
    arguments: Any = None
    type: str = ""
    index: int = 0


@dataclass
class ObservationContext:
    input: Any = None
    output: Any = None
    metadata: Any = None
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class ExperimentContext:
    item_expected_output: Any = None
    item_metadata: Any = None


@dataclass
class EvaluationContext:
    observation: ObservationContext
    experiment: ExperimentContext | None = None


@dataclass
class Score:
    name: str
    value: int | float | str | bool
    data_type: str
    comment: str | None = None
    config_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class EvaluationResult:
    scores: list[Score]


SCORE_NAME = "parse-json-schema-valid"
ALLOWED_KEYS = {
    "route",
    "operation",
    "project_named",
    "task_id",
    "title",
    "description",
    "due_date",
    "priority",
    "done",
    "filter",
    "search",
    "category",
}
ROUTES = {"vikunja", "zammad"}
TEXT_OR_NULL = {"operation", "task_id", "title", "description", "due_date", "filter", "search", "category"}


def strip_json_fence(text: str) -> str:
    """Mirror of strip_json_fence in agents/dify-src/helpers/json_fence.py.

    The hosted evaluator cannot import repository files. agents/judges/test_json_fence.py keeps the two in step.
    """
    stripped = str(text).strip()
    if len(stripped) >= 6 and stripped.startswith("```") and stripped.endswith("```"):
        body = stripped[3:-3].strip()
        if body[:4].lower() == "json":
            body = body[4:].strip()
        return body
    return stripped


def check_reply(value: Any) -> str | None:
    """Return the first problem found, or None when the reply is valid."""
    if isinstance(value, str):
        try:
            value = json.loads(strip_json_fence(value))
        except json.JSONDecodeError:
            return "reply is not JSON"
    if not isinstance(value, dict):
        return "reply is not a JSON object"
    if "project_id" in value:
        return "project_id must not appear"
    extra = set(value) - ALLOWED_KEYS
    if extra:
        return f"unexpected keys: {sorted(extra)}"
    if "route" in value and value["route"] not in ROUTES:
        return "route must be vikunja or zammad"
    for key in TEXT_OR_NULL & set(value):
        if value[key] is not None and not isinstance(value[key], str):
            return f"{key} must be a string or null"
    if "project_named" in value and value["project_named"] is not None and not isinstance(value["project_named"], bool):
        return "project_named must be a boolean or null"
    if "done" in value and value["done"] is not None and not isinstance(value["done"], bool):
        return "done must be a boolean or null"
    priority = value.get("priority")
    if priority is not None and (isinstance(priority, bool) or not isinstance(priority, (int, float))):
        return "priority must be a number or null"
    return None


def evaluate(ctx: EvaluationContext) -> EvaluationResult:
    problem = check_reply(ctx.observation.output)
    valid = problem is None
    return EvaluationResult(
        scores=[
            Score(
                name=SCORE_NAME,
                value=valid,
                data_type="BOOLEAN",
                comment="Reply matches the parse schema." if valid else problem,
            )
        ]
    )
