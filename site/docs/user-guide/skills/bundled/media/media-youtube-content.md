---
title: "Youtube Content — YouTube 转录文本转摘要、推文串、博客文章"
sidebar_label: "Youtube Content"
description: "YouTube 转录文本转摘要、推文串、博客文章"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Youtube Content {#youtube-content}

YouTube 转录文本转摘要、推文串、博客文章。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/youtube-content` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# YouTube 内容工具 {#youtube-content-tool}

## 何时使用 {#when-to-use}

当用户分享 YouTube URL 或视频链接、要求总结视频、请求转录文本，或希望从任何 YouTube 视频中提取并重新格式化内容时使用。将转录文本转换为结构化内容（章节、摘要、推文串、博客文章）。

从 YouTube 视频中提取转录文本并将其转换为有用的格式。

## 设置 {#setup}

```bash
pip install youtube-transcript-api
```

## 辅助脚本 {#helper-script}

`SKILL_DIR` 是包含此 SKILL.md 文件的目录。该脚本接受任何标准 YouTube URL 格式、短链接（youtu.be）、Shorts、嵌入链接、直播链接或原始的 11 字符视频 ID。

```bash
# 带元数据的 JSON 输出
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# 纯文本（适合管道进一步处理）
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# 带时间戳
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# 指定语言并设置回退链
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## 输出格式 {#output-formats}

获取转录文本后，根据用户要求进行格式化：

- **章节**：按主题切换分组，输出带时间戳的章节列表
- **摘要**：整个视频的简洁概述，5-10 句话
- **章节摘要**：每个章节附带一段简短摘要
- **推文串**：Twitter/X 推文串格式——编号帖子，每条不超过 280 字符
- **博客文章**：包含标题、章节和关键要点的完整文章
- **引文**：带时间戳的值得注意的引述

### 示例——章节输出 {#example-chapters-output}

```
00:00 引言——主持人以问题陈述开场
03:45 背景——先前工作及现有解决方案的不足
12:20 核心方法——所提方法的逐步讲解
24:10 结果——基准对比与关键要点
31:55 问答——观众关于可扩展性和后续步骤的提问
```

## 工作流程 {#workflow}

1. **获取**：使用辅助脚本配合 `--text-only --timestamps` 获取转录文本。
2. **验证**：确认输出非空且为预期语言。如果为空，则在不加 `--language` 的情况下重试以获取任何可用的转录文本。如果仍然为空，告知用户该视频可能已禁用转录文本。
3. **按需分块**：如果转录文本超过约 50K 字符，则将其拆分为重叠的分块（约 40K，重叠 2K），并在合并前对每个分块进行摘要。
4. **转换**：转换为请求的输出格式。如果用户未指定格式，默认输出摘要。
5. **验证**：重新阅读转换后的输出，检查连贯性、时间戳正确性和完整性，然后再呈现给用户。
## 错误处理 {#error-handling}

- **字幕已禁用**：告知用户，并建议他们检查视频页面是否提供了字幕。
- **私密/不可用的视频**：转发错误信息，并请用户确认 URL 是否正确。
- **没有匹配的语言**：不使用 `--language` 参数重试，以获取任何可用的字幕，然后向用户说明实际使用的语言。
- **缺少依赖**：运行 `pip install youtube-transcript-api` 并重试。
