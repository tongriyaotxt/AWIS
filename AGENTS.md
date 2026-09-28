# AGENTS.md

Guidance for AI coding agents working in this repository. Read this before making changes.

## Project overview

**AWIS (Auto-Work-In-Sleep)** — an overnight, unattended autonomous-work harness
for AI coding agents (primary runtimes: **Kimi Code CLI** and **dsh-tui**;
Claude Code / Codex also supported). Sibling project of ARIS (research-domain);
AWIS targets **all work, programmers first**.

Key architectural facts:

- **There is no application to build.** The skill layer is plain Markdown
  (`SKILL.md` with YAML frontmatter). No framework, no build step, no
  dependency manifest at the repo root.
- The only Python code lives in `tools/` (4 stdlib-only scripts) and
  `mcp-servers/` (3 single-file stdio/HTTP servers).
- Lineage and attribution: see `NOTICE`. Components adapted from ARIS (MIT)
  must retain their attribution there.

## Repository layout

| Path | Contents |
|---|---|
| `skills/` | 3 skills (`night-shift`, `cross-model-review`, `morning-report`) + `shared-references/` doctrine docs. The core product. |
| `tools/` | stdlib-only Python 3.9+ helpers invoked by skills (`review_gate.py`, `run_state.py`, `iteration_log.py`, `watchdog.py`) plus the `configure_dsh_kimi.py` dsh-tui setup popup. |
| `mcp-servers/` | `llm-chat` (OpenAI-compatible reviewer bridge, dep: `httpx`), `manual-review`, `codex-exec` (stdio MCP, zero-dep, optional); `feishu-bridge` (HTTP, dep: `lark-oapi`). |
| `templates/` | Copy-and-fill runtime templates (authorization block, work log, handoff, morning report, failure signatures). |
| `tests/` | pytest suite for `tools/` and `mcp-servers/`. |
| `install.sh` | Installer: copies skills to `~/.claude/skills` / `~/.kimi/skills`, registers MCP servers, writes resolver pointer. |

## Build, install, and test commands

No build step. Everything except `feishu-bridge` and `llm-chat` is zero-dependency stdlib Python (3.9+).

```bash
python -m pip install pytest httpx
python -m pytest tests/ -q
bash install.sh --dry-run        # preview install actions
```

## Reviewer routing (Kimi/dsh primary setup)

The Type-B gate reviewer must be a **different model family** from the
executor. Default matrix (all empirically verified against `tools/review_gate.py`):

| Executor | Reviewer backend | API config | Gate flag |
|---|---|---|---|
| Kimi Code CLI (moonshot) | `llm-chat` → DeepSeek API | `LLM_BASE_URL=https://api.deepseek.com/v1` | no flag (family check built in) |
| dsh (deepseek) | `llm-chat` → Moonshot/Kimi API | `LLM_BASE_URL=https://api.moonshot.cn/v1` | no flag |
| any + codex CLI | `codex` (openai) | codex CLI | `--requires-external-acquittal` REQUIRED |
| no keys | `manual` human relay | none | flag + `--manual-identity-reported` |

Never point `llm-chat` at the same family as the executor (e.g. dsh → DeepSeek
API) — the gate is fail-closed and will refuse to acquit, by design.

## Code style guidelines

- **Skills are the product.** A skill is a directory with a `SKILL.md`:
  YAML frontmatter (`name`, `description`, `argument-hint`, `allowed-tools`)
  followed by a Markdown workflow (`## Workflow`, `### Step N`, `$ARGUMENTS`).
  The behavior source of truth for a skill is always its own `SKILL.md`.
- **Keep everything stdlib-only.** Do not add third-party dependencies to
  `tools/` or MCP servers unless there is no reasonable stdlib alternative
  (precedent: `lark-oapi` for feishu-bridge, with its own `requirements.txt`).
- Python conventions: module docstring naming the owning skill,
  `from __future__ import annotations`, `argparse` CLIs for `tools/` scripts.
- **Helper-resolution contract**: SKILL.md files must not hardcode
  `python3 tools/<helper>.py` paths; follow
  `skills/shared-references/integration-contract.md`.
- Runtime state lives under `.nightshift/` in the *target* project (not this
  repo): runs, review state, acquittal logs, watchdog summaries.
  `.nightshift/` must be gitignored here and documented for users.
- Line endings: LF repo-wide via `.gitattributes`.
- Shell scripts must work with macOS bash 3.2.
- Documentation: English primary, Chinese `*_CN.md` counterparts for
  user-facing docs. Update both when behavior changes.

## Core doctrine (do not weaken)

1. **A loop can DRIVE; it cannot ACQUIT.** Type-A gates (exit codes, file
   existence) may be self-judged; Type-B gates (quality/correctness verdicts)
   must be signed by a different model family via `tools/review_gate.py`
   (fail-closed: same-family or unknown-family can never acquit).
2. **done ≠ accepted** in `tools/run_state.py`; resume re-verifies unsigned stages.
3. `tools/watchdog.py` and `tools/iteration_log.py` are the mechanical
   anti-stall/anti-spin guards — preserve their "detect, never restart" and
   "stale → pivot → escalate" semantics.
4. MCP servers handle API keys from env vars — never log secrets.

See `skills/shared-references/acceptance-gate.md` for the full gate taxonomy.

## Testing instructions

- Framework: pytest, no `conftest.py`, no config file. Tests import tool/server
  modules via `importlib.util` without triggering stdio rebinding.
- Environment-dependent tests self-skip (e.g. live codex CLI tests need the
  `codex` binary). Do not add hard skips that mask real failures.
- CI: `.github/workflows/test.yml` runs pytest on ubuntu + macOS.

## Security considerations

- Never commit secrets. `.env` is gitignored; `.env.example` documents
  optional integration keys (Feishu). Core AWIS needs none.
- `.nightshift/` runtime state is gitignored.
- Diff content sent to external reviewer CLIs is user code — treat as
  sensitive; honor the `*_DEBUG_LOG` opt-in pattern, never log by default.
