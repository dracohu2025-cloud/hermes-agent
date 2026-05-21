---
sidebar_position: 3
---

<a id="profile-distributions-share-a-whole-agent"></a>
# Agent 配置分发：共享一个完整的 Agent

**配置文件分发（profile distribution）** 将一个完整的 Hermes Agent（包括个性、技能、定时任务、MCP 连接、配置）打包成一个 Git 仓库。任何能访问该仓库的人都可以通过一条命令安装整个 Agent、就地更新，同时保留自己的记忆、会话和 API 密钥。

如果 [配置（profile）](./profiles.md) 是一个本地 Agent，那么配置分发就是让这个 Agent 变得可共享。

<a id="what-this-means"></a>
## 这意味着什么

在配置分发出现之前，分享一个 Hermes Agent 需要发送以下内容：

1.  你的 SOUL.md
2.  一份需要安装的技能列表
3.  你的 config.yaml（去掉密钥部分）
4.  一份你连接了哪些 MCP 服务器的描述
5.  你安排的定时任务
6.  需要设置哪些环境变量的说明

……然后祈祷接收者能正确组装。每次版本更新或 bug 修复都要重复一遍交接过程。

有了配置分发，所有内容都放在一个 Git 仓库里：

```
my-research-agent/
├── distribution.yaml    # 清单：名称、版本、环境变量要求
├── SOUL.md              # Agent 的个性 / 系统提示词
├── config.yaml          # 模型、温度、推理、工具默认值
├── skills/              # Agent 自带的捆绑技能
├── cron/                # Agent 运行的定时任务
└── mcp.json             # Agent 连接的 MCP 服务器
```

接收者运行：

```bash
hermes profile install github.com/you/my-research-agent --alias
```

……然后他们就拥有了整个 Agent。他们填入自己的 API 密钥（`.env.EXAMPLE` → `.env`），然后就可以运行 `my-research-agent chat`，或通过 Telegram / Discord / Slack 等任何网关平台与之交互。当你推送新版本时，他们运行 `hermes profile update my-research-agent` 就能拉取你的更改——而他们的记忆和会话会保持不变。

<a id="why-git"></a>
## 为什么选择 Git？

我们考虑过 tarball、HTTP 归档、自定义格式。但没有任何一种比 Git 更好：

- **作者无需构建步骤。** 推送到 GitHub，消费者即可安装。没有“打包、上传、更新索引”这一循环。
- **标签、分支和提交本身就是版本控制系统。** 推送一个标签所做的事情，相当于其他工具“打包并上传一个发布版”。
- **更新只是 fetch。** 不需要重新下载整个归档文件。
- **透明。** 用户可以浏览仓库、查看版本之间的差异、提 Issue、fork 进行定制。
- **私有仓库也可以免费使用。** SSH 密钥、`git credential` 助手、GitHub CLI 存储的凭证——你终端已经设置好的任何认证方式都能透明地生效。
- **可重现性就是一个 commit SHA。** 和 pip 与 npm 记录的一样。

代价：接收者需要安装 git。但在 2026 年，任何运行 Hermes 的机器上都已经安装了。

<a id="when-should-you-use-a-distribution"></a>
## 何时应该使用配置分发？

适用场景：

- **你正在分享一个专门的 Agent**（例如合规监控、代码审查、研究助手、客服机器人）给团队或社区。
- **你将同一个 Agent 部署到多台机器**，不想每次都手动复制文件。
- **你正在迭代一个 Agent**，并希望接收者用一条命令获取新版本。
- **你正在将 Agent 作为产品来构建**（带有固定默认值、精选技能、调校过的提示词），供其他人作为起点使用。
不适合的情况：

- **你只是想在自己的机器上备份一个 profile。** 使用 [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) — 这些命令就是干这个的。
- **你想把 API 密钥随 Agent 一起分享。** `auth.json` 和 `.env` 被有意排除在发行版之外。每个安装者自带自己的凭据。
- **你想分享记忆/会话/对话历史。** 那些是用户数据，不是发行版内容。绝不随发行版分发。

<a id="the-lifecycle-author-to-installer-to-update"></a>
## 生命周期：从作者到安装者再到更新

以下是完整的端到端流程。选择你关心的部分。

---

<a id="for-authors-publishing-a-distribution"></a>
## 面向作者：发布一个发行版

<a id="step-1-start-from-a-working-profile"></a>
### 步骤 1 — 从一个可用的 profile 开始

像构建其他 profile 一样构建和完善 Agent：

```bash
hermes profile create research-bot
research-bot setup                    # configure model, API keys
# Edit ~/.hermes/profiles/research-bot/SOUL.md
# Install skills, wire up MCP servers, schedule cron jobs, etc.
research-bot chat                     # dogfood until it feels right
```

<a id="step-2-add-a-distribution-yaml"></a>
### 步骤 2 — 添加 `distribution.yaml`

创建 `~/.hermes/profiles/research-bot/distribution.yaml`：

```yaml
name: research-bot
version: 1.0.0
description: "Autonomous research assistant with arXiv and web tools"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"

# Tell installers which env vars the agent needs. These are checked against
# the installer's shell and existing .env file so they don't get nagged
# about keys they already have configured.
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API key (for model access)"
    required: true
  - name: SERPAPI_KEY
    description: "SerpAPI key for web search"
    required: false
    default: ""
```

这就是完整的清单。除了 `name` 之外，每个字段都有合理的默认值。

<a id="step-3-push-to-a-git-repo"></a>
### 步骤 3 — 推送到 git 仓库

```bash
cd ~/.hermes/profiles/research-bot
git init
git add .
git commit -m "v1.0.0"
git remote add origin git@github.com:you/research-bot.git
git tag v1.0.0
git push -u origin main --tags
```

现在这个仓库就是一个发行版。任何有权限的人都可以安装它。

:::note
git 仓库包含 **profile 目录中的所有内容，但已从发行版中排除的内容除外**：`auth.json`、`.env`、`memories/`、`sessions/`、`state.db*`、`logs/`、`workspace/`、`*_cache/`、`local/`。这些文件保留在你的机器上。如果你还想排除其他路径，可以添加一个 `.gitignore` 文件。
:::

<a id="step-4-tag-versioned-releases"></a>
### 步骤 4 — 标记版本发布

每当 Agent 达到一个稳定状态时，更新版本号并打标签：

```bash
# Edit distribution.yaml: version: 1.1.0
git add distribution.yaml SOUL.md skills/
git commit -m "v1.1.0: tighter research SOUL, add arxiv skill"
git tag v1.1.0
git push --tags
```

运行 `hermes profile update research-bot` 的接收者将拉取最新版本。

<a id="what-the-repo-looks-like"></a>
### 仓库结构示例

一个完整的作者发布的发行版：

```
research-bot/
├── distribution.yaml            # 必需
├── SOUL.md                      # 强烈推荐
├── config.yaml                  # 模型、提供商、工具默认值
├── mcp.json                     # MCP 服务器连接
├── skills/
│   ├── arxiv-search/SKILL.md
│   ├── paper-summarization/SKILL.md
│   └── citation-lookup/SKILL.md
├── cron/
│   └── weekly-digest.json       # 定时任务
└── README.md                    # 面向人类的描述（可选）
```
<a id="distribution-owned-vs-user-owned"></a>
### Distribution-owned vs User-owned（分发所拥有 vs 用户所拥有）

当安装者更新到新版本时，有些内容会被替换（作者域），有些则保持不变（安装者域）。默认：

| 类别 | 路径 | 更新时 |
|---|---|---|
| **Distribution-owned（分发所拥有）** | `SOUL.md`, `config.yaml`, `mcp.json`, `skills/`, `cron/`, `distribution.yaml` | 从新克隆中替换 |
| **Config override（配置覆盖）** | `config.yaml` | 默认情况下会保留——安装者可能调整了模型或提供商。更新时传入 `--force-config` 可重置。 |
| **User-owned（用户所拥有）** | `memories/`, `sessions/`, `state.db*`, `auth.json`, `.env`, `logs/`, `workspace/`, `plans/`, `home/`, `*_cache/`, `local/` | 从不修改 |

你可以在清单中覆盖 distribution-owned 列表：

```yaml
distribution_owned:
  - SOUL.md
  - skills/research/            # 仅我的研究技能；其他已安装的技能保持不变
  - cron/digest.json
```

如果省略，则应用上面的默认值——这也是大多数分发所期望的。

---

<a id="for-installers-using-a-distribution"></a>
## 对安装者：使用一个分发

<a id="install"></a>
### 安装

```bash
hermes profile install github.com/you/research-bot --alias
```

发生的事情：

1. 将仓库克隆到临时目录。
2. 读取 `distribution.yaml`，向你展示清单（名称、版本、描述、作者、所需环境变量）。
3. 针对每个所需环境变量，检查你的 shell 环境和目标 profile 已有的 `.env`。标记为 `✓ 已设置` 或 `需要设置`，这样你就清楚需要配置什么。
4. 请求确认。传入 `-y` / `--yes` 可跳过。
5. 将 distribution-owned 文件复制到 `~/.hermes/profiles/research-bot/`（或清单中 `name` 解析到的目录）。
6. 写入 `.env.EXAMPLE`，其中所需键被注释掉——复制到 `.env` 并填入值。
7. 使用 `--alias` 创建一个包装器，这样你可以直接运行 `research-bot chat`。

<a id="source-types"></a>
### 源类型

任何 git URL 都有效：

```bash
# GitHub 简写
hermes profile install github.com/you/research-bot

# 完整 HTTPS
hermes profile install https://github.com/you/research-bot.git

# SSH
hermes profile install git@github.com:you/research-bot.git

# 自托管、GitLab、Gitea、Forgejo —— 任何 Git 托管平台
hermes profile install https://git.example.com/team/research-bot.git

# 私有仓库，使用你已配置的 git 认证
hermes profile install git@github.com:your-org/internal-bot.git

# 开发中的本地目录（无需 git push）
hermes profile install ~/my-profile-in-progress/
```

<a id="override-the-profile-name"></a>
### 覆盖 profile 名称

两个用户想要相同分发但使用不同的 profile 名称：

```bash
# Alice
hermes profile install github.com/acme/support-bot --name support-us --alias
# Bob（相同分发，不同本地名称）
hermes profile install github.com/acme/support-bot --name support-eu --alias
```

<a id="fill-in-env-vars"></a>
### 填写环境变量

安装后，该 Agent 的 profile 目录下会有一个 `.env.EXAMPLE`：

```
# 该 Hermes 分发所需的环境变量。
# 复制到 `.env` 并填入你自己的值后再运行。

# OpenAI API 密钥（用于模型访问）
# （必需）
OPENAI_API_KEY=

# 用于网页搜索的 SerpAPI 密钥
# （可选）
# SERPAPI_KEY=
```
复制它：

```bash
cp ~/.hermes/profiles/research-bot/.env.EXAMPLE ~/.hermes/profiles/research-bot/.env
# 编辑 .env，粘贴你的真实密钥
```

所需的环境变量中，如果已经在你的 shell 环境里设置过（例如在 `~/.zshrc` 中导出了 `OPENAI_API_KEY`），安装时会标记为 `✓ set`，你不需要在 `.env` 中重复填写。

<a id="check-what-you-installed"></a>
### 检查已安装的内容

```bash
hermes profile info research-bot
```

显示：

```
Distribution: research-bot
Version:      1.0.0
Description:  Autonomous research assistant with arXiv and web tools
Author:       Your Name
Requires:     Hermes >=0.12.0
Source:       https://github.com/you/research-bot
Installed:    2026-05-08T17:04:32+00:00

Environment variables:
  OPENAI_API_KEY (required) — OpenAI API key (for model access)
  SERPAPI_KEY (optional) — SerpAPI key for web search
```

`hermes profile list` 也会显示一个 `Distribution` 列，这样你一眼就能看出哪个 profile 来自仓库，哪个是自己手写的：

```
 Profile          Model                        Gateway      Alias        Distribution
 ───────────────    ───────────────────────────    ───────────    ───────────    ────────────────────
◆default         claude-sonnet-4              stopped      —            —
  coder           gpt-5                        stopped      coder        —
  research-bot    claude-opus-4                stopped      research-bot research-bot@1.0.0
  telemetry       claude-sonnet-4              running      telemetry    telemetry@2.3.1
```

<a id="update"></a>
### 更新

```bash
hermes profile update research-bot
```

执行过程：

1. 从记录的源 URL 重新克隆仓库。
2. 替换由发行版拥有的文件（SOUL、skills、cron、mcp.json）。
3. **保留**你的 `config.yaml` —— 你可能已经调整过模型、温度或其他设置。传递 `--force-config` 可以覆盖它。
4. **绝不触碰**用户数据：记忆、会话、认证、`.env`、日志、状态。

不需要重新下载整个归档文件，不会覆盖你对配置的本地修改，也不会删除你的对话历史。

<a id="remove"></a>
### 删除

```bash
hermes profile delete research-bot
```

在要求你确认之前，删除提示会显示发行版信息：

```
Profile: research-bot
Path:    ~/.hermes/profiles/research-bot
Model:   claude-opus-4 (anthropic)
Skills:  12
Distribution: research-bot@1.0.0
Installed from: https://github.com/you/research-bot

This will permanently delete:
  • All config, API keys, memories, sessions, skills, cron jobs
  • Command alias (~/.local/bin/research-bot)

Type 'research-bot' to confirm:
```

这样你就不会在不知道 Agent 来自哪里或能否重新安装的情况下，意外删除它。

---

<a id="use-cases-and-patterns"></a>
## 使用场景与模式

<a id="personal-sync-one-agent-across-machines"></a>
### 个人：跨机器同步一个 Agent

你在笔记本电脑上构建了一个研究助手。你希望在另一台工作站上使用同一个 Agent。

```bash
# 笔记本电脑
cd ~/.hermes/profiles/research-bot
git init && git add . && git commit -m "initial"
git remote add origin git@github.com:you/research-bot.git
git push -u origin main

# 工作站
hermes profile install github.com/you/research-bot --alias
# 填写 .env。完成。
```
在笔记本电脑上的任何迭代（`git commit && push`）都会通过 `hermes profile update research-bot` 拉取到工作站。记忆按机器独立存储——笔记本电脑记住自己的对话，工作站记住自己的对话，它们不会冲突。

<a id="team-ship-a-reviewed-internal-agent"></a>
### 团队：发布一个经过审核的内部 Agent

你的工程团队想要一个共享的 PR 审查机器人，它具有特定的 SOUL、特定的技能，以及一个让每个 PR 都通过它运行的 cron 任务。

```bash
# Engineering lead
cd ~/.hermes/profiles/pr-reviewer
# ... build and tune ...
git init && git add . && git commit -m "v1.0 PR reviewer"
git tag v1.0.0
git push -u origin main --tags    # push to your company's internal Git host

# Each engineer
hermes profile install git@github.com:your-org/pr-reviewer.git --alias
# Fill in .env with their own API key (billed to them), .env.EXAMPLE points at what's required
pr-reviewer chat
```

当负责人发布 v1.1（更好的 SOUL、新技能）时，工程师运行 `hermes profile update pr-reviewer`，每个人都能在几分钟内用上新版本。

<a id="community-publish-a-public-agent"></a>
### 社区：发布一个公开的 Agent

你构建了一些新颖的东西——也许是“Polymarket 交易员”或“学术论文摘要器”或“Minecraft 服务器运维助手”。你想分享它。

```bash
# You
cd ~/.hermes/profiles/polymarket-trader
# Write a solid README.md at the repo root — GitHub shows it on the repo page
git init && git add . && git commit -m "v1.0"
git tag v1.0.0
# Publish to a public GitHub repo
git remote add origin https://github.com/you/hermes-polymarket-trader.git
git push -u origin main --tags

# Anyone
hermes profile install github.com/you/hermes-polymarket-trader --alias
```

在推特上发布安装命令。尝试的人会给你发 issue 和 PR。如果有人想自定义，他们可以 fork——这是大家都熟悉的 git 工作流。

<a id="product-ship-an-opinionated-agent"></a>
### 产品：发布一个有主见的 Agent

你构建了基于 Hermes 的上层应用——也许是合规监控工具、客户支持栈、特定领域的研究平台。你想把它作为产品分发。

```yaml
# distribution.yaml
name: telemetry-harness
version: 2.3.1
description: "Compliance telemetry harness — monitors and reviews regulated workflows"
hermes_requires: ">=0.13.0"
author: "Acme Compliance Inc."
license: "Commercial"

env_requires:
  - name: ACME_API_KEY
    description: "Your Acme Compliance license key (email support@acme.com)"
    required: true
  - name: OPENAI_API_KEY
    description: "OpenAI API key for model access"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "URL for your Graphiti knowledge graph instance"
    required: false
    default: "http://127.0.0.1:8000/sse"
```

你的客户通过一条命令安装；安装预览会准确告诉他们需要准备哪些密钥；一旦你标记新版本，更新就会立即推出；他们的合规数据（`memories/`、`sessions/`）永远不会离开他们的机器。

<a id="ephemeral-one-off-scripts-on-shared-infra"></a>
### 临时：在共享基础设施上运行的一次性脚本

你是运维负责人。你想要一个临时的 Agent 来诊断生产事故——一个预置了合适工具和 MCP 连接的 SOUL——并在接下来的一周内运行在三位值班工程师的笔记本电脑上。
```bash
# 你
# 构建 profile，提交，推送私有仓库
git push -u origin main

# 每次值班时
hermes profile install git@github.com:your-org/incident-2026-q2.git --alias

# 事故解决——拆除
hermes profile delete incident-2026-q2
```

安装-删除的周期非常轻量，用完即可丢弃。

---

<a id="recipes"></a>
## 实用技巧

<a id="pin-to-a-specific-version"></a>
### 锁定到特定版本

:::note
Git ref 锁定（`#v1.2.0`）计划中，但初始版本尚未支持——当前安装跟踪的是默认分支。通过 `hermes profile info &lt;name&gt;` 跟踪你安装的版本，在准备好之前暂停更新。
:::

<a id="check-what-version-you-re-on-vs-latest"></a>
### 检查当前版本与最新版本

```bash
# 你安装的版本
hermes profile info research-bot | grep Version

# 最新上游（不安装）
git ls-remote --tags https://github.com/you/research-bot | tail -5
```

<a id="keep-local-config-customizations-through-updates"></a>
### 通过更新保留本地配置自定义

默认的更新行为已经做到了这一点：`config.yaml` 会被保留。为了保险，将本地调整写入 distribution 不拥有的文件：

```yaml
# ~/.hermes/profiles/research-bot/local/my-overrides.yaml
# (distribution 永远不会碰 local/ 目录)
```

……然后在 `config.yaml` 或 SOUL 中按需引用。

<a id="force-a-clean-re-install"></a>
### 强制全新重新安装

```bash
# 清除并从头重新安装（也会丢失记忆/会话）
hermes profile delete research-bot --yes
hermes profile install github.com/you/research-bot --alias

# 更新到当前 main 分支，但将 config.yaml 重置为 distribution 的默认值
hermes profile update research-bot --force-config --yes
```

<a id="fork-and-customize"></a>
### Fork 并自定义

标准的 git 工作流——distributions 就是仓库：

```bash
# 在 GitHub 上 fork 仓库，然后安装你的 fork
hermes profile install github.com/yourname/forked-research-bot --alias

# 在 ~/.hermes/profiles/forked-research-bot/ 本地迭代
# 编辑 SOUL.md，提交，推送到你的 fork
# 上游更改：按常规方式拉取到你的 fork
```

<a id="test-a-distribution-before-pushing"></a>
### 在推送前测试 distribution

从作者机器操作：

```bash
# 从本地目录安装（无需 git push）
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test --alias

# 微调、删除、重新安装直到正确
hermes profile delete research-bot-test --yes
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test
```

---

<a id="what-s-not-in-a-distribution-ever"></a>
## distribution 中绝不包含的内容

安装程序会硬性排除以下路径，即使作者意外打包了它们。没有配置选项可以覆盖此设置——这个安全机制是一个经过回归测试的不变量：

- `auth.json` —— OAuth 令牌、平台凭据
- `.env` —— API 密钥、机密
- `memories/` —— 对话记忆
- `sessions/` —— 对话历史
- `state.db`、`state.db-shm`、`state.db-wal` —— 会话元数据
- `logs/` —— Agent 和错误日志
- `workspace/` —— 生成的工作文件
- `plans/` —— 草稿计划
- `home/` —— Docker 后端中用户的家目录挂载
- `*_cache/` —— 图像/音频/文档缓存
- `local/` —— 用户保留的自定义命名空间
当你克隆一个分布时，这些数据根本不存在。当你更新时，它们会保留。如果你在五台机器上安装了同一个分布，你会得到五组相互隔离的数据——每台机器一组。

<a id="security-and-trust"></a>
## 安全与信任

配置分布默认未签名。你需要信任：

- **Git 托管平台**（GitHub / GitLab / 任何平台）能提供作者推送的原始字节。
- **作者**不会夹带恶意的 SOUL、技能或定时任务。

来自分布的定时任务**不会自动调度**——安装程序会打印 `hermes -p &lt;name&gt; cron list`，你需要手动启用它们。SOUL.md 和技能在你开始与配置文件对话时就会激活，所以如果你安装的是不熟悉的人的分布，在首次运行前请务必阅读它们。

大致类比：安装一个分布就像安装浏览器扩展或 VS Code 扩展。低摩擦、高能力、信任来源。对于公司内部分布，使用私有仓库和常规的 git 认证即可——无需额外配置。

未来版本可能会增加签名、包含已解析提交 SHA 的锁文件（`.distribution-lock.yaml`），以及一个在应用更新前打印差异的 `--dry-run` 标志。这些功能都尚未发布。

<a id="under-the-hood"></a>
## 底层实现

有关实现细节、精确的 CLI 行为以及所有标志，请参见[配置文件命令参考](../reference/profile-commands.md#distribution-commands)。

简而言之：

- `install`、`update`、`info` 位于 `hermes profile` 下——而不是一个并行的命令树。
- 清单格式为 YAML，带有一个很小的必需模式（仅 `name`）。
- 安装程序使用本地的 `git` 二进制文件进行克隆，因此你的 shell 已经处理的所有认证（SSH 密钥、凭据辅助工具）都可以透明地工作。
- 克隆后，`.git/` 会被剥离——已安装的配置文件本身不是一个 git 仓库，从而避免“哎呀，我不小心把我的 `.env` 提交到了分布的 git 历史中”的陷阱。
- 保留的配置文件名称（`hermes`、`test`、`tmp`、`root`、`sudo`）在安装时会被拒绝，以避免与常见二进制文件冲突。

<a id="see-also"></a>
## 另请参阅

- [配置文件：运行多个 Agent](./profiles.md) — 基础概念
- [配置文件命令参考](../reference/profile-commands.md) — 所有标志和选项
- [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) — 本地备份/恢复（非分布）
- [将 SOUL 与 Hermes 一起使用](../guides/use-soul-with-hermes.md) — 编写个性
- [个性与 SOUL](./features/personality.md) — SOUL 如何融入 Agent
- [技能目录](../reference/skills-catalog.md) — 你可以打包的技能
