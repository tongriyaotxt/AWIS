# Acceptance Gate — Who Is Allowed To Say "Done"

> Adapted and condensed from ARIS `skills/shared-references/acceptance-gate.md` (MIT), see NOTICE.

**One sentence: a goal/loop can DRIVE; it cannot ACQUIT.**

The executor agent may drive an autonomous loop all night, but it must never
be the one who declares its own work *good*. Every stop/accept gate in an AWIS
loop is classified into exactly one of two types:

## Type-A gates — execution / objective

Decidable without taste: exit codes, file existence, counters, timeouts,
`pytest` passing, `npm run build` succeeding.

- The executor **may** self-judge these.
- Prefer external deterministic checks over the agent reading its own output.

## Type-B gates — quality / correctness / acceptance

Require merit judgment: "is this diff good?", "does this implement the
requirement?", "score ≥ 6/10" (when the score came from the executor's own
family).

- The executor **must not** self-judge these.
- Route to a **different model family** reviewer (for Kimi/dsh executors the
  default is the opposite family via the `llm-chat` MCP bridge — DeepSeek API
  reviews Kimi's work, Moonshot/Kimi API reviews dsh's work; `codex-exec` is
  an optional OpenAI backend; `manual-review` is the zero-cost human relay),
  adjudicated by `tools/review_gate.py`.
- The verdict must land on disk as an inspectable artifact
  (`.nightshift/review/ACQUITTAL_LOG.jsonl`).

**Fail-closed**: if the reviewer's model family is the same as the executor's,
or unknown, `review_gate.py` returns `review_unavailable` — the loop pauses or
escalates; it never silently acquits.

## Composite gates must be split

"Tests pass and the code looks good" is Type-A **and** Type-B. It is forbidden
to keep only the Type-A half and pretend the gate is safe.

## Anti-patterns

- **N same-family agents voting ≠ a jury.** N correlated Claudes share the
  same blind spots; the verdict is one sample with error bars, not ground truth.
- **"The reviewer said accept 5 times"** is still one reviewer family.
- **Self-scoring then stopping on your own score.** If the number came from
  your family, the gate is Type-B and unsatisfied.
- **Degrading a Type-B gate to self-judgment at 3 AM because no reviewer is
  configured.** Configure `manual-review` — it tolerates an overnight wait by
  design. Better parked than falsely accepted.

## Gate map for AWIS skills

| Skill / loop | Stop condition | Type | Adjudicated by |
|---|---|---|---|
| `night-shift` task verify | build/tests/lint exit 0 | A | executor (deterministic commands) |
| `night-shift` task accept | work item is good enough | B | `cross-model-review` → `review_gate.py` |
| `cross-model-review` loop | score ≥ 6 **and** verdict ∈ {ready, almost} | B | `review_gate.py`, cross-family only |
| `morning-report` ✅ badge | item accepted | B | only if ACQUITTAL_LOG has a cross-family signature |

## Epistemic status of a cross-model PASS

A heterogeneous second opinion, not ground truth. It lowers risk; it does not
transfer responsibility. Record who signed (reviewer model + family) in every
acquittal entry.
