---
title: "Jupyter Live Kernel — 通过实时 Jupyter 内核进行迭代式 Python 开发 (hamelnb)"
sidebar_label: "Jupyter Live Kernel"
description: "通过实时 Jupyter 内核进行迭代式 Python 开发 (hamelnb)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Jupyter Live Kernel {#jupyter-live-kernel}

通过实时 Jupyter 内核进行迭代式 Python 开发 (hamelnb)。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/data-science/jupyter-live-kernel` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `jupyter`, `notebook`, `repl`, `data-science`, `exploration`, `iterative` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Jupyter Live Kernel (hamelnb) {#jupyter-live-kernel-hamelnb}

通过实时 Jupyter 内核为你提供一个**有状态的 Python REPL**。变量在多次执行之间保持持久化。当你需要逐步构建状态、探索 API、检查 DataFrame 或迭代复杂代码时，请使用此技能，而不是 `execute_code`。

## 何时使用此技能与其他工具 {#when-to-use-this-vs-other-tools}

| 工具 | 使用场景 |
|------|----------|
| **此技能** | 迭代式探索、跨步骤状态保持、数据科学、机器学习、“让我试试这个并检查一下” |
| `execute_code` | 需要 hermes 工具访问（web_search、文件操作）的一次性脚本。无状态。 |
| `terminal` | Shell 命令、构建、安装、git、进程管理 |

**经验法则：** 如果某个任务你想用 Jupyter notebook 来做，就用此技能。

## 前提条件 {#prerequisites}

1. 必须安装 **uv**（检查：`which uv`）
2. 必须安装 **JupyterLab**：`uv tool install jupyterlab`
3. 必须运行一个 Jupyter 服务器（参见下面的“设置”）

## 设置 {#setup}

hamelnb 脚本位置：
```
SCRIPT="$HOME/.agent-skills/hamelnb/skills/jupyter-live-kernel/scripts/jupyter_live_kernel.py"
```

如果尚未克隆：
```
git clone https://github.com/hamelsmu/hamelnb.git ~/.agent-skills/hamelnb
```

### 启动 JupyterLab {#starting-jupyterlab}

检查服务器是否已在运行：
```
uv run "$SCRIPT" servers
```

如果没有找到服务器，启动一个：
```
jupyter-lab --no-browser --port=8888 --notebook-dir=$HOME/notebooks \
  --IdentityProvider.token='' --ServerApp.password='' > /tmp/jupyter.log 2>&1 &
sleep 3
```

注意：为本地 Agent 访问禁用了令牌/密码。服务器以无界面模式运行。

### 创建用于 REPL 的 Notebook {#creating-a-notebook-for-repl-use}

如果你只需要一个 REPL（没有现有 notebook），创建一个最小的 notebook 文件：
```
mkdir -p ~/notebooks
```
写入一个包含一个空代码单元格的最小 .ipynb JSON 文件，然后通过 Jupyter REST API 启动一个内核会话：
```
curl -s -X POST http://127.0.0.1:8888/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"path":"scratch.ipynb","type":"notebook","name":"scratch.ipynb","kernel":{"name":"python3"}}'
```

## 核心工作流程 {#core-workflow}

所有命令都返回结构化的 JSON。始终使用 `--compact` 以节省令牌。

### 1. 发现服务器和 notebooks {#1-discover-servers-and-notebooks}

```
uv run "$SCRIPT" servers --compact
uv run "$SCRIPT" notebooks --compact
```

### 2. 执行代码（主要操作） {#2-execute-code-primary-operation}

```
uv run "$SCRIPT" execute --path <notebook.ipynb> --code '<python code>' --compact
```
状态在多次执行调用之间保持持久。变量、导入、对象都会保留。

多行代码可以使用 `$'...'` 引号：
```
uv run "$SCRIPT" execute --path scratch.ipynb --code $'import os\nfiles = os.listdir(".")\nprint(f"Found {len(files)} files")' --compact
```

### 3. 检查实时变量 {#3-inspect-live-variables}

```
uv run "$SCRIPT" variables --path <notebook.ipynb> list --compact
uv run "$SCRIPT" variables --path <notebook.ipynb> preview --name <varname> --compact
```

### 4. 编辑笔记本单元格 {#4-edit-notebook-cells}

```
# 查看当前单元格
uv run "$SCRIPT" contents --path <notebook.ipynb> --compact

# 插入新单元格
uv run "$SCRIPT" edit --path <notebook.ipynb> insert \
  --at-index <N> --cell-type code --source '<code>' --compact

# 替换单元格源码（使用 contents 输出中的 cell-id）
uv run "$SCRIPT" edit --path <notebook.ipynb> replace-source \
  --cell-id <id> --source '<new code>' --compact

# 删除单元格
uv run "$SCRIPT" edit --path <notebook.ipynb> delete --cell-id <id> --compact
```

### 5. 验证（重启并全部运行） {#5-verification-restart-run-all}

仅当用户要求进行干净的验证，或者你需要确认笔记本能从头到尾正常运行时才使用：

```
uv run "$SCRIPT" restart-run-all --path <notebook.ipynb> --save-outputs --compact
```

## 来自实践的经验技巧 {#practical-tips-from-experience}

1. **服务器启动后的首次执行可能会超时**——内核需要一点时间来初始化。如果遇到超时，重试即可。

2. **内核的 Python 是 JupyterLab 的 Python**——包必须安装在该环境中。如果你需要额外的包，请先将其安装到 JupyterLab 工具环境中。

3. **--compact 标志能节省大量 token**——始终使用它。不使用该标志时，JSON 输出会非常冗长。

4. **纯 REPL 使用场景**：创建一个 scratch.ipynb，无需操心单元格编辑。只需反复使用 `execute` 即可。

5. **参数顺序很重要**——子命令标志（如 `--path`）必须放在子子命令之前。例如：`variables --path nb.ipynb list`，而不是 `variables list --path nb.ipynb`。

6. **如果会话尚不存在**，你需要通过 REST API 启动一个（参见设置部分）。没有活动的内核会话，工具无法执行。

7. **错误以 JSON 形式返回**，并附带回溯信息——读取 `ename` 和 `evalue` 字段来了解哪里出了问题。

8. **偶尔的 WebSocket 超时**——某些操作可能在首次尝试时超时，尤其是在内核重启之后。在升级问题之前，先重试一次。

## 超时默认值 {#timeout-defaults}

脚本每次执行默认超时时间为 30 秒。对于长时间运行的操作，请传递 `--timeout 120`。对于初始设置或繁重计算，请使用宽松的超时时间（60 秒以上）。
