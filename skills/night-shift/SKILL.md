---
name: night-shift
description: Overnight unattended autonomous work on a task backlog. Use when user says /night-shift, "整晚自主跑/夜间自主推进/过夜干活/autonomous overnight/work the backlog", or needs plan → implement → test → cross-model accept → morning report without human presence.
argument-hint: "[backlog-file-or-task-description] — authorize <paths/commands>; require <named-risky-ops>"
allowed-tools: Bash(*), Read, Grep, Glob, Edit, Write, Skill(cross-model-review), Skill(morning-report)
---

# Night Shift — Overnight Autonomous Orchestrator

Backlog or task description: $ARGUMENTS

**Do NOT wrap this skill in `/loop`, `CronCreate`, or any external scheduler** —
the loop below owns its cadence. External timers may only *wait for external
facts* (see `../shared-references/integration-contract.md`). Read the three
shared references before starting: `acceptance-gate.md`, `resumable-runs.md`,
`integration-contract.md`.

## Constants

- `MAX_TASKS` — task budget for the night (default: unlimited)
- `MAX_REVIEW_ROUNDS` — per-task review rounds, forwarded to `/cross-model-review` (default: 4)
- `TIME_BUDGET_HOURS` — wall-clock budget (default: none; stop when backlog empties)
- `HUMAN_CHECKPOINT` — `false` (default, fully autonomous); `true` = pause per task
- User overrides: `night-shift TODO.md — max-tasks: 5 — time-budget: 8h`

## When to use / Do NOT use

- Use: a queue of programming chores to burn through unattended (bugfixes,
  refactors, migrations, test backfill, docs), especially overnight.
- Do NOT use: single interactive task (just do it); research/paper work
  (that's ARIS); anything requiring *undecided* product judgment every step.

## Why this exists

Generalized from the author's `night-auto-work` skill, battle-tested on
multi-service (Minecraft server fleet) overnight runs: the failure modes that
kill an unattended night are (1) unbounded blast radius, (2) the agent
acquitting its own work at 3 AM, (3) silent stall/spin, (4) dead sessions with
no resumable state, (5) morning archaeology. Every step below exists to kill
one of those.

## Step 0: Startup authorization block

Before touching anything, **recite the boundary once** and record it to
`.nightshift/runs/<run_id>/AUTHORIZATION.md` (template:
`templates/AUTHORIZATION_TEMPLATE.md`). Ask the user ONLY if a key
authorization is missing or a destructive op is needed. Defaults:

- **Allowed**: read the whole repo; edit whitelisted paths (from the
  invocation, e.g. `src/ tests/ docs/`); run builds/tests/smokes and project
  services; write reports under `.nightshift/` and `docs/reports/`.
- **Must be explicitly named**: `git commit` / `git push` / deleting or
  resetting data / installing software / stopping non-project processes /
  editing outside the whitelist.
- Prefer creating new scratch resources over deleting old ones. When unsure
  whether a gate is explicit, treat it as explicit and stop there.
- If the project has `AGENTS.md` / `PROJECT_STATUS.md` / `docs/failure-signatures.md`,
  read them first — project-specific hooks (verify commands, service
  health checks, taboos) are injected from there.

## Step 1: Sync state

1. `git status` / `git log --oneline -5` — know the baseline; never trample
   uncommitted user work (snapshot-commit first if authorized, else work
   around it).
2. Read `.nightshift/runs/` for a resumable run: if one exists, resolve
   helpers per `integration-contract.md` and run
   `run_state.py resume . <id>`（首个未验收阶段即续跑点）; stages `done` but not `accepted`
   are **re-verified**, never skipped (`resumable-runs.md`).
3. Read `findings.md` / failure signatures — known failure signatures recur
   first on the priority list.

## Step 2: Pick the next target

**Backlog durability first**: if the backlog was given as natural language
(no `TODO.md` / issue list file), transcribe it verbatim to
`.nightshift/runs/<run_id>/BACKLOG.md` BEFORE starting the loop. The file is
the contract; conversation memory is not. Resume sessions read the file, never
the chat history.

Priority order: (a) user-designated; (b) recurrence of a known failure
signature's root cause; (c) first unchecked item of the backlog
(`TODO.md` / `BACKLOG.md` / `PROJECT_STATUS.md`「下一步」/ GitHub issues /
the `$ARGUMENTS` list). Write a one-paragraph mini-plan to
`.nightshift/runs/<run_id>/<task_id>/PLAN.md` before editing.

## Step 3: Minimal fix

- One to two files per iteration; no drive-by refactors outside the plan.
- Never hardcode environment-specific values (paths, versions, seeds,
  coordinates) that belong in config/detection layers.
- Stay inside the authorization whitelist; log every rejected-by-whitelist
  edit to the task's `WORK_LOG.md` instead of silently dropping it.

## Step 4: Verify — evidence levels

Acceptance evidence is leveled; a lower level never substitutes for a higher:

1. **Deterministic gate (Type-A, self-judgeable)**: build / lint / test
   commands exit 0. Report counts (`64/64`), never "should be fine".
2. **Robustness**: fresh environment / fresh seed / fresh data where the task
   can be gamed by a fixed fixture. A pinned fixture only proves the fixture
   passes.
3. **Cross-model review (Type-B)**: invoke `/cross-model-review` with
   (diff + test output + original requirement). The task is `accepted` only
   when the review loop stops on a cross-family verdict recorded in
   `.nightshift/review/ACQUITTAL_LOG.jsonl`. No signature → task stays
   `done`, never `accepted`.

On failure, triage into exactly one bucket and log it:
**capability gap** (fix the implementation) / **environment flake** (reduce
concurrency, retry) / **test design flaw** (fix the test, note it honestly).

## Step 5: Anti-stall bookkeeping

- Append every round via `iteration_log.py note . <run_id> <task_id> <new_findings>`
  with the count of *new* findings. `stale ≥ 2` (no new findings) → **mandatory structural pivot**
  (different approach, not another nudge); `stale ≥ 4` → stop the task and
  escalate to the human (Feishu if configured, else 🛑 in morning report).
- Register the run with `watchdog.py` (state file + staleness threshold);
  it detects death/stall, never restarts anything.
- Background task lost ≠ process dead: check `ps` / service health / result
  files before concluding. On resource contention signatures (timeouts,
  "can't keep up"), lower concurrency — don't push harder.

## Step 6: Record

- `run_state.py` stage transitions; `accept` requires verdict_id + reviewer.
- Task `WORK_LOG.md` (template `templates/WORK_LOG_TEMPLATE.md`): every
  conclusion carries evidence — RUN_ID, duration, commit hash or
  "uncommitted" status.
- One line per discovery appended to `findings.md`.
- If `HUMAN_CHECKPOINT=true`: show the scoreboard and wait for
  "go" / "skip N" / "stop".

## Step 7: Continue or wrap

- Backlog remains and budget remains → Step 2.
- Backlog empty / budget spent / human said stop → invoke `/morning-report`
  for this run_id.
- Session must hand off mid-run → write `HANDOFF.md`
  (`templates/HANDOFF_TEMPLATE.md`) BEFORE stopping; the next session resumes
  from `HANDOFF.md` + run file + failure signatures and assumes nothing else.

## Human blockers — three exits, in order

1. Self-decidable choice? Decide, log `level=decision` with rationale, proceed
   **in the same turn** (a question asked at 3 AM to an empty room kills the
   run — never end a turn on an unanswered self-asked question).
2. Genuinely needs a human AND Feishu interactive is configured? Push the
   checkpoint to the phone and park the task (not the whole night — continue
   with the next independent task).
3. Otherwise: park as 🛑 with a precise resume command, continue with the
   next task. Morning report aggregates all 🛑 items.
