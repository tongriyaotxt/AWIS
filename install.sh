#!/usr/bin/env bash
# AWIS installer — installs skills into agent skill directories, registers
# MCP servers, and writes the helper-resolution pointer.
# Compatible with macOS bash 3.2. Usage:
#   bash install.sh [--dry-run] [--uninstall] [--skills-only] [--no-mcp]
set -u

AWIS_ROOT="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=0
UNINSTALL=0
NO_MCP=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --no-mcp) NO_MCP=1 ;;
    -h|--help)
      echo "Usage: bash install.sh [--dry-run] [--uninstall] [--no-mcp]"
      exit 0 ;;
    *) echo "Unknown flag: $arg" >&2; exit 2 ;;
  esac
done

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

SKILL_NAMES="night-shift cross-model-review morning-report shared-references"

# --- skill target directories -------------------------------------------------
TARGETS=""
[ -d "$HOME/.claude" ] && TARGETS="$TARGETS $HOME/.claude/skills"
[ -d "$HOME/.kimi" ]   && TARGETS="$TARGETS $HOME/.kimi/skills"
if [ -z "$TARGETS" ]; then
  TARGETS="$HOME/.claude/skills"
fi

for target in $TARGETS; do
  for skill in $SKILL_NAMES; do
    src="$AWIS_ROOT/skills/$skill"
    dst="$target/$skill"
    if [ "$UNINSTALL" -eq 1 ]; then
      [ -d "$dst" ] && run rm -rf "$dst" && echo "removed $dst"
      continue
    fi
    echo "installing skill: $skill -> $dst"
    run mkdir -p "$dst"
    if [ "$DRY_RUN" -eq 0 ]; then
      cp -R "$src/" "$dst/"
    else
      echo "[dry-run] cp -R $src/ $dst/"
    fi
  done
done

# --- helper-resolution pointer -------------------------------------------------
if [ "$UNINSTALL" -eq 1 ]; then
  [ -f "$HOME/.nightshift/repo" ] && run rm -f "$HOME/.nightshift/repo"
else
  run mkdir -p "$HOME/.nightshift"
  if [ "$DRY_RUN" -eq 0 ]; then
    printf '%s\n' "$AWIS_ROOT" > "$HOME/.nightshift/repo"
  else
    echo "[dry-run] write $AWIS_ROOT -> $HOME/.nightshift/repo"
  fi
fi

# --- MCP servers ---------------------------------------------------------------
if [ "$NO_MCP" -eq 0 ] && [ "$UNINSTALL" -eq 0 ]; then
  REGISTERED=0
  if command -v kimi >/dev/null 2>&1; then
    echo "registering MCP servers with kimi..."
    run kimi mcp add llm-chat -- python3 "$AWIS_ROOT/mcp-servers/llm-chat/server.py" || true
    run kimi mcp add manual-review -- python3 "$AWIS_ROOT/mcp-servers/manual-review/server.py" || true
    REGISTERED=1
  fi
  if command -v claude >/dev/null 2>&1; then
    echo "registering MCP servers with claude..."
    run claude mcp add llm-chat -- python3 "$AWIS_ROOT/mcp-servers/llm-chat/server.py" || true
    run claude mcp add manual-review -- python3 "$AWIS_ROOT/mcp-servers/manual-review/server.py" || true
    # codex-exec is only useful when the codex CLI is present:
    if command -v codex >/dev/null 2>&1; then
      run claude mcp add codex-exec -- python3 "$AWIS_ROOT/mcp-servers/codex-exec/server.py" || true
    fi
    REGISTERED=1
  fi
  if [ "$REGISTERED" -eq 0 ]; then
    echo "NOTE: no supported CLI found; register MCP servers manually, e.g.:"
    echo "  kimi mcp add llm-chat -- python3 $AWIS_ROOT/mcp-servers/llm-chat/server.py"
    echo "  kimi mcp add manual-review -- python3 $AWIS_ROOT/mcp-servers/manual-review/server.py"
  fi
  echo "NOTE: llm-chat needs LLM_API_KEY/LLM_BASE_URL/LLM_MODEL pointing at the"
  echo "      OPPOSITE model family's API (see mcp-servers/llm-chat/README.md)."
  echo "NOTE: feishu-bridge is an HTTP server (optional). See mcp-servers/feishu-bridge/README.md."
fi

echo "AWIS install $([ "$UNINSTALL" -eq 1 ] && echo 'uninstall ')done. Skills: $SKILL_NAMES"
