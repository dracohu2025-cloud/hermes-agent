---
title: "Blogwatcher — 通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源"
sidebar_label: "Blogwatcher"
description: "通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Blogwatcher {#blogwatcher}

通过 blogwatcher-cli 工具监控博客和 RSS/Atom 订阅源。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/research/blogwatcher` |
| 版本 | `2.0.0` |
| 作者 | JulienTant（Hyaxia/blogwatcher 的分支） |
| 许可证 | MIT |
| 标签 | `RSS`、`Blogs`、`Feed-Reader`、`Monitoring` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 agent 在技能激活时看到的指令。
:::

<a id="blogwatcher"></a>
# Blogwatcher

使用 `blogwatcher-cli` 工具跟踪博客和 RSS/Atom 订阅源更新。支持自动订阅源发现、HTML 抓取回退、OPML 导入以及已读/未读文章管理。

## 安装 {#installation}

选择以下任一方式：

- **Go：** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker：** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **二进制（Linux amd64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制（Linux arm64）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制（macOS Apple Silicon）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **二进制（macOS Intel）：** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

所有发布版本：https://github.com/JulienTant/blogwatcher-cli/releases

### 使用持久化存储的 Docker {#docker-with-persistent-storage}

默认情况下，数据库位于 `~/.blogwatcher-cli/blogwatcher-cli.db`。在 Docker 中，容器重启后该数据会丢失。请使用 `BLOGWATCHER_DB` 或卷挂载来持久化数据：

```bash
# 命名卷（最简单）
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan

# 主机绑定挂载
docker run --rm -v /path/on/host:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

### 从原始 blogwatcher 迁移 {#migrating-from-the-original-blogwatcher}

如果从 `Hyaxia/blogwatcher` 升级，请移动数据库：

```bash
mv ~/.blogwatcher/blogwatcher.db ~/.blogwatcher-cli/blogwatcher-cli.db
```

二进制名称已从 `blogwatcher` 变更为 `blogwatcher-cli`。

## 常用命令 {#common-commands}

### 管理博客 {#managing-blogs}

- 添加博客：`blogwatcher-cli add "My Blog" https://example.com`
- 添加并指定订阅源：`blogwatcher-cli add "My Blog" https://example.com --feed-url https://example.com/feed.xml`
- 添加并通过 HTML 抓取：`blogwatcher-cli add "My Blog" https://example.com --scrape-selector "article h2 a"`
- 列出已跟踪的博客：`blogwatcher-cli blogs`
- 删除博客：`blogwatcher-cli remove "My Blog" --yes`
- 从 OPML 导入：`blogwatcher-cli import subscriptions.opml`
### 扫描与阅读 {#scanning-and-reading}

- 扫描所有博客：`blogwatcher-cli scan`
- 扫描单个博客：`blogwatcher-cli scan "我的博客"`
- 列出未读文章：`blogwatcher-cli articles`
- 列出所有文章：`blogwatcher-cli articles --all`
- 按博客筛选：`blogwatcher-cli articles --blog "我的博客"`
- 按分类筛选：`blogwatcher-cli articles --category "工程"`
- 标记文章为已读：`blogwatcher-cli read 1`
- 标记文章为未读：`blogwatcher-cli unread 1`
- 全部标记为已读：`blogwatcher-cli read-all`
- 将某个博客的全部文章标记为已读：`blogwatcher-cli read-all --blog "我的博客" --yes`

## 环境变量 {#environment-variables}

所有标志都可以通过带有 `BLOGWATCHER_` 前缀的环境变量设置：

| 变量 | 描述 |
|---|---|
| `BLOGWATCHER_DB` | SQLite 数据库文件的路径 |
| `BLOGWATCHER_WORKERS` | 并发扫描工作线程数（默认：8） |
| `BLOGWATCHER_SILENT` | 扫描时仅输出“扫描完成” |
| `BLOGWATCHER_YES` | 跳过确认提示 |
| `BLOGWATCHER_CATEGORY` | 按分类筛选文章的默认过滤器 |

## 示例输出 {#example-output}

```
$ blogwatcher-cli blogs
已跟踪的博客（1）：

  xkcd
    URL：https://xkcd.com
    订阅源：https://xkcd.com/atom.xml
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
未读文章（2）：

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

## 注意事项 {#notes}

- 当未提供 `--feed-url` 时，会自动从博客首页发现 RSS/Atom 订阅源。
- 如果 RSS 获取失败且配置了 `--scrape-selector`，则会回退到 HTML 抓取。
- 来自 RSS/Atom 订阅源的分类会被存储，并可用于筛选文章。
- 可通过 Feedly、Inoreader、NewsBlur 等导出的 OPML 文件批量导入博客。
- 数据库默认存储在 `~/.blogwatcher-cli/blogwatcher-cli.db`（可通过 `--db` 或 `BLOGWATCHER_DB` 覆盖）。
- 使用 `blogwatcher-cli &lt;command&gt; --help` 查看所有标志和选项。
