---
name: code-scout
description: >-
  A cheaper scout agent maps the code that a task needs. Use before work in
  unfamiliar code. Skip when a focused read or a current report is enough.
---

## Goal

Code search fills your context with files that the task does not need.
If no rule fits a case, keep broad code reading with a cheaper scout.

## Rules

- Reuse a scout report that still applies.
- Do not search the code before you start the scout.
- If you cannot start agents, research the code yourself.

## Agents

- Claude Code: `subagent_type: general-purpose`, `model: sonnet`.
- Codex: Luna, `reasoning_effort: medium`, `fork_turns: "none"`. Use the longest `wait_agent` timeout.
- The user's model and effort choices override these settings.
- Send the scout the Scout brief section verbatim, then the task context in English. Do not poll the scout.
- As a Claude Code subagent, start the scout in the foreground. Do not continue it, because its replies do not reach you. For a follow-up, start a new scout with the brief, the task context, the last report, and the question.

## Steps

1. Start one scout. The task context is the absolute repository path, the task, research questions, constraints, and known entry points.
2. Read only the code on the map that you need to implement and check the task.
3. Send follow-up questions to the same scout.

## Scout brief

You are a scout. Your map lets the lead read only the code that the task needs.

### Work

- Read the project instructions.
- Find the code that owns the behavior. Search before you read. Read only the ranges that you need.
- Trace the callers, data model, data flow, contracts, and tests that the task needs.
- Find code that the task can reuse.
- If output is truncated, narrow the search.
- Stop when the lead can start the implementation.

### Limits

Do not edit files, run checks, start agents, or use a browser.

### Report

Return a compact map in English, without search logs. Aim for 500 words or fewer.

1. **Start here**: files and symbols with absolute paths and current line numbers, why each matters, and code to reuse.
2. **Flow**: how these parts connect, and which rules affect the task.
3. **Checks**: relevant tests, commands, and project constraints.
4. **Gaps**: what you could not find or verify, and where you searched. Omit this section if there are none.

Keep facts and inferences separate. Do not propose speculative fixes.
