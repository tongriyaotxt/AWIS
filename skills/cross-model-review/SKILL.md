---
name: cross-model-review
description: Cross-model-family review loop for code changes (Type-B acceptance gate). Use when user says /cross-model-review, "跨模型评审/让 GPT 看看这个 diff/code review by another model", or a night-shift task needs external acceptance before being marked done.
argument-hint: "[task-id or diff-range] — base <git-ref> — rounds <N>"
allowed-tools: Bash(*), Read, Grep, Glob, Edit, Write
---

# Cross-Model Review — Type-B Acceptance Loop

Review target: $ARGUMENTS

**Do NOT wrap this skill in `/loop`/`CronCreate`.** The loop owns its cadence.
Read `../shared-references/acceptance-gate.md` first — this skill is AWIS's
Type-B gate; its verdict decides whether work may be called `accepted`.

## Constants

- `MAX_ROUNDS` — default 4
- `REVIEWER_BACKEND` — choose by what the executor is (the reviewer must be a
  **different model family**):

  | Executor | Default reviewer backend | Config needed |
  |---|---|---|
  | Kimi Code CLI (moonshot) | `llm-chat` → DeepSeek API | `DEEPSEEK` key in llm-chat env |
  | dsh / DeepSeek (deepseek) | `llm-chat` → Moonshot/Kimi API | `MOONSHOT` key in llm-chat env |
  | any + codex CLI present | `codex` (OpenAI) | codex CLI |
  | no API keys at all | `manual` (human relay, 24 h timeout) | none |

- `SCORE_THRESHOLD` — default 6 (out of 10)
- User overrides: `cross-model-review task-3 — backend: manual — rounds: 3`

### Gate-flag discipline per backend (verified against `review_gate.py`)

- `llm-chat`: do **NOT** pass `--requires-external-acquittal` — this backend's
  family check is built into its normal path (both families must be known and
  different); passing the flag hard-rejects it (`review_unavailable`).
- `codex`: **must** pass `--requires-external-acquittal` — without it, a
  positive codex score stops the loop with no family check.
- `manual`: pass `--requires-external-acquittal --manual-identity-reported`
  once the human relay reply carries a `Reviewer-Model:` header.

## Why this exists

An executor reviewing its own diff is grading its own homework — at 3 AM,
unattended, it *will* pass itself. The stop condition of this loop is
adjudicated by `tools/review_gate.py`, a deterministic transition table that
is **fail-closed**: a same-family or unknown-family reviewer can never acquit;
the decision lands in `.nightshift/review/ACQUITTAL_LOG.jsonl` as an
inspectable artifact.

## Inputs (the honest trio)

Every round, the reviewer receives all three — never a filtered subset:

1. **The diff**: `git diff <base>` (or the task's changed-file set), full text.
2. **The evidence**: build/test/lint output from the Type-A gate, verbatim.
3. **The requirement**: the original task text / acceptance criteria, verbatim.

## Workflow

### Step 1: Initialize or resume loop state

- Resolve helpers per `../shared-references/integration-contract.md`.
- Read `.nightshift/review/REVIEW_STATE.json`; if it matches this target and
  is < 24 h old, resume at its round; otherwise start round 1.
- Loop state, reviewer memory (`.nightshift/review/REVIEWER_MEMORY.md`,
  append-only, raw replies verbatim), and the acquittal log all live under
  `.nightshift/review/`.

### Step 2: Dispatch to the reviewer backend

- **llm-chat** (default for Kimi/dsh executors): call the `llm-chat` MCP
  server, whose env points at the *opposite* family's OpenAI-compatible API —
  Kimi executor → `LLM_BASE_URL=https://api.deepseek.com/v1`,
  `LLM_MODEL=deepseek-chat`; dsh executor → Moonshot/Kimi API. There is no
  shared thread: prepend the previous round's issue list + what was fixed to
  each new prompt for continuity. Ask for: a score 0–10, a verdict ∈ {ready,
  almost, not ready}, and a numbered issue list ordered by severity.
- **codex** (optional, if the codex CLI is installed): call the `codex` MCP
  tool (`codex-exec` server) with the honest trio; keep the threadId across
  rounds for continuity (reply mode).
- **manual**: write the prompt bundle via the `manual-review` server; a human
  pastes it to any *different-family* model and pastes the reply back. The
  reply must begin with `Reviewer-Model: <name>`; unlabeled or same-family
  replies cannot acquit. Default timeout 24 h — it is *designed* to wait
  overnight for a morning human.

### Step 3: Adjudicate — never in prose

Pipe round metadata through the gate; its JSON verdict is the only source of
truth for stop/continue/escalate:

```bash
# llm-chat backend (family check is built in — do NOT add the acquittal flag):
python3 "$AWIS_TOOLS/review_gate.py" \
  --round-backend llm-chat --score "$SCORE" --verdict "$VERDICT" \
  --executor-model "$EXECUTOR_MODEL" --reviewer-model "$REVIEWER_MODEL"

# codex backend (flag REQUIRED — it activates the fail-closed family check):
python3 "$AWIS_TOOLS/review_gate.py" \
  --round-backend codex --score "$SCORE" --verdict "$VERDICT" \
  --executor-model "$EXECUTOR_MODEL" --reviewer-model "$REVIEWER_MODEL" \
  --requires-external-acquittal
```

（verdict 取值为 `ready` / `almost` / `not ready`。已实测：llm-chat 路径下
kimi↔deepseek 异家族正向分 → `stop`；同家族 → `review_unavailable`。
codex 不在场时加 `--no-codex-available` 让转移表改路由。）

- `accept` (score ≥ 6 **and** verdict ∈ {ready, almost} **and** cross-family)
  → mark the stage `accepted` via `run_state.py accept . <run_id> <phase>
  --verdict-id <id> --reviewer <model>`; loop ends.
- `continue` → Step 4.
- `review_unavailable` / escalate → pause the loop, park as 🛑 with the
  backend-switch command (`— backend: manual`), surface in morning report.

### Step 4: Implement fixes, re-run Type-A, next round

- Address the reviewer's numbered issues top-down; one round = one fix batch.
- Re-run the deterministic gate; a regression resets the evidence, not the
  round counter.
- Re-dispatch with the *updated* trio (fresh diff, fresh test output).
- Hard stop at `MAX_ROUNDS`: park as ⚠️ done-unaccepted with the last issue
  list; never force-accept.

## Anti-patterns (all forbidden)

- Self-scoring ("as the reviewer, I give this 8/10") — that is the executor
  acquitting itself; `review_gate.py` rejects it by construction.
- Summarizing away the reviewer's issues before fixing them; the memory file
  keeps raw replies verbatim for a reason.
- Retrying the same prompt hoping for a higher score — bias-guard: if a round
  must be re-reviewed, start a **fresh** reviewer thread with the full trio,
  not a "was it better this time?" nudge.
