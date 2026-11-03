"""The finder's findings validator fails closed, verifies quotes, and forces dedupe, on the rendered Dify node."""

import json
from pathlib import Path

import yaml


_ROOT = Path(__file__).resolve().parents[2]
_DSL = _ROOT / "agents" / "dify" / "doc-contradiction-finder.dsl.yml"
_TITLE = "Validate contradiction findings"
_TEXTS = {
    "/services/import.md": "# Import\nThe import uses App DSL 0.7.0.",
    "/services/requirements.md": "# Requirements\nApp DSL 0.6.0 is required.",
}
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


def _load_main():
    nodes = yaml.safe_load(_DSL.read_text())["workflow"]["graph"]["nodes"]
    codes = [node["data"]["code"] for node in nodes if node.get("data", {}).get("title") == _TITLE]
    assert len(codes) == 1, f"expected one node titled {_TITLE!r}"
    namespace = {}
    exec(compile(codes[0], _TITLE, "exec"), namespace)  # defines the node's functions only
    return namespace["main"]


_MAIN = _load_main()


def _run(model, known="[]", texts=None):
    texts = _TEXTS if texts is None else texts
    return _MAIN(model, json.dumps(sorted(texts)), known, json.dumps(texts))


def _model(*findings, **extra):
    return json.dumps({"findings": list(findings), **extra})


def _finding_with_quote(index, quote):
    finding = json.loads(json.dumps(_FINDING))
    finding["statements"][index]["quote"] = quote
    return finding


def _findings(output):
    return json.loads(output["findings_json"])["findings"]


def test_valid_proposal_passes_and_zero_findings_is_the_exact_empty_object():
    assert [(f["severity"], f["ask"]) for f in _findings(_run(_model(_FINDING)))] == [("S2", True)]
    assert _run('{"findings": []}') == {"findings_json": '{"findings": []}'}


def test_quote_present_in_the_cited_page_passes_despite_whitespace_differences():
    finding = _finding_with_quote(0, "The import  uses\nApp DSL 0.7.0.")
    assert len(_findings(_run(_model(finding)))) == 1


def test_quote_absent_from_the_cited_page_drops_only_that_finding():
    bad = _finding_with_quote(0, "The import uses App DSL 9.9.9.")
    assert _findings(_run(_model(bad))) == []
    survivors = _findings(_run(_model(bad, _FINDING)))
    assert [f["fingerprint"] for f in survivors] == [_FINGERPRINT]


def test_quote_must_appear_in_the_page_it_cites_not_in_another_page():
    wrong_page = _finding_with_quote(0, "App DSL 0.6.0 is required.")
    assert _findings(_run(_model(wrong_page))) == []


def test_redacted_quote_verifies_against_unredacted_page_text():
    # The page still holds the raw value; the quote holds the redacted form that the prompt asks for.
    quote = "The import uses App DSL 0.7.0 with token = [REDACTED] for CI."
    page = "# Import\nThe import uses App DSL 0.7.0 with token = " + "A" * 24 + " for CI."
    texts = {**_TEXTS, "/services/import.md": page}
    kept = _findings(_run(_model(_finding_with_quote(0, quote)), texts=texts))
    assert [f["statements"][0]["quote"] for f in kept] == [quote]


def test_quote_that_needed_redaction_is_a_security_finding_and_is_never_asked():
    secret_quote = "The import uses App DSL 0.7.0 with token = " + "A" * 24 + " for CI."
    address_quote = "The import runs on 192.0.2.10."
    ipv6_colon_quote = "Peer 2001:db8::1: is down."
    ipv6_double_colon_quote = "Gateway 2001:db8::: is down."
    ipv6_leading_colon_quote = "Peer:2001:db8::7 is down."
    ipv6_glued_quote = "Peer ab2001:db8::9 is down."
    cctld_host_quote = "Backups go to backup.example.md nightly."
    quotes = (
        secret_quote,
        address_quote,
        ipv6_colon_quote,
        ipv6_double_colon_quote,
        ipv6_leading_colon_quote,
        ipv6_glued_quote,
        cctld_host_quote,
    )
    texts = {**_TEXTS, "/services/import.md": "# Import\n" + "\n".join(quotes)}
    assert _findings(_run(_model(_FINDING)))[0]["security"] is False
    for quote in quotes:
        (finding,) = _findings(_run(_model(_finding_with_quote(0, quote)), texts=texts))
        assert finding["security"] is True
        assert finding["ask"] is False
        assert "[REDACTED]" in finding["statements"][0]["quote"]
        serialized = json.dumps(finding)
        for raw in ("A" * 24, "192.0.2.10", "2001:db8:", "backup.example.md"):
            assert raw not in serialized


def test_two_label_file_name_is_not_a_hostname():
    quote = "The import is described in README.md."
    texts = {**_TEXTS, "/services/import.md": "# Import\n" + quote}
    (finding,) = _findings(_run(_model(_finding_with_quote(0, quote)), texts=texts))
    assert finding["security"] is False and finding["statements"][0]["quote"] == quote


def test_unknown_top_level_key_fails_closed():
    assert _run(_model(_FINDING, decision="write")) == {"findings_json": ""}


def test_unknown_finding_key_fails_closed():
    assert _run(_model({**_FINDING, "proposed_calls": []})) == {"findings_json": ""}


def test_statement_on_an_unsupplied_page_fails_closed():
    finding = json.loads(json.dumps(_FINDING))
    finding["statements"][1]["page_path"] = "/services/other.md"
    assert _run(_model(finding)) == {"findings_json": ""}


def test_duplicate_fingerprint_forces_ask_false_even_when_the_model_asks():
    fresh = _findings(_run(_model(_FINDING)))
    duplicate = _findings(_run(_model(_FINDING), known=json.dumps([_FINGERPRINT])))
    assert fresh[0]["ask"] is True
    assert duplicate[0]["ask"] is False
    assert duplicate[0]["fingerprint"] == _FINGERPRINT
