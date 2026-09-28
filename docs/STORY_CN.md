# A Night Shift Story — 一个普通周五夜里的真实使用过程

> English version: [STORY.md](STORY.md)
>
> 本故事是教学用叙事：人物与项目是虚构的，但**每一步命令、状态机输出、
> 门禁裁决都来自 AWIS 的真实运行**（评审模型的具体措辞为示意，真实运行时
> 由 llm-chat/codex/manual 后端产生）。

**人物**：林，后端程序员，维护一个 Flask 订单服务 `order-service`。
**时间**：某个周五，23:20。下周一要封版，backlog 里压着 5 件事。
他决定：今晚让 AWIS 值第一个夜班。

---

## 第一幕 · 睡前 20 分钟

### 23:22 — 写任务清单：什么该放进夜里

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

### 23:28 — 项目钩子与评审配置

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

### 23:35 — 启动

```text
/night-shift TODO.md — 授权"可改 src/ tests/ docs/，可跑 pytest，
可重启本地 dev server" — 需点名"git commit/push、动 migrations/、装依赖"
```

agent 复述了授权块并写入 `.nightshift/runs/night-001/AUTHORIZATION.md`。
林扫了一眼，发现复述里把 `docs/` 和 `migrations/` 列得太近，特意确认了
一遍 migrations 在"需点名"侧。确认无误，他去睡了。

---

## 第二幕 · 夜里（他睡着之后）

### 23:47 · task-1：顺风局

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

### 00:30 · task-2：评审真的在干活

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

### 01:15 · task-3：空转熔断

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

### 03:02 · task-4：授权块挡下一颗子弹

task-4 需要改 `migrations/`。agent 查了授权块——**不在白名单**。

它没有硬闯，也没有对着空房间提问（凌晨三点问了也没人答，turn 一结束
整夜就废了），而是做了一套标准动作：

1. 把"需要动 migrations/ 的迁移方案"写进任务日志；
2. task-4 标 **🛑 waiting-on-human**，附上恢复命令；
3. 继续干 task-5。

> 📌 **信条 7**：人类卡点有三条出路——能自决的记审计日志自决；必须人批
> 的推手机或停下；**绝不对着空房间提问**。第二天早上看到的不是七小时
> 空转，而是一行 🛑 加恢复命令。

### 03:40 · task-5：宁可挂着，不可错放

README 重写完成，测试也过，但送审时 DeepSeek API 恰好抽风，连续超时。
门禁返回（真实行为）：

```
decision: review_unavailable        ← 评审不可用 = 不能签字
```

task-5 被标为 **⚠️ done-unverified**：活干完了，但没人验收，那就不是 ✅。

> 📌 这就是 fail-closed 的全部含义：**系统宁可让一件完成的工作挂着，
> 也不让一件没验收的工作蒙混过关。**

### 04:10 · 收工

清单耗尽。`/morning-report` 自动汇总，晨报写好；配了飞书的话，此刻
林的手机会收到一张卡片。

---

## 第三幕 · 早上 7:40

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

## 这个故事教你的使用要点

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
