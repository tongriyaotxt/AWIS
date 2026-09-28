# 在 dsh-tui 中使用 AWIS

> English summary: see below. dsh-tui(DeepSeek 系执行器）使用 AWIS 的配置要点。

## 原理

dsh-tui 与 Kimi Code CLI 使用相同的 skill 约定（`SKILL.md` + YAML frontmatter），
用户级 skill 目录为 `~/.dsh/skills/`，MCP 通过 profile 补丁层
（`~/.dsh/profiles/dsh-tui/cordis.patch.yml`）注入。

**家族方向反过来**：dsh 是 deepseek 系执行器，所以评审必须是**非 deepseek**
家族 —— 默认 llm-chat 指向 Moonshot/Kimi API。指向 DeepSeek API 会被
`review_gate.py` 以同家族为由拒绝（fail-closed，这是特性）。

## 配置步骤

1. **skills**：把 4 个目录拷到 `~/.dsh/skills/`（注意摊平，不要嵌套）：

   ```bash
   cd ~/.dsh/skills
   cp -R /path/to/AWIS/skills/night-shift . && cp -R /path/to/AWIS/skills/cross-model-review . \
     && cp -R /path/to/AWIS/skills/morning-report . && cp -R /path/to/AWIS/skills/shared-references .
   ```

   profile 补丁需启用 `tool-skill` / `agent-instructions`（见 dsh-tui 的
   `cordis.patch.yml`）。

2. **MCP**：在 `cordis.patch.yml` 的 `- insert:` 列表追加：

   ```yaml
   - id: mcp-awis-manual-review
     name: '@deepseek-ai/dsh-mcp-client'
     config:
       serverName: manual-review
       transport: stdio
       command: python3
       args: ['<AWIS路径>\mcp-servers\manual-review\server.py']

   - id: mcp-awis-llm-chat
     name: '@deepseek-ai/dsh-mcp-client'
     config:
       serverName: llm-chat
       transport: stdio
       command: python3
       args: ['<AWIS路径>\mcp-servers\llm-chat\server.py']
       env:
         LLM_API_KEY: '<你的 Kimi key>'
         LLM_BASE_URL: 'https://api.kimi.com/coding/v1'   # Kimi Code 订阅 key 用这个端点
         LLM_MODEL: 'kimi-for-coding'                    # 名字必须含 "kimi"（见下）
         LLM_REVIEW_FALLBACK_ENABLED: '1'
   ```

   **两个实测的坑**（均已在本机踩过并修复）：
   - `sk-kimi-...` 开头的 Kimi Code 订阅 key **不通** `api.moonshot.cn`（401），
     它属于 Kimi Code 专用端点 `https://api.kimi.com/coding/v1`；Moonshot 开放平台
     的 key 才用 `api.moonshot.cn/v1`（模型名如 `kimi-k2-0905-preview`）。
   - `LLM_MODEL` 的名字里**必须含 "kimi"**（如 `kimi-for-coding`、`kimi-k2-*`）：
     `review_gate.py` 靠模型名识别家族，用 `k3` 这类不含 kimi 的名字会被判为
     未知家族 → `review_unavailable`（实测）。
   - 便捷方式：运行 `python tools/configure_dsh_kimi.py` 会弹出配置窗口，
     粘贴 key 保存即可（自动写入补丁并校验 dsh 解析）。

   改完用 `dsh --profile dsh-tui --dump-config` 验证补丁解析无误。

3. **tools 指针**：`~/.nightshift/repo`（`bash install.sh` 已写）让 skill
   在任何项目里找到 `tools/`。

4. **使用**：与 Kimi 会话相同 —— 项目里写 `TODO.md`，然后
   `/night-shift TODO.md — 授权"…"`。没有 Moonshot key 时评审用
   `— backend: manual`（人工中转，24h 超时容忍过夜）。

## 已验证 / 待验证（诚实标注）

- ✅ 已验证：skill 目录结构与 AWIS 源逐字节一致；补丁层 `dump-config` 解析通过；
  家族方向（dsh→Kimi 为异家族）经 `review_gate.py` 实测放行、同家族实测拒绝；
  Kimi Code 端点 + `kimi-for-coding` 真实 API 冒烟通过（200）。
- ⚠️ 待实测：dsh-tui 内 skill 的实际加载与 `allowed-tools` 字段的兼容性
  （dsh 工具命名与 Claude 风格不同，可能忽略该字段）；首次夜班前建议先跑一个
  小任务观察。

## English summary

AWIS works in dsh-tui: copy the 4 skill dirs (flattened) into `~/.dsh/skills/`,
register `manual-review` + `llm-chat` via the dsh-tui profile patch
(`cordis.patch.yml`), and point llm-chat at **Kimi** — dsh is a deepseek-family
executor, so a DeepSeek reviewer would be same-family and is refused by the gate.
Kimi Code subscription keys (`sk-kimi-...`) need `https://api.kimi.com/coding/v1`
with model `kimi-for-coding` (the model name must contain "kimi" for the gate's
family detection). Without a Kimi key, use `— backend: manual`.
Skill loading / `allowed-tools` compatibility in dsh-tui is not yet battle-tested.
