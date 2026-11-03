"""Tests for the pure helper that builds the doc-contradiction finder's start inputs."""

import importlib.util
import json
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("finder_inputs", _ROOT / "agents" / "dify-src" / "helpers" / "finder_inputs.py")
finder_inputs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(finder_inputs)
build = finder_inputs.build_finder_inputs


def _paths(json_text):
    return [item["page_path"] for item in json.loads(json_text)]


def test_changed_pages_are_the_pr_files_that_are_pages_in_sorted_order():
    pages = {"/policy/merge.md": "merge", "/policy/roles.md": "roles", "/other/x.md": "x"}

    result = build(["/policy/roles.md", "/policy/merge.md", "README.md"], pages, [])

    assert _paths(result["changed_pages"]) == ["/policy/merge.md", "/policy/roles.md"]
    assert json.loads(result["changed_pages"])[0] == {"page_path": "/policy/merge.md", "text": "merge"}


def test_related_pages_are_siblings_and_nearest_index_deduped_and_exclude_changed():
    pages = {
        "/policy/merge.md": "merge",
        "/policy/roles.md": "roles",
        "/policy/index.md": "policy index",
        "/services/a.md": "service",
        "/index.md": "root index",
    }

    result = build(["/policy/merge.md"], pages, [])

    assert _paths(result["related_pages"]) == ["/policy/index.md", "/policy/roles.md"]


def test_nearest_index_walks_up_when_the_directory_has_none():
    pages = {"/services/deep/page.md": "page", "/services/index.md": "services index", "/index.md": "root index"}

    result = build(["/services/deep/page.md"], pages, [])

    assert _paths(result["related_pages"]) == ["/services/index.md"]


def test_an_index_page_is_not_its_own_nearest_index():
    pages = {"/policy/index.md": "policy index", "/index.md": "root index"}

    result = build(["/policy/index.md"], pages, [])

    assert _paths(result["related_pages"]) == ["/index.md"]


def test_changed_pages_over_the_cap_are_dropped_and_listed():
    pages = {"/a/big.md": "x" * 61000, "/a/small.md": "y"}

    result = build(["/a/big.md", "/a/small.md"], pages, [])

    assert _paths(result["changed_pages"]) == ["/a/small.md"]
    assert result["dropped"]["changed_pages"] == ["/a/big.md"]
    assert len(result["changed_pages"]) <= finder_inputs.CHANGED_CAP


def test_related_pages_over_the_cap_are_dropped_and_listed():
    pages = {"/a/c.md": "changed", "/a/big.md": "x" * 61000}

    result = build(["/a/c.md"], pages, [])

    assert result["related_pages"] == "[]"
    assert result["dropped"]["related_pages"] == ["/a/big.md"]


def test_fingerprints_are_deduped_non_strings_skipped_and_capped():
    tail = [f"topic-{index:03d}:/p/{index}.md" for index in range(400)]
    fingerprints = ["merge-rules:/a.md:/b.md", "merge-rules:/a.md:/b.md", None, "", 3] + tail

    result = build([], {}, fingerprints)
    kept = json.loads(result["known_open_fingerprints"])

    assert kept[0] == "merge-rules:/a.md:/b.md"
    assert kept.count("merge-rules:/a.md:/b.md") == 1
    assert len(result["known_open_fingerprints"]) <= finder_inputs.FINGERPRINT_CAP
    assert result["dropped"]["known_open_fingerprints"]
    # kept is the first fingerprint followed by tail[0 : len(kept) - 1], so the first dropped one is tail[len(kept) - 1].
    assert result["dropped"]["known_open_fingerprints"][0] == tail[len(kept) - 1]


def test_empty_inputs_return_empty_arrays():
    result = build([], {}, [])

    assert result["changed_pages"] == "[]"
    assert result["related_pages"] == "[]"
    assert result["known_open_fingerprints"] == "[]"
    assert result["dropped"] == {"changed_pages": [], "related_pages": [], "known_open_fingerprints": []}


def test_unsafe_paths_are_not_candidate_pages():
    pages = {"../escape.md": "escape", "/a/../b.md": "traversal", "/a/ok.md": "ok"}

    result = build(["../escape.md", "/a/../b.md", "/a/ok.md"], pages, [])

    assert _paths(result["changed_pages"]) == ["/a/ok.md"]


def test_a_dropped_changed_page_is_not_listed_as_related():
    pages = {"/a/x.md": "x" * 40000, "/a/y.md": "y" * 30000}

    result = build(["/a/x.md", "/a/y.md"], pages, [])

    assert _paths(result["changed_pages"]) == ["/a/x.md"]
    assert result["dropped"]["changed_pages"] == ["/a/y.md"]
    assert result["related_pages"] == "[]"


def test_string_path_helpers_match_posixpath_for_paths_the_workflow_admits():
    import posixpath

    for path in ["a.md", "docs/a.md", "/docs/a.md", "/index.md", "docs/guide/a.md", "docs/index.md"]:
        assert finder_inputs._dirname(path) == posixpath.dirname(path), path
    for directory in ["", "/", "/docs", "docs", "docs/guide"]:
        assert finder_inputs._index_in(directory) == posixpath.join(directory, "index.md"), directory


def test_a_double_slash_path_terminates():
    result = build(["//x.md"], {"//x.md": "t"}, [])

    assert _paths(result["changed_pages"]) == ["//x.md"]
    assert result["related_pages"] == "[]"


def test_non_list_and_non_dict_inputs_are_ignored():
    result = build(None, None, None)

    assert result["changed_pages"] == "[]"
    assert result["related_pages"] == "[]"
    assert result["known_open_fingerprints"] == "[]"
