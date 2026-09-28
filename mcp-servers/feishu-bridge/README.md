# Feishu Bridge Server (AWIS)

Adapted from ARIS (MIT), see NOTICE.

A small HTTP bridge that lets AWIS overnight coding runs push progress
notifications to Feishu/Lark and long-poll for your reply (e.g. approving a
checkpoint from your phone while the night shift keeps working).

## Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /send`   | Send a card (or text) message to a Feishu user, returns `message_id` |
| `GET  /poll`   | Long-poll for the user's reply to a `message_id` (`timeout` in seconds) |
| `POST /reply`  | Webhook-style hook: deliver a user reply into the bridge |
| `GET  /health` | Health check |

## Install

```bash
pip install -r requirements.txt   # lark-oapi is the only third-party dependency
```

## Run

```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
export FEISHU_USER_ID=ou_xxx        # open_id of the user who receives notifications
export BRIDGE_PORT=5000             # optional, default 5000

python mcp-servers/feishu-bridge/server.py
```

`FEISHU_APP_ID` and `FEISHU_APP_SECRET` are required. Without `FEISHU_USER_ID`,
`/send` requires a `user_id` in the request body.

## User-side config convention (`~/.claude/feishu.json`)

The bridge itself reads only environment variables. AWIS skills, however, may
check for a user-side config file `~/.claude/feishu.json` (same convention as
the upstream project) to decide whether Feishu notifications are enabled and
which bridge port to talk to. This path is a **user-side convention and is
intentionally unchanged** — if the file is absent or its mode is `"off"`, all
Feishu functionality is skipped silently and skills behave as before.
