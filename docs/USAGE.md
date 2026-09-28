# AWIS Usage Guide — From Install to Your First Night Shift

> 中文版本: [USAGE_CN.md](USAGE_CN.md)

This guide walks through the complete loop: install → configure → prepare a
project → run a night shift → read the morning report → resume from blockers.

## 1. Install

```bash
git clone https://github.com/tongriyaotxt/AWIS.git && cd AWIS
bash install.sh
```

What the installer does (preview anytime with `bash install.sh --dry-run`):

1. Copies the 3 skills + `shared-references/` into `~/.kimi/skills/`
   (and `~/.claude/skills/` if that directory exists).
2. Registers MCP servers with whichever CLI is present
   (`kimi mcp add …` / `claude mcp add …`): `llm-chat`, `manual-review`
   (`codex-exec` only if the `codex` CLI is installed).
3. Writes `~/.nightshift/repo` — a one-line pointer to this checkout so the
   skills can find `tools/` from any project.

Verify:

```bash
kimi mcp list                 # llm-chat and manual-review should appear
kimi mcp test manual-review   # 2 tools: review, review_reply
ls ~/.kimi/skills/            # night-shift, cross-model-review, morning-report
```

> **Windows note**: if `kimi mcp test` fails with
> `UnicodeEncodeError: 'gbk' codec`, that is a console-rendering quirk of the
> CLI, not the server. Run `export PYTHONIOENCODING=utf-8` first (or set it in
> your shell profile).

## 2. Configure the reviewer (one env block)

The reviewer must be the **opposite model family** from your executor:

| Your executor | Set llm-chat to | Env |
|---|---|---|
| Kimi Code CLI | DeepSeek | `LLM_BASE_URL=https://api.deepseek.com/v1`, `LLM_MODEL=deepseek-chat` |
| dsh (DeepSeek) | Moonshot/Kimi | `LLM_BASE_URL=https://api.moonshot.cn/v1`, `LLM_MODEL=kimi-k2` |

```bash
export LLM_API_KEY=sk-your-key
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
export LLM_REVIEW_FALLBACK_ENABLED=1   # exposes the `review` tool too
```

Make it permanent: add to your shell profile, or bake into the MCP
registration (`kimi mcp add llm-chat -e LLM_API_KEY=... -e LLM_BASE_URL=... -- python3 ...`).

**No API key?** Skip this section entirely and use `— backend: manual` at
review time. The review parks (up to 24 h, by design) while you paste the
prompt into any web model and paste the reply back. Zero cost.

**Feishu push (optional)**: see `mcp-servers/feishu-bridge/README.md`. Once
running, checkpoints and morning reports arrive on your phone, and
interactive mode lets you approve/reject from bed.

## 3. Prepare the target project (5 minutes)

In the project you want worked on:

```bash
# 1. The backlog — one checkbox per independently-completable task
cat > TODO.md <<'EOF'
# Backlog
- [ ] fix divide-by-zero in calc.divide (should return None)
- [ ] add calc.sub(a, b) with tests
- [ ] backfill tests for parser edge cases
EOF

# 2. Tell git to ignore runtime state
echo ".nightshift/" >> .gitignore
```

Optional but recommended — project hooks the agent will read first:

- `AGENTS.md`: build/test commands, service health checks, taboos.
- `docs/failure-signatures.md` (template in `templates/FAILURE_SIGNATURES_TEMPLATE.md`):
  known recurring failures; their root causes jump the priority queue.
- `PROJECT_STATUS.md` with a「下一步」section — used as the default backlog.

## 4. Start the night shift

In the project directory, in your agent CLI:

```
/night-shift TODO.md — authorize "edit src/ tests/ docs/, run pytest, restart dev server" — require "git commit, deleting fixtures"
```

Read the authorization recital it prints. Adjust if the boundary is wrong —
this is the last thing you owe it before bed.

Useful overrides:

```
/night-shift TODO.md — max-tasks: 5 — time-budget: 8h
/night-shift — resume night-001            # continue an interrupted run
/night-shift — checkpoint: true            # pause for "go/skip/stop" per task
```

## 5. What happens overnight (you don't need to watch)

For each task: mini-plan on disk → 1–2 file minimal fix → build/tests
(self-judged, they're objective) → **cross-model review** (diff + test output
+ your requirement text sent to the other family; ≤ 4 rounds) → work log with
evidence → next task. Human blockers: self-decided with an audit log when
safe, pushed to your phone if Feishu is on, otherwise parked 🛑 and the agent
moves to the next independent task. Two consecutive no-progress rounds force
a strategy pivot; four escalate to you.

## 6. Morning

Open `MORNING_REPORT.md` in the project root:

- **✅ items** — done AND signed by the other model family (verdict IDs link
  into `.nightshift/review/ACQUITTAL_LOG.jsonl`). Trust these.
- **⚠️ items** — finished but unsigned. Resume command is right there:
  `/cross-model-review <task>`.
- **❌ items** — failed, with failure signature and triage bucket.
- **🛑 items** — waiting for a decision only you can make, each with a
  one-line resume command.
- Then the 5-line summary at the top is all you truly need.

Common morning actions:

```bash
git diff                          # review what the night produced
git add -p && git commit          # commit was not authorized, so it's yours to do
/cross-model-review task-3        # clear an ⚠️ item
```

## 7. If the night died mid-run

Machine rebooted, terminal closed, context compacted — doesn't matter:

```
/night-shift — resume <run-id>
```

The state machine (`.nightshift/runs/<run-id>.json`) points at the first
stage that was never externally accepted; `done`-but-unsigned stages are
re-verified, never skipped. If a `HANDOFF.md` exists, the new session reads
it first.

## 8. Command cheat sheet (tools/, rarely needed by hand)

```bash
python3 "$AWIS_ROOT/tools/run_state.py" status . <run-id>      # where is the run
python3 "$AWIS_ROOT/tools/run_state.py" resume . <run-id>      # first unsigned stage
python3 "$AWIS_ROOT/tools/iteration_log.py" show . <run-id>    # stall history
python3 "$AWIS_ROOT/tools/watchdog.py" --status                # dead/stalled loops
python3 "$AWIS_ROOT/tools/review_gate.py" --round-backend llm-chat \
  --score 7 --verdict ready --executor-model kimi-k2 \
  --reviewer-model deepseek-chat                               # dry-run a verdict
```

## 9. Troubleshooting

| Symptom | Cause → fix |
|---|---|
| `review_unavailable`, `identity_assurance: failed` | reviewer is the same family as the executor (e.g. dsh → DeepSeek API). Point llm-chat at the OTHER family, or use `— backend: manual` |
| `AWIS tools not found` | `~/.nightshift/repo` missing → re-run `bash install.sh` |
| llm-chat calls fail but `kimi mcp test` connects | `LLM_API_KEY`/`LLM_BASE_URL` not set in the server env → re-register with `-e` flags |
| morning report shows ⚠️ everywhere | reviewer backend down all night — items are fine but unsigned; clear them with `/cross-model-review <task>` per item |
| UnicodeEncodeError / mojibake on Windows | `export PYTHONIOENCODING=utf-8` |

## 10. Rules that keep you safe (do not disable)

1. No ✅ in the morning report without a cross-family signature in
   `ACQUITTAL_LOG.jsonl`.
2. `done` ≠ `accepted` — resume always re-verifies.
3. The agent never commits/pushes/deletes unless you named it in the
   authorization block.
4. A question the agent can answer itself is answered and logged, never
   asked into an empty room; a question it can't is parked 🛑, and the night
   moves on.
