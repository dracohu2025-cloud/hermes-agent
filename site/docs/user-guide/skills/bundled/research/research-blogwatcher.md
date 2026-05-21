---
title: "Blogwatcher — 通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源"
sidebar_label: "Blogwatcher"
description: "通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="blogwatcher"></a>
# Blogwatcher

通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/blogwatcher` |
| 版本 | `2.0.0` |
| 作者 | JulienTant（Hyaxia/blogwatcher 的分支） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `RSS`, `Blogs`, `Feed-Reader`, `Monitoring` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是该技能的完整定义，Hermes 在触发该技能时会加载它。这是技能激活时 Agent 看到的指令。
:::

# Blogwatcher

使用 `blogwatcher-cli` 工具跟踪博客和 RSS/Atom 订阅源更新。支持自动订阅源发现、HTML 抓取回退、OPML 导入和已读/未读文章管理。

<a id="installation"></a>
## 安装

选择一种方式：

- **Go：** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker：** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **二进制包（Linux amd64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制包（Linux arm64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制包（macOS Apple Silicon）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制包（macOS Intel）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

所有发布版本：https://github.com/JulienTant/blogwatcher-cli/releases

<a id="docker-with-persistent-storage"></a>
### 使用持久化存储的 Docker

默认情况下，数据库位于 `~/.blogwatcher-cli/blogwatcher-cli.db`。在 Docker 中，重启容器后数据会丢失。使用 `BLOGWATCHER_DB` 或挂载卷来持久化数据：

```bash
# 命名卷（最简单）
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan

# 宿主机绑定挂载
docker run --rm -v /path/on/host:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

<a id="migrating-from-the-original-blogwatcher"></a>
### 从原版 blogwatcher 迁移

如果从 `Hyaxia/blogwatcher` 升级，请移动数据库：

```bash
mv ~/.blogwatcher/blogwatcher.db ~/.blogwatcher-cli/blogwatcher-cli.db
```

二进制名称已从 `blogwatcher` 改为 `blogwatcher-cli`。

<a id="common-commands"></a>
## 常用命令

<a id="managing-blogs"></a>
### 管理博客

- 添加博客：`blogwatcher-cli add "My Blog" https://example.com`
- 通过显式订阅源添加：`blogwatcher-cli add "My Blog" https://example.com --feed-url https://example.com/feed.xml`
- 通过 HTML 抓取添加：`blogwatcher-cli add "My Blog" https://example.com --scrape-selector "article h2 a"`
- 列出已跟踪的博客：`blogwatcher-cli blogs`
- 删除博客：`blogwatcher-cli remove "My Blog" --yes`
- 从 OPML 导入：`blogwatcher-cli import subscriptions.opml`

--- END DOCUMENT CHUNK ---
<a id="scanning-and-reading"></a>
### 扫描与阅读

- 扫描所有博客：`blogwatcher-cli scan`
- 扫描单个博客：`blogwatcher-cli scan "My Blog"`
- 列出未读文章：`blogwatcher-cli articles`
- 列出所有文章：`blogwatcher-cli articles --all`
- 按博客筛选：`blogwatcher-cli articles --blog "My Blog"`
- 按分类筛选：`blogwatcher-cli articles --category "Engineering"`
- 标记文章为已读：`blogwatcher-cli read 1`
- 标记文章为未读：`blogwatcher-cli unread 1`
- 全部标记为已读：`blogwatcher-cli read-all`
- 将某个博客全部标记为已读：`blogwatcher-cli read-all --blog "My Blog" --yes`

<a id="environment-variables"></a>
## 环境变量

所有标志都可以通过带有 `BLOGWATCHER_` 前缀的环境变量来设置：

| 变量 | 说明 |
|---|---|
| `BLOGWATCHER_DB` | SQLite 数据库文件的路径 |
| `BLOGWATCHER_WORKERS` | 并发扫描工作线程数（默认：8） |
| `BLOGWATCHER_SILENT` | 扫描时仅输出“扫描完成” |
| `BLOGWATCHER_YES` | 跳过确认提示 |
| `BLOGWATCHER_CATEGORY` | 按分类筛选文章的默认过滤器 |

<a id="example-output"></a>
## 示例输出

```
$ blogwatcher-cli blogs
已跟踪的博客（1 个）：

  xkcd
    URL：https://xkcd.com
    Feed：https://xkcd.com/atom.xml
    上次扫描：2026-04-03 10:30
```

```
$ blogwatcher-cli scan
正在扫描 1 个博客...

  xkcd
    来源：RSS | 找到：4 | 新增：4

共找到 4 篇新文章！
```

```
$ blogwatcher-cli articles
未读文章（2 篇）：

  [1] [新] Barrel - Part 13
       博客：xkcd
       URL：https://xkcd.com/3095/
       发布时间：2026-04-02
       分类：Comics, Science

  [2] [新] Volcano Fact
       博客：xkcd
       URL：https://xkcd.com/3094/
       发布时间：2026-04-01
       分类：Comics
```

<a id="notes"></a>
## 注意事项

- 当未提供 `--feed-url` 时，会自动从博客首页发现 RSS/Atom 订阅源。
- 如果 RSS 获取失败且配置了 `--scrape-selector`，则会回退到 HTML 抓取。
- 来自 RSS/Atom 订阅源的分类会被存储，并可用于筛选文章。
- 支持从 Feedly、Inoreader、NewsBlur 等导出的 OPML 文件批量导入博客。
- 数据库默认存储在 `~/.blogwatcher-cli/blogwatcher-cli.db`（可通过 `--db` 或 `BLOGWATCHER_DB` 覆盖）。
- 使用 `blogwatcher-cli &lt;command&gt; --help` 查看所有标志和选项。
