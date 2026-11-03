"""The finder's findings validator fails closed and forces dedupe, on the rendered Dify node."""

import json
from pathlib import Path

import yaml


_ROOT = Path(__file__).resolve().parents[2]
_DSL = _ROOT / "agents" / "dify" / "doc-contradiction-finder.dsl.yml"
_TITLE = "Validate contradiction findings"
_PAGES = json.dumps(["/services/import.md", "/services/requirements.md"])
_FINGERPRINT = "app-dsl-version:/services/import.md:/services/requirements.md"
_FINDING = {
    "severity": "S2",
    "fingerprint": _FINGERPRINT,
    "statements": [
        {"page_path": "/services/import.md", "line": 2, "quote": "The import uses App DSL 0.7.0."},
        {"page_path": "/services/requirements.md", "line": 2, "quote": "App DSL 0.6.0 is required."},
    ],
    "question": "Which is right? A: the import uses 0.7.0 B: 0.6.0 is required Neither: take no action.",
    "ask": True,
}


def _main():
    nodes = yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["nodes"]
    codes = [node["data"]["code"] for node in nodes if node.get("data", {}).get("title") == _TITLE]
    assert len(codes) == 1, f"expected one node titled {_TITLE!r}"
    namespace = {}
    exec(compile(codes[0], _TITLE, "exec"), namespace)  # defines the node's functions only
    return namespace["main"]


def _model(*findings, **extra):
    return json.dumps({"findings": list(findings), **extra})


def _findings(output):
    return json.loads(output["findings_json"])["findings"]


def test_valid_proposal_passes_and_zero_findings_is_the_exact_empty_object():
    main = _main()
    result = main(_model(_FINDING), _PAGES, "[]")
    assert [(f["severity"], f["ask"]) for f in _findings(result)] == [("S2", True)]
    assert main('{"findings": []}', _PAGES, "[]") == {"findings_json": '{"findings": []}'}


def test_private_ip_address_in_a_quote_is_rejected():
    main = _main()
    finding = json.loads(json.dumps(_FINDING))
    finding["statements"][0]["quote"] = "The import runs on 192.0.2.10."
    assert main(_model(finding), _PAGES, "[]") == {"findings_json": ""}


def test_unknown_top_level_key_fails_closed():
    main = _main()
    assert main(_model(_FINDING, decision="write"), _PAGES, "[]") == {"findings_json": ""}


def test_unknown_finding_key_fails_closed():
    main = _main()
    assert main(_model({**_FINDING, "proposed_calls": []}), _PAGES, "[]") == {"findings_json": ""}


def test_statement_on_an_unsupplied_page_fails_closed():
    main = _main()
    finding = json.loads(json.dumps(_FINDING))
    finding["statements"][1]["page_path"] = "/services/other.md"
    assert main(_model(finding), _PAGES, "[]") == {"findings_json": ""}


def test_secret_shaped_quote_fails_closed():
    main = _main()
    finding = json.loads(json.dumps(_FINDING))
    finding["statements"][0]["quote"] = "token = <TOKEN>".replace("<TOKEN>", "A" * 24)
    assert main(_model(finding), _PAGES, "[]") == {"findings_json": ""}


def test_duplicate_fingerprint_forces_ask_false_even_when_the_model_asks():
    main = _main()
    fresh = _findings(main(_model(_FINDING), _PAGES, "[]"))
    duplicate = _findings(main(_model(_FINDING), _PAGES, json.dumps([_FINGERPRINT])))
    assert fresh[0]["ask"] is True
    assert duplicate[0]["ask"] is False
    assert duplicate[0]["fingerprint"] == _FINGERPRINT
