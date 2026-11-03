def strip_json_fence(text):
    # Remove one surrounding Markdown fence (```json or a bare ```) from model output. Other text is returned trimmed.
    stripped = str(text).strip()
    if len(stripped) >= 6 and stripped.startswith("```") and stripped.endswith("```"):
        body = stripped[3:-3].strip()
        if body[:4].lower() == "json":
            body = body[4:].strip()
        return body
    return stripped
