def build_envelope(status, reason, result):
    return {"status": status, "reason": reason, "result": result}


def schema_problem(value, schema, path="reply"):
    # Check the JSON Schema subset that agent output_schema blocks use. Return None when the value fits, else a reason.
    if "anyOf" in schema:
        if any(schema_problem(value, option, path) is None for option in schema["anyOf"]):
            return None
        return f"{path} matches no allowed shape"
    if "enum" in schema:
        return None if value in schema["enum"] else f"{path} is not an allowed value"
    kind = schema.get("type")
    kinds = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int, "null": type(None)}
    if kind in kinds and type(value) is not kinds[kind]:
        return f"{path} must be {kind}"
    if kind == "object":
        missing = [key for key in schema.get("required", []) if key not in value]
        if missing:
            return f"{path} is missing {', '.join(missing)}"
        properties = schema.get("properties", {})
        extra = [key for key in value if key not in properties]
        if extra and schema.get("additionalProperties") is False:
            return f"{path} has unexpected {', '.join(sorted(extra))}"
        for key, child in properties.items():
            if key in value:
                problem = schema_problem(value[key], child, f"{path}.{key}")
                if problem:
                    return problem
    if kind == "array":
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", len(value)):
            return f"{path} has the wrong number of items"
        for index, item in enumerate(value):
            problem = schema_problem(item, schema.get("items", {}), f"{path}[{index}]")
            if problem:
                return problem
    if kind == "string" and not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", len(value)):
        return f"{path} has the wrong length"
    if kind == "integer" and value < schema.get("minimum", value):
        return f"{path} is below its minimum"
    return None


def check_envelope(raw, schema):
    # Parse one model reply and check it against the agent's {status, reason, result} output schema.
    try:
        reply = json.loads(strip_json_fence(raw))
    except (TypeError, ValueError):
        return None, "model reply is not one JSON object"
    problem = schema_problem(reply, schema)
    if problem:
        return None, problem
    if reply["status"] != "ok" and reply["result"] is not None:
        return None, "reply.result must be null unless status is ok"
    return reply, None
