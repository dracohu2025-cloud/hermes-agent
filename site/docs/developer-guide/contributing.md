---
sidebar_position: 4
title: "贡献指南"
description: "如何为 Hermes Agent 做贡献——开发环境搭建、代码风格、PR 流程"
---

# 贡献指南 {#contributing}

感谢你为 Hermes Agent 做贡献！本指南涵盖如何搭建开发环境、理解代码库以及让你的 PR 被合并。

## 贡献优先级 {#contribution-priorities}

我们按以下顺序评估贡献的价值：

1. **Bug 修复** — 崩溃、错误行为、数据丢失
2. **跨平台兼容性** — macOS、不同 Linux 发行版、WSL2
3. **安全加固** — shell 注入、提示注入、路径遍历
4. **性能与健壮性** — 重试逻辑、错误处理、优雅降级
5. **新技能** — 广泛有用的技能（参见[创建技能](creating-skills.md)）
6. **新工具** — 很少需要；大多数能力应该以技能形式实现
7. **文档** — 修复、澄清、新示例

## 常见的贡献路径 {#common-contribution-paths}

- 想构建一个新工具？从[添加工具](./adding-tools.md)开始
- 想构建一个新技能？从[创建技能](./creating-skills.md)开始
- 想构建一个新的推理提供方？从[添加提供方](./adding-providers.md)开始

## 开发环境搭建 {#development-setup}

### 前置条件 {#prerequisites}

| 要求 | 说明 |
|-------------|-------|
| **Git** | 需支持 `--recurse-submodules`，并安装 `git-lfs` 扩展 |
| **Python 3.11+** | 如果缺失，uv 会自动安装 |
| **uv** | 快速的 Python 包管理器（[安装](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 可选——浏览器工具和 WhatsApp 桥接需要（与根目录 `package.json` 的 engines 字段一致） |

### 克隆与安装 {#clone-and-install}

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建虚拟环境
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有附加组件（消息、定时任务、CLI 菜单、开发工具）
uv pip install -e ".[all,dev]"
uv pip install -e "./tinker-atropos"

# 可选：浏览器工具
npm install
```

### 配置开发环境 {#configure-for-development}

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# 至少添加一个 LLM 提供方的密钥：
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env
```

### 运行 {#run}

```bash
# 创建全局访问的符号链接
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# 验证
hermes doctor
hermes chat -q "Hello"
```

### 运行测试 {#run-tests}

```bash
pytest tests/ -v
```

## 代码风格 {#code-style}

- **PEP 8** 标准，但允许实际例外（不强制严格的行长度限制）
- **注释**：仅在解释非显而易见的意图、权衡或 API 特殊行为时使用
- **错误处理**：捕获特定异常。对意外错误使用 `logger.warning()`/`logger.error()` 并带上 `exc_info=True`
- **跨平台**：永远不要假设是 Unix 系统（见下文）
- **配置文件安全路径**：永远不要硬编码 `~/.hermes`——代码路径使用 `hermes_constants` 中的 `get_hermes_home()`，面向用户的消息使用 `display_hermes_home()`。完整规则见 [AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md#profiles-multi-instance-support)。

## 跨平台兼容性 {#cross-platform-compatibility}
Hermes 官方支持 Linux、macOS 和 WSL2。原生 Windows **不支持**，但代码库中包含一些防御性编码模式，以避免在极端情况下硬崩溃。关键规则：

### 1. `termios` 和 `fcntl` 仅适用于 Unix {#1-termios-and-fcntl-are-unix-only}

始终捕获 `ImportError` 和 `NotImplementedError`：

```python
try:
    from simple_term_menu import TerminalMenu
    menu = TerminalMenu(options)
    idx = menu.show()
except (ImportError, NotImplementedError):
    # 回退：编号菜单
    for i, opt in enumerate(options):
        print(f"  {i+1}. {opt}")
    idx = int(input("选择: ")) - 1
```

### 2. 文件编码 {#2-file-encoding}

某些环境可能以非 UTF-8 编码保存 `.env` 文件：

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

### 3. 进程管理 {#3-process-management}

`os.setsid()`、`os.killpg()` 和信号处理在不同平台上有所不同：

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.setsid
```

### 4. 路径分隔符 {#4-path-separators}

使用 `pathlib.Path` 而不是用 `/` 进行字符串拼接。

## 安全注意事项 {#security-considerations}

Hermes 具有终端访问权限。安全很重要。

### 现有保护措施 {#existing-protections}

| 层 | 实现 |
|-------|---------------|
| **Sudo 密码管道** | 使用 `shlex.quote()` 防止 shell 注入 |
| **危险命令检测** | `tools/approval.py` 中的正则模式，带有用户批准流程 |
| **Cron 提示注入** | 扫描器阻止指令覆盖模式 |
| **写入拒绝列表** | 通过 `os.path.realpath()` 解析受保护路径，防止符号链接绕过 |
| **技能守卫** | 针对从中心安装的技能的安全扫描器 |
| **代码执行沙箱** | 子进程运行，API 密钥被剥离 |
| **容器加固** | Docker：删除所有能力，无权限提升，PID 限制 |

### 贡献安全敏感代码 {#contributing-security-sensitive-code}

- 在将用户输入插入 shell 命令时，始终使用 `shlex.quote()`
- 在访问控制检查之前，使用 `os.path.realpath()` 解析符号链接
- 不要记录密钥
- 在工具执行周围捕获广泛的异常
- 如果您的更改涉及文件路径或进程，请在所有平台上测试

## 拉取请求流程 {#pull-request-process}

### 分支命名 {#branch-naming}

```
fix/description        # 错误修复
feat/description       # 新功能
docs/description       # 文档
test/description       # 测试
refactor/description   # 代码重构
```

### 提交前 {#before-submitting}

1. **运行测试**：`pytest tests/ -v`
2. **手动测试**：运行 `hermes` 并执行您更改的代码路径
3. **检查跨平台影响**：考虑 macOS 和不同的 Linux 发行版
4. **保持 PR 聚焦**：每个 PR 只做一项逻辑更改

### PR 描述 {#pr-description}

包括：
- **什么**发生了变化以及**为什么**
- **如何测试**
- **您在哪些平台**上测试过
- 引用任何相关问题

### 提交信息 {#commit-messages}

我们使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <description>
```

| 类型 | 用途 |
|------|---------|
| `fix` | 错误修复 |
| `feat` | 新功能 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 代码重构 |
| `chore` | 构建、CI、依赖更新 |
作用域：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security`

示例：
```
fix(cli): 修复当 model 为字符串时 save_config_value 崩溃的问题
feat(gateway): 添加 WhatsApp 多用户会话隔离功能
fix(security): 防止 sudo 密码管道传输中的 shell 注入
```

## 报告问题 {#reporting-issues}

- 使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- 请包含：操作系统、Python 版本、Hermes 版本（`hermes version`）、完整的错误回溯信息
- 请包含复现步骤
- 在创建重复问题前，先检查已有问题
- 对于安全漏洞，请私下报告

## 社区 {#community}

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**：用于设计提案和架构讨论
- **Skills Hub**：上传专业技能并与社区分享

## 许可证 {#license}

通过贡献，您同意您的贡献将根据 [MIT 许可证](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 进行许可。
