---
title: "Gif Search — 通过 curl + jq 从 Tenor 搜索/下载 GIF"
sidebar_label: "Gif Search"
description: "通过 curl + jq 从 Tenor 搜索/下载 GIF"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="gif-search"></a>
# Gif Search

通过 curl + jq 从 Tenor 搜索/下载 GIF。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/gif-search` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `GIF`, `Media`, `Search`, `Tenor`, `API` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。即当技能激活时，Agent 所看到的指令内容。
:::

<a id="gif-search-tenor-api"></a>
# GIF 搜索 (Tenor API)

直接通过 curl 调用 Tenor API 搜索和下载 GIF。无需额外工具。

<a id="when-to-use"></a>
## 何时使用

适用于查找反应 GIF、创建视觉内容以及在聊天中发送 GIF。

<a id="setup"></a>
## 设置

在环境变量中设置你的 Tenor API 密钥（添加到 `~/.hermes/.env`）：

```bash
TENOR_API_KEY=your_key_here
```

在 https://developers.google.com/tenor/guides/quickstart 获取免费 API 密钥——Google Cloud Console 的 Tenor API 密钥免费且拥有慷慨的速率限制。

<a id="prerequisites"></a>
## 前提条件

- `curl` 和 `jq`（macOS/Linux 上均为标准工具）
- 环境变量 `TENOR_API_KEY`

<a id="search-for-gifs"></a>
## 搜索 GIF

```bash
# 搜索并获取 GIF 链接
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# 获取较小/预览版本
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

<a id="download-a-gif"></a>
## 下载 GIF

```bash
# 搜索并下载顶部结果
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

<a id="get-full-metadata"></a>
## 获取完整元数据

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | jq '.results[] | {title: .title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url, dimensions: .media_formats.gif.dims}'
```

<a id="api-parameters"></a>
## API 参数

| 参数 | 描述 |
|-----------|-------------|
| `q` | 搜索查询（空格用 `+` 进行 URL 编码） |
| `limit` | 最大结果数（1-50，默认 20） |
| `key` | API 密钥（来自 `$TENOR_API_KEY` 环境变量） |
| `media_filter` | 过滤格式：`gif`、`tinygif`、`mp4`、`tinymp4`、`webm` |
| `contentfilter` | 安全级别：`off`、`low`、`medium`、`high` |
| `locale` | 语言：`en_US`、`es`、`fr` 等 |

<a id="available-media-formats"></a>
## 可用媒体格式

每个结果在 `.media_formats` 下都有多种格式：

| 格式 | 用途 |
|--------|----------|
| `gif` | 全质量 GIF |
| `tinygif` | 小预览 GIF |
| `mp4` | 视频版本（文件体积更小） |
| `tinymp4` | 小预览视频 |
| `webm` | WebM 视频 |
| `nanogif` | 微缩略图 |

<a id="notes"></a>
## 备注

- 对查询进行 URL 编码：空格用 `+`，特殊字符用 `%XX`
- 在聊天中发送时，`tinygif` 链接更轻量
- GIF 链接可直接在 markdown 中使用：`![alt](https://github.com/NousResearch/hermes-agent/blob/main/skills/media/gif-search/url)`
