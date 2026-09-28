---
name: morning-report
description: Generate the morning report for an overnight run — what passed, what didn't, evidence, blockers — and push to Feishu. Use when user says /morning-report, "晨报/夜间结果汇报/昨晚跑得怎么样", or when night-shift finishes its backlog.
argument-hint: "[run-id] — push"
allowed-tools: Bash(*), Read, Grep, Glob, Write
---

# Morning Report — What Happened Last Night

Run to summarize: $ARGUMENTS (default: most recent run in `.nightshift/runs/`)

## Why this exists

The value of an overnight run is decided in the 3 minutes after the human
wakes up. This skill turns machine state into a scannable report where every
✅ is backed by an external signature and every 🛑 has a one-line resume
command. Read `../shared-references/acceptance-gate.md`: **no ✅ without a
cross-family acquittal entry.**

## Workflow

### Step 1: Collect machine state

Resolve helpers per `../shared-references/integration-contract.md`, then read:

- `.nightshift/runs/<run_id>.json` — stage states (`run_state.py status . <id>`)
- `.nightshift/runs/<run_id>.iterations.jsonl` — stall/pivot history
- `.nightshift/review/ACQUITTAL_LOG.jsonl` — cross-family sign-offs
- `.nightshift/watchdog/summary.txt` + `alerts.log` — death/stall events
- task `WORK_LOG.md` files + `findings.md`
- `git log --oneline --since="<run start>"` and `git status` — commit reality

### Step 2: Classify every work item

| Badge | Meaning | Requirement |
|---|---|---|
| ✅ accepted | done **and** externally signed | matching ACQUITTAL_LOG entry with a cross-family reviewer |
| ⚠️ done-unverified | executor says done, no signature | listed with the exact `/cross-model-review` resume command |
| ❌ failed | deterministic gate or review failed | failure signature + triage bucket (capability / flake / test-design) |
| 🛑 waiting-on-human | parked blocker | what is needed + one-line resume command |
| ⏭️ skipped/not started | budget or dependency | one-line reason |

### Step 3: Write the report

Write `MORNING_REPORT.md` in the project root (template:
`templates/MORNING_REPORT_TEMPLATE.md`):

1. **5-line summary** at top: what passed / what didn't / evidence IDs /
   commit-or-uncommitted status / recommended next step.
2. Badge table of all items with evidence links (RUN_ID, verdict_id, log paths).
3. 🛑 blocker list with resume commands.
4. Anomalies: watchdog alerts, stall pivots, rejected-by-whitelist edits,
   uncommitted leftovers.

Honesty rules: an item with no acquittal entry is ⚠️ even if tests passed;
dev/scratch data is never presented as acceptance evidence; uncertainty is
labeled "待核实", never smoothed over.

### Step 4: Push (optional)

If `— push` and Feishu is configured (`~/.claude/feishu.json` or the
project's configured bridge): send the 5-line summary + badge counts as a
`morning_report` card via the `feishu-bridge` server (`POST /send`). If not
configured, skip silently — notification is a side effect, never a gate.
