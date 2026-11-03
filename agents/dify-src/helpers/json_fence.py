def strip_json_fence(text):
    # Remove one surrounding Markdown fence (```json or a bare ```) from model output. Only ASCII spaces, tabs, and
    # line breaks count as whitespace, so the JavaScript mirror trims the same characters. Text without a surrounding
    # fence is returned unchanged.
    value = str(text)
    stripped = value.strip(" \t\r\n")
    if len(stripped) >= 6 and stripped.startswith("```") and stripped.endswith("```"):
        body = stripped[3:-3].strip(" \t\r\n")
        if body[:4].lower() == "json":
            body = body[4:].strip(" \t\r\n")
        return body
    return value
