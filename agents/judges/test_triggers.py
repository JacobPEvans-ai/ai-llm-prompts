"""Rotation intervals and daily UTC anchors replace source cron schedules."""

import re

import pytest


def validate_triggers(agent):
    def no_raw_schedule(value):
        if isinstance(value, dict):
            assert not {"cron", "cadence"}.intersection(value), "renderer owns schedules"
            if "cron_expression" in value:
                assert value["cron_expression"] == "__DIFY_TRIGGER_CRON__", "renderer owns schedules"
            for child in value.values():
                no_raw_schedule(child)
        elif isinstance(value, list):
            for child in value:
                no_raw_schedule(child)

    no_raw_schedule(agent)
    triggers = agent.get("triggers")
    assert isinstance(triggers, list) and triggers, "triggers must be a non-empty list"
    for trigger in triggers:
        assert isinstance(trigger, dict), "trigger must be a mapping"
        kind = trigger.get("kind")
        assert kind in ("rotation", "anchor", "event", "call"), "invalid trigger kind"
        if kind == "rotation":
            assert isinstance(trigger.get("every"), str) and re.fullmatch(r"[1-9]\d*[mhd]", trigger["every"]), "invalid every"
            assert "at" not in trigger and "days" not in trigger, "anchor-only fields"
        elif kind == "anchor":
            at = trigger.get("at")
            assert isinstance(at, str) and re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", at), "invalid UTC time"
            minute = int(at[3:])
            assert minute % 2 == 1 and minute not in (15, 45), "anchor minute must be odd and non-quarter"
            assert "every" not in trigger, "every is rotation-only"
            if "days" in trigger:
                days = trigger["days"]
                assert isinstance(days, list) and days and all(day in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun") for day in days) and len(days) == len(set(days)), "invalid anchor days"
        else:
            assert isinstance(trigger.get("source"), str) and trigger["source"].strip(), "trigger source required"
            assert "at" not in trigger and "every" not in trigger and "days" not in trigger, "unexpected timing field"
    assert sum(t["kind"] == "anchor" for t in triggers) <= 1, "one daily anchor per agent"


@pytest.mark.parametrize("trigger", [
    {"kind": "rotation", "every": "1d"}, {"kind": "rotation", "every": "12h"},
    {"kind": "rotation", "every": "10m"}, {"kind": "anchor", "at": "06:07"},
    {"kind": "anchor", "at": "23:59"}, {"kind": "event", "source": "vikunja"},
    {"kind": "call", "source": "caller"},
])
def test_valid_triggers(trigger):
    validate_triggers({"triggers": [trigger]})


@pytest.mark.parametrize("every", [None, "", "0m", "-1h", "1.5d", "1w", "01d", 1, True])
def test_invalid_rotation_intervals(every):
    with pytest.raises(AssertionError, match="invalid every"):
        validate_triggers({"triggers": [{"kind": "rotation", "every": every}]})


@pytest.mark.parametrize("at", [None, "", "6:07", "24:07", "06:60", "06:00", "06:15", "06:30", "06:45", "06:08", "06:07Z", 607])
def test_invalid_anchor_times(at):
    with pytest.raises(AssertionError):
        validate_triggers({"triggers": [{"kind": "anchor", "at": at}]})


@pytest.mark.parametrize("trigger", [
    {"kind": "schedule", "source": "dify"}, {"kind": "webhook", "source": "dify"},
    {"kind": "event"}, {"kind": "event", "source": " "}, {"kind": "call", "source": 1},
    {"kind": "call", "source": "caller", "every": "1d"},
    {"kind": "rotation", "every": "1d", "at": "06:07"},
    {"kind": "anchor", "at": "06:07", "every": "1d"},
])
def test_invalid_trigger_shapes(trigger):
    with pytest.raises(AssertionError):
        validate_triggers({"triggers": [trigger]})


@pytest.mark.parametrize("field", ["cron", "cadence", "cron_expression"])
@pytest.mark.parametrize("nested", [False, True])
def test_raw_schedules_are_rejected_even_in_graphs(field, nested):
    value = {field: "7 * * * *"}
    agent = {"triggers": [{"kind": "call", "source": "caller"}]}
    agent.update(dify={"nodes": [value]} if nested else value)
    with pytest.raises(AssertionError, match="renderer owns schedules"):
        validate_triggers(agent)


def test_event_and_rotation_catchup():
    validate_triggers({"triggers": [{"kind": "event", "source": "vikunja"}, {"kind": "rotation", "every": "1d"}]})


def test_two_anchors_are_rejected():
    with pytest.raises(AssertionError, match="one daily anchor"):
        validate_triggers({"triggers": [{"kind": "anchor", "at": "06:07"}, {"kind": "anchor", "at": "18:17"}]})
