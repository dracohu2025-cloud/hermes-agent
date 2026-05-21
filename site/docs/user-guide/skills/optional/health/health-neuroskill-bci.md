---
title: "Neuroskill Bci"
sidebar_label: "Neuroskill Bci"
description: "连接到正在运行的 NeuroSkill 实例，并将用户的实时认知与情绪状态（专注度、放松度、情绪、认知负荷、困倦程度、心率、心率变异性、睡眠分期以及 40 多项衍生 EXG 评分）融入响应中。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="neuroskill-bci"></a>
# Neuroskill Bci

连接到正在运行的 NeuroSkill 实例，并将用户的实时认知与情绪状态（专注度、放松度、情绪、认知负荷、困倦程度、心率、心率变异性、睡眠分期以及 40 多项衍生 EXG 评分）融入响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）以及本地运行的 NeuroSkill 桌面应用。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/health/neuroskill-bci` 安装 |
| 路径 | `optional-skills/health/neuroskill-bci` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Nous Research |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `BCI`、`神经反馈`、`健康`、`专注度`、`EEG`、`认知状态`、`生物特征`、`neuroskill` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::
<a id="neuroskill-bci-integration"></a>
# NeuroSkill BCI 集成

将 Hermes 连接到正在运行的 [NeuroSkill](https://neuroskill.com/) 实例，以读取来自 BCI 可穿戴设备的实时大脑和身体指标。利用这些数据提供认知感知响应、建议干预措施，并随时间追踪心理表现。

> **⚠️ 仅限研究用途** — NeuroSkill 是一个开源研究工具。它**不是**医疗设备，**未经过** FDA、CE 或任何监管机构的批准。切勿将这些指标用于临床诊断或治疗。

完整的指标参考请见 `references/metrics.md`，干预协议请见 `references/protocols.md`，WebSocket/HTTP API 请见 `references/api.md`。

---

<a id="prerequisites"></a>
## 前提条件

- 已安装 **Node.js 20+**（`node --version`）
- **NeuroSkill 桌面应用**正在运行，并已连接 BCI 设备
- **BCI 硬件**：Muse 2、Muse S 或 OpenBCI（通过 BLE 连接 4 通道脑电图 + 光电容积描记 + 惯性测量单元）
- `npx neuroskill status` 返回数据且无错误

<a id="verify-setup"></a>
### 验证安装
```bash
node --version                    # 必须为 20+
npx neuroskill status             # 完整系统快照
npx neuroskill status --json      # 机器可解析的 JSON
```
如果 `npx neuroskill status` 返回错误，请告知用户：
- 确保 NeuroSkill 桌面应用已打开
- 确保 BCI 设备已开机并通过蓝牙连接
- 检查信号质量 — NeuroSkill 中的绿色指示（每电极 ≥0.7）
- 如果显示 `command not found`，请安装 Node.js 20+

---

<a id="cli-reference-npx-neuroskill"></a>
## CLI 参考：`npx neuroskill &lt;command&gt;`

所有命令均支持 `--json`（原始 JSON，管道安全）和 `--full`（人类可读摘要 + JSON）。

| 命令 | 描述 |
|---------|-------------|
| `status` | 完整系统快照：设备、分数、频带、比值、睡眠、历史 |
| `session [N]` | 单次 session 详情，包含前/后半段趋势（0=最近一次） |
| `sessions` | 列出所有天数的所有已记录 session |
| `search` | ANN 相似性搜索，查找神经上相似的历史时刻 |
| `compare` | A/B session 比较，包含指标差异和趋势分析 |
| `sleep [N]` | 睡眠阶段分类（清醒/N1/N2/N3/REM），带分析 |
| `label "text"` | 在当前时刻创建带时间戳的注释 |
| `search-labels "query"` | 对过去标签进行语义向量搜索 |
| `interactive "query"` | 跨模态 4 层图搜索（文本 → EXG → 标签） |
| `listen` | 实时事件流（默认 5 秒，可设置 `--seconds N`） |
| `umap` | session 嵌入的 3D UMAP 投影 |
| `calibrate` | 打开校准窗口并启动配置文件 |
| `timer` | 启动专注计时器（番茄钟/深度工作/短时专注预设） |
| `notify "title" "body"` | 通过 NeuroSkill 应用发送操作系统通知 |
| `raw '{json}'` | 原始 JSON 直通到服务器 |
<a id="global-flags"></a>
### 全局标志
| 标志 | 描述 |
|------|-------------|
| `--json` | 原始 JSON 输出（无 ANSI，管道安全） |
| `--full` | 人类可读摘要 + 彩色 JSON |
| `--port &lt;N&gt;` | 覆盖服务器端口（默认：自动发现，通常是8375） |
| `--ws` | 强制使用 WebSocket 传输 |
| `--http` | 强制使用 HTTP 传输 |
| `--k &lt;N&gt;` | 最近邻数量（用于 search, search-labels） |
| `--seconds &lt;N&gt;` | 监听持续时间（默认：5） |
| `--trends` | 显示每个会话的指标趋势（会话） |
| `--dot` | Graphviz DOT 格式输出（交互式） |

---

<a id="1-checking-current-state"></a>
## 1. 检查当前状态

<a id="get-live-metrics"></a>
### 获取实时指标
```bash
npx neuroskill status --json
```

**始终使用 `--json`** 以获得可靠的解析。默认输出是彩色的人类可读文本。

<a id="key-fields-in-the-response"></a>
### 响应中的关键字段

`scores` 对象包含所有实时指标（除非另有说明，范围均为 0–1）：

```jsonc
{
  "scores": {
    "focus": 0.70,           // β / (α + θ) — 持续注意力
    "relaxation": 0.40,      // α / (β + θ) — 平静清醒
    "engagement": 0.60,      // 积极的脑力投入
    "meditation": 0.52,      // Alpha波 + 静止 + HRV 相干性
    "mood": 0.55,            // 由 FAA、TAR、BAR 综合得出
    "cognitive_load": 0.33,  // 前额θ / 颞叶α · f(FAA, TBR)
    "drowsiness": 0.10,      // TAR + TBR + 频谱质心下降
    "hr": 68.2,              // 心率，单位 bpm（来自 PPG）
    "snr": 14.3,             // 信噪比，单位 dB
    "stillness": 0.88,       // 0–1；1 = 完全静止
    "faa": 0.042,            // 前额Alpha不对称性（正值表示接近）
    "tar": 0.56,             // Theta/Alpha 比率
    "bar": 0.53,             // Beta/Alpha 比率
    "tbr": 1.06,             // Theta/Beta 比率（ADHD 替代指标）
    "apf": 10.1,             // Alpha峰频率，单位 Hz
    "coherence": 0.614,      // 半球间相干性
    "bands": {
      "rel_delta": 0.28, "rel_theta": 0.18,
      "rel_alpha": 0.32, "rel_beta": 0.17, "rel_gamma": 0.05
    }
  }
}
```
也包括：`device`（状态、电量、固件）、`signal_quality`（每个电极的 0–1 值）、
`session`（时长、eopchs）、`embeddings`、`labels`、`sleep` 摘要以及 `history`。

<a id="interpreting-the-output"></a>
### 解读输出

解析 JSON 并将指标转化为自然语言。永远不要只汇报原始数字——要赋予它们意义：

**正确做法：**
> “你目前的专注度很扎实，达到 0.70 —— 这属于心流状态区间。心率稳定在 68 bpm，FAA 为正，表明接近动机良好。这正是处理复杂任务的好时机。”

**错误做法：**
> “专注度：0.70，放松度：0.40，心率：68”

关键解读阈值（完整指南见 `references/metrics.md`）：
- **专注度 > 0.70** → 心流状态区间，保持好
- **专注度 < 0.40** → 建议休息或执行协议
- **困倦度 > 0.60** → 疲劳警告，存在微睡眠风险
- **放松度 < 0.30** → 需要压力干预
- **认知负荷 > 0.70 持续** → 大脑排空或休息
- **TBR > 1.5** → θ 波主导，执行控制下降
- **FAA < 0** → 退缩/负面情绪 —— 考虑进行 FAA 重新平衡
- **SNR < 3 dB** → 信号不可靠，建议重新调整电极位置

## 3. 历史检索

### 神经相似性检索
```bash
npx neuroskill search --json                    # 自动：最近一次会话，k=5
npx neuroskill search --k 10 --json             # 10 个最近邻居
npx neuroskill search --start <UTC> --end <UTC> --json
```
使用 HNSW 近似最近邻搜索在 128 维 ZUNA 嵌入上查找历史上神经相似的时刻。返回距离统计、时间分布（一天中的小时）以及最佳匹配天数。

当用户提出以下问题时使用此功能：
- "我上次处于类似状态是什么时候？"
- "找到我最佳的专注时段"
- "我通常下午什么时候状态崩溃？"

<a id="semantic-label-search"></a>
### 语义标签搜索
```bash
npx neuroskill search-labels "deep focus" --k 10 --json
npx neuroskill search-labels "stress" --json | jq '[.results[].EXG_metrics.tbr]'
```

使用向量嵌入（Xenova/bge-small-en-v1.5）搜索标签文本。返回匹配的标签及其在标记时的关联 EXG 指标。

<a id="cross-modal-graph-search"></a>
### 跨模态图搜索
```bash
npx neuroskill interactive "deep focus" --json
npx neuroskill interactive "deep focus" --dot | dot -Tsvg > graph.svg
```

4 层图：查询 → 文本标签 → EXG 点 → 附近标签。使用 `--k-text`、`--k-EXG`、`--reach &lt;minutes&gt;` 进行调整。

---

<a id="4-session-comparison"></a>
## 4. 会话比较
```bash
npx neuroskill compare --json                   # 自动：最近两次会话
npx neuroskill compare --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```
返回约 50 个指标的绝对变化、百分比变化和方向等指标增量。同时包含 `insights.improved[]` 和 `insights.declined[]` 数组、两次会话的睡眠分期数据以及一个 UMAP 任务 ID。

解读对比时要结合上下文——提及趋势，而不仅仅是增量：
> “昨天你有两个强专注时段（上午 10 点和下午 2 点）。今天你从上午 11 点左右开始有一个专注时段，目前仍在持续。你今天的整体参与度更高，但压力峰值也更多——你的压力指数上升了 15%，FAA 更频繁地出现负值。”

```bash
# 按改善百分比排序指标
npx neuroskill compare --json | jq '.insights.deltas | to_entries | sort_by(.value.pct) | reverse'
```

---

<a id="5-sleep-data"></a>
## 5. 睡眠数据
```bash
npx neuroskill sleep --json                     # 最近 24 小时
npx neuroskill sleep 0 --json                   # 最近一次睡眠会话
npx neuroskill sleep --start <UTC> --end <UTC> --json
```

返回逐 epoch 的睡眠分期（5 秒窗口）及分析：
- **分期代码**：0=清醒，1=N1，2=N2，3=N3（深睡），4=REM
- **分析**：效率百分比、入睡潜伏期（分钟）、REM 潜伏期（分钟）、片段计数
- **健康目标**：N3 15–25%，REM 20–25%，效率 >85%，入睡潜伏期 &lt;20 分钟
```bash
npx neuroskill sleep --json | jq '.summary | {n3: .n3_epochs, rem: .rem_epochs}'
npx neuroskill sleep --json | jq '.analysis.efficiency_pct'
```

当用户提到睡眠、疲劳或恢复时使用此命令。

---

<a id="6-labeling-moments"></a>
## 6. 标记时刻
```bash
npx neuroskill label "突破"
npx neuroskill label "学习算法"
npx neuroskill label "冥想后"
npx neuroskill label --json "专注块开始"   # 返回 label_id
```

在以下情况自动标记时刻：
- 用户报告突破或洞见
- 用户开始新任务类型（例如"切换到代码审查"）
- 用户完成重要协议
- 用户要求你标记当前时刻
- 发生显著状态转换（进入/离开心流状态）

标签存储在数据库中，并通过 `search-labels` 和 `interactive` 命令建立索引以便后续检索。

---

<a id="7-real-time-streaming"></a>
## 7. 实时流式传输
```bash
npx neuroskill listen --seconds 30 --json
npx neuroskill listen --seconds 5 --json | jq '[.[] | select(.event == "scores")]'
```
Streams 实时 WebSocket 事件（EXG、PPG、IMU、分数、标签），持续指定时长。需要 WebSocket 连接（不适用于 `--http`）。

在连续监控场景中，或需要在协议期间实时观察指标变化时使用。

---

<a id="8-umap-visualization"></a>
## 8. UMAP 可视化
```bash
npx neuroskill umap --json                      # 自动：最近 2 次会话
npx neuroskill umap --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```

GPU 加速的 ZUNA 嵌入 3D UMAP 投影。`separation_score` 表示两次会话的神经区分程度：
- **> 1.5** → 会话在神经上具有明显差异（不同的大脑状态）
- **&lt; 0.5** → 两次会话的大脑状态相似

---

<a id="9-proactive-state-awareness"></a>
## 9. 主动状态感知

<a id="session-start-check"></a>
### 会话开始检查
在会话开始时，如果用户提到他们佩戴了设备或询问自身状态，可选运行状态检查：
```bash
npx neuroskill status --json
```

注入简短的状态摘要：
> “快速检查：专注度正在建立，为 0.62；放松状态良好，为 0.55；您的 FAA 为正值——趋近动机已激活。看起来是一个不错的开始。”
<a id="when-to-proactively-mention-state"></a>
### 何时主动提及状态

**仅**在以下情况提及认知状态：
- 用户明确询问（"我现在状态如何？"、"检查一下我的专注度"）
- 用户报告难以集中注意力、感到压力或疲劳
- 超过关键阈值（困倦度 > 0.70，专注度持续 < 0.30）
- 用户即将进行高认知需求的任务并询问准备情况

**不要**打断心流状态来报告指标。如果专注度 > 0.75，请保护当前会话——保持沉默才是正确的回应。

---

<a id="10-suggesting-protocols"></a>
## 10. 建议方案

当指标显示需要时，从 `references/protocols.md` 中建议一个方案。开始前务必先询问，切勿打断心流状态：

> "过去15分钟你的专注度持续下降，TBR 已攀升超过 1.5——这是 theta 波主导和精神疲劳的迹象。要不要我带你做一个 Theta-Beta 神经反馈锚定练习？这是一个90秒的练习，通过有节奏的计数和呼吸来抑制 theta 波、提升 beta 波。"

关键触发条件：
- **专注度 < 0.40，TBR > 1.5** → Theta-Beta 神经反馈锚定或箱式呼吸
- **放松度 < 0.30，压力指数高** → 心脏相干呼吸或 4-7-8 呼吸法
- **认知负荷持续 > 0.70** → 认知负荷卸载（思维清空）
- **困倦度 > 0.60** → 超昼夜节律重置或清醒重置
- **FAA < 0（负值）** → FAA 再平衡
- **心流状态（专注度 > 0.75，投入度 > 0.70）** → 不要打断
- **高静止度 + 头痛指数** → 颈部放松序列
- **低 RMSSD（< 25ms）** → 迷走神经调音

## 错误处理

| 错误 | 可能原因 | 解决方法 |
|-------|-------------|------|
| `npx neuroskill status` 卡住 | NeuroSkill 应用未运行 | 打开 NeuroSkill 桌面应用 |
| `device.state: "disconnected"` | BCI 设备未连接 | 检查蓝牙、设备电池 |
| 所有分数返回 0 | 电极接触不良 | 重新调整头带，湿润电极 |
| `signal_quality` 值 < 0.7 | 电极松动 | 调整佩戴位置，清洁电极接触点 |
| SNR < 3 dB | 信号噪音大 | 尽量减少头部移动，检查环境 |
| `command not found: npx` | 未安装 Node.js | 安装 Node.js 20+ |
---

<a id="example-interactions"></a>
## 示例交互

**“我现在的状态如何？”**
```bash
npx neuroskill status --json
```
→ 自然解读各项分数，提及专注度、放松度、情绪以及任何值得关注的比值（FAA、TBR）。仅当指标显示存在需求时，才建议采取行动。

**“我无法集中注意力”**
```bash
npx neuroskill status --json
```
→ 检查指标是否证实了这一情况（θ 波偏高、β 波偏低、TBR 上升、嗜睡程度升高）。
→ 若得到证实，从 `references/protocols.md` 中推荐相应方案。
→ 若指标看起来正常，问题可能出在动机层面，而非神经层面。

**“比较一下我今天和昨天的专注度”**
```bash
npx neuroskill compare --json
```
→ 解读趋势，而不仅仅是数字。指出哪些方面改善、哪些下降以及可能的原因。

**“我上一次处于心流状态是什么时候？”**
```bash
npx neuroskill search-labels "flow" --json
npx neuroskill search --json
```
→ 报告时间戳、相关指标以及用户当时在做什么（来自标签）。

**“我睡得怎么样？”**
```bash
npx neuroskill sleep --json
```
→ 报告睡眠结构（N3%、REM%、效率），与健康目标对比，并指出任何问题（高觉醒期、低 REM）。
**"记住这一刻——我刚刚取得了一个突破"**
```bash
npx neuroskill label "breakthrough"
```
→ 确认标签已保存。可选择记录当前指标以记住该状态。

---

<a id="references"></a>
## 参考资料

- [NeuroSkill 论文 — arXiv:2603.03212](https://arxiv.org/abs/2603.03212)（Kosmyna 与 Hauptmann，MIT 媒体实验室）
- [NeuroSkill 桌面应用](https://github.com/NeuroSkill-com/skill)（GPLv3 协议）
- [NeuroLoop 命令行伴侣](https://github.com/NeuroSkill-com/neuroloop)（GPLv3 协议）
- [MIT 媒体实验室项目](https://www.media.mit.edu/projects/neuroskill/overview/)
