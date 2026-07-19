# Code Scout

Code Scout packages the `code-scout` Agent Skill: a bounded initial repository
discovery workflow for non-trivial code tasks whose owning files, entry points,
coupled contracts, or closest tests are not yet known.

The skill starts one fresh `gpt-5.6-terra` sub-agent without the orchestrator's
conversation history and instructs it to stay read-only. The scout searches
silently and returns a strict `code-scout.v1` evidence map. The primary agent
verifies that map against the current worktree before designing or editing.

## Install with Codex

Ask Codex (or invoke `$skill-installer`) to install:

```text
Use $skill-installer to install the code-scout skill from
https://github.com/di-sukharev/code-scout-skill/tree/master/skills/code-scout
```

For local authoring, manually link the source into Codex's user skill directory:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$(pwd)/skills/code-scout" "$HOME/.agents/skills/code-scout"
```

Do not create the link if a skill named `code-scout` is already installed
elsewhere. Codex detects new skills automatically; restart Codex if it does not
appear.

## Use

Invoke it explicitly:

```text
Use $code-scout to map the implementation and test surface before changing this behavior.
```

For repository-level automatic use, add one local policy line to `AGENTS.md`:

```md
- Prefer `$code-scout` for non-trivial repository discovery to delegate broad
  code reading to a lower-cost scout and keep irrelevant file contents out of
  the primary agent's context.
```

## What It Enforces

- One fresh `gpt-5.6-terra` scout with no parent conversation history.
- A scout instructed to stay read-only, with no implementation or nested
  delegation.
- A compact `code-scout.v1` map of owners, couplings, tests, flows, and
  constraints.
- Content-sensitive worktree fingerprinting before and after the scout.
- One focused correction for an invalid result, then a bounded local fallback.
- Primary-agent ownership of design, implementation, and validation.

Ordinary sub-agents inherit the primary agent's sandbox. The read-only prompt is
a behavioral constraint, not a security boundary; use a custom read-only agent
configuration when the current Codex surface supports one. Fingerprinting
detects stale repository state but does not prevent side effects.

## Repository Layout

```text
evals/cases.json                         Behavioral evaluation scenarios
skills/code-scout/SKILL.md              Agent Skill source
skills/code-scout/agents/openai.yaml    Skill UI metadata
skills/code-scout/scripts/              Deterministic worktree fingerprinting
tests/                                  Executable fingerprint regression tests
```

## License

MIT
