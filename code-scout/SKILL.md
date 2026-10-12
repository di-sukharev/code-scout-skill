---
name: code-scout
description: >-
  A cheaper scout maps the code a task needs to save tokens for a more capable
  lead model. Use before broad research in unfamiliar code. Skip when a
  focused read or a current report is enough.
---

Use a scout to find the code a task needs and keep search results out of the lead's context.
Reuse a report that still applies. Skip delegation when a focused read is enough.
Follow project rules. Use English with the scout and the user's language with the user.

## Search

Start one subagent without chat history. Choose a low-cost model and enough effort for the task. Follow the user's model and effort choices.
Give it the absolute repository path, task, questions, constraints, known entry points, and scout brief below.
If agents are unavailable, search the code yourself.

Use the map to read the code needed to implement and check the task. Ask the same scout to resolve gaps.

## Scout brief

Find the code that owns the requested behavior. Read project instructions first.
Search before reading files. Read relevant ranges. Narrow searches when results are truncated.
Trace the callers, data flow, data model, contracts, and tests needed for the task. Find existing code to reuse.
Stop when the lead has enough information to start implementation.
Do not edit files, run checks, start agents, or use a browser.

Return a compact map in English. Give absolute paths, symbols, current line numbers, and each location's purpose.
Explain how the relevant parts connect and which project rules apply.
Name code to reuse, relevant tests, and check commands.
Report gaps and where you searched. Separate facts from inferences. Do not suggest fixes without evidence or include search logs.
