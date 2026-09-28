# Resumable Runs — done Is Not accepted

> Adapted and condensed from ARIS `skills/shared-references/resumable-runs.md` (MIT), see NOTICE.

Overnight runs die: context compacts, terminals close, machines reboot. Every
AWIS loop must be resumable from disk state alone — no assumption that the next
session inherits anything from this one's memory.

## Stage states

`tools/run_state.py` tracks each stage of a run in
`.nightshift/runs/<run_id>.json`:

| State | Meaning | Who may set it |
|---|---|---|
| `pending` | not started | — |
| `running` | in progress | executor |
| `failed` | errored | executor / deterministic check |
| `done` | executor *says* it finished | executor |
| `accepted` | externally verified | cross-model review / deterministic verifier only |
| `skipped` | deliberately bypassed | human only |

**`done` is a claim; `accepted` is a fact.** `run_state.py accept` requires a
`verdict_id` and a `reviewer`; same-family reviewers trigger a warning (see
`acceptance-gate.md`).

## Resume protocol

1. On startup, the loop reads the run file. `resume_point()` returns the first
   stage that is not in a terminal-verified state.
2. A stage that is `done` but **not** `accepted` is **re-verified on resume** —
   never silently treated as finished.
3. `failed` stages resume with the failure signature attached (see the
   project's `docs/failure-signatures.md` or `FAILURE_SIGNATURES.md`) so the
   same root cause is attacked first instead of rediscovered.
4. State writes are atomic; the state file is the single source of truth.

## HANDOFF protocol (for humans and fresh sessions)

When a session must hand off mid-run (context exhaustion, tool failure), write
`HANDOFF.md` in the target project root before stopping:

- goal / current run_id
- committed vs uncommitted changes
- running background tasks (PIDs, log paths)
- the exact next command
- taboos (what the next session must NOT do)

The next session reads `HANDOFF.md` + the run file + failure signatures and
assumes **nothing** else. A one-minute-readable `PROJECT_STATUS.md` section
serves the same role across days, not just sessions.
