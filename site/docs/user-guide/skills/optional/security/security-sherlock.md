---
title: "Sherlock — 在 400+ 社交网络上进行 OSINT 用户名搜索"
sidebar_label: "Sherlock"
description: "在 400+ 社交网络上进行 OSINT 用户名搜索"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Sherlock {#sherlock}

在 400+ 社交网络上进行 OSINT 用户名搜索。通过用户名查找社交媒体账号。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/security/sherlock` 安装 |
| 路径 | `optional-skills/security/sherlock` |
| 版本 | `1.0.0` |
| 作者 | unmodeled-tyler |
| 许可证 | MIT |
| 标签 | `osint`, `security`, `username`, `social-media`, `reconnaissance` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Sherlock OSINT 用户名搜索 {#sherlock-osint-username-search}

使用 [Sherlock 项目](https://github.com/sherlock-project/sherlock) 在 400+ 社交网络上通过用户名查找社交媒体账号。

## 何时使用 {#when-to-use}

- 用户要求查找与某个用户名关联的账号
- 用户想检查用户名在各平台上的可用性
- 用户正在进行 OSINT 或侦察研究
- 用户询问“这个用户名注册在哪里？”或类似问题

## 前提条件 {#requirements}

- 已安装 Sherlock CLI：`pipx install sherlock-project` 或 `pip install sherlock-project`
- 或者：可用 Docker（`docker run -it --rm sherlock/sherlock`）
- 能够访问网络以查询社交平台

## 操作步骤 {#procedure}

### 1. 检查 Sherlock 是否已安装 {#1-check-if-sherlock-is-installed}

**在做任何其他事情之前**，先确认 sherlock 可用：

```bash
sherlock --version
```

如果命令失败：
- 提供安装方式：`pipx install sherlock-project`（推荐）或 `pip install sherlock-project`
- **不要**尝试多种安装方法——选一种并继续
- 如果安装失败，告知用户并停止

### 2. 提取用户名 {#2-extract-username}

**如果用户消息中明确提到了用户名，直接提取。**

以下情况**不要**使用澄清：
- “查找 nasa 的账号” → 用户名为 `nasa`
- “搜索 johndoe123” → 用户名为 `johndoe123`
- “检查 alice 是否在社交媒体上存在” → 用户名为 `alice`
- “查找用户 bob 在社交网络上的信息” → 用户名为 `bob`

**仅在以下情况使用澄清：**
- 提到了多个可能的用户名（“搜索 alice 或 bob”）
- 表述模糊（“搜索我的用户名”但未指定）
- 完全没有提到用户名（“做一个 OSINT 搜索”）

提取时，使用**确切的**用户名——保留大小写、数字、下划线等。

### 3. 构建命令 {#3-build-command}

**默认命令**（除非用户特别要求，否则使用此命令）：
```bash
sherlock --print-found --no-color "<用户名>" --timeout 90
```

**可选标志**（仅在用户明确要求时添加）：
- `--nsfw` — 包含 NSFW 网站（仅当用户要求时）
- `--tor` — 通过 Tor 路由（仅当用户要求匿名时）

**不要通过澄清询问选项**——直接运行默认搜索。用户如果需要特定选项，可以自行提出。

### 4. 执行搜索 {#4-execute-search}
通过 `terminal` 工具运行。该命令通常需要 30-120 秒，具体取决于网络状况和站点数量。

**终端调用示例：**
```json
{
  "command": "sherlock --print-found --no-color \"target_username\"",
  "timeout": 180
}
```

### 5. 解析并展示结果 {#5-parse-and-present-results}

Sherlock 以简单格式输出找到的账户。解析输出并展示：

1. **摘要行：** "为用户名 'Y' 找到 X 个账户"
2. **分类链接：** 如果方便，按平台类型分组（社交、职业、论坛等）
3. **输出文件位置：** Sherlock 默认将结果保存到 `&lt;username&gt;.txt`

**输出解析示例：**
```
[+] Instagram: https://instagram.com/username
[+] Twitter: https://twitter.com/username
[+] GitHub: https://github.com/username
```

尽可能将发现结果展示为可点击的链接。

## 注意事项 {#pitfalls}

### 未找到结果 {#no-results-found}
如果 Sherlock 没有找到任何账户，这通常是正确的——该用户名可能未在检查的平台上注册。建议：
- 检查拼写/变体
- 使用 `?` 通配符尝试相似用户名：`sherlock "user?name"`
- 用户可能设置了隐私设置或已删除账户

### 超时问题 {#timeout-issues}
某些网站响应缓慢或阻止自动请求。使用 `--timeout 120` 增加等待时间，或使用 `--site` 限制范围。

### Tor 配置 {#tor-configuration}
`--tor` 需要 Tor 守护进程正在运行。如果用户希望匿名但 Tor 不可用，建议：
- 安装 Tor 服务
- 使用 `--proxy` 配合替代代理

### 误报 {#false-positives}
某些网站由于其响应结构，总是返回"已找到"。对意外结果进行人工交叉验证。

### 速率限制 {#rate-limiting}
激进的搜索可能触发速率限制。对于批量用户名搜索，在调用之间添加延迟，或使用 `--local` 配合缓存数据。

## 安装 {#installation}

### pipx（推荐） {#pipx-recommended}
```bash
pipx install sherlock-project
```

### pip {#pip}
```bash
pip install sherlock-project
```

### Docker {#docker}
```bash
docker pull sherlock/sherlock
docker run -it --rm sherlock/sherlock <username>
```

### Linux 包 {#linux-packages}
适用于 Debian 13+、Ubuntu 22.10+、Homebrew、Kali、BlackArch。

## 道德使用 {#ethical-use}

此工具仅用于合法的开源情报（OSINT）和研究目的。提醒用户：
- 仅搜索自己拥有或有权调查的用户名
- 尊重平台服务条款
- 不得用于骚扰、跟踪或非法活动
- 在分享结果前考虑隐私影响

## 验证 {#verification}

运行 sherlock 后，验证：
1. 输出列出找到的站点及其 URL
2. 如果使用文件输出，则创建了 `&lt;username&gt;.txt` 文件（默认输出）
3. 如果使用了 `--print-found`，输出应仅包含匹配项的 `[+]` 行

## 交互示例 {#example-interaction}

**用户：** "你能检查一下用户名 'johndoe123' 是否存在于社交媒体上吗？"

**Agent 流程：**
1. 检查 `sherlock --version`（验证已安装）
2. 用户名已提供——直接进行
3. 运行：`sherlock --print-found --no-color "johndoe123" --timeout 90`
4. 解析输出并展示链接

**回复格式：**
> 为用户名 'johndoe123' 找到 12 个账户：
>
> • https://twitter.com/johndoe123
> • https://github.com/johndoe123
> • https://instagram.com/johndoe123
> • [... 其他链接]
>
> 结果已保存到：johndoe123.txt
