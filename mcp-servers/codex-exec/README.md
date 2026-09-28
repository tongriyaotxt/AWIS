# codex-exec — the `codex` MCP server, over `codex exec`

Adapted from ARIS (MIT), see NOTICE.

codex-cli 0.154.0 removed the `codex mcp-server` entry point that AWIS
registered as the `codex` MCP server. This bridge speaks the same contract —
tools `codex` and `codex-reply`, results `{threadId, content}` — and runs each
call as a `codex exec` subprocess. Nothing in the skills changes.

During an overnight coding run, AWIS uses this bridge to send code-review
prompts to Codex (a different model family than the executor) and to continue
the review thread across rounds while you sleep.

## Register

```bash
cd /d/项目/03_应用软件开发/AWIS          # your AWIS checkout
claude mcp remove codex -s user        # only if the old `codex mcp-server` registration exists
claude mcp add codex -s user -- python "$(pwd)/mcp-servers/codex-exec/server.py"
```

Use the absolute path of your AWIS checkout (`$(pwd)` from inside it). Restart
Claude Code; `claude mcp list` should show `codex … ✓ Connected`. Needs a
codex-cli version with `codex exec resume` (verified on 0.153.4 and 0.154.0).
Skills need no change.

Other MCP hosts (Cursor, Trae, Antigravity, Copilot CLI) use the same key with
`"command": "python", "args": ["/absolute/path/to/AWIS/mcp-servers/codex-exec/server.py"]`.

Requirements: `codex` on PATH and logged in; Python 3.9+; no packages.

## What a call becomes

| MCP argument | `codex exec` |
|---|---|
| `prompt` | stdin (no argv limit) |
| `model` | `-m MODEL` |
| `config` `{"model_reasoning_effort": "ultra"}` | `-c model_reasoning_effort="ultra"` (nested objects become dotted keys) |
| `sandbox` | `--sandbox MODE` |
| `cwd` | `--cd DIR` |
| `codex-reply` `threadId` | `codex exec resume THREAD` **plus the model, config, sandbox and cwd the thread was created with** — `resume` alone would fall back to `config.toml` defaults, and AWIS's routing contract relies on a continued thread keeping its reviewer model and effort |

Per-thread settings live in `~/.codex/state/codex-exec/threads/<threadId>.json`, one file each.

A failed turn (unknown model, auth, API error) comes back as `isError: true`
with codex's own error text, so the capability fallback in
`skills/shared-references/` keys on the same wording as before.

While a review runs the bridge streams `codex/event` notifications and, when the
host passes a `progressToken`, a `notifications/progress` heartbeat every 15 s
(`CODEX_EXEC_PROGRESS_INTERVAL_SEC`), answers `ping`, and honours
`notifications/cancelled`. Notifications cannot override a host's hard tool
timeout — deep code reviews at `ultra` effort can run 30+ minutes, which is
normal during an unattended night shift.

Not offered, because `codex exec` cannot honour them: `approval-policy`,
`base-instructions`, `developer-instructions`, `compact-prompt`. No AWIS skill
passed them.

Debugging: `CODEX_EXEC_DEBUG_LOG=/path/to/log` records every request and the
exact `codex exec` command line; `CODEX_BIN` points at a specific codex binary.
