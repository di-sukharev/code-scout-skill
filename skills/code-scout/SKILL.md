---
name: code-scout
description: Map the minimal evidence-backed implementation, coupling, test, and repository-constraint surface for a non-trivial code task by delegating one fresh repository scout instructed to remain read-only to gpt-5.6-terra. Use when explicitly invoked with `$code-scout`, or before implementing, debugging, reviewing, or planning a cross-file or cross-layer change whose owning files, symbols, entry points, or closest tests are not already known. Skip for documentation-only work, exact file-and-symbol edits, obvious local copy or style changes, tasks that need no repository search, repeated discovery for an unchanged task scope, or when the user forbids delegation.
---

# Code Scout

## Purpose

Run one bounded discovery pass before the primary agent designs or edits a
non-trivial code change. Keep repository-search noise out of the primary
conversation by returning a small, verifiable evidence map instead of a search
transcript.

Keep ownership with the primary agent. The scout identifies likely owners,
couplings, tests, flows, and constraints; it does not choose the fix, edit files,
or replace local verification of its result.

## Apply the Eligibility Gate

Run the scout only when all of these are true:

- The task requires repository discovery.
- The work is non-trivial or crosses files, modules, layers, contracts, or tests.
- The owning files, entry points, important symbols, or closest tests are not
  already sufficiently explicit.
- A fresh sub-agent can be started without inheriting the parent conversation.

Skip the scout when any of these are true:

- The task is documentation-only.
- The requested edit already names the exact file and symbol and nearby
  inspection is enough.
- The change is an obvious local copy, style, or similarly bounded edit.
- The user asks only for an answer that needs no code search.
- The user forbids delegation.
- This skill already produced a verified map for the same stable task scope and
  repository state.
- The repository or fresh-agent capability is unavailable.

An explicit `$code-scout` invocation overrides the ordinary cost/benefit
heuristic, but not a user prohibition, missing capability, or safety constraint.
Run exactly one scout at a time. Do not turn discovery into a review loop.

## Prepare the Scout

1. Normalize the task into one implementation goal and one observable primary
   signal.
2. Resolve the absolute Git repository root.
3. Identify only the repository guidance the scout needs to read, such as
   `AGENTS.md`, a root `README.md`, `CONTRIBUTING.md`, and directly relevant
   architecture documents. Pass filenames and task constraints, not summaries of
   the expected answer.
4. Resolve `scripts/repository_fingerprint.py` relative to this `SKILL.md`.
5. Run the fingerprint script against the repository before spawning:

   ```bash
   python3 <skill-dir>/scripts/repository_fingerprint.py <repository-root>
   ```

   Preserve its `head` and `worktree_sha256` values for the result check. The
   script hashes tracked changes plus non-ignored untracked file contents without
   printing file contents. If it cannot safely fingerprint the repository within
   its bounds, report that briefly and use narrow local discovery instead.

Do not pass parent reasoning, hypotheses, prior search output, expected owners,
or a desired implementation. The scout must reconstruct the map from repository
evidence.

## Start One Fresh Terra Scout

Use the platform's fresh sub-agent mechanism with:

- model: exact `gpt-5.6-terra`;
- conversation inheritance: none (`fork_turns: "none"` when that field exists);
- one self-contained prompt;
- explicit read-only instructions and, when supported, a read-only sandbox;
- no nested delegation.

Ordinary sub-agents inherit the primary agent's sandbox and permissions. Treat
the prompt constraint as required behavior, not a security boundary. When the
current surface supports a custom agent configured with
`sandbox_mode = "read-only"`, prefer it without adding conversation history.
The fingerprint detects stale repository state; it does not prevent temporary
writes or external side effects.

Use a prompt with this content, adapted only for the current task:

```text
You are the single read-only code scout for this task.

Repository root: <absolute-root>
Task: <normalized implementation goal>
Primary signal: <observable proof>
Repository guidance to read: <filenames>
Task and repository constraints: <concise constraints>
Fingerprint command:
python3 <absolute-skill-dir>/scripts/repository_fingerprint.py <absolute-root>

Search the repository directly with rg/rg --files and focused reads. Read the
listed guidance before mapping code. Find the minimal evidence-backed
implementation owners, coupled contracts or consumers, closest tests, important
flow, and constraints needed by the primary agent.

Stay read-only. Do not edit, format, stage, commit, reset, stash, clean, or push.
Do not implement the task. Do not spawn or delegate to another agent, and do not
invoke code-scout recursively. Work silently.

Run the fingerprint command immediately before producing the result. Return
exactly one JSON object conforming to code-scout.v1. Return no commentary,
Markdown, code fences, prose preamble, snippets, chain of thought, or search
transcript.

<insert the complete code-scout.v1 contract and invariants from the calling skill>
```

If `gpt-5.6-terra` is unavailable, say so briefly and perform the narrowest safe
local discovery. Do not silently substitute another model.

## Require the `code-scout.v1` Contract

Require every top-level field and no additional top-level fields:

```json
{
  "schema_version": "code-scout.v1",
  "status": "ready",
  "repository_state": {
    "head": "40- or 64-character lowercase Git commit SHA, or unborn",
    "worktree_sha256": "64-character lowercase SHA-256"
  },
  "task_summary": "One-sentence normalized implementation goal",
  "primary_signal": "Observable behavior that should prove the task",
  "targets": [
    {
      "path": "src/repository-relative-file.ts",
      "lines": [10, 42],
      "symbols": ["owningSymbol"],
      "kind": "implementation",
      "role": "owner",
      "reason": "Concrete repository evidence for this exact target"
    }
  ],
  "flow": [
    {
      "from": "src/entry.ts:entrySymbol",
      "to": "src/owner.ts:owningSymbol",
      "relation": "dispatches"
    }
  ],
  "open_questions": []
}
```

Apply these invariants:

- `schema_version` is exactly `code-scout.v1`.
- `status` is exactly `ready`, `not_found`, or `needs_clarification`.
- `repository_state` is the scout's final fingerprint output.
- `repository_state.head` is `unborn` or a lowercase 40- or 64-character Git
  object ID.
- `task_summary` and `primary_signal` are non-empty single sentences.
- `targets` contains no more than 16 entries.
- Each target contains exactly `path`, `lines`, `symbols`, `kind`, `role`, and
  `reason`.
- `kind` is exactly `implementation`, `coupled`, `test`, or `constraint`.
- `role` is a concise lowercase role token such as `owner`, `entrypoint`,
  `caller`, `consumer`, `contract`, `validator`, `serializer`, `renderer`,
  `persistence`, `test`, or `constraint`.
- `path` is repository-relative, exists inside the repository, contains neither
  `..` nor an absolute prefix, and does not point into generated output, vendored
  dependencies, coverage, logs, or test artifacts.
- `lines` is an inclusive pair of positive integers with start less than or equal
  to end. Keep ranges current and tight.
- `symbols` is a non-empty array. Cite declared symbol names when available. For
  anonymous `test` or `describe` callbacks, cite the exact test or suite title,
  not the generic identifier `test` or `describe`. Use `"<file>"` only for a
  genuine file-level constraint; headings, JSON keys, and CSS selectors count as
  symbols.
- `reason` identifies concrete evidence and coupling, not speculation.
- `flow` contains no more than eight entries. Every entry contains exactly
  `from`, `to`, and `relation`; endpoints use `path:symbol`, and `relation` is a
  concise lowercase verb such as `calls`, `imports`, `dispatches`, `validates`,
  `serializes`, `renders`, `persists`, `loads`, `transforms`, or `tests`.
- `open_questions` contains no more than five short strings.
- A `ready` result contains at least one `implementation` target and, when the
  behavior is testable and tests exist, at least one `test` target.
- `not_found` and `needs_clarification` may use empty `targets` and `flow`.
  `needs_clarification` includes at least one concrete question.

Keep the payload minimal. Include a file only when the primary agent needs it to
understand ownership, preserve a coupled contract, verify the behavior, or obey a
task-relevant repository constraint.

## Validate Before Consuming

After the scout finishes:

1. Parse the final response as one JSON object. Do not inspect or request the
   scout's chain of thought or search transcript.
2. Validate the schema, exact enums, limits, path safety, ranges, required owner,
   and test expectation.
3. Run `repository_fingerprint.py` again in the primary process.
4. Accept the map only when the primary pre-scout fingerprint, the scout's
   reported fingerprint, and the primary post-scout fingerprint all match.
5. Verify every reported path exists. Open only the reported ranges plus
   immediately required definitions, then confirm each symbol appears in or
   directly adjacent to its range.
6. Use narrow import, export, caller, validator, serializer, and test searches
   only as needed to verify the map.

Treat unexpected workspace changes as a shared-workspace conflict to inspect and
preserve. Do not revert them, attribute them to the scout without evidence, or
consume a stale map.

The primary agent owns all design, implementation, tests, and validation after
the evidence map is verified. Repeat broad discovery only when a cited range is
stale, the task scope materially changes, or implementation exposes a concrete
missing edge.

## Correct One Invalid Result

If the response is malformed, stale, unsafe, internally inconsistent, or
insufficient, send the same scout one focused follow-up. List only validation
defects, such as:

- invalid JSON or schema;
- missing implementation owner or discoverable test;
- unsafe or nonexistent path;
- symbol absent from the cited range;
- stale repository fingerprint;
- vague reason or excessive target surface.

Require a complete replacement `code-scout.v1` object and no narrative. Do not
leak a proposed answer or implementation into the correction.

Allow only one correction. After a second invalid result, timeout, tool error, or
unstable worktree, report the problem briefly and continue with the narrowest
safe local discovery. Do not lower the contract or substitute another model
silently.

For a valid `needs_clarification`, first try to resolve the question from narrow
repository evidence. Ask the user only when the missing decision is genuinely
blocking. For a valid `not_found`, report the bounded result and continue locally
only when useful.
