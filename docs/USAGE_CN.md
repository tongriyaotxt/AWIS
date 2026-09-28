# AWIS 使用手册 —— 从安装到第一次夜班

> English version: [USAGE.md](USAGE.md)

这份指南走一遍完整闭环：安装 → 配置 → 准备项目 → 开夜班 → 看晨报 → 从卡点恢复。

## 1. 安装

```bash
git clone https://github.com/tongriyaotxt/AWIS.git && cd AWIS
bash install.sh
```

安装器做了三件事（随时可用 `bash install.sh --dry-run` 预览）：

1. 把 3 个 skill + `shared-references/` 拷进 `~/.kimi/skills/`
   （如果存在 `~/.claude/skills/` 也会拷一份）。
2. 向在场的 CLI 注册 MCP server（`kimi mcp add …` / `claude mcp add …`）：
   `llm-chat`、`manual-review`（检测到 codex CLI 才注册 `codex-exec`）。
3. 写 `~/.nightshift/repo` —— 一行指向本仓库的路径，让 skill 能在任何
   项目里找到 `tools/`。

验证：

```bash
kimi mcp list                 # 应出现 llm-chat 和 manual-review
kimi mcp test manual-review   # 2 个工具: review, review_reply
ls ~/.kimi/skills/            # night-shift, cross-model-review, morning-report
```

> **Windows 注意**：如果 `kimi mcp test` 报
> `UnicodeEncodeError: 'gbk' codec`，那是 CLI 控制台渲染的怪癖，不是
> server 的问题。先 `export PYTHONIOENCODING=utf-8`（或写进 shell 配置文件）。

## 2. 配置评审（一段环境变量）

评审必须是你执行器的**对面家族**：

| 你的执行器 | llm-chat 指向 | 环境变量 |
|---|---|---|
| Kimi Code CLI | DeepSeek | `LLM_BASE_URL=https://api.deepseek.com/v1`，`LLM_MODEL=deepseek-chat` |
| dsh（DeepSeek） | Moonshot/Kimi | `LLM_BASE_URL=https://api.moonshot.cn/v1`，`LLM_MODEL=kimi-k2` |

```bash
export LLM_API_KEY=sk-你的key
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
export LLM_REVIEW_FALLBACK_ENABLED=1   # 同时暴露 review 工具
```

持久化：写进 shell 配置文件，或注册 MCP 时带上
（`kimi mcp add llm-chat -e LLM_API_KEY=... -e LLM_BASE_URL=... -- python3 ...`）。

**没有 API key？** 跳过本节，评审时用 `— backend: manual`。评审会停在那里
（按设计最长 24h），等你把 prompt 贴给任意网页模型、把回复贴回来。零成本。

**飞书推送（可选）**：见 `mcp-servers/feishu-bridge/README.md`。配好后
checkpoint 和晨报会推到你手机，interactive 模式让你躺在床上 approve/reject。

## 3. 准备目标项目（5 分钟）

在要被干活的项目里：

```bash
# 1. 任务清单 —— 每行一个能独立完成的任务
cat > TODO.md <<'EOF'
# Backlog
- [ ] 修 calc.divide 的除零崩溃（应返回 None）
- [ ] 加 calc.sub(a, b) 并补测试
- [ ] 给 parser 边界情况补测试
EOF

# 2. 让 git 忽略运行状态
echo ".nightshift/" >> .gitignore
```

可选但推荐 —— agent 会最先读的项目钩子：

- `AGENTS.md`：构建/测试命令、服务健康检查、禁忌。
- `docs/failure-signatures.md`（模板在 `templates/FAILURE_SIGNATURES_TEMPLATE.md`）：
  已知复发故障；其根因会插到优先级最前。
- 带「下一步」段的 `PROJECT_STATUS.md` —— 可当默认任务清单用。

## 4. 开夜班

在项目目录里，对你的 agent CLI 说：

```
/night-shift TODO.md — 授权"可改 src/ tests/ docs/，可跑 pytest，可重启 dev server" — 需点名"git commit、删除 fixture"
```

读一遍它打印的授权复述。边界不对就现在改 —— 这是你睡前欠它的最后一件事。

常用覆盖项：

```
/night-shift TODO.md — max-tasks: 5 — time-budget: 8h
/night-shift — resume night-001            # 续跑中断的 run
/night-shift — checkpoint: true            # 每个任务暂停等 "go/skip/stop"
```

## 5. 夜里发生什么（你不用盯）

每个任务：计划落盘 → 1~2 个文件的最小修复 → 构建/测试（客观门，自判）
→ **跨模型评审**（diff + 测试输出 + 你的需求原文送给对面家族，最多 4 轮）
→ 带证据的工作日志 → 下一个任务。人类卡点：能安全自决的记审计日志自决；
配了飞书就推你手机；否则标 🛑 然后去做下一个独立任务。连续 2 轮无进展
强制换思路；4 轮上报你。

## 6. 早上

打开项目根目录的 `MORNING_REPORT.md`：

- **✅ 项** —— 完成且有异家族签字（verdict ID 可查
  `.nightshift/review/ACQUITTAL_LOG.jsonl`）。这些可以信。
- **⚠️ 项** —— 做完但没签字。恢复命令就在旁边：`/cross-model-review <任务>`。
- **❌ 项** —— 失败，附失败签名和归因桶。
- **🛑 项** —— 等只有你能做的决定，每条附一行恢复命令。
- 其实只看顶部的 5 行摘要就够了。

早上常见动作：

```bash
git diff                          # 看看夜里产出了什么
git add -p && git commit          # commit 没被授权，所以由你来做
/cross-model-review task-3        # 清掉一个 ⚠️ 项
```

## 7. 夜里跑死了怎么办

机器重启、终端被关、context 被压缩 —— 都没关系：

```
/night-shift — resume <run-id>
```

状态机（`.nightshift/runs/<run-id>.json`）会指向第一个没被外部验收的
阶段；`done` 但没签字的阶段会被重验，绝不跳过。如果存在 `HANDOFF.md`，
新会话会先读它。

## 8. 命令速查（tools/，平时基本不用手敲）

```bash
python3 "$AWIS_ROOT/tools/run_state.py" status . <run-id>      # run 跑到哪了
python3 "$AWIS_ROOT/tools/run_state.py" resume . <run-id>      # 第一个未签字阶段
python3 "$AWIS_ROOT/tools/iteration_log.py" show . <run-id>    # 空转历史
python3 "$AWIS_ROOT/tools/watchdog.py" --status                # 死了/停了的循环
python3 "$AWIS_ROOT/tools/review_gate.py" --round-backend llm-chat \
  --score 7 --verdict ready --executor-model kimi-k2 \
  --reviewer-model deepseek-chat                               # 试跑一次裁决
```

## 9. 故障排查

| 症状 | 原因 → 解法 |
|---|---|
| `review_unavailable`，`identity_assurance: failed` | 评审和执行器同家族（如 dsh → DeepSeek API）。把 llm-chat 指向对面家族，或 `— backend: manual` |
| `AWIS tools not found` | `~/.nightshift/repo` 丢了 → 重跑 `bash install.sh` |
| `kimi mcp test` 能连但调用失败 | server 环境里没 `LLM_API_KEY`/`LLM_BASE_URL` → 带 `-e` 参数重新注册 |
| 晨报全是 ⚠️ | 评审后端挂了一整夜 —— 活干完了但没签字；逐条 `/cross-model-review <任务>` 补签 |
| Windows 乱码 / UnicodeEncodeError | `export PYTHONIOENCODING=utf-8` |

## 10. 保命规则（不要关）

1. 晨报里的 ✅ 必须能在 `ACQUITTAL_LOG.jsonl` 找到异家族签字。
2. `done` ≠ `accepted` —— 续跑永远重验。
3. 除非你在授权块里点了名，agent 不会 commit/push/删除。
4. agent 能自己答的问题就自己答并记日志，绝不对着空房间提问；答不了的
   标 🛑，夜班继续。
