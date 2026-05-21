---
title: "Youtube Content — YouTube 字幕转摘要、推文、博客"
sidebar_label: "Youtube Content"
description: "YouTube 字幕转摘要、推文、博客"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="youtube-content"></a>
# Youtube Content

将 YouTube 字幕转换为摘要、推文、博客。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/youtube-content` |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活后 Agent 看到的指令。
:::

<a id="youtube-content-tool"></a>
# YouTube 内容工具

<a id="when-to-use"></a>
## 使用时机

当用户分享 YouTube URL 或视频链接、要求总结视频、请求字幕、或希望从任何 YouTube 视频中提取并重新格式化内容时使用。将字幕转换为结构化内容（章节、摘要、推文、博客文章）。

从 YouTube 视频中提取字幕并将其转换为有用的格式。

<a id="setup"></a>
## 设置

```bash
pip install youtube-transcript-api
```

<a id="helper-script"></a>
## 辅助脚本

`SKILL_DIR` 是包含此 SKILL.md 文件的目录。该脚本接受任何标准 YouTube URL 格式、短链接（youtu.be）、短视频、嵌入链接、直播链接或原始的 11 字符视频 ID。

```bash
# JSON 输出（含元数据）
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# 纯文本（适合管道传递到后续处理）
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# 带时间戳
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# 指定语言并设置回退链
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

<a id="output-formats"></a>
## 输出格式

获取字幕之后，根据用户要求进行格式化：

- **章节**：按主题切换分组，输出带时间戳的章节列表
- **摘要**：对整个视频进行 5-10 句的简洁概述
- **章节摘要**：每个章节附带一段简短摘要
- **推文**：Twitter/X 推文格式——编号帖子，每条不超过 280 字符
- **博客文章**：包含标题、章节和关键要点的完整文章
- **引文**：带时间戳的值得注意的引述

<a id="example-chapters-output"></a>
### 示例——章节输出

```
00:00 引言——主持人以问题陈述开场
03:45 背景——先前工作及现有解决方案的不足
12:20 核心方法——逐步讲解提出的方法
24:10 结果——基准对比和关键要点
31:55 问答——观众关于可扩展性和后续步骤的提问
```

<a id="workflow"></a>
## 工作流程

1. **获取**：使用辅助脚本配合 `--text-only --timestamps` 获取字幕。
2. **验证**：确认输出非空且语言符合预期。如果为空，则在不加 `--language` 的情况下重试，以获取任何可用的字幕。如果仍然为空，告知用户该视频可能已禁用字幕。
3. **分块（如需）**：如果字幕超过约 5 万字符，则将其拆分为重叠的块（约 4 万字符，重叠 2 千字符），并在合并前对每个块进行摘要。
4. **转换**：转换为请求的输出格式。如果用户未指定格式，则默认输出摘要。
5. **验证**：重新阅读转换后的输出，检查连贯性、时间戳正确性和完整性，然后再呈现给用户。
<a id="error-handling"></a>
## 错误处理

- **字幕不可用**：告知用户；建议他们检查视频页面上是否有字幕可用。
- **私有/不可用视频**：转发错误信息，并让用户验证 URL。
- **没有匹配的语言**：使用不带 `--language` 参数重试以获取任何可用的字幕，然后向用户说明实际的语言。
- **依赖缺失**：运行 `pip install youtube-transcript-api` 后重试。
