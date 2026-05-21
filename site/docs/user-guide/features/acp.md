---
sidebar_position: 11
title: "ACP 编辑器集成"
description: "在兼容 ACP 的编辑器（如 VS Code、Zed 和 JetBrains）中使用 Hermes Agent"
---

<a id="acp-editor-integration"></a>
# ACP 编辑器集成

Hermes Agent 可以作为 ACP 服务器运行，让兼容 ACP 的编辑器通过 stdio 与 Hermes 通信并渲染：

- 聊天消息
- 工具活动
- 文件差异
- 终端命令
- 审批提示
- 流式思考/响应片段

当你希望 Hermes 表现得像一个编辑器原生的编码 Agent，而不是独立的 CLI 或消息机器人时，ACP 是一个很好的选择。

<a id="what-hermes-exposes-in-acp-mode"></a>
## Hermes 在 ACP 模式下暴露的内容

Hermes 使用为编辑器工作流设计的精选 `hermes-acp` 工具集运行。它包括：

- 文件工具：`read_file`、`write_file`、`patch`、`search_files`
- 终端工具：`terminal`、`process`
- 网页/浏览器工具
- 记忆、待办事项、会话搜索
- 技能
- execute_code 和 delegate_task
- 视觉

它有意排除了不适合典型编辑器用户体验的内容，例如消息投递和定时任务管理。

<a id="installation"></a>
## 安装

正常安装 Hermes，然后添加 ACP 额外依赖：

```bash
pip install -e '.[acp]'
```

这会安装 `agent-client-protocol` 依赖，并启用：

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

对于 Zed 注册表安装，Zed 通过官方的 ACP 注册表条目启动 Hermes。该条目使用 `uvx` 发行版运行：

```bash
uvx --from 'hermes-agent[acp]==<version>' hermes-acp
```

在使用注册表安装路径之前，请确保 `uv` 在 `PATH` 中可用。

<a id="launching-the-acp-server"></a>
## 启动 ACP 服务器

以下任一命令都可以在 ACP 模式下启动 Hermes：

```bash
hermes acp
```

```bash
hermes-acp
```

```bash
python -m acp_adapter
```

Hermes 将日志输出到 stderr，因此 stdout 保留给 ACP JSON-RPC 流量。

用于非交互式检查：

```bash
hermes acp --version
hermes acp --check
```

<a id="browser-tools-optional"></a>
### 浏览器工具（可选）

浏览器工具（`browser_navigate`、`browser_click` 等）依赖于
`agent-browser` npm 包和 Chromium，它们不属于 Python
wheel 的一部分。使用以下命令安装：

```bash
hermes acp --setup-browser           # 交互式（下载约 400 MB 前会提示）
hermes acp --setup-browser --yes     # 非交互式接受下载
```

这是独立命令。Zed 注册表的终端认证流程（`hermes acp --setup`）在模型选择后也会提供浏览器引导作为后续问题，因此大多数用户无需直接运行 `--setup-browser`。

它的作用：

- 如果缺失，将 Node.js 22 LTS 安装到 `~/.hermes/node/`
- 在该前缀下执行 `npm install -g agent-browser @askjo/camofox-browser`（无需 sudo——`npm` 的 `--prefix` 指向用户可写的 Hermes 管理的 Node）
- 安装 Playwright Chromium，或在可用时使用检测到的系统 Chrome/Chromium

引导是幂等的——重新运行很快，并且会跳过已完成的工作。

<a id="editor-setup"></a>
## 编辑器设置

<a id="vs-code"></a>
### VS Code

安装 [ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client) 扩展。

要连接：

1. 从活动栏打开 ACP Client 面板。
2. 从内置 Agent 列表中选择 **Hermes Agent**。
3. 连接并开始聊天。
如果你希望手动定义 Hermes，可以通过 VS Code 设置中的 `acp.agents` 添加：

```json
{
  "acp.agents": {
    "Hermes Agent": {
      "command": "hermes",
      "args": ["acp"]
    }
  }
}
```

<a id="zed"></a>
### Zed

Zed v0.221.x 及更新版本通过官方 ACP Registry 安装外部 Agent。

1. 打开 Agent 面板。
2. 点击 **Add Agent**，或运行 `zed: acp registry` 命令。
3. 搜索 **Hermes Agent**。
4. 安装它并启动一个新的 Hermes 外部 Agent 线程。

先决条件：

- 首先使用 `hermes model` 配置 Hermes 提供商凭据，或者将其设置在 `~/.hermes/.env` / `~/.hermes/config.yaml` 中。
- 安装 `uv`，以便 registry 启动器可以运行 `uvx --from 'hermes-agent[acp]==&lt;version&gt;' hermes-acp`。

在 registry 条目可用之前进行本地开发时，请在 Zed 设置中使用自定义 Agent 服务器：

```json
{
  "agent_servers": {
    "hermes-agent": {
      "type": "custom",
      "command": "hermes",
      "args": ["acp"]
    }
  }
}
```

<a id="jetbrains"></a>
### JetBrains

使用一个兼容 ACP 的插件，并将其指向：

```text
/path/to/hermes-agent/acp_registry
```

<a id="registry-manifest"></a>
## Registry 清单

Hermes 官方 ACP Registry 元数据的源副本位于：

```text
acp_registry/agent.json
acp_registry/icon.svg
```

上游 registry PR 会将这些文件复制到 `agentclientprotocol/registry` 下的顶层 `hermes-agent/` 目录中。

registry 条目使用一个 `uvx` 分发，直接指向 `hermes-agent` PyPI 发布版本：

```text
uvx --from 'hermes-agent[acp]==<version>' hermes-acp
```

Registry CI 会验证固定的版本是否存在于 PyPI 上，因此清单的 `version` 和 uvx 的 `package` 固定值必须始终与 `pyproject.toml` 匹配。`scripts/release.py` 会自动保持它们同步。

<a id="configuration-and-credentials"></a>
## 配置与凭据

ACP 模式使用与 CLI 相同的 Hermes 配置：

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

提供商解析使用 Hermes 的常规运行时解析器，因此 ACP 继承当前配置的提供商和凭据。Hermes 还为首次运行的 registry 客户端提供一种终端身份验证方法（`--setup`）；这会打开 Hermes 的交互式模型/提供商设置。

<a id="session-behavior"></a>
## 会话行为

ACP 会话由 ACP 适配器的内存会话管理器在服务器运行期间跟踪。

每个会话存储：

- 会话 ID
- 工作目录
- 选定的模型
- 当前对话历史记录
- 取消事件

底层的 `AIAgent` 仍然使用 Hermes 的常规持久化/日志路径，但 ACP 的 `list/load/resume/fork` 作用域仅限于当前正在运行的 ACP 服务器进程。

<a id="working-directory-behavior"></a>
## 工作目录行为

ACP 会话将编辑器的 cwd 绑定到 Hermes 任务 ID，以便文件和终端工具相对于编辑器工作区运行，而不是服务器进程的 cwd。

<a id="approvals"></a>
## 批准

危险的终端命令可以以批准提示的形式路由回编辑器。ACP 的批准选项比 CLI 流程更简单：

- 允许一次
- 始终允许
- 拒绝

在超时或出错时，批准桥会拒绝该请求。
<a id="session-scoped-edit-auto-approval"></a>
### 会话级编辑自动批准

ACP 在"允许一次"和"始终允许"之间提供了第三层：**会话允许**。从编辑器的权限提示中选择它会将批准记录在当前 ACP 会话中——该会话中后续的每个匹配命令都会自动通过而不提示，但新的 ACP 会话（或重启编辑器）会重置状态，并在首次再次提示。

| 选项 | 编辑器标签 | 作用范围 | 重启后是否持久化 |
|---|---|---|---|
| `allow_once` | 允许一次 | 这一次工具调用 | 否 |
| `allow_session` | 会话允许 | 该 ACP 会话中的所有匹配调用 | 否——会话结束时清除 |
| `allow_always` | 始终允许 | 所有未来会话 | 是（写入 Hermes 永久允许列表） |
| `deny` | 拒绝 | 这一次工具调用 | 否 |

`allow_session` 是编辑器工作流的合理默认选项，当你信任一个 Agent 在任务期间的行为，但又不希望授予长期有效的允许列表条目时。安全权衡很直接：作用范围越广，编辑器打断你的次数越少，但在你注意到之前，行为异常的 Agent（或提示注入）可能造成的损害就越大。对于不熟悉的命令，从 `allow_once` 开始；当你看到 Agent 正确运行相同模式几次后，升级到 `allow_session`；将 `allow_always` 留给那些你永远信任的真正幂等命令（例如 `git status`）。

ACP 桥将这些选项映射到 Hermes 的内部批准语义—— `allow_always` 像 CLI 一样写入永久允许列表条目，而 `allow_session` 仅影响当前 ACP 会话的进程内批准缓存。

<a id="troubleshooting"></a>
## 疑难解答

<a id="acp-agent-does-not-appear-in-the-editor"></a>
### ACP Agent 未在编辑器中显示

检查：

- 在 Zed 中，使用 `zed: acp registry` 打开 ACP 注册表并搜索 **Hermes Agent**。
- 对于手动/本地开发，验证自定义 `agent_servers` 命令指向 `hermes acp`。
- Hermes 已安装且在 PATH 中。
- ACP 扩展已安装（`pip install -e '.[acp]'`）。
- 如果从官方 Zed 注册表条目启动，需要安装 `uv`。

<a id="acp-starts-but-immediately-errors"></a>
### ACP 启动但立即出错

尝试以下检查：

```bash
hermes acp --version
hermes acp --check
hermes doctor
hermes status
```

<a id="missing-credentials"></a>
### 缺少凭据

ACP 模式使用 Hermes 现有的提供商设置。通过以下方式配置凭据：

```bash
hermes model
```

或编辑 `~/.hermes/.env`。注册表客户端也可以触发 Hermes 的终端身份验证流程，该流程运行相同的交互式提供商/模型设置。

<a id="zed-registry-launcher-cannot-find-uv"></a>
### Zed 注册表启动器找不到 uv

从官方 uv 安装文档安装 `uv`，然后从 Zed 重试 Hermes Agent 线程。

<a id="see-also"></a>
## 另请参阅

- [ACP Internals](../../developer-guide/acp-internals.md)
- [Provider Runtime Resolution](../../developer-guide/provider-runtime.md)
- [Tools Runtime](../../developer-guide/tools-runtime.md)
