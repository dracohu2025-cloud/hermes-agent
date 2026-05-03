---
title: "Memento Flashcards — 基于间隔重复的记忆卡片系统"
sidebar_label: "Memento Flashcards"
description: "基于间隔重复的记忆卡片系统"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Memento Flashcards {#memento-flashcards}

基于间隔重复的记忆卡片系统。从事实或文本创建卡片，通过自由文本回答并由 Agent 评分来与卡片交互，从 YouTube 转录生成测验，通过自适应调度复习到期的卡片，以及以 CSV 格式导出/导入卡组。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/productivity/memento-flashcards` 安装 |
| 路径 | `optional-skills/productivity/memento-flashcards` |
| 版本 | `1.0.0` |
| 作者 | Memento AI |
| 许可证 | MIT |
| 平台 | macos, linux |
| 标签 | `Education`, `Flashcards`, `Spaced Repetition`, `Learning`, `Quiz`, `YouTube` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Memento Flashcards — 间隔重复记忆卡片技能 {#memento-flashcards-spaced-repetition-flashcard-skill}

## 概述 {#overview}

Memento 为你提供一个本地、基于文件的记忆卡片系统，并带有间隔重复调度功能。
用户可以通过自由文本回答并与 Agent 互动，Agent 会对回答进行评分，然后安排下一次复习。
在用户希望以下场景时使用：

- **记住一个事实** — 将任何陈述转换为问答卡片
- **利用间隔重复学习** — 复习到期的卡片，采用自适应间隔和 Agent 评分的自由文本回答
- **根据 YouTube 视频进行测验** — 获取转录并生成包含 5 个问题的测验
- **管理卡组** — 将卡片组织到集合中，导出/导入 CSV

所有卡片数据存储在一个 JSON 文件中。无需外部 API 密钥 — 你（Agent）直接生成卡片内容和测验问题。

Memento Flashcards 的用户响应风格：
- 仅使用纯文本。回复用户时不要使用 Markdown 格式。
- 保持复习和测验反馈简洁中立。避免额外的表扬、鼓励或冗长的解释。

## 何时使用 {#when-to-use}

在用户希望以下场景时使用此技能：
- 将事实保存为卡片以便日后复习
- 使用间隔重复复习到期的卡片
- 从 YouTube 视频转录生成测验
- 导入、导出、查看或删除卡片数据

不要将此技能用于一般问答、编码帮助或非记忆任务。

## 快速参考 {#quick-reference}

| 用户意图 | 操作 |
|---|---|
| “记住那个 X” / “把这个保存为记忆卡片” | 生成问答卡片，调用 `memento_cards.py add` |
| 发送一个事实但没有提到卡片 | 询问“是否想将其保存为 Memento 卡片？” — 仅在确认后创建 |
| “创建一张记忆卡片” | 询问问题、答案、集合；调用 `memento_cards.py add` |
| “复习我的卡片” | 调用 `memento_cards.py due`，逐一展示卡片 |
| “用 [YouTube 链接] 给我做个测验” | 调用 `youtube_quiz.py fetch VIDEO_ID`，生成 5 个问题，调用 `memento_cards.py add-quiz` |
| “导出我的卡片” | 调用 `memento_cards.py export --output PATH` |
| “从 CSV 导入卡片” | 调用 `memento_cards.py import --file PATH --collection NAME` |
| “显示我的统计数据” | 调用 `memento_cards.py stats` |
| “删除一张卡片” | 调用 `memento_cards.py delete --id ID` |
| “删除一个集合” | 调用 `memento_cards.py delete-collection --collection NAME` |
## 卡片存储 {#card-storage}

卡片存储在以下路径的 JSON 文件中：

```
~/.hermes/skills/productivity/memento-flashcards/data/cards.json
```

**切勿直接编辑此文件。** 请始终使用 `memento_cards.py` 子命令进行操作。该脚本通过原子写入（先写入临时文件，再重命名）来防止数据损坏。

该文件会在首次使用时自动创建。

## 操作流程 {#procedure}

### 从知识点创建卡片 {#creating-cards-from-facts}

### 激活规则 {#activation-rules}

并非所有事实性陈述都应该变成闪卡。请使用以下三级检查：

1. **明确意图** —— 用户提到“memento”“flashcard”“记住这个”“保存此卡片”“添加卡片”或类似明确要求闪卡的措辞 → **直接创建卡片**，无需确认。
2. **隐含意图** —— 用户发送事实性陈述但未提及闪卡（例如“光速是 299,792 km/s”） → **先询问**：“需要我将其保存为 Memento 闪卡吗？”仅当用户确认时才创建卡片。
3. **无意图** —— 消息是编码任务、问题、指令、正常对话，或任何明显不是需要记忆的事实 → **完全不激活此技能**。让其他技能或默认行为处理。

确认激活后（级别 1 直接，级别 2 经确认后），生成一张闪卡：

**步骤 1：** 将陈述转换为问答对。内部使用以下格式：

```
将事实性陈述转换为正反面配对。
仅返回两行：
Q: <问题文本>
A: <答案文本>

陈述："{statement}"
```

规则：
- 问题应测试关键事实的记忆
- 答案应简洁直接

**步骤 2：** 调用脚本存储卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add \
  --question "第二次世界大战在哪一年结束？" \
  --answer "1945" \
  --collection "历史"
```

如果用户未指定集合，则使用 `"General"` 作为默认值。

脚本会输出 JSON 确认所创建的卡片。

### 手动创建卡片 {#manual-card-creation}

当用户明确要求创建闪卡时，请询问他们：
1. 问题（卡片正面）
2. 答案（卡片背面）
3. 集合名称（可选 — 默认为 `"General"`）

然后如上所示调用 `memento_cards.py add`。

### 复习到期的卡片 {#reviewing-due-cards}

当用户想要复习时，获取所有到期的卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

这会返回一个 JSON 数组，其中包含 `next_review_at <= now` 的卡片。如果需要集合过滤：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due --collection "History"
```

**复习流程（自由文本评分）：**

以下是您必须遵循的精确交互模式示例。用户回答，您评分，告知正确答案，然后对卡片进行评级。

**示例交互：**

> **Agent：** 柏林墙是在哪一年倒塌的？
>
> **用户：** 1991
>
> **Agent：** 不对。柏林墙是在 1989 年倒塌的。下次复习是明天。
> *(Agent 调用：memento_cards.py rate --id ABC --rating hard --user-answer "1991")*
>
> 下一个问题：第一个登上月球的人是谁？
**规则：**

1. 仅显示问题。等待用户回答。
2. 收到回答后，将其与预期答案进行比较并评分：
   - **正确** → 用户答对了关键事实（即使措辞不同）
   - **部分正确** → 方向正确但缺少核心细节
   - **错误** → 回答错误或离题
3. **你必须告诉用户正确答案以及他们的表现。** 保持简短且纯文本。使用以下格式：
   - 正确："正确。答案：&#123;答案&#125;。7天后再次复习。"
   - 部分正确："接近。答案：&#123;答案&#125;。&#123;他们遗漏的内容&#125;。3天后再次复习。"
   - 错误："不太对。答案：&#123;答案&#125;。明天再次复习。"
4. 然后调用评分命令：正确→easy，部分正确→good，错误→hard。
5. 然后显示下一个问题。

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "用户所说的内容"
```

**永远不要跳过第3步。** 在继续之前，用户必须始终看到正确答案和反馈。

如果没有卡片到期，告诉用户："当前没有卡片需要复习。请稍后再来！"

**退休覆盖：** 用户可以在任何时候说"retire this card"来永久将其从复习中移除。为此使用 `--rating retire`。

### 间隔重复算法 {#spaced-repetition-algorithm}

评分决定下一次复习间隔：

| 评分 | 间隔 | ease_streak | 状态变化 |
|---|---|---|---|
| **hard** | +1 天 | 重置为 0 | 保持学习状态 |
| **good** | +3 天 | 重置为 0 | 保持学习状态 |
| **easy** | +7 天 | +1 | 如果 ease_streak >= 3 → 已退休 |
| **retire** | 永久 | 重置为 0 | → 已退休 |

- **学习状态**：卡片正在轮换中
- **已退休**：卡片不会出现在复习中（用户已掌握或手动退休）
- 连续三次"easy"评分会自动将卡片退休

### YouTube 测验生成 {#youtube-quiz-generation}

当用户发送 YouTube 链接并希望进行测验时：

**第1步：** 从 URL 中提取视频 ID（例如从 `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 提取 `dQw4w9WgXcQ`）。

**第2步：** 获取转录：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/youtube_quiz.py fetch VIDEO_ID
```

这将返回 `{"title": "...", "transcript": "..."}` 或一个错误。

如果脚本报告 `missing_dependency`，告诉用户安装它：
```bash
pip install youtube-transcript-api
```

**第3步：** 从转录中生成5个测验问题。使用以下规则：

```
你正在为一集播客创建包含5个问题的测验。
仅返回一个 JSON 数组，其中恰好包含5个对象。
每个对象必须包含键 'question' 和 'answer'。

选择标准：
- 优先选择重要、令人惊讶或基础性的事实。
- 跳过填充内容、显而易见的事实以及需要大量上下文才能理解的事实。
- 绝不返回是非题。
- 绝不只问一个日期。

问题规则：
- 每个问题必须只测试一个独立的事实。
- 使用清晰、无歧义的措辞。
- 优先使用 What、Who、How many、Which。
- 避免开放式的 Describe 或 Explain 提示。

答案规则：
- 每个答案必须少于240个字符。
- 以答案本身开头，不要有前言。
- 仅在必要时添加最少的澄清细节。
```
使用转录文本的前 15,000 个字符作为上下文。由你（LLM）自己生成问题。

**第 4 步：** 验证输出是否为有效的 JSON，且恰好包含 5 项，每项都有非空的 `question` 和 `answer` 字符串。如果验证失败，重试一次。

**第 5 步：** 存储测验卡片：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add-quiz \
  --video-id "VIDEO_ID" \
  --questions '[{"question":"...","answer":"..."},...]' \
  --collection "Quiz - Episode Title"
```

该脚本会根据 `video_id` 去重——如果该视频的卡片已存在，则跳过创建并报告已有卡片。

**第 6 步：** 使用相同的自由文本评分流程逐一呈现问题：
1. 显示“问题 1/5：...”并等待用户回答。**切勿**包含答案或任何关于揭示答案的提示。
2. 等待用户用自己的话回答。
3. 使用评分提示（参见“复习到期卡片”部分）对答案进行评分。
4. **重要：在继续其他操作之前，你必须先向用户回复反馈。** 显示评分、正确答案以及卡片下次到期时间。不要静默跳到下一个问题。保持简短且纯文本。例如：“不太对。答案：&#123;answer&#125;。下次复习在明天。”
5. **在显示反馈之后**，调用评分命令，然后在同一条消息中显示下一个问题：
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "what the user said"
```
6. 重复。每个答案**必须**在下一个问题之前收到可见的反馈。

### 导出/导入 CSV {#export-import-csv}

**导出：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py export \
  --output ~/flashcards.csv
```

生成一个三列 CSV：`question,answer,collection`（无表头行）。

**导入：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py import \
  --file ~/flashcards.csv \
  --collection "Imported"
```

读取一个包含列：question、answer 以及可选的 collection（第 3 列）的 CSV。如果缺少 collection 列，则使用 `--collection` 参数。

### 统计信息 {#statistics}

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
```

返回 JSON，包含：
- `total`：卡片总数
- `learning`：正在主动轮换的卡片
- `retired`：已掌握的卡片
- `due_now`：当前到期待复习的卡片
- `collections`：按集合名称分类的明细

## 常见陷阱 {#pitfalls}

- **切勿直接编辑 `cards.json`**——始终使用脚本子命令以避免损坏
- **转录失败**——某些 YouTube 视频没有英文字幕或字幕被禁用；告知用户并建议换一个视频
- **可选依赖**——`youtube_quiz.py` 需要 `youtube-transcript-api`；如果缺失，请让用户运行 `pip install youtube-transcript-api`
- **大量导入**——导入数千行的 CSV 没有问题，但 JSON 输出可能很冗长；为用户总结结果
- **视频 ID 提取**——同时支持 `youtube.com/watch?v=ID` 和 `youtu.be/ID` 两种 URL 格式
## 验证 {#verification}

直接验证辅助脚本：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
python3 ~/.hermes/skills/productivity/productivity-memento-flashcards/scripts/memento_cards.py add --question "Capital of France?" --answer "Paris" --collection "General"
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

如果从仓库检出进行测试，运行：

```bash
pytest tests/skills/test_memento_cards.py tests/skills/test_youtube_quiz.py -q
```

Agent 级别的验证：
- 开始一次复习，确认反馈是纯文本、简洁，并且在下一张卡片之前始终包含正确答案
- 运行一次 YouTube 问答流程，确认每个答案在下一个问题之前都能收到可见的反馈
