"use strict";

const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "../../..");

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

// Mirrors strip_json_fence in agents/dify-src/helpers/json_fence.py. Only ASCII spaces, tabs, and line breaks count
// as whitespace, the same set the Python helper trims.
const TRIM_ASCII = /^[ \t\r\n]+|[ \t\r\n]+$/g;

function stripJsonFence(text) {
  const value = String(text);
  const stripped = value.replace(TRIM_ASCII, "");
  if (stripped.length >= 6 && stripped.startsWith("```") && stripped.endsWith("```")) {
    let body = stripped.slice(3, -3).replace(TRIM_ASCII, "");
    if (body.slice(0, 4).toLowerCase() === "json") body = body.slice(4).replace(TRIM_ASCII, "");
    return body;
  }
  return value;
}

function parseOutput(output) {
  try {
    return typeof output === "string" ? JSON.parse(stripJsonFence(output)) : output;
  } catch {
    return null;
  }
}

// A literal `null` is valid JSON, so validity is decided by the parse itself, not by parseOutput's null sentinel.
function jsonValid(output) {
  if (typeof output !== "string") return output !== null && output !== undefined;
  try {
    JSON.parse(stripJsonFence(output));
    return true;
  } catch {
    return false;
  }
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function sourceFromInputDiff(diff, sourcePath) {
  if (typeof diff !== "string") return null;

  const lines = diff.split(/\r?\n/);
  const fileHeader = `diff --git a/${sourcePath} b/${sourcePath}`;
  const start = lines.indexOf(fileHeader);
  if (start < 0) return null;

  const source = [];
  let remaining = 0;
  let sawHunk = false;
  for (const line of lines.slice(start + 1)) {
    if (line.startsWith("diff --git ")) break;
    // The case diff introduced the bug, so the file under test is its post-image: context and added lines.
    const hunk = line.match(/^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@/);
    if (hunk) {
      if (remaining > 0 || Number(hunk[1]) !== source.length + 1) return null;
      remaining = Number(hunk[2] ?? 1);
      sawHunk = true;
      continue;
    }
    if (remaining === 0) continue;
    if (line.startsWith("\\")) continue;
    if (line.startsWith(" ") || line.startsWith("+")) {
      source.push(line.slice(1));
      remaining -= 1;
    } else if (!line.startsWith("-")) {
      return null;
    }
  }

  return sawHunk && remaining === 0 && source.length > 0 ? `${source.join("\n")}\n` : null;
}

function patchBehaviorMatches(actual, context) {
  const check = context.vars.expected.expected_patch_check;
  const input = parseOutput(context.vars.case_data);
  const source = sourceFromInputDiff(input?.input_event_summary?.diff, check?.source_path);
  const patches = actual.patches;
  if (!source || !Array.isArray(patches) || patches.length === 0 || !Array.isArray(check?.test_command) || check.test_command.length === 0) {
    return false;
  }

  if (typeof check.source_path !== "string" || path.isAbsolute(check.source_path) || check.source_path.split(/[\\/]/).includes("..")) {
    return false;
  }
  const testPath = path.resolve(REPO_ROOT, check.test_fixture);
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "promptfoo-patch-check-"));
  try {
    if (!testPath.startsWith(`${REPO_ROOT}${path.sep}`) || !fs.statSync(testPath).isFile()) return false;

    const sourceFile = path.resolve(tempDir, check.source_path);
    if (!sourceFile.startsWith(`${tempDir}${path.sep}`)) return false;
    fs.mkdirSync(path.dirname(sourceFile), { recursive: true });
    fs.writeFileSync(sourceFile, source);
    fs.copyFileSync(testPath, path.join(tempDir, path.basename(testPath)));
    execFileSync("git", ["init", "--quiet"], { cwd: tempDir, timeout: 60000, stdio: "pipe" });
    for (const patch of patches) {
      if (!patch || typeof patch.diff !== "string" || patch.diff.length === 0) return false;
      execFileSync("git", ["apply", "--"], { cwd: tempDir, input: patch.diff, timeout: 60000, stdio: "pipe" });
    }
    execFileSync(check.test_command[0], check.test_command.slice(1), {
      cwd: tempDir,
      timeout: 60000,
      stdio: "pipe",
    });
    return true;
  } catch {
    return false;
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

function expectedOutput(output, context) {
  const actual = parseOutput(output);
  const expectedOutput = context.vars.expected.expected_output;
  const expectedEntries = Object.entries(expectedOutput);
  const mismatches = [];
  for (const [field, expected] of expectedEntries) {
    if (!isObject(actual)) {
      mismatches.push(field);
      continue;
    }
    if (field === "patches" && Array.isArray(expected) && expected.length > 0) {
      if (!patchBehaviorMatches(actual, context)) mismatches.push(field);
      continue;
    }
    if (!field.endsWith("_contains")) {
      if (!same(actual[field], expected)) mismatches.push(field);
      continue;
    }
    const target = field.slice(0, -9);
    const text = String(actual[target] ?? actual.reply ?? "");
    if (!(Array.isArray(expected) ? expected : [expected]).some((keyword) => text.includes(keyword))) {
      mismatches.push(field);
    }
  }
  const pass = mismatches.length === 0;
  // The suite's expected_output_scoring: "strict" scores all-or-nothing, "field-credit" the share of matching keys.
  const score = context.vars.expected.expected_output_scoring === "strict" || expectedEntries.length === 0
    ? Number(pass)
    : (expectedEntries.length - mismatches.length) / expectedEntries.length;
  return {
    pass,
    score,
    reason: mismatches.length ? `Mismatched keys: ${mismatches.join(", ")}` : "All expected keys match.",
  };
}

function notTruncated(output, context) {
  const finishReason = context.providerResponse?.finishReason?.toLowerCase();
  const lengthStop = typeof finishReason === "string"
    && (finishReason === "length" || finishReason === "max_tokens" || finishReason.includes("token_limit"));
  const completeObject = isObject(parseOutput(output));
  const pass = !lengthStop && completeObject;
  return {
    pass,
    score: pass ? 1 : 0,
    reason: lengthStop ? "Provider stopped at the output length limit." : completeObject ? "Complete JSON object." : "Output is not one complete JSON object.",
  };
}

// An expected call with no `args` checks only its tool and operation. One with `args` compares the whole call.
function callMatches(actual, expected) {
  if ("args" in expected) return same(actual, expected);
  return same(actual.tool, expected.tool) && same(actual.operation, expected.operation);
}

function expectedCalls(output, context) {
  const actual = parseOutput(output);
  if (!isObject(actual)) return false;
  const calls = actual.proposed_calls || [];
  const expected = context.vars.expected.expected_calls;
  return Array.isArray(calls) && calls.length === expected.length
    && expected.every((item, index) => isObject(calls[index]) && callMatches(calls[index], item));
}

// Top-level keys that the prompt says never to output. Any present key fails the case.
function forbiddenKeys(output, context) {
  const actual = parseOutput(output);
  if (!isObject(actual)) return { pass: false, score: 0, reason: "Output is not one JSON object." };
  const present = (context.vars.expected.forbidden_keys || []).filter((key) => Object.prototype.hasOwnProperty.call(actual, key));
  return present.length
    ? { pass: false, score: 0, reason: `Forbidden keys present: ${present.join(", ")}` }
    : { pass: true, score: 1, reason: "No forbidden keys." };
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

module.exports = { expectedOutput, expectedCalls, forbiddenKeys, noWrites, expectedFieldsMatch, notTruncated, jsonValid, stripJsonFence };
