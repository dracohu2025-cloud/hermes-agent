---
title: "Sherlock — 跨400多个社交网络的OSINT用户名搜索"
sidebar_label: "Sherlock"
description: "跨400多个社交网络的OSINT用户名搜索"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="sherlock"></a>
# Sherlock

跨400多个社交网络的OSINT用户名搜索。通过用户名追踪社交媒体账户。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| Source | 可选 — 使用 `hermes skills install official/security/sherlock` 安装 |
| Path | `optional-skills/security/sherlock` |
| Version | `1.0.0` |
| Author | unmodeled-tyler |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `osint`, `security`, `username`, `social-media`, `reconnaissance` |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在此技能被触发时加载的完整技能定义。这是 Agent 在技能激活时所看到的指令。
:::

<a id="sherlock-osint-username-search"></a>
# Sherlock OSINT 用户名搜索

使用 [Sherlock Project](https://github.com/sherlock-project/sherlock) 通过用户名在 400 多个社交网络中追踪社交媒体帐户。

<a id="when-to-use"></a>
## 何时使用

- 用户要求查找与用户名关联的帐户
- 用户想要检查用户名在各平台的可用性
- 用户正在进行 OSINT 或侦察研究
- 用户询问“这个用户名在哪里注册？”或类似问题

<a id="requirements"></a>
## 要求

- Sherlock CLI 已安装：`pipx install sherlock-project` 或 `pip install sherlock-project`
- 或者：Docker 可用（`docker run -it --rm sherlock/sherlock`）
- 能联网以查询社交平台

<a id="procedure"></a>
## 步骤

<a id="1-check-if-sherlock-is-installed"></a>
### 1. 检查 Sherlock 是否已安装

**在执行其他操作之前**，验证 sherlock 是否可用：

```bash
sherlock --version
```

如果命令失败：
- 提供安装方式：`pipx install sherlock-project`（推荐）或 `pip install sherlock-project`
- **不要**尝试多种安装方式 — 选择一种并继续
- 如果安装失败，通知用户并停止

<a id="2-extract-username"></a>
### 2. 提取用户名

**如果用户消息中明确陈述了用户名，则直接提取。**

以下情况中你**不应**使用 clarify：
- “查找 nasa 的账户” → 用户名为 `nasa`
- “搜索 johndoe123” → 用户名为 `johndoe123`
- “检查 alice 是否在社交媒体上存在” → 用户名为 `alice`
- “在社交网络上查找用户 bob” → 用户名为 `bob`

**仅在以下情况下使用 clarify：**
- 提到多个潜在用户名（例如“搜索 alice 或 bob”）
- 措辞含糊（例如未指定具体用户名的“搜索我的用户名”）
- 完全没有提到用户名（例如“进行 OSINT 搜索”）

提取时，取**准确**的用户名原文——保留大小写、数字、下划线等。

<a id="3-build-command"></a>
### 3. 构建命令

**默认命令**（除非用户另有明确要求，否则使用此命令）：
```bash
sherlock --print-found --no-color "<username>" --timeout 90
```

**可选标志**（仅在用户明确要求时添加）：
- `--nsfw` — 包含 NSFW 站点（仅当用户要求时）
- `--tor` — 通过 Tor 路由（仅当用户要求匿名时）

**不要通过 clarify 询问选项** — 直接运行默认搜索。用户可以在需要时请求特定选项。
<a id="4-execute-search"></a>
### 4. 执行搜索

通过 `terminal` 工具运行。该命令通常需要 30–120 秒，具体取决于网络状况和站点数量。

**终端调用示例：**
```json
{
  "command": "sherlock --print-found --no-color \"target_username\"",
  "timeout": 180
}
```

<a id="5-parse-and-present-results"></a>
### 5. 解析并呈现结果

Sherlock 以简单格式输出已找到的账户。解析输出并呈现：

1. **摘要行：** "为用户名 'Y' 找到 X 个账户"
2. **分类链接：** 如果有助于区分，可按平台类型分组（社交、职业、论坛等）
3. **输出文件位置：** Sherlock 默认将结果保存到 `&lt;username&gt;.txt`

**输出解析示例：**
```
[+] Instagram: https://instagram.com/username
[+] Twitter: https://twitter.com/username
[+] GitHub: https://github.com/username
```

尽可能以可点击链接的形式呈现结果。

<a id="pitfalls"></a>
## 常见陷阱

<a id="no-results-found"></a>
### 未找到结果
如果 Sherlock 未找到任何账户，这通常正确——该用户名可能未在已检查的平台上注册。建议：
- 检查拼写/变体
- 尝试用 `?` 通配符查找类似用户名：`sherlock "user?name"`
- 用户可能设置了隐私设置或已删除账户

<a id="timeout-issues"></a>
### 超时问题
部分站点响应缓慢或阻止自动化请求。可使用 `--timeout 120` 增加等待时间，或使用 `--site` 限制搜索范围。

<a id="tor-configuration"></a>
### Tor 配置
`--tor` 需要 Tor 守护进程正在运行。如果用户希望匿名但 Tor 不可用，建议：
- 安装 Tor 服务
- 使用 `--proxy` 配合其他代理

<a id="false-positives"></a>
### 误报
某些站点由于其响应结构总是返回“已找到”。对于意外结果，请手动交叉验证。

<a id="rate-limiting"></a>
### 速率限制
激进的搜索可能触发速率限制。对于批量用户名搜索，可在调用之间添加延迟，或使用带缓存的 `--local`。

<a id="installation"></a>
## 安装

<a id="pipx-recommended"></a>
### pipx（推荐）
```bash
pipx install sherlock-project
```

<a id="pip"></a>
### pip
```bash
pip install sherlock-project
```

<a id="docker"></a>
### Docker
```bash
docker pull sherlock/sherlock
docker run -it --rm sherlock/sherlock <username>
```

<a id="linux-packages"></a>
### Linux 包
适用于 Debian 13+、Ubuntu 22.10+、Homebrew、Kali、BlackArch。

<a id="ethical-use"></a>
## 道德使用

此工具仅用于合法的开源情报（OSINT）和研究目的。提醒用户：
- 仅搜索自己拥有或获得授权调查的用户名
- 遵守各平台的服务条款
- 不得用于骚扰、跟踪或非法活动
- 在分享结果前考虑隐私影响

<a id="verification"></a>
## 验证

运行 Sherlock 后，验证以下内容：
1. 输出列出已找到的站点及其 URL
2. 如果使用文件输出，会创建 `&lt;username&gt;.txt` 文件（默认输出）
3. 如果使用了 `--print-found`，输出应仅包含匹配项的 `[+]` 行

<a id="example-interaction"></a>
## 交互示例

**用户：** "你能检查一下用户名 'johndoe123' 是否存在于社交媒体上吗？"

**Agent 流程：**
1. 检查 `sherlock --version`（验证已安装）
2. 用户已提供用户名——直接进行
3. 运行：`sherlock --print-found --no-color "johndoe123" --timeout 90`
4. 解析输出并呈现链接

**回复格式：**
> 为用户 'johndoe123' 找到 12 个账户：
>
> • https://twitter.com/johndoe123
> • https://github.com/johndoe123
> • https://instagram.com/johndoe123
> • [... 其他链接]
>
> 结果已保存至：johndoe123.txt
