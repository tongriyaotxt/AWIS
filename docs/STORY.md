# A Night Shift Story — One Ordinary Friday, Told End to End

> 中文版: [STORY_CN.md](STORY_CN.md)
>
> This is a teaching narrative: the person and project are fictional, but
> **every command, state-machine output, and gate decision quoted here comes
> from real AWIS runs** (the reviewer's exact wording is illustrative; in
> production it comes from the llm-chat / codex / manual backends).

**Cast**: Lin, a backend developer maintaining a Flask `order-service`.
**When**: Friday, 23:20. Release freeze Monday. Five items on the backlog.
Tonight, AWIS works its first shift.

---

## Act I · Twenty minutes before bed

### 23:22 — The backlog: what belongs in the night

Lin writes `TODO.md` with a private rule: **only work with clear boundaries
and objective acceptance criteria goes into the night.** Vague features and
data migrations would just become morning regrets.

```markdown
# Backlog
- [ ] task-1: /api/orders crashes on amount=0 (ZeroDivision), should 400
- [ ] task-2: implement utils.top_customers(orders, n) + tests (by spend, desc)
- [ ] task-3: backfill parser edge-case tests (blank lines, missing cols, BOM)
- [ ] task-4: add user.last_login column (touches migrations/)
- [ ] task-5: deployment section of README is stale, rewrite from docker-compose.yml
```

task-4 stays on the list — but `migrations/` will be excluded in the
authorization block. **Writing it down ≠ authorizing it.** Two separate layers.

> 📌 **Doctrine 2, previewed**: the list is "what I hope gets done"; the
> authorization block is "what the agent may touch".

### 23:28 — Project hooks and reviewer config

The repo already has `AGENTS.md` (`pytest tests/ -q`, "never touch
migrations/"); Lin adds `.nightshift/` to `.gitignore`.

Lin's executor is **Kimi Code CLI**, so the reviewer must be the opposite
family — DeepSeek — already in his shell profile:

```bash
export LLM_API_KEY=sk-****        # DeepSeek key
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
```

> 📌 If his executor were dsh (DeepSeek), this block would point at
> Moonshot/Kimi instead. Same-family review is **refused by the gate** —
> task-5 will show the flip side of that.

### 23:35 — Launch

```text
/night-shift TODO.md — authorize "edit src/ tests/ docs/, run pytest,
restart local dev server" — require "git commit/push, touching migrations/, installing deps"
```

The agent recites the authorization block and writes it to
`.nightshift/runs/night-001/AUTHORIZATION.md`. Lin double-checks that
migrations landed on the *require* side, then goes to bed.

---

## Act II · Overnight (after he falls asleep)

### 23:47 · task-1: the smooth one

Plan on disk → one-file fix → `pytest` green (Type-A, self-judged — it's
objective) → Type-B: full diff + test output + requirement sent to DeepSeek.

Round 1: **6/10 · almost** — "amount=None still returns 500, not 400." The
agent fixes the edge, retests, resubmits. Round 2: **8/10 · ready**. The gate
(real output):

```
decision: stop        ← cross-family + threshold met → accepted
```

```
   ✅  task-1  [accepted]  ← deepseek-chat / v-101
```

> 📌 **Doctrine 1**: the agent saying "fixed" is worth `done`; the other
> family saying ready is worth `accepted`. Signatures live in
> `.nightshift/review/ACQUITTAL_LOG.jsonl`, append-only, auditable over coffee.

### 00:30 · task-2: the review earns its keep

`top_customers` goes for review. Round 1: **5/10 · not ready**:

> 1. [major] tied spend amounts return in nondeterministic order — flaky test;
> 2. [minor] case-variant customer names counted as different people.

Gate (real output):

```
decision: continue | positive threshold not met
```

The agent fixes both (secondary sort by name, case normalization). Round 2:
**7/10 · ready** → ✅.

> 📌 With a same-family reviewer, that first-round thorn would likely have
> been swallowed. **That is the entire reason cross-family review exists.**

### 01:15 · task-3: the stall breaker

Three consecutive failures, all `address already in use`.
`iteration_log` records two rounds with zero new findings → **forced pivot**.

Instead of retrying a fourth time, the agent triages: not a capability gap —
an **environment flake**. The dev server it restarted at 23:47 still holds
port 8000. Kill it, rerun, green. The failure lands in
`docs/failure-signatures.md`:

```
| pytest hang + "address already in use" | night-001 | leftover dev server on :8000 | flake | kill old server first | fixed |
```

> 📌 **Doctrine 5**: every failure gets a bucket — capability gap → fix code;
> environment flake → retry calmly; test design flaw → fix the test honestly.
> **Retrying 40 times without triage is forbidden.**

### 03:02 · task-4: the authorization block stops a bullet

task-4 requires editing `migrations/` — **not in the whitelist**.

The agent neither forces its way through nor asks the empty room (a question
at 3 AM ends the turn and kills the night). Standard procedure instead:

1. Write "migration plan needs human sign-off" into the task log;
2. Mark task-4 **🛑 waiting-on-human**, with a resume command;
3. Move on to task-5.

> 📌 **Doctrine 7**: human blockers have three exits — self-decide with an
> audit log, push to the phone, or park 🛑. **Never ask the empty room.**
> Morning brings a parked item with a command, not seven idle hours.

### 03:40 · task-5: better parked than passed

README rewritten, tests green — but the DeepSeek API is flaky and the review
times out. The gate (real behavior):

```
decision: review_unavailable        ← no reviewer = no signature
```

task-5 becomes **⚠️ done-unverified**: finished, but nobody signed it, so it
is not ✅.

> 📌 Fail-closed, in one sentence: **the system would rather park finished
> work than let unverified work slip through.**

### 04:10 · Wrap

Backlog exhausted. `/morning-report` aggregates everything; with Feishu
configured, a card lands on Lin's phone.

---

## Act III · 7:40 AM

```markdown
## 5-line summary
1. Passed: 3 items — task-1 zero-division, task-2 top_customers, task-3 parser tests
2. Not passed: 0 failed; task-5 done-but-unsigned (review API outage); task-4 needs human (migrations/)
3. Evidence: run night-001, verdicts v-101/v-102/v-103, .nightshift/review/ACQUITTAL_LOG.jsonl
4. Commits: none (not authorized) — all changes in working tree, 6 files
5. Next: review diff, then commit; one command to sign task-5
```

Fifteen minutes of his morning:

```bash
git diff                        # the night's 6 files, quality fine
git add -p && git commit        # commit was never authorized — it's his call
/cross-model-review task-5      # API is back; signature → ✅
```

task-4 waits for a migration plan review with the team — it never belonged
to the night anyway.

> 📌 Three minutes is enough: ✅ items carry auditable signatures, ⚠️ items
> are one command away, 🛑 items were always yours. **No archaeology, no
> surprises.**

---

## What the story teaches

| When | You do | Key idea |
|---|---|---|
| Before bed | write crisp TODOs; point the reviewer at the opposite family; read the authorization recital | list ≠ authorization |
| At launch | put commit/delete/migration on the "require naming" side | blast radius locks at bedtime |
| Overnight | sleep | blockers can't kill the night: self-decide / phone / 🛑 |
| Morning | 5-line summary → diff → commit → sign ⚠️ → handle 🛑 | trust ✅ because it's signed, not because it looks fine |
| Daily | maintain failure-signatures.md | no pit twice; recurrences jump the queue |

**When NOT to use a night shift**: vague features (no objective acceptance),
data migrations/deletions, work needing continuous product judgment. Those
belong to daylight.

Your turn: pick a project, write 3–5 TODO lines, and at 23:30 type
`/night-shift TODO.md — authorize "…"`. Tomorrow's coffee will taste better. 🌙
