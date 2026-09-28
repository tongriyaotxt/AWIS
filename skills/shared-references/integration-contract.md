# Integration Contract — How Skills Call Helpers

> Adapted and condensed from ARIS `skills/shared-references/integration-contract.md` (MIT), see NOTICE.

SKILL.md prose can *describe* an integration; it cannot *guarantee* one. Under
context pressure, an executor will skip a "MUST invoke X" sentence. Every
cross-skill integration in AWIS therefore provides concrete machinery instead
of wishes.

## The six components of a real integration

1. **Activation predicate** — one externally observable line (a file exists, a
   flag is set). Never "if the user seems to want this".
2. **Canonical helper** — the logic lives in exactly one place (`tools/`);
   every caller resolves it through the same chain (below).
3. **Concrete artifact** — success leaves a receipt: a file, JSON, or log line.
4. **Visible checklist** — multi-step workflows render 📋 checkboxes.
5. **Backfill command** — an explicit repair entry when the integration was
   missed (e.g. re-run `run_state.py accept` for a stage verified late).
6. **Verifier** — for load-bearing integrations, an external process whose
   exit code is the downstream gate's source of truth (not the LLM's say-so).

## Helper resolution (canonical chain)

SKILL.md files must **never** hardcode `python3 tools/<helper>.py`. Resolve
helpers through this chain, first hit wins:

```bash
# Resolve the AWIS repo root, then call helpers as "$AWIS_ROOT/tools/<helper>.py"
for d in "$PWD/.nightshift/repo" "$HOME/.nightshift/repo" "$AWIS_ROOT"; do
  [ -f "$d/tools/$HELPER" ] && { AWIS_TOOLS="$d/tools"; break; }
done
[ -n "$AWIS_ROOT" ] && [ -f "$AWIS_ROOT/tools/$HELPER" ] && AWIS_TOOLS="$AWIS_ROOT/tools"
[ -z "$AWIS_TOOLS" ] && { echo "AWIS tools not found — run install.sh"; exit 2; }
python3 "$AWIS_TOOLS/$HELPER" "$@"
```

- `.nightshift/repo` in the target project is a one-line text file written by
  `install.sh` containing the absolute path of the AWIS checkout.
- Failure policy for helpers in AWIS is **gate** (fail loudly, block the step)
  unless the SKILL.md explicitly documents warn-and-skip for that helper.
  "Optional and automatic" is a rejected phrase — every integration is either
  required or explicitly opt-in.

## Runtime state convention

All AWIS runtime state in a *target* project lives under `.nightshift/`:

```
.nightshift/
├── repo                       # pointer to AWIS checkout (installer-written)
├── runs/<run_id>.json         # run_state.py stage states
├── runs/<run_id>.iterations.jsonl  # iteration_log.py staleness tracking
├── review/
│   ├── REVIEW_STATE.json      # cross-model-review loop state (24 h TTL)
│   ├── REVIEWER_MEMORY.md     # append-only reviewer context
│   └── ACQUITTAL_LOG.jsonl    # append-only cross-family sign-offs
├── watchdog/
│   ├── summary.txt
│   └── alerts.log
└── pending_review/            # manual-review file-mode handoff
```

Add `.nightshift/` to the target project's `.gitignore` (or commit it
deliberately if the team wants shared run history — decide per project).
