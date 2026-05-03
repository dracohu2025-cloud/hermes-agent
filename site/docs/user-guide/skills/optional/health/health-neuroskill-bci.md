---
title: "Neuroskill Bci"
sidebar_label: "Neuroskill Bci"
description: "连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦程度、心率、心率变异性、睡眠分期以及 40 多项衍生 EXG 分数）整合到响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）以及本地运行的 NeuroSkill 桌面应用。"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Neuroskill Bci {#neuroskill-bci}

连接到正在运行的 NeuroSkill 实例，并将用户的实时认知和情绪状态（专注度、放松度、情绪、认知负荷、困倦程度、心率、心率变异性、睡眠分期以及 40 多项衍生 EXG 分数）整合到响应中。需要 BCI 可穿戴设备（Muse 2/S 或 OpenBCI）以及本地运行的 NeuroSkill 桌面应用。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/health/neuroskill-bci` 安装 |
| 路径 | `optional-skills/health/neuroskill-bci` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Nous Research |
| 许可证 | MIT |
| 标签 | `BCI`、`neurofeedback`、`health`、`focus`、`EEG`、`cognitive-state`、`biometrics`、`neuroskill` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# NeuroSkill BCI 集成 {#neuroskill-bci-integration}

将 Hermes 连接到正在运行的 [NeuroSkill](https://neuroskill.com/) 实例，以从 BCI 可穿戴设备读取实时的大脑和身体指标。利用这些数据提供具有认知感知能力的响应、建议干预措施，并长期跟踪心理表现。

> **⚠️ 仅限研究用途** — NeuroSkill 是一个开源研究工具。它**不是**医疗设备，也**未**获得 FDA、CE 或任何监管机构的批准。切勿将这些指标用于临床诊断或治疗。

完整的指标参考请参见 `references/metrics.md`，干预协议请参见 `references/protocols.md`，WebSocket/HTTP API 请参见 `references/api.md`。

---

## 前提条件 {#prerequisites}

- 已安装 **Node.js 20+**（`node --version`）
- **NeuroSkill 桌面应用**正在运行，并已连接 BCI 设备
- **BCI 硬件**：Muse 2、Muse S 或 OpenBCI（通过 BLE 连接的 4 通道 EEG + PPG + IMU）
- `npx neuroskill status` 返回数据且无错误

### 验证设置 {#verify-setup}
```bash
node --version                    # 必须为 20+
npx neuroskill status             # 完整系统快照
npx neuroskill status --json      # 机器可解析的 JSON
```

如果 `npx neuroskill status` 返回错误，请告知用户：
- 确保 NeuroSkill 桌面应用已打开
- 确保 BCI 设备已开机并通过蓝牙连接
- 检查信号质量 — NeuroSkill 中的绿色指示灯（每个电极 ≥0.7）
- 如果提示 `command not found`，请安装 Node.js 20+

---

## CLI 参考：`npx neuroskill &lt;command&gt;` {#cli-reference-npx-neuroskill}

所有命令均支持 `--json`（原始 JSON，管道安全）和 `--full`（人类可读摘要 + JSON）。

| 命令 | 描述 |
|---------|-------------|
| `status` | 完整系统快照：设备、分数、频段、比率、睡眠、历史 |
| `session [N]` | 单次会话分解，包含前半段/后半段趋势（0=最近一次） |
| `sessions` | 列出所有天数的所有已记录会话 |
| `search` | 对神经相似的历史时刻进行 ANN 相似性搜索 |
| `compare` | A/B 会话比较，包含指标差异和趋势分析 |
| `sleep [N]` | 睡眠分期分类（清醒/N1/N2/N3/REM）及分析 |
| `label "text"` | 在当前时刻创建带时间戳的注释 |
| `search-labels "query"` | 对历史标签进行语义向量搜索 |
| `interactive "query"` | 跨模态 4 层图搜索（文本 → EXG → 标签） |
| `listen` | 实时事件流（默认 5 秒，使用 `--seconds N` 设置） |
| `umap` | 会话嵌入的 3D UMAP 投影 |
| `calibrate` | 打开校准窗口并启动配置文件 |
| `timer` | 启动专注计时器（番茄钟/深度工作/短时专注预设） |
| `notify "title" "body"` | 通过 NeuroSkill 应用发送操作系统通知 |
| `raw '{json}'` | 向服务器传递原始 JSON |
### 全局标志 {#global-flags}
| 标志 | 描述 |
|------|------|
| `--json` | 原始 JSON 输出（无 ANSI，管道安全） |
| `--full` | 人类可读摘要 + 彩色 JSON |
| `--port &lt;N&gt;` | 覆盖服务器端口（默认：自动发现，通常为 8375） |
| `--ws` | 强制使用 WebSocket 传输 |
| `--http` | 强制使用 HTTP 传输 |
| `--k &lt;N&gt;` | 最近邻数量（search, search-labels） |
| `--seconds &lt;N&gt;` | 监听持续时间（默认：5） |
| `--trends` | 显示每个会话的指标趋势（sessions） |
| `--dot` | Graphviz DOT 输出（交互式） |

---

## 1. 检查当前状态 {#1-checking-current-state}

### 获取实时指标 {#get-live-metrics}
```bash
npx neuroskill status --json
```

**始终使用 `--json`** 以确保可靠解析。默认输出是带颜色的、人类可读的文本。

### 响应中的关键字段 {#key-fields-in-the-response}

`scores` 对象包含所有实时指标（除非另有说明，范围为 0–1）：

```jsonc
{
  "scores": {
    "focus": 0.70,           // β / (α + θ) — 持续注意力
    "relaxation": 0.40,      // α / (β + θ) — 平静清醒
    "engagement": 0.60,      // 主动心理投入
    "meditation": 0.52,      // alpha + 静止 + HRV 相干性
    "mood": 0.55,            // 由 FAA、TAR、BAR 综合得出
    "cognitive_load": 0.33,  // 额叶 θ / 颞叶 α · f(FAA, TBR)
    "drowsiness": 0.10,      // TAR + TBR + 频谱质心下降
    "hr": 68.2,              // 心率，单位 bpm（来自 PPG）
    "snr": 14.3,             // 信噪比，单位 dB
    "stillness": 0.88,       // 0–1；1 = 完全静止
    "faa": 0.042,            // 额叶 Alpha 不对称性（正值 = 趋近）
    "tar": 0.56,             // Theta/Alpha 比值
    "bar": 0.53,             // Beta/Alpha 比值
    "tbr": 1.06,             // Theta/Beta 比值（ADHD 代理指标）
    "apf": 10.1,             // Alpha 峰值频率，单位 Hz
    "coherence": 0.614,      // 半球间相干性
    "bands": {
      "rel_delta": 0.28, "rel_theta": 0.18,
      "rel_alpha": 0.32, "rel_beta": 0.17, "rel_gamma": 0.05
    }
  }
}
```

还包括：`device`（状态、电量、固件）、`signal_quality`（每个电极 0–1）、
`session`（时长、周期数）、`embeddings`、`labels`、`sleep` 摘要和 `history`。

### 解读输出 {#interpreting-the-output}

解析 JSON 并将指标转化为自然语言。永远不要只报告原始数字——始终赋予它们意义：

**正确做法：**
> "你现在的专注度很扎实，达到了 0.70——这属于心流状态区间。心率稳定在 68 bpm，FAA 为正值，表明趋近动机良好。非常适合处理复杂任务。"

**错误做法：**
> "专注度：0.70，放松度：0.40，心率：68"

关键解读阈值（完整指南请参见 `references/metrics.md`）：
- **专注度 > 0.70** → 心流状态区间，请保持
- **专注度 < 0.40** → 建议休息或执行协议
- **困倦度 > 0.60** → 疲劳警告，有微睡眠风险
- **放松度 < 0.30** → 需要压力干预
- **认知负荷 > 0.70 持续** → 建议清空思绪或休息
- **TBR > 1.5** → θ 波主导，执行控制能力下降
- **FAA < 0** → 退缩/负面情绪——考虑 FAA 再平衡
- **SNR < 3 dB** → 信号不可靠，建议重新调整电极位置

## 3. 历史搜索

### 神经相似性搜索
```bash
npx neuroskill search --json                    # 自动：上次会话，k=5
npx neuroskill search --k 10 --json             # 10 个最近邻
npx neuroskill search --start <UTC> --end <UTC> --json
```

通过 HNSW 近似最近邻搜索，在 128 维 ZUNA 嵌入中查找历史上神经状态相似的时刻。返回距离统计、时间分布（一天中的小时）以及最匹配的天数。

当用户询问以下问题时使用此功能：
- “我上次处于这种状态是什么时候？”
- “找到我最好的专注会话”
- “我通常下午什么时候崩溃？”

### 语义标签搜索
```bash
npx neuroskill search-labels "deep focus" --k 10 --json
npx neuroskill search-labels "stress" --json | jq '[.results[].EXG_metrics.tbr]'
```

使用向量嵌入（Xenova/bge-small-en-v1.5）搜索标签文本。返回匹配的标签及其在标记时刻关联的 EXG 指标。

### 跨模态图搜索
```bash
npx neuroskill interactive "deep focus" --json
npx neuroskill interactive "deep focus" --dot | dot -Tsvg > graph.svg
```

4 层图：查询 → 文本标签 → EXG 点 → 附近标签。使用 `--k-text`、`--k-EXG`、`--reach &lt;minutes&gt;` 进行调整。

---

## 4. 会话对比
```bash
npx neuroskill compare --json                   # 自动：最近 2 次会话
npx neuroskill compare --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```

返回约 50 个指标的差值，包含绝对变化、百分比变化和方向。还包括 `insights.improved[]` 和 `insights.declined[]` 数组、两次会话的睡眠分期以及一个 UMAP 任务 ID。

结合上下文解读对比结果——不仅要提差值，还要提趋势：
> “昨天你有两个强专注时段（上午 10 点和下午 2 点）。今天你有一个从 11 点左右开始的专注时段，目前仍在持续。你今天的整体投入度更高，但压力尖峰也更多——压力指数上升了 15%，FAA 更频繁地跌入负值。”

```bash
# 按改善百分比排序指标
npx neuroskill compare --json | jq '.insights.deltas | to_entries | sort_by(.value.pct) | reverse'
```

---

## 5. 睡眠数据
```bash
npx neuroskill sleep --json                     # 最近 24 小时
npx neuroskill sleep 0 --json                   # 最近一次睡眠会话
npx neuroskill sleep --start <UTC> --end <UTC> --json
```
返回逐周期（5秒窗口）的睡眠分期及分析结果：
- **阶段代码**：0=清醒，1=N1，2=N2，3=N3（深睡），4=REM（快速眼动）
- **分析指标**：效率百分比、入睡潜伏期（分钟）、REM潜伏期（分钟）、睡眠周期次数
- **健康目标**：N3 15–25%，REM 20–25%，效率 >85%，入睡潜伏期 &lt;20分钟

```bash
npx neuroskill sleep --json | jq '.summary | {n3: .n3_epochs, rem: .rem_epochs}'
npx neuroskill sleep --json | jq '.analysis.efficiency_pct'
```

当用户提到睡眠、疲劳或恢复时使用此功能。

---

## 6. 标记时刻 {#6-labeling-moments}
```bash
npx neuroskill label "突破性进展"
npx neuroskill label "学习算法"
npx neuroskill label "冥想后"
npx neuroskill label --json "专注块开始"   # 返回 label_id
```

自动标记以下时刻：
- 用户报告突破性进展或洞见
- 用户开始新任务类型（例如"切换到代码审查"）
- 用户完成重要协议
- 用户要求标记当前时刻
- 发生显著状态转换（进入/离开心流状态）

标签存储在数据库中，并通过 `search-labels` 和 `interactive` 命令建立索引以便后续检索。

---

## 7. 实时流式传输 {#7-real-time-streaming}
```bash
npx neuroskill listen --seconds 30 --json
npx neuroskill listen --seconds 5 --json | jq '[.[] | select(.event == "scores")]'
```

在指定持续时间内流式传输实时 WebSocket 事件（EXG、PPG、IMU、分数、标签）。需要 WebSocket 连接（`--http` 模式下不可用）。

用于持续监控场景，或在协议执行期间实时观察指标变化。

---

## 8. UMAP 可视化 {#8-umap-visualization}
```bash
npx neuroskill umap --json                      # 自动：最近2个会话
npx neuroskill umap --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```

GPU 加速的 ZUNA 嵌入 3D UMAP 投影。`separation_score` 表示两个会话的神经差异程度：
- **> 1.5** → 会话在神经层面存在差异（不同大脑状态）
- **< 0.5** → 两个会话的大脑状态相似

---

## 9. 主动状态感知 {#9-proactive-state-awareness}

### 会话开始检查 {#session-start-check}
在会话开始时，如果用户提到正在佩戴设备或询问自身状态，可选择运行状态检查：
```bash
npx neuroskill status --json
```

注入简短的状态摘要：
> "快速检查：专注度正在提升至0.62，放松状态良好为0.55，FAA呈阳性——趋近动机已激活。看起来是个不错的开始。"

### 何时主动提及状态 {#when-to-proactively-mention-state}

**仅**在以下情况提及认知状态：
- 用户明确询问（"我现在状态如何？"、"检查我的专注度"）
- 用户报告难以集中注意力、压力或疲劳
- 达到关键阈值（困倦度 > 0.70，专注度 < 0.30 持续）
- 用户即将进行高认知需求活动并询问准备状态

**不要**打断心流状态来报告指标。如果专注度 > 0.75，请保护会话——保持沉默才是正确做法。

---

## 10. 建议协议 {#10-suggesting-protocols}

当指标显示需要时，从 `references/protocols.md` 中建议一个协议。开始前务必征询用户意见——切勿打断心流状态：
> "过去15分钟你的专注力持续下降，TBR已超过1.5——这是θ波主导和精神疲劳的迹象。需要我带你做一个θ-β神经反馈锚定练习吗？这是一个90秒的练习，通过节奏计数和呼吸来抑制θ波、提升β波。"

关键触发条件：
- **Focus < 0.40, TBR > 1.5** → θ-β神经反馈锚定或箱式呼吸
- **Relaxation < 0.30, stress_index high** → 心脏相干性或4-7-8呼吸
- **Cognitive Load > 0.70 持续** → 认知负荷卸载（思维倾倒）
- **Drowsiness > 0.60** → 超日节律重置或唤醒重置
- **FAA < 0（负值）** → FAA再平衡
- **心流状态（focus > 0.75, engagement > 0.70）** → 请勿打断
- **高静止度 + headache_index** → 颈部放松序列
- **低RMSSD（< 25ms）** → 迷走神经调音

---

## 11. 附加工具 {#11-additional-tools}

### 专注计时器 {#focus-timer}
```bash
npx neuroskill timer --json
```
启动专注计时器窗口，提供番茄钟（25/5）、深度工作（50/10）或短时专注（15/5）预设。

### 校准 {#calibration}
```bash
npx neuroskill calibrate
npx neuroskill calibrate --profile "Eyes Open"
```
打开校准窗口。当信号质量较差或用户希望建立个性化基线时使用。

### 操作系统通知 {#os-notifications}
```bash
npx neuroskill notify "Break Time" "Your focus has been declining for 20 minutes"
```

### 原始JSON透传 {#raw-json-passthrough}
```bash
npx neuroskill raw '{"command":"status"}' --json
```
用于尚未映射到CLI子命令的任何服务器命令。

---

## 错误处理 {#error-handling}

| 错误 | 可能原因 | 修复方法 |
|------|----------|----------|
| `npx neuroskill status` 卡住 | NeuroSkill应用未运行 | 打开NeuroSkill桌面应用 |
| `device.state: "disconnected"` | BCI设备未连接 | 检查蓝牙、设备电量 |
| 所有评分返回0 | 电极接触不良 | 重新佩戴头带，湿润电极 |
| `signal_quality` 值 < 0.7 | 电极松动 | 调整佩戴，清洁电极触点 |
| SNR < 3 dB | 信号噪声大 | 尽量减少头部移动，检查环境 |
| `command not found: npx` | 未安装Node.js | 安装Node.js 20+ |

---

## 示例交互 {#example-interactions}

**"我现在状态如何？"**
```bash
npx neuroskill status --json
```
→ 自然解读各项评分，提及专注力、放松度、情绪以及任何值得注意的比率（FAA、TBR）。仅在指标显示需要时建议采取行动。

**"我无法集中注意力"**
```bash
npx neuroskill status --json
```
→ 检查指标是否确认了问题（高θ波、低β波、TBR上升、高困倦度）。
→ 如果确认，从 `references/protocols.md` 中建议合适的方案。
→ 如果指标看起来正常，问题可能出在动机而非神经层面。

**"比较我今天和昨天的专注力"**
```bash
npx neuroskill compare --json
```
→ 解读趋势，而非仅仅数字。指出哪些方面改善、哪些下降以及可能的原因。

**"我上次进入心流状态是什么时候？"**
```bash
npx neuroskill search-labels "flow" --json
npx neuroskill search --json
```
→ 报告时间戳、相关指标以及用户当时在做什么（来自标签）。
**“我睡得怎么样？”**
```bash
npx neuroskill sleep --json
```
→ 报告睡眠结构（深睡期 N3%、REM 睡眠占比、睡眠效率），与健康目标对比，
并指出任何异常（高觉醒次数、REM 不足）。

**“标记这一刻——我刚有了重大突破”**
```bash
npx neuroskill label "breakthrough"
```
→ 确认标签已保存。可选地记录当前指标以便记住该状态。

---

## 参考文献 {#references}

- [NeuroSkill 论文 — arXiv:2603.03212](https://arxiv.org/abs/2603.03212)（Kosmyna & Hauptmann，MIT 媒体实验室）
- [NeuroSkill 桌面应用](https://github.com/NeuroSkill-com/skill)（GPLv3）
- [NeuroLoop CLI 伴侣](https://github.com/NeuroSkill-com/neuroloop)（GPLv3）
- [MIT 媒体实验室项目](https://www.media.mit.edu/projects/neuroskill/overview/)
