# Authorization Block — Run <RUN_ID>

Recited at night-shift startup, <DATE>. The agent acts ONLY within this boundary.

## Allowed (default, no further asking)

- Read the entire repository.
- Edit these paths only: `<src/ tests/ docs/>`
- Run: `<pytest / npm test / build / smoke commands>`; start/stop project services: `<list>`.
- Write reports under `.nightshift/` and `docs/reports/`.
- Create new scratch resources (temp branches, temp services, scratch dirs).

## Requires explicit naming by the user (stop and ask / park as 🛑)

- [ ] `git commit` (further restricted to: `<files or "none">`)
- [ ] `git push` — default: **forbidden**
- [ ] Deleting / resetting data, worlds, databases — default: **forbidden** (move to `.trash/` instead)
- [ ] Installing software / new dependencies
- [ ] Stopping non-project processes
- [ ] Editing outside the whitelist paths

## Project-injected hooks (from AGENTS.md / PROJECT_STATUS.md)

- Verify commands: `<project-specific gates>`
- Health checks: `<services / endpoints>`
- Taboos: `<project-specific prohibitions>`

## Rules

- Uncertain whether a gate is explicit → treat as explicit, stop there.
- Rejected-by-whitelist actions are logged to the task WORK_LOG, never silently dropped.
- Prefer creating new resources over deleting old ones.
