# Morning Report — <DATE> — Run <RUN_ID>

## 5-line summary

1. Passed: `<N items>` — `<headline>`
2. Not passed: `<N items>` — `<headline>`
3. Evidence: run `<RUN_ID>`, verdicts `<id1, id2>`, logs `.nightshift/`
4. Commits: `<hashes>` / uncommitted: `<files or "none">`
5. Next: `<single recommended action for today>`

## Badge board

| Badge | Item | Evidence | Note |
|---|---|---|---|
| ✅ | `<task>` | verdict `<id>` by `<reviewer model>` | |
| ⚠️ | `<task>` | tests `<64/64>`, **no cross-family signature** | resume: `/cross-model-review <task>` |
| ❌ | `<task>` | failure signature `<sig>` | bucket: `<capability/flake/test-design>` |
| 🛑 | `<blocker>` | needs: `<what>` | resume: `<one-line command>` |
| ⏭️ | `<task>` | not started | reason: `<budget/dependency>` |

> Badge rules: ✅ requires an ACQUITTAL_LOG entry signed by a *different model
> family*. Tests passing alone earns ⚠️ at best. Dev/scratch data is never
> acceptance evidence.

## Blockers waiting on you

1. `<🛑 item — decision needed — resume command>`

## Anomalies overnight

- Watchdog: `<STALE/death events or "none">`
- Stall pivots: `<tasks that needed structural pivot>`
- Rejected-by-whitelist: `<count, see WORK_LOGs>`
- Leftovers: `<uncommitted files / stray services>`

## Failure signatures updated

- `<new entries appended to docs/failure-signatures.md>`
