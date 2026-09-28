# AWIS 🌙 — Auto-Work-In-Sleep

<p align="center">
  <img src="assets/hero.svg" alt="AWIS — 晚上 11 点交出任务清单；执行器开车；异家族模型陪审团签字；早上 7 点读晨报" width="100%">
</p>

[![快速开始](https://img.shields.io/badge/🚀_快速开始-3_条命令-2E7D32?style=flat)](#快速开始) · [![使用手册](https://img.shields.io/badge/📖_使用手册-安装_→_第一次夜班-1a4a8c?style=flat)](docs/USAGE_CN.md) · [![信条](https://img.shields.io/badge/📜_信条-循环只能开车不能签字-4B2E83?style=flat)](#核心信条) · [![Skills](https://img.shields.io/badge/Skills-3_个-orange?style=flat)](#三个-skill) · [![测试](https://img.shields.io/badge/测试-226_通过_·_CI_ubuntu+%2B+macOS-brightgreen?style=flat)](#诚实性与测试) · [![运行时](https://img.shields.io/badge/运行时-Kimi_Code_CLI_·_dsh_·_Claude_Code_·_Codex-1a4a8c?style=flat)](#评审路由) · [![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

🌱 *AWIS 是一套纪律，不是一个平台。3 个 Markdown skill + 4 个纯标准库脚本 + 3 个 MCP 小桥 —— 你的 agent 去哪儿，它跟到哪儿。*

💡 *主力支持 [Kimi Code CLI](https://www.kimi.com/) 与 DeepSeek Harness（dsh）—— **Kimi 干的活由 DeepSeek 审，dsh 干的活由 Kimi 审** —— 有 Claude Code / Codex 也可以用。不需要 Claude 或 OpenAI 的 API key。*

⚔️ *[ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)（Auto-**Research**-In-Sleep）的姊妹项目。ARIS 在 ML 研究上验证了过夜方法论；AWIS 把同一件武器对准**每个程序员的任务清单**。*

---

## 凌晨三点的问题

现在的编程 agent 都能连续自主工作几小时。于是你睡前丢给它一份任务清单。但凌晨三点，空无一人的房间里，实际发生的是什么？

- agent **给自己的作业打分**。"测试过了，我觉得没问题" —— 写出 bug 的那个脑子，宣布 bug 修好了。
- 一个没人回答的问题 —— *"要不要删旧表？"* —— **杀死一整夜**。你早上看到的，是凌晨 1:07 发出的一句礼貌提问，和之后七个小时的空转。
- 或者相反：午夜一个自信的错方向，到早上滚成 **400 行没人审过的 diff**。
- 或者什么都没坏 —— 循环只是**空转**：同一个失败重试 40 次，没有新信息，token 照烧。

AWIS 用一句话杀死第一种死法，用一套机器杀死后三种：

> **循环只能开车，不能签字。**

执行器可以开一整夜的车，但永远不许给自己的工作签字。每个工作项都必须拿到**异家族模型的裁决** —— Kimi 的产出由 DeepSeek 判，DeepSeek 的由 Kimi 判，谁的都可以由 Codex/GPT 判，或者由人工中转判 —— 裁决走一张确定性的、有测试覆盖的转移表（`tools/review_gate.py`），并写进 append-only 日志，早上你可以边喝咖啡边审计。同家族的喝彩**直接拒绝（fail-closed）**：宁可挂着，不可错放。

## 核心信条

| # | 原则 | 防的死法 |
|---|---|---|
| 1 | **循环只能开车，不能签字。** 客观门（测试 exit code）机器自判；质量门必须*异家族模型*签字 | 自己给自己打分 |
| 2 | **启动授权块。** 读仓、改白名单路径、跑测试 —— 默认放行；commit/push/删除/装软件 —— 必须点名 | 凌晨三点爆破半径 |
| 3 | **done ≠ accepted。** 续跑时重验每一个没被外部签字的阶段 | "它说它做完了" |
| 4 | **证据等级制。** 确定性门 → 新环境鲁棒性 → 跨模型评审。低级证据不充高级验收 | 固定夹具表演 |
| 5 | **失败三分类。** capability gap / environment flake / test design flaw。空转 2 轮强制换思路，4 轮上报你 | 40 次重试的空转 |
| 6 | **定时器只等事实，不判胜负。** 定时等待仅用于外部事实 | 调度器和循环打架 |
| 7 | **人类卡点三条出路。** 能自决的记审计日志自决 → 推手机（飞书）→ 标 🛑 继续下一项 | 凌晨 1:07 的提问 |
| 8 | **晨报 5 行。** 过了 / 没过 / 证据 ID / commit 状态 / 下一步 | 早上考古 |

## 快速开始

> 📖 完整手册：[USAGE_CN.md](docs/USAGE_CN.md)

```bash
git clone https://github.com/tongriyaotxt/AWIS.git && cd AWIS
bash install.sh          # skills → ~/.kimi/skills（+ ~/.claude/skills），MCP 自动注册
# 把评审指向"对面"家族的 API（一段环境变量）：
export LLM_API_KEY=sk-... LLM_BASE_URL=https://api.deepseek.com/v1 LLM_MODEL=deepseek-chat
```

然后在任意项目里，睡前：

```
/night-shift TODO.md — 授权"可改 src/ tests/，可跑 pytest，禁止 commit"
```

早上看 `MORNING_REPORT.md`。一个 key 都没有？加 `— backend: manual`，评审会（按设计，最长 24h）等你早上把它贴给任意网页模型中转。

## 一个周五夜的故事（教学叙事）

> 人物与项目虚构，但每条命令、状态机输出、门禁裁决都来自 AWIS 的真实运行（评审措辞为示意）。

**人物**：林，后端程序员，维护一个 Flask 订单服务 `order-service`。
**时间**：某个周五，23:20。下周一要封版，backlog 里压着 5 件事。
他决定：今晚让 AWIS 值第一个夜班。

---

### 第一幕 · 睡前 20 分钟

#### 23:22 — 写任务清单：什么该放进夜里

林打开 `TODO.md`，写下 5 行。他心里有杆秤：**边界清晰、有客观验收标准
的活才适合过夜**；需求模糊、要动数据的活，写进去也是给早上添堵。

```markdown
# Backlog
- [ ] task-1: /api/orders 在 amount=0 时除零崩溃，应返回 400
- [ ] task-2: 给 utils.top_customers(orders, n) 补实现和测试（按消费额降序）
- [ ] task-3: parser 的边界情况补测试（空行、缺列、BOM 头）
- [ ] task-4: user 表加 last_login 字段（涉及 migrations/）
- [ ] task-5: README 的部署章节过时，按 docker-compose.yml 现状重写
```

task-4 他犹豫了一下还是写了 —— 但待会儿授权块里会把 `migrations/` 排除
在外。**写进清单 ≠ 授权去碰**，这正是两层设计的用意。

> 📌 **信条 2 预演**：清单是"希望做什么"，授权块是"允许做什么"。

#### 23:28 — 项目钩子与评审配置

项目里已有 `AGENTS.md`（写着 `pytest tests/ -q` 和"禁止动 migrations/"），
他把 `.nightshift/` 加进 `.gitignore`。

评审配置：林平时用 **Kimi Code CLI**，所以评审必须是**对面家族**——
DeepSeek。他在 shell 配置里早已写好：

```bash
export LLM_API_KEY=sk-****        # DeepSeek 的 key
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
```

> 📌 如果他用的是 dsh（DeepSeek 系）干活，这段就要指向 Moonshot/Kimi。
> 同家族评审会被门禁**直接拒绝**——后面 task-5 会看到另一面。

#### 23:35 — 启动

```text
/night-shift TODO.md — 授权"可改 src/ tests/ docs/，可跑 pytest，
可重启本地 dev server" — 需点名"git commit/push、动 migrations/、装依赖"
```

agent 复述了授权块并写入 `.nightshift/runs/night-001/AUTHORIZATION.md`。
林扫了一眼，发现复述里把 `docs/` 和 `migrations/` 列得太近，特意确认了
一遍 migrations 在"需点名"侧。确认无误，他去睡了。

---

### 第二幕 · 夜里（他睡着之后）

#### 23:47 · task-1：顺风局

计划落盘 → 改 1 个文件 → `pytest` 全绿（Type-A 门，自判有效）→
进入 Type-B：完整 diff + 测试输出 + 需求原文发给 DeepSeek。

第一轮，DeepSeek 打 **6/10 · almost**，挑了个刺：`amount=None` 时还是
500 而不是 400。agent 补上这个边界，重跑测试，再送审。第二轮
**8/10 · ready**。门禁裁决（真实输出）：

```
decision: stop        ← 异家族（deepseek 评 kimi）+ 分数达标 → 通过
```

```
   ✅  task-1  [accepted]  ← deepseek-chat / v-101
```

> 📌 **信条 1**：agent 自己说"修好了"只值 `done`；对面家族说 ready 才值
> `accepted`。签字记录在 `.nightshift/review/ACQUITTAL_LOG.jsonl`，
> append-only，早上可审计。

#### 00:30 · task-2：评审真的在干活

`top_customers` 实现送审，第一轮 DeepSeek 只给 **5/10 · not ready**：

> 1. [major] 消费额并列时返回顺序不确定，测试是 flaky 的；
> 2. [minor] 客户名大小写不统一会被当成两个人。

门禁裁决（真实输出）：

```
decision: continue | positive threshold not met     ← 分不够，回去改
```

agent 按 issue 修复（并列时按名字二次排序 + 归一化大小写），第二轮
**7/10 · ready** → ✅。

> 📌 如果评审是"自己人"，第一轮那根刺多半就被咽下去了。
> **这就是异家族评审存在的全部理由。**

#### 01:15 · task-3：空转熔断

补测试时接连 3 次失败，报错都是 `address already in use`。
`iteration_log` 记下：连续 2 轮没有新发现 → **强制换思路**。

agent 不再硬跑，转而归因：这不是代码 bug（capability gap），是**环境
flake**——它自己 23:47 重启的 dev server 还占着 8000 端口。停掉旧进程
重跑，测试通过。失败被记进 `docs/failure-signatures.md`：

```
| pytest 挂起 + "address already in use" | night-001 | dev server 残留占端口 | flake | 先停旧进程再跑 | fixed |
```

> 📌 **信条 5**：失败必须归类——能力 gap 修代码，环境 flake 降并发重跑，
> 测试设计 flaw 改测试。**不许归因都不做就重试 40 次。**

#### 03:02 · task-4：授权块挡下一颗子弹

task-4 需要改 `migrations/`。agent 查了授权块——**不在白名单**。

它没有硬闯，也没有对着空房间提问（凌晨三点问了也没人答，turn 一结束
整夜就废了），而是做了一套标准动作：

1. 把"需要动 migrations/ 的迁移方案"写进任务日志；
2. task-4 标 **🛑 waiting-on-human**，附上恢复命令；
3. 继续干 task-5。

> 📌 **信条 7**：人类卡点有三条出路——能自决的记审计日志自决；必须人批
> 的推手机或停下；**绝不对着空房间提问**。第二天早上看到的不是七小时
> 空转，而是一行 🛑 加恢复命令。

#### 03:40 · task-5：宁可挂着，不可错放

README 重写完成，测试也过，但送审时 DeepSeek API 恰好抽风，连续超时。
门禁返回（真实行为）：

```
decision: review_unavailable        ← 评审不可用 = 不能签字
```

task-5 被标为 **⚠️ done-unverified**：活干完了，但没人验收，那就不是 ✅。

> 📌 这就是 fail-closed 的全部含义：**系统宁可让一件完成的工作挂着，
> 也不让一件没验收的工作蒙混过关。**

#### 04:10 · 收工

清单耗尽。`/morning-report` 自动汇总，晨报写好；配了飞书的话，此刻
林的手机会收到一张卡片。

---

### 第三幕 · 早上 7:40

林端着咖啡打开 `MORNING_REPORT.md`：

```markdown
## 5-line summary
1. Passed: 3 items — task-1 除零修复, task-2 top_customers, task-3 parser 测试
2. Not passed: 0 failed; task-5 完成但未验收(评审 API 故障), task-4 需人工(动 migrations/)
3. Evidence: run night-001, verdicts v-101/v-102/v-103, .nightshift/review/ACQUITTAL_LOG.jsonl
4. Commits: 无(未授权) — 所有改动在工作区, 共 6 文件
5. Next: 先过 diff 再 commit; 一条命令给 task-5 补签字

## Badge board
| Badge | Item | Evidence |
|---|---|---|
| ✅ | task-1 | v-101 by deepseek-chat(2 rounds: 6/almost → 8/ready) |
| ✅ | task-2 | v-102 by deepseek-chat(2 rounds: 5/not-ready → 7/ready) |
| ✅ | task-3 | v-103 by deepseek-chat(环境 flake 归因后通过) |
| ⚠️ | task-5 | 测试通过但无签字 | resume: /cross-model-review task-5 |
| 🛑 | task-4 | 需动 migrations/ | 恢复: 与产品确认方案后手动迁移 |
```

他花 15 分钟：

```bash
git diff                        # 过目夜里的 6 个文件，质量正常
git add -p && git commit        # commit 从未授权 —— 这是留给他的人工环节
/cross-model-review task-5      # DeepSeek API 已恢复，补签 → ✅
```

task-4 留到上班和产品确认迁移方案 —— 它本来就不该在夜里发生。

> 📌 看晨报只需要 3 分钟：✅ 的可以信（有签字编号可查），⚠️ 的一键补签，
> 🛑 的本来就是你的活。**没有考古，没有惊喜。**

---

### 这个故事教你的使用要点

| 时点 | 你要做的 | 关键认知 |
|---|---|---|
| 睡前 | 写边界清晰的 TODO；确认评审指向对面家族；读授权复述 | 清单≠授权，两层设计 |
| 启动 | 授权块里把 commit/删改/数据迁移放在"需点名"侧 | 爆破半径在入睡前锁死 |
| 夜里 | 睡觉 | 卡点不会杀死夜晚：自决/手机/🛑 三出路 |
| 早上 | 看 5 行摘要 → diff 过目 → commit → 补签 ⚠️ → 处理 🛑 | ✅ 凭签字信任，不是凭感觉 |
| 日常 | 维护 failure-signatures.md | 同一坑不复发，复发优先修根因 |

**什么时候不要用夜班**：需求模糊的新功能（没有客观验收标准）、
涉及数据迁移/删除的活、需要连续产品判断的活。这些白天来。

现在轮到你了：挑一个项目，写 3~5 行 TODO，今晚 23:30 输入
`/night-shift TODO.md — 授权"…"`。明早的咖啡会更有味道。🌙

## 三个 skill

| Skill | 职责 |
|---|---|
| **`/night-shift`** | 过夜总编排。清单 → 授权块 → 每任务：迷你计划 → 最小修复 → 确定性门 → **跨模型评审** → 工作日志 → 下一项。人类卡点走 自决/手机/🛑 三条出路，绝不死停 |
| **`/cross-model-review`** | Type-B 验收门。把"诚实三件套"（完整 diff + 测试输出 + 需求原文，绝不给过滤后的子集）送给异家族模型；`review_gate.py` 裁决停/继续/升级；最多 4 轮；永不强放 |
| **`/morning-report`** | 把机器状态变成 3 分钟简报：✅ 已验收（必须有签字）/ ⚠️ 未验收 / ❌ 失败 / 🛑 等你批，附恢复命令。可选飞书推送 |

## 评审路由

评审必须与执行器**异家族**。以下全部经 `tools/review_gate.py` 实测：

| 执行器 | 评审 | 通道 | 配置 |
|---|---|---|---|
| Kimi Code CLI（moonshot） | DeepSeek（deepseek） | `llm-chat` MCP → `api.deepseek.com` | `LLM_API_KEY` |
| dsh / DeepSeek（deepseek） | Kimi（moonshot） | `llm-chat` MCP → `api.moonshot.cn` | `LLM_API_KEY` |
| 任意 | GPT/Codex（openai） | `codex-exec` MCP → codex CLI | codex CLI |
| 任意 | **你**，中转给任意网页模型 | `manual-review` MCP，24h 超时 | 无 |

把评审指向执行器自己家族（dsh → DeepSeek API），门会拒绝签字 —— `review_unavailable`，`identity_assurance: failed`。这不是 bug，这就是产品本身。

## 一夜长什么样

来自真实的端到端模拟（`run night-001`，执行器 `kimi-k2`，评审 `deepseek-chat`）：

```
run night-001
   ✅  task-1  [accepted]  ← deepseek-chat / v-001     （divide-by-zero 修复，7/10 ready）
   ✅  task-2  [accepted]  ← deepseek-chat / v-002     （calc.sub，第 1 轮 5/10 not-ready
                                                         → 修 → 第 2 轮 8/10 almost）
  resume → COMPLETE

run night-002
   ✓(unaccepted)  task-3  [done]                      （dsh 执行 → DeepSeek 评审：
  resume → task-3                                       同家族 —— 拒绝签字）
```

所有状态都落盘在目标项目的 `.nightshift/` —— run 状态机、append-only 的 `ACQUITTAL_LOG.jsonl`、空转追踪、watchdog 警报。会话可以死，状态机不死。`done` 没签字的，续跑时重验，绝不轻信。

## 架构

```
skills/            产品本体 —— Markdown 工作流（给 LLM 读的纪律）
  night-shift/  cross-model-review/  morning-report/  shared-references/
tools/           不许 LLM 自裁的部分 —— 纯标准库 Python，226 个测试
  review_gate.py    确定性裁决转移表，fail-closed 家族检查
  run_state.py      done ≠ accepted 状态机，原子写盘
  iteration_log.py  空转 → 强制换思路 → 上报人类
  watchdog.py       心跳停滞检测（只检测，不重启）
mcp-servers/     单文件桥（stdio 上的手写 JSON-RPC，零 SDK 依赖）
  llm-chat（DeepSeek/Kimi API）· manual-review（人工中转）· codex-exec · feishu-bridge
templates/       授权块 · 工作日志 · 交接 · 晨报 · 失败签名
```

## 诚实性与测试

- `python -m pytest tests/ -q` → **226 passed, 13 skipped**（skip：Windows 上 POSIX-only 的 codex 桥测试，Linux/macOS CI 上会跑）。
- 最关键的安全声明 —— *同家族永远签不了字* —— 不是散文，是一张有测试的转移表；上面的路由矩阵在 CI 里可复现。
- **尚未声称的事**：在真实任务清单上的完整生产级过夜。方法论与机制继承自两个实战验证过的亲本（ARIS 的研究循环、`night-auto-work` 在真实多服务项目上的过夜跑批）；AWIS 本体是新组装的，第一次真正的夜班是下一个里程碑。欢迎反馈。

## ARIS 家族

- [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) —— ML 研究的过夜 harness（文献 → idea → 实验 → 论文 → rebuttal）。AWIS 的门禁、状态机、看门狗与 MCP 桥改编自它（MIT），致谢 —— 见 [NOTICE](NOTICE)。
- **AWIS**（本仓库）—— 同一套方法论，给其他所有人的任务清单。研究是一个领域，编程是其余所有。

## 路线图

- [ ] 第一次生产级过夜（dogfood）—— *v0.1 的门*
- [ ] 远程/批量执行队列（SSH 任务调度器，改编自 ARIS `experiment-queue`）
- [ ] 一键插件打包
- [ ] 同一骨架上的更多领域包（运维 runbook、数据管道、写作）

## License

MIT —— 见 [LICENSE](LICENSE)；ARIS 血统署名见 [NOTICE](NOTICE)。
