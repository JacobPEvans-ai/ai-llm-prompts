"""Builds the doc-contradiction finder's start inputs from the pages the finder has read.

Pure: no network and no tokens. The finder's build step calls it. Caps are measured on the exact JSON
strings returned, so each value fits its start variable.
"""

import json

CHANGED_CAP = 60000
RELATED_CAP = 60000
FINGERPRINT_CAP = 8000


def _dump(value):
    return json.dumps(value, ensure_ascii=False)


def _fit(items, cap, dropped):
    # Keep items in order while the serialized list fits. An item that does not fit is recorded and skipped.
    kept = []
    for item in items:
        candidate = kept + [item]
        if len(_dump(candidate)) <= cap:
            kept = candidate
        else:
            dropped.append(item)
    return kept


def _usable(path):
    return isinstance(path, str) and path != "" and ".." not in path.split("/")


def _dirname(path):
    # Matches posixpath.dirname for paths with no empty segment, which the workflow guarantees. Avoids importing posixpath.
    if "/" not in path:
        return ""
    return path.rsplit("/", 1)[0] or "/"


def _index_in(directory):
    return "index.md" if directory == "" else directory.rstrip("/") + "/index.md"


def _nearest_index(page, pages):
    # The nearest index.md in the page's directory or an ancestor. A page that is itself an index is never its own index.
    directory = _dirname(page)
    while True:
        candidate = _index_in(directory)
        if candidate != page and candidate in pages:
            return candidate
        parent = _dirname(directory)
        if parent == directory:
            return None
        directory = parent


def related_paths(changed, pages):
    # Same-directory siblings of each changed page, plus its nearest index.md. Deduped, changed pages excluded, sorted.
    found = set()
    for page in changed:
        directory = _dirname(page)
        found.update(path for path in pages if path != page and _dirname(path) == directory)
        index = _nearest_index(page, pages)
        if index is not None:
            found.add(index)
    return sorted(found - set(changed))


def _fingerprint_list(values, dropped):
    if not isinstance(values, list):
        return []
    unique = []
    for value in values:
        if isinstance(value, str) and value.strip() and value not in unique:
            unique.append(value)
    return _fit(unique, FINGERPRINT_CAP, dropped)


def build_finder_inputs(pr_files, page_texts, fingerprints):
    """Return the three start inputs as JSON strings, plus the paths and fingerprints dropped for size.

    pr_files: file paths the PR changed.
    page_texts: {page_path: text} for every candidate page the fetcher could read.
    fingerprints: open fingerprint strings from the operator's store.
    """
    pages = {}
    if isinstance(page_texts, dict):
        pages = {path: text for path, text in page_texts.items() if _usable(path) and isinstance(text, str)}
    changed_paths = sorted({path for path in pr_files if _usable(path) and path in pages}) if isinstance(pr_files, list) else []

    changed_dropped = []
    changed = _fit([{"page_path": path, "text": pages[path]} for path in changed_paths], CHANGED_CAP, changed_dropped)

    related_dropped = []
    related_items = [{"page_path": path, "text": pages[path]} for path in related_paths(changed_paths, pages)]
    related = _fit(related_items, RELATED_CAP, related_dropped)

    fingerprint_dropped = []
    known = _fingerprint_list(fingerprints, fingerprint_dropped)

    return {
        "changed_pages": _dump(changed),
        "related_pages": _dump(related),
        "known_open_fingerprints": _dump(known),
        "dropped": {
            "changed_pages": [item["page_path"] for item in changed_dropped],
            "related_pages": [item["page_path"] for item in related_dropped],
            "known_open_fingerprints": fingerprint_dropped,
        },
    }
