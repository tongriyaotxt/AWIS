# AWIS 🌙 — Auto-Work-In-Sleep

<p align="center">
  <img src="assets/hero.svg" alt="AWIS — you hand over the backlog at 11 PM; an executor drives; a jury of another model family signs; you read the morning report at 7 AM" width="100%">
</p>

[![Quick Start](https://img.shields.io/badge/🚀_Quick_Start-3_commands-2E7D32?style=flat)](#quick-start) · [![Usage Guide](https://img.shields.io/badge/📖_Usage_Guide-install_→_first_night_shift-1a4a8c?style=flat)](docs/USAGE.md) · [![Doctrine](https://img.shields.io/badge/📜_Doctrine-a_loop_can_DRIVE%2C_it_cannot_ACQUIT-4B2E83?style=flat)](#the-doctrine) · [![Skills](https://img.shields.io/badge/Skills-3_·_night--shift_·_cross--model--review_·_morning--report-orange?style=flat)](#the-three-skills) · [![Tests](https://img.shields.io/badge/Tests-226_passed_·_CI_ubuntu+%2B+macOS-brightgreen?style=flat)](#honesty--testing) · [![Runtime](https://img.shields.io/badge/Runtimes-Kimi_Code_CLI_·_dsh_·_Claude_Code_·_Codex-1a4a8c?style=flat)](#reviewer-routing) · [![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

🌱 *AWIS is a discipline, not a platform. Three Markdown skills + four stdlib scripts + three tiny MCP bridges — take it wherever your agent goes.*

💡 *Works with [Kimi Code CLI](https://www.kimi.com/) and [DeepSeek Harness (dsh)](https://github.com/) as first-class executors — **Kimi's work gets reviewed by DeepSeek, dsh's work gets reviewed by Kimi** — plus Claude Code / Codex if you have them. No Claude or OpenAI API key required.*

⚔️ *Sibling of [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) (Auto-**Research**-In-Sleep). ARIS proved the overnight doctrine on ML research; AWIS points the same weapon at **every programmer's backlog**.*

---

## The 3 AM problem

Every coding agent can now work autonomously for hours. So you give it a backlog and go to bed. What actually happens at 3 AM, in an empty room?

- The agent **grades its own homework**. "Tests pass, looks good to me" — the same mind that wrote the bug declares it fixed.
- One unanswered question — *"should I delete the old table?"* — **kills the whole night**. You wake to a polite question posted at 1:07 AM and seven idle hours.
- Or the opposite: a confident wrong turn at midnight compounds into a **400-line unreviewed diff** by morning.
- Or nothing broke at all — the loop just **spun**: same failure, retried 40 times, no new information, tokens burning.

AWIS is built around one sentence that kills the first failure mode, and machinery that kills the other three:

> **A loop can DRIVE; it cannot ACQUIT.**

The executor may drive all night. It may never sign off its own work. Every work item needs a **verdict from a different model family** — Kimi's output judged by DeepSeek, DeepSeek's by Kimi, anyone's by Codex/GPT, or by a human relay — adjudicated by a deterministic, test-covered gate (`tools/review_gate.py`), and written to an append-only log you can audit over coffee. Same-family applause is rejected **fail-closed**: better parked than falsely accepted.

## The doctrine

| # | Principle | What it prevents |
|---|---|---|
| 1 | **A loop can DRIVE; it cannot ACQUIT.** Objective gates (test exit codes) are machine-judged; quality gates need a *different model family's* signature | self-graded homework |
| 2 | **Startup authorization block.** Read the repo, edit whitelisted paths, run tests — fine. Commit/push/delete/install — only if you named it | 3 AM blast radius |
| 3 | **done ≠ accepted.** Resuming re-verifies every stage that was never externally signed | "it said it finished" |
| 4 | **Evidence levels.** Deterministic gate → fresh-env robustness → cross-model review. Low-level evidence never substitutes for high | pinned-fixture theater |
| 5 | **Failure triage.** capability gap / environment flake / test design flaw. 2 stale rounds force a pivot; 4 escalate to you | the 40-retry spin |
| 6 | **Schedule the wait, never the verdict.** Timers wait for external facts only | scheduler fighting the loop |
| 7 | **Human blockers have three exits.** Self-decide with an audit log → push to your phone (Feishu) → park as 🛑 and move on | the 1:07 AM question |
| 8 | **5-line morning summary.** passed / not passed / evidence IDs / commit status / next step | morning archaeology |

## Quick start

> 📖 Full guide: [USAGE.md](docs/USAGE.md)

```bash
git clone https://github.com/tongriyaotxt/AWIS.git && cd AWIS
bash install.sh          # skills → ~/.kimi/skills (+ ~/.claude/skills), MCP servers registered
# point the reviewer at the OPPOSITE family's API (one env block):
export LLM_API_KEY=sk-... LLM_BASE_URL=https://api.deepseek.com/v1 LLM_MODEL=deepseek-chat
```

Then, in any project, before bed:

```
/night-shift TODO.md — authorize "edit src/ tests/, run pytest, no commit"
```

Wake up to `MORNING_REPORT.md`. No API keys at all? Add `— backend: manual` and the review waits (by design, up to 24 h) for you to relay it to any web model in the morning.

## One Friday Night (a story walkthrough)

> Person and project are fictional; every command, state output, and gate decision comes from real AWIS runs (reviewer wording illustrative).

**Cast**: Lin, a backend developer maintaining a Flask `order-service`.
**When**: Friday, 23:20. Release freeze Monday. Five items on the backlog.
Tonight, AWIS works its first shift.

---

### Act I · Twenty minutes before bed

#### 23:22 — The backlog: what belongs in the night

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

#### 23:28 — Project hooks and reviewer config

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

#### 23:35 — Launch

```text
/night-shift TODO.md — authorize "edit src/ tests/ docs/, run pytest,
restart local dev server" — require "git commit/push, touching migrations/, installing deps"
```

The agent recites the authorization block and writes it to
`.nightshift/runs/night-001/AUTHORIZATION.md`. Lin double-checks that
migrations landed on the *require* side, then goes to bed.

---

### Act II · Overnight (after he falls asleep)

#### 23:47 · task-1: the smooth one

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

#### 00:30 · task-2: the review earns its keep

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

#### 01:15 · task-3: the stall breaker

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

#### 03:02 · task-4: the authorization block stops a bullet

task-4 requires editing `migrations/` — **not in the whitelist**.

The agent neither forces its way through nor asks the empty room (a question
at 3 AM ends the turn and kills the night). Standard procedure instead:

1. Write "migration plan needs human sign-off" into the task log;
2. Mark task-4 **🛑 waiting-on-human**, with a resume command;
3. Move on to task-5.

> 📌 **Doctrine 7**: human blockers have three exits — self-decide with an
> audit log, push to the phone, or park 🛑. **Never ask the empty room.**
> Morning brings a parked item with a command, not seven idle hours.

#### 03:40 · task-5: better parked than passed

README rewritten, tests green — but the DeepSeek API is flaky and the review
times out. The gate (real behavior):

```
decision: review_unavailable        ← no reviewer = no signature
```

task-5 becomes **⚠️ done-unverified**: finished, but nobody signed it, so it
is not ✅.

> 📌 Fail-closed, in one sentence: **the system would rather park finished
> work than let unverified work slip through.**

#### 04:10 · Wrap

Backlog exhausted. `/morning-report` aggregates everything; with Feishu
configured, a card lands on Lin's phone.

---

### Act III · 7:40 AM

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

### What the story teaches

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

## The three skills

| Skill | What it does |
|---|---|
| **`/night-shift`** | The overnight orchestrator. Backlog → authorization block → per task: mini-plan → minimal fix → deterministic gate → **cross-model review** → work log → next. Human blockers route to self-decision / phone / 🛑, never to a dead stop |
| **`/cross-model-review`** | The Type-B gate. Sends the *honest trio* (full diff + test output + original requirement — never a filtered subset) to a different model family; `review_gate.py` owns stop/continue/escalate; ≤ 4 rounds; no force-accepts |
| **`/morning-report`** | Turns machine state into a 3-minute brief: ✅ accepted (signature required) / ⚠️ done-unverified / ❌ failed / 🛑 waiting-on-you, with resume commands. Optional Feishu push |

## Reviewer routing

The reviewer must be a **different model family** than the executor. Verified against `tools/review_gate.py`:

| Executor | Reviewer | Transport | Config |
|---|---|---|---|
| Kimi Code CLI (moonshot) | DeepSeek (deepseek) | `llm-chat` MCP → `api.deepseek.com` | `LLM_API_KEY` |
| dsh / DeepSeek (deepseek) | Kimi (moonshot) | `llm-chat` MCP → `api.moonshot.cn` | `LLM_API_KEY` |
| any | GPT/Codex (openai) | `codex-exec` MCP → codex CLI | codex CLI |
| any | **you**, relaying to any web model | `manual-review` MCP, 24 h timeout | none |

Point the reviewer at the executor's own family (dsh → DeepSeek API) and the gate refuses to acquit — `review_unavailable`, `identity_assurance: failed`. That is not a bug; that is the product.

## What a night looks like

From the actual end-to-end simulation (`run night-001`, executor `kimi-k2`, reviewer `deepseek-chat`):

```
run night-001
   ✅  task-1  [accepted]  ← deepseek-chat / v-001     (divide-by-zero fix, 7/10 ready)
   ✅  task-2  [accepted]  ← deepseek-chat / v-002     (calc.sub, round 1: 5/10 not-ready
                                                         → fix → round 2: 8/10 almost)
  resume → COMPLETE

run night-002
   ✓(unaccepted)  task-3  [done]                      (dsh executor → DeepSeek reviewer:
  resume → task-3                                       SAME family — refused to sign)
```

Everything lives on disk in the target project's `.nightshift/` — run states, the append-only `ACQUITTAL_LOG.jsonl`, iteration/staleness tracking, watchdog alerts. Sessions may die; the state machine doesn't. `done` without a signature is re-verified on resume, never silently believed.

## Architecture

```
skills/            the product — Markdown workflows (LLM-readable discipline)
  night-shift/  cross-model-review/  morning-report/  shared-references/
tools/           the parts no LLM may self-adjudicate — stdlib Python, 226 tests
  review_gate.py    deterministic verdict transitions, fail-closed family check
  run_state.py      done ≠ accepted stage machine, atomic state files
  iteration_log.py  stale-round → forced pivot → human escalation
  watchdog.py       heartbeat staleness detector (detects, never restarts)
mcp-servers/     single-file bridges (JSON-RPC over stdio, zero SDK deps)
  llm-chat (DeepSeek/Kimi APIs) · manual-review (human relay) · codex-exec · feishu-bridge
templates/       authorization block · work log · handoff · morning report · failure signatures
```

## Honesty & testing

- `python -m pytest tests/ -q` → **226 passed, 13 skipped** (skips: POSIX-only codex bridge tests on Windows; they run on Linux/macOS CI).
- The safety-critical claim — *same-family can never acquit* — is not prose; it is a tested transition table, and the routing matrix above is empirically reproduced in CI.
- **What is NOT yet claimed**: a full production overnight run on a real backlog. The doctrine and machinery are inherited from two battle-tested parents (ARIS's research loops, the `night-auto-work` skill on a live multi-service project); AWIS itself is freshly assembled and its first real night shift is the next milestone. Reports welcome.

## The ARIS family

- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) — the overnight harness for ML research (literature → idea → experiment → paper → rebuttal). AWIS's gates, state machine, watchdog and MCP bridges are adapted from it (MIT), with thanks — see [NOTICE](NOTICE).
- **AWIS** (this repo) — the same doctrine for everyone else's backlog. Research is one domain; programming is all the others.

## Roadmap

- [ ] First production overnight run (dogfood) — *the v0.1 gate*
- [ ] Remote/batch execution queue (SSH job scheduler, adapted from ARIS `experiment-queue`)
- [ ] One-command plugin packaging
- [ ] More domain packs on the same spine (ops runbooks, data pipelines, writing)

## License

MIT — see [LICENSE](LICENSE) and [NOTICE](NOTICE) for ARIS attribution.
