---
sidebar_position: 4
title: "贡献指南"
description: "如何为 Hermes Agent 贡献代码 —— 开发环境设置、代码风格、PR 流程"
---

# 贡献指南

感谢你为 Hermes Agent 贡献代码！本指南涵盖了设置开发环境、理解代码库以及让你的 PR 被合并的流程。

## 贡献优先级

我们按以下顺序看重贡献：

1. **Bug 修复** —— 崩溃、错误行为、数据丢失
2. **跨平台兼容性** —— macOS、不同的 Linux 发行版、WSL2
3. **安全性加固** —— shell 注入、提示词注入、路径遍历
4. **性能和健壮性** —— 重试逻辑、错误处理、优雅降级
5. **新技能** —— 广泛有用的（参见[创建技能](creating-skills.md)）
6. **新工具** —— 很少需要；大部分功能应该作为技能实现
7. **文档** —— 修复、澄清、新示例

## 常见的贡献路径

- 构建新工具？请先阅读[添加工具](./adding-tools.md)
- 构建新技能？请先阅读[创建技能](./creating-skills.md)
- 构建新的推理提供商？请先阅读[添加提供商](./adding-providers.md)

## 开发环境设置

### 前置条件

| 要求 | 说明 |
|-------------|-------|
| **Git** | 支持 `--recurse-submodules` |
| **Python 3.10+** | uv 会在缺失时安装它 |
| **uv** | 快速的 Python 包管理器 ([安装](https://docs.astral.sh/uv/)) |
| **Node.js 18+** | 可选 —— 浏览器工具和 WhatsApp 桥接需要 |

### 克隆与安装

```bash
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 使用 Python 3.11 创建虚拟环境
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 安装所有额外功能（消息传递、定时任务、CLI 菜单、开发工具）
uv pip install -e ".[all,dev]"
uv pip install -e "./tinker-atropos"

# 可选：浏览器工具
npm install
```

### 为开发配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# 至少添加一个 LLM 提供商密钥：
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env
```

### 运行

```bash
# 为全局访问创建符号链接
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

- **PEP 8** 结合实际例外情况（不严格限制行长度）
- **注释**：仅在解释非显而易见的意图、权衡或 API 特性时使用
- **错误处理**：捕获特定的异常。对于意外错误，使用 `logger.warning()`/`logger.error()` 并带上 `exc_info=True`
- **跨平台**：不要假设 Unix（见下文）
- **配置文件安全的路径**：永远不要硬编码 `~/.hermes` —— 代码路径请使用 `hermes_constants` 中的 `get_hermes_home()`，面向用户的消息请使用 `display_hermes_home()`。完整规则参见 [AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md#profiles-multi-instance-support)。

## 跨平台兼容性

Hermes 官方支持 Linux、macOS 和 WSL2。原生 Windows **不支持**，但代码库包含一些防御性编码模式，以避免边缘情况下的严重崩溃。关键规则：

### 1. `termios` 和 `fcntl` 仅限 Unix

始终捕获 `ImportError` 和 `NotImplementedError`：

```python
try:
    from simple_term_menu import TerminalMenu
    menu = TerminalMenu(options)
    idx = menu.show()
except (ImportError, NotImplementedError):
    # 后备方案：编号菜单
    for i, opt in enumerate(options):
        print(f"  {i+1}. {opt}")
    idx = int(input("Choice: ")) - 1
```

### 2. 文件编码

某些环境可能以非 UTF-8 编码保存 `.env` 文件：

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

### 3. 进程管理

`os.setsid()`、`os.killpg()` 和信号处理在不同平台上有差异：

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.setsid
```

### 4. 路径分隔符

使用 `pathlib.Path` 而不是用 `/` 进行字符串拼接。

## 安全性考量

Hermes 拥有终端访问权限。安全性很重要。

### 已有保护措施

| 层级 | 实现 |
|-------|---------------|
| **Sudo 密码管道传输** | 使用 `shlex.quote()` 防止 shell 注入 |
| **危险命令检测** | `tools/approval.py` 中的正则模式配合用户审批流程 |
| **定时任务提示词注入** | 扫描器阻止指令覆盖模式 |
| **写入拒绝列表** | 通过 `os.path.realpath()` 解析受保护路径以防止符号链接绕过 |
| **技能守卫** | 针对 hub 安装技能的安全扫描器 |
| **代码执行沙箱** | 子进程运行时剥离 API 密钥 |
| **容器加固** | Docker：所有权限被丢弃，无权限提升，PID 限制 |

### 贡献安全敏感代码

- 将用户输入插值到 shell 命令时，始终使用 `shlex.quote()`
- 在访问控制检查之前，使用 `os.path.realpath()` 解析符号链接
- 不要记录密钥
- 在工具执行周围捕获广泛的异常
- 如果你的改动涉及文件路径或进程，请在所有平台上测试

## Pull Request 流程

### 分支命名

```
fix/description        # Bug 修复
feat/description       # 新功能
docs/description       # 文档
test/description       # 测试
refactor/description   # 代码重构
```

### 提交前检查

1. **运行测试**：`pytest tests/ -v`
2. **手动测试**：运行 `hermes` 并测试你更改的代码路径
3. **检查跨平台影响**：考虑 macOS 和不同的 Linux 发行版
4. **保持 PR 专注**：每个 PR 一个逻辑变更

### PR 描述

包含：
- **变更了什么**和**为什么**
- **如何测试**它
- **在什么平台**上测试过
- 引用任何相关 issues

### 提交消息

我们使用[约定式提交](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

| 类型 | 用于 |
|------|---------|
| `fix` | Bug 修复 |
| `feat` | 新功能 |
| `docs` | 文档 |
| `test` | 测试 |
| `refactor` | 代码重构 |
| `chore` | 构建、CI、依赖更新 |

范围：`cli`, `gateway`, `tools`, `skills`, `agent`, `install`, `whatsapp`, `security`

示例：
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
```

## 报告问题

- 使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
- 包含：操作系统、Python 版本、Hermes 版本 (`hermes version`)、完整错误回溯
- 包含复现步骤
- 创建新问题前检查现有问题
- 对于安全漏洞，请私下报告

## 社区

- **Discord**: [discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**: 用于设计提案和架构讨论
- **技能中心**: 上传专业技能并与社区分享

## 许可证

通过贡献，你同意你的贡献将按照[MIT 许可证](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE)进行许可。
