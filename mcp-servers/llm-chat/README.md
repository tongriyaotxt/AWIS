# llm-chat — OpenAI-compatible HTTP reviewer backend (AWIS)

Adapted from ARIS (MIT), see NOTICE.

A generic MCP server that bridges MCP tool calls to any **OpenAI-compatible
chat-completions HTTP API**. In AWIS it serves as the cross-model review
backend for overnight coding runs: the executor (Kimi Code CLI or dsh/DeepSeek)
sends review prompts through this bridge to a reviewer model from a *different*
model family (e.g. DeepSeek API when the executor is Kimi, or Moonshot API when
the executor is DeepSeek).

Tools: `chat` (general LLM call with 504 retry + fallback model), plus opt-in
verdict-bearing `review` / `review_reply` (single-attempt, fail-closed,
cross-family enforced) enabled via `LLM_REVIEW_FALLBACK_ENABLED=true`.

## Install

```bash
pip install -r requirements.txt   # httpx is the only third-party dependency
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | (required) | API key for the provider |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible base URL |
| `LLM_MODEL` | `gpt-4o` | Model name for chat / reviewer |
| `LLM_FALLBACK_MODEL` | `gpt-4o` | Fallback model after repeated 504 (chat tool only) |
| `LLM_SERVER_NAME` | `llm-chat` | MCP server name |
| `LLM_REVIEW_FALLBACK_ENABLED` | `false` | Set `true` to expose the `review` / `review_reply` tools |

## Configuration examples

DeepSeek (use as reviewer when the executor is Kimi/Moonshot family):

```bash
export LLM_API_KEY=sk-xxx
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
export LLM_FALLBACK_MODEL=deepseek-chat
export LLM_REVIEW_FALLBACK_ENABLED=true
```

Moonshot / Kimi (use as reviewer when the executor is DeepSeek family):

```bash
export LLM_API_KEY=sk-xxx
export LLM_BASE_URL=https://api.moonshot.cn/v1
export LLM_MODEL=kimi-k2        # e.g. kimi-k2-thinking; check the official docs for the current model id
export LLM_FALLBACK_MODEL=kimi-k2
export LLM_REVIEW_FALLBACK_ENABLED=true
```

## Register

With Kimi Code CLI:

```bash
kimi mcp add llm-chat -- python3 /path/to/AWIS/mcp-servers/llm-chat/server.py
```

With Claude Code:

```bash
claude mcp add llm-chat -- python3 /path/to/AWIS/mcp-servers/llm-chat/server.py
```

The server reads its configuration from environment variables at startup, so
export them in the shell/profile that launches the MCP host (or configure them
in the host's MCP env settings) before registering.
