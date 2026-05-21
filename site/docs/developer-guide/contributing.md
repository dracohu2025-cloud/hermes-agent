---
sidebar_position: 4
title: "贡献指南"
description: "如何为 Hermes Agent 做贡献——开发环境搭建、代码规范、PR 流程"
---

<a id="contributing"></a>
# 贡献指南

感谢你为 Hermes Agent 做贡献！本指南将帮助你搭建开发环境、理解代码库，以及让你的 PR 顺利合并。

<a id="contribution-priorities"></a>
## 贡献优先级

我们按以下顺序评估贡献：

1. **Bug 修复** —— 崩溃、行为错误、数据丢失
2. **跨平台兼容性** —— macOS、不同 Linux 发行版、WSL2
3. **安全加固** —— Shell 注入、提示注入、路径遍历
4. **性能与健壮性** —— 重试逻辑、错误处理、优雅降级
5. **新技能** —— 具有广泛实用性的技能（参见[创建技能](creating-skills.md)）
6. **新工具** —— 很少需要；大多数能力应通过技能实现
7. **文档** —— 修复、澄清、新示例

<a id="common-contribution-paths"></a>
## 常见的贡献路径

- 想在不修改 Hermes 核心的情况下构建自定义/本地工具？从[构建 Hermes 插件](../guides/build-a-hermes-plugin.md)开始
- 想为 Hermes 自身构建一个新的内置核心工具？从[添加工具](./adding-tools.md)开始
- 想构建一个新技能？从[创建技能](./creating-skills.md)开始
- 想构建一个新的推理提供商？从[添加提供商](./adding-providers.md)开始

<a id="development-setup"></a>
## 开发环境搭建

<a id="prerequisites"></a>
### 前置条件

| 要求 | 说明 |
|------|------|
| **Git** | 需支持 `--recurse-submodules`，并安装 `git-lfs` 扩展 |
| **Python 3.11+** | 如果缺失，uv 会自动安装 |
| **uv** | 快速 Python 包管理器（[安装](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 可选 —— 浏览器工具和 WhatsApp 桥接需要（与根目录 `package.json` 中引擎版本一致） |

<a id="clone-and-install"></a>
### 克隆与安装

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建虚拟环境
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有附加功能（消息、定时任务、CLI 菜单、开发工具）
uv pip install -e ".[all,dev]"

# 可选：浏览器工具
npm install
```

<a id="configure-for-development"></a>
### 开发配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# 至少添加一个 LLM 提供商密钥：
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env
```

<a id="run"></a>
### 运行

```bash
# 创建全局访问的符号链接
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# 验证
hermes doctor
hermes chat -q "Hello"
```

<a id="run-tests"></a>
### 运行测试

```bash
pytest tests/ -v
```

<a id="code-style"></a>
## 代码风格

- **PEP 8**，但允许实际例外（不强制严格的行长度限制）
- **注释**：仅在需要解释非显而易见的意图、权衡或 API 细节时才写注释
- **错误处理**：捕获特定的异常。对意外错误使用 `logger.warning()`/`logger.error()` 并带上 `exc_info=True`
- **跨平台**：不要假定是 Unix 系统（参见下文）
- **配置文件安全的路径**：不要硬编码 `~/.hermes` —— 代码路径应使用 `hermes_constants` 中的 `get_hermes_home()`，用户可见信息应使用 `display_hermes_home()`。完整规则参见 [AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md#profiles-multi-instance-support)。
<a id="cross-platform-compatibility"></a>
## 跨平台兼容性

Hermes 官方支持 **Linux、macOS、WSL2 以及原生 Windows（早期测试版 — 通过 PowerShell 安装）**。原生 Windows 使用 Git Bash（来自 [Git for Windows](https://git-scm.com/download/win)）执行 shell 命令。少数功能需要 POSIX 内核原语，并做了限制：控制台的嵌入式 PTY 终端面板（`/chat` 标签页）仅限 WSL2 使用。原生 Windows 路径较新且变化较快——如果你主要从事 Windows 开发，可能会遇到并需要修复一些小问题。

在贡献代码时，请牢记以下规则：

- **不要添加未经保护的 `signal.SIGKILL` 引用。** 它在 Windows 上未定义。要么通过 `gateway.status.terminate_pid(pid, force=True)`（它在 Windows 上执行 `taskkill /T /F`，在 POSIX 上执行 SIGKILL）路由，要么使用 `getattr(signal, "SIGKILL", signal.SIGTERM)` 作为后备。
- **在 `os.kill(pid, 0)` 探测时，同时捕获 `OSError` 和 `ProcessLookupError`。** 对于已经消失的 PID，Windows 会抛出 `OSError`（WinError 87，“参数不正确”），而不是 `ProcessLookupError`。
- **不要让终端强制遵循 POSIX 语义。** `os.setsid`、`os.killpg`、`os.getpgid`、`os.fork` 在 Windows 上都会引发异常——请用 `if sys.platform != "win32":` 或 `if os.name != "nt":` 进行保护。
- **以显式的 `encoding="utf-8"` 打开文件。** Python 在 Windows 上的默认编码是系统区域设置（通常是 cp1252），这会导致非拉丁文本出现乱码或崩溃。
- **使用 `pathlib.Path` / `os.path.join`——永远不要手动拼接 `/`。** 对于操作系统返回给我们的字符串，这点影响不大；但对我们构造并传递给子进程的字符串则很重要。

关键模式：

<a id="1-termios-and-fcntl-are-unix-only"></a>
### 1. `termios` 和 `fcntl` 仅适用于 Unix

始终同时捕获 `ImportError` 和 `NotImplementedError`：

```python
try:
    from simple_term_menu import TerminalMenu
    menu = TerminalMenu(options)
    idx = menu.show()
except (ImportError, NotImplementedError):
    # 后备方案：带编号的菜单
    for i, opt in enumerate(options):
        print(f"  {i+1}. {opt}")
    idx = int(input("选择: ")) - 1
```

<a id="2-file-encoding"></a>
### 2. 文件编码

某些环境可能以非 UTF-8 编码保存 `.env` 文件：

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

<a id="3-process-management"></a>
### 3. 进程管理

`os.setsid()`、`os.killpg()` 以及信号处理在不同平台上有所差异：

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.setsid
```

<a id="4-path-separators"></a>
### 4. 路径分隔符

使用 `pathlib.Path` 代替使用 `/` 进行字符串拼接。

<a id="security-considerations"></a>
## 安全注意事项

Hermes 拥有终端访问权限，安全性至关重要。

<a id="existing-protections"></a>
### 现有防护措施

| 层面 | 实现方式 |
|-------|---------------|
| **Sudo 密码管道** | 使用 `shlex.quote()` 防止 shell 注入 |
| **危险命令检测** | 在 `tools/approval.py` 中通过正则表达式进行检测，并引入用户批准流程 |
| **Cron 提示注入** | 扫描器可拦截指令覆盖模式 |
| **写入禁止列表** | 受保护路径通过 `os.path.realpath()` 解析，防止符号链接绕过 |
| **技能防护** | 对从 Hub 安装的技能进行安全扫描 |
| **代码执行沙箱** | 子进程运行时剥离 API 密钥 |
| **容器加固** | Docker：丢弃所有能力，禁止提权，限制 PID |
<a id="contributing-security-sensitive-code"></a>
### 贡献安全敏感代码

- 在将用户输入插入到 shell 命令时，始终使用 `shlex.quote()`
- 在访问控制检查前，使用 `os.path.realpath()` 解析符号链接
- 不要记录机密信息
- 在工具执行时捕获宽泛异常
- 如果更改涉及文件路径或进程，在所有平台上进行测试

<a id="pull-request-process"></a>
## Pull Request 流程

<a id="branch-naming"></a>
### 分支命名

```
fix/description        # 错误修复
feat/description       # 新功能
docs/description       # 文档
test/description       # 测试
refactor/description   # 代码重构
```

<a id="before-submitting"></a>
### 提交前

1. **运行测试**：`pytest tests/ -v`
2. **手动测试**：运行 `hermes` 并执行你所修改的代码路径
3. **检查跨平台影响**：考虑 macOS 和不同的 Linux 发行版
4. **保持 PR 专注**：每个 PR 只做一项逻辑变更

<a id="pr-description"></a>
### PR 描述

包含：
- **什么**发生了变化以及**为什么**
- **如何测试**它
- **你在哪些平台上**测试过
- 引用任何相关的问题

<a id="commit-messages"></a>
### 提交信息

我们使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<类型>(<作用域>): <描述>
```

| 类型 | 用途 |
|------|------|
| `fix` | 错误修复 |
| `feat` | 新功能 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 代码重构 |
| `chore` | 构建、CI、依赖更新 |

作用域：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security`

示例：
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
```

<a id="reporting-issues"></a>
## 报告问题

- 使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- 包含：操作系统、Python 版本、Hermes 版本（`hermes version`）、完整错误回溯
- 包含复现步骤
- 在创建重复问题前，先检查已有问题
- 对于安全漏洞，请私下报告

<a id="community"></a>
## 社区

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**：用于设计方案与架构讨论
- **Skills Hub**：上传专业技能并与社区分享

<a id="license"></a>
## 许可证

通过贡献，你同意你的贡献将根据 [MIT License](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 进行许可。
