# Work Log — <TASK_ID> — Run <RUN_ID>

## Task

- Source: `<TODO.md line / issue #N / user instruction>`
- Requirement (verbatim): `<original acceptance criteria>`
- Plan: `.nightshift/runs/<RUN_ID>/<TASK_ID>/PLAN.md`

## Execution

| Time | Action | Files touched | Result |
|---|---|---|---|
| `<HH:MM>` | `<what>` | `<1–2 files>` | `<outcome>` |

## Verification evidence

- Type-A (deterministic): `<command>` → exit 0, `<64/64 tests>`
- Robustness: `<fresh env/seed/data check, or "n/a — why">`
- Type-B (cross-model): reviewer `<model/family>`, score `<N/10>`, verdict `<ready/almost/not-ready>`, verdict_id `<id>` → `.nightshift/review/ACQUITTAL_LOG.jsonl`

## Failures & triage

| Failure signature | Bucket (capability / flake / test-design) | Resolution |
|---|---|---|
| `<signature>` | `<bucket>` | `<what fixed it>` |

## Status

- Final state: `<accepted / done-unverified / failed / parked>`
- Commit: `<hash>` or **uncommitted** (`<list files>`)
- Duration: `<Nh NM>` · Review rounds: `<N>`

## Rejected-by-whitelist actions (transparency, never silent)

- `<action attempted → why rejected>`
