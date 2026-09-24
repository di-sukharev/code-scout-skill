---
name: code-scout
description: >-
  Save the primary agent's context during initial codebase discovery.
  Use a scout to find task-relevant entry points and connections.
  Skip when a focused read or current report is enough.
---

## Dispatch

Use the model selected by the user. Otherwise, use Luna in Codex or Sonnet in Claude Code.
Start one fresh scout without the parent conversation history.
In Codex, set `fork_turns: "none"`. In Claude Code, start a new `general-purpose` agent.

Give the scout the absolute repository path, task, research questions, constraints,
and entry points already known. Do not search the code just to prepare the brief.
Include the **Scout research** and **Scout report** instructions in the brief.
Reuse reports that still apply. If delegation is unavailable, research locally.

## Scout research

Read the project instructions. Do not edit files, run tests or builds, or use a browser.
Use `rg`, `rg --files`, and focused reads to find the code that owns the behavior.
Trace the callers, data flow, contracts, and tests needed to understand the task.
If output is truncated, narrow the search. Separate facts, inferences, and unknowns.
Stop when the primary agent has enough information to start implementation.

## Scout report

Return a compact map, without search logs or routine status updates.
Aim for 500 words or fewer. Use more words when essential evidence requires them.

1. **Start here:** link to the relevant files and symbols with absolute paths and
   current line numbers. State why each one matters.
2. **Flow:** explain how these parts connect and which rules affect the task.
3. **Checks:** list relevant tests, commands, and project constraints. Do not run them.
4. **Gaps:** state what you could not verify or find, and where you searched.
   Omit this section if there are no gaps.

Avoid speculative fixes. Mark inferences as inferences.

## Use the report

Use the map to read only the code needed to implement and validate the task.
Repeat broad discovery only if the report is incomplete or stale.
Send focused follow-up questions to the same scout.
