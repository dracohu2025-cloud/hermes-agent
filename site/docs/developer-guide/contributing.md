---
sidebar_position: 4
title: "贡献指南"
description: "如何为 Hermes Agent 贡献代码 —— 开发设置、代码风格、PR 流程"
---

# 贡献指南

感谢你为 Hermes Agent 做出贡献！本指南涵盖了开发环境搭建、代码库理解以及如何让你的 PR 被合并。

## 贡献优先级

我们按以下顺序评估贡献的价值：

1. **Bug 修复** —— 崩溃、错误行为、数据丢失
2. **跨平台兼容性** —— macOS、不同的 Linux 发行版、WSL2
3. **安全加固** —— Shell 注入、提示词注入、路径穿越
4. **性能与健壮性** —— 重试逻辑、错误处理、优雅降级
5. **新 Skill** —— 具有广泛用途的 Skill（参见 [创建 Skill](creating-skills.md)）
6. **新 Tool** —— 很少需要；大多数功能应该作为 Skill 实现
7. **文档** —— 修复、澄清、新示例

## 常见的贡献路径

- 想要构建新 Tool？从 [添加 Tool](./adding-tools.md) 开始
- 想要构建新 Skill？从 [创建 Skill](./creating-skills.md) 开始
- 想要构建新的推理提供商（Provider）？从 [添加 Provider](./adding-providers.md) 开始

## 开发设置

### 前置条件

| 要求 | 备注 |
|-------------|-------|
| **Git** | 需支持 `--recurse-submodules` |
| **Python 3.11+** | 如果缺失，uv 会自动安装 |
| **uv** | 极速 Python 包管理器 ([安装](https://docs.astral.sh/uv/)) |
| **Node.js 18+** | 可选 —— 浏览器 Tool 和 WhatsApp 桥接需要 |

### 克隆与安装

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建虚拟环境
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有额外组件（消息、cron、CLI 菜单、开发工具）
uv pip install -e ".[all,dev]"
uv pip install -e "./tinker-atropos"

# 可选：浏览器 Tool
npm install
```

### 开发配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# 至少添加一个 LLM Provider 的 API Key：
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env
```

### 运行

```bash
# 创建软链接以便全局访问
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# 验证
hermes doctor
hermes chat -q "Hello"
```

### 运行测试

```bash
pytest tests/ -v
```

## 代码风格

- **PEP 8**：允许实际开发中的例外（不强制限制行宽）
- **注释**：仅在解释非显图意图、权衡取舍或 API 特性时使用
- **错误处理**：捕获具体的异常。对于非预期错误，使用 `logger.warning()`/`logger.error()` 并带上 `exc_info=True`
- **跨平台**：永远不要假设环境是 Unix（见下文）
- **Profile 安全路径**：永远不要硬编码 `~/.hermes` —— 代码路径请使用 `hermes_constants` 中的 `get_hermes_home()`，面向用户的消息请使用 `display_hermes_home()`。完整规则请参考 [AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md#profiles-multi-instance-support)。

## 跨平台兼容性

Hermes 正式支持 Linux、macOS 和 WSL2。**不支持**原生 Windows，但代码库包含了一些防御性编程模式，以避免在极端情况下发生硬崩溃。关键规则：

### 1. `termios` 和 `fcntl` 仅限 Unix

务必同时捕获 `ImportError` 和 `NotImplementedError`：

```python
try:
    from simple_term_menu import TerminalMenu
    menu = TerminalMenu(options)
    idx = menu.show()
except (ImportError, NotImplementedError):
    # 备选方案：数字菜单
    for i, opt in enumerate(options):
        print(f"  {i+1}. {opt}")
    idx = int(input("Choice: ")) - 1
```

### 2. 文件编码

某些环境可能会以非 UTF-8 编码保存 `.env` 文件：

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

### 3. 进程管理

`os.setsid()`、`os.killpg()` 和信号处理在不同平台上有所不同：

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.sid
```

### 4. 路径分隔符

使用 `pathlib.Path` 而不是使用 `/` 进行字符串拼接。

## 安全考量

Hermes 拥有终端访问权限。安全性至关重要。

### 现有保护机制

| 层级 | 实现方式 |
|-------|---------------|
| **Sudo 密码管道** | 使用 `shlex.quote()` 防止 Shell 注入 |
| **危险命令检测** | `tools/approval.py` 中的正则模式配合用户确认流程 |
| **Cron 提示词注入** | 扫描器拦截指令覆盖（instruction-override）模式 |
| **写入黑名单** | 通过 `os.path.realpath()` 解析受保护路径，防止符号链接绕过 |
| **Skills 守卫** | 针对 Hub 安装的 Skill 的安全扫描器 |
| **代码执行沙箱** | 子进程运行时会剥离 API Key |
| **容器加固** | Docker：丢弃所有 capability，禁止权限提升，限制 PID 数量 |

### 贡献安全敏感代码

- 在将用户输入插入 Shell 命令时，务必使用 `shlex.quote()`
- 在进行访问控制检查前，先用 `os.path.realpath()` 解析符号链接
- 不要记录敏感信息（Secrets）到日志
- 在 Tool 执行周围捕获宽泛的异常
- 如果你的更改涉及文件路径或进程，请在所有平台上进行测试

## Pull Request 流程

### 分支命名

```
fix/description        # Bug 修复
feat/description       # 新功能
docs/description       # 文档
test/description       # 测试
refactor/description   # 代码重构
```

### 提交之前

1. **运行测试**：`pytest tests/ -v`
2. **手动测试**：运行 `hermes` 并执行你修改的代码路径
3. **检查跨平台影响**：考虑 macOS 和不同的 Linux 发行版
4. **保持 PR 聚焦**：每个 PR 只包含一个逻辑变更

### PR 描述

需包含：
- **修改了什么**以及**为什么**修改
- **如何测试**
- 你在**哪些平台**上进行了测试
- 引用任何相关的 Issue

### Commit 消息

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>
```

| 类型 | 用途 |
|------|---------|
| `fix` | Bug 修复 |
| `feat` | 新功能 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 代码重构 |
| `chore` | 构建、CI、依赖更新 |

作用域（Scopes）：`cli`, `gateway`, `tools`, `skills`, `agent`, `install`, `whatsapp`, `security`

示例：
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
```

## 报告问题

- 使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- 包含：操作系统、Python 版本、Hermes 版本（`hermes version`）、完整的错误堆栈追踪
- 包含复现步骤
- 在创建重复问题前先检查现有 Issue
- 对于安全漏洞，请进行私下报告

## 社区

- **Discord**: [discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**: 用于设计提案和架构讨论
- **Skills Hub**: 上传专门的 Skill 并与社区分享

## 许可证

通过贡献代码，你同意你的贡献将基于 [MIT License](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 进行授权。
