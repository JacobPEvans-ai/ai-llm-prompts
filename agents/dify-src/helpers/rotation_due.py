"""Select two-minute rotation windows from UTC epoch minutes, without I/O or state."""

import json
import math


def rotation_due(now, agents, ROTATION_SPEED=1.0, ROTATION_OFFSET=0, ROTATION_PAUSED=False):
    speed = float(ROTATION_SPEED)
    shift = float(ROTATION_OFFSET)
    now = float(now)
    if not all(math.isfinite(value) for value in (now, speed, shift)) or speed <= 0:
        raise ValueError("rotation time and offset must be finite; speed must be positive")
    if str(ROTATION_PAUSED).lower() not in {"true", "false"}:
        raise ValueError("ROTATION_PAUSED must be true or false")
    paused = str(ROTATION_PAUSED).lower() == "true"
    due, skipped = [], []
    for agent in agents:
        period = round(agent["every_minutes"] * speed)
        if period < 2:
            raise ValueError("scaled rotation interval must be at least two minutes")
        target = due if not paused and (now + shift - agent["offset_minutes"]) % period < 2 else skipped
        target.append(agent["name"])
    return {
        "due": due,
        "skipped": skipped,
        "log": json.dumps({
            "due": due, "skipped": skipped,
            "ROTATION_SPEED": speed, "ROTATION_OFFSET": shift, "ROTATION_PAUSED": paused,
        }, separators=(",", ":")),
    }
