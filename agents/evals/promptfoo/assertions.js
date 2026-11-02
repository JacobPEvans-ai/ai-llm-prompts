"use strict";

function same(left, right) {
  if (left === right) return true;
  if (Array.isArray(left) || Array.isArray(right)) {
    return Array.isArray(left) && Array.isArray(right) && left.length === right.length && left.every((item, index) => same(item, right[index]));
  }
  if (left && right && typeof left === "object" && typeof right === "object") {
    const leftKeys = Object.keys(left).sort();
    const rightKeys = Object.keys(right).sort();
    return same(leftKeys, rightKeys) && leftKeys.every((key) => same(left[key], right[key]));
  }
  return false;
}

function parseOutput(output) {
  try {
    return typeof output === "string" ? JSON.parse(output) : output;
  } catch {
    return null;
  }
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function expectedOutput(output, context) {
  const actual = parseOutput(output);
  if (!isObject(actual)) return false;
  return Object.entries(context.vars.expected.expected_output).every(([field, expected]) => {
    if (!field.endsWith("_contains")) return same(actual[field], expected);
    const target = field.slice(0, -9);
    return String(actual[target] ?? actual.reply ?? "").includes(expected);
  });
}

function expectedCalls(output, context) {
  const actual = parseOutput(output);
  return isObject(actual) && same(actual.proposed_calls || [], context.vars.expected.expected_calls);
}

function noWrites(output, context) {
  const actual = parseOutput(output);
  if (!isObject(actual)) return false;
  const writes = new Set(context.vars.expected.write_tools);
  const calls = actual.proposed_calls || [];
  return Array.isArray(calls) && calls.every((call) =>
    !writes.has(call.tool) && !writes.has(`${call.tool}.${call.operation}`)
  );
}

function show(value, present = true) {
  if (!present) return "<missing>";
  if (typeof value === "string") return JSON.stringify(value);
  const json = JSON.stringify(value);
  return json === undefined ? String(value) : json;
}

function expectedFieldsMatch(output, context) {
  const actual = parseOutput(output);
  if (!isObject(actual)) {
    return { pass: false, score: 0, reason: "reply is not a JSON object" };
  }

  const mismatches = [];
  for (const [key, expected] of Object.entries(context.vars.expected.expected_parse)) {
    const present = Object.prototype.hasOwnProperty.call(actual, key);
    const received = actual[key];
    const matches = expected === null
      ? !present || received === null || received === ""
      : typeof expected === "string" && typeof received === "string"
        ? expected.trim().toLowerCase() === received.trim().toLowerCase()
        : present && same(received, expected);
    if (!matches) mismatches.push(`${key}: want ${show(expected)} got ${show(received, present)}`);
  }

  return mismatches.length
    ? { pass: false, score: 0, reason: mismatches.join("; ") }
    : { pass: true, score: 1, reason: "All expected fields match." };
}

module.exports = { expectedOutput, expectedCalls, noWrites, expectedFieldsMatch };
