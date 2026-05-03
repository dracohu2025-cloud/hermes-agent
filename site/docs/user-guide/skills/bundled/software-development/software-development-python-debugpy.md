---
title: "Python Debugpy — 调试 Python：pdb REPL + debugpy 远程 (DAP)"
sidebar_label: "Python Debugpy"
description: "调试 Python：pdb REPL + debugpy 远程 (DAP)"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Python Debugpy {#python-debugpy}

调试 Python：pdb REPL + debugpy 远程 (DAP)。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/python-debugpy` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `debugging`, `python`, `pdb`, `debugpy`, `breakpoints`, `dap`, `post-mortem` |
| 相关技能 | [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`node-inspect-debugger`](/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), [`debugging-hermes-tui-commands`](/user-guide/skills/bundled/software-development/software-development-debugging-hermes-tui-commands) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Python 调试器（pdb + debugpy） {#python-debugger-pdb-debugpy}

## 概述 {#overview}

三种工具，按场景选用：

| 工具 | 适用场景 |
|---|---|
| **`breakpoint()` + pdb** | 本地、交互式、最简单。在源码中添加 `breakpoint()`，正常运行，即可在该行获得 REPL。 |
| **`python -m pdb`** | 在 pdb 下启动现有脚本，无需修改源码。适合快速探查。 |
| **`debugpy`** | 远程 / 无头 / “附加到正在运行的进程”。使用 DAP 协议，可通过终端脚本化，适用于长期运行的进程（网关、守护进程、PTY 子进程）。 |

**从 `breakpoint()` 开始。** 这是最省事的办法。

## 何时使用 {#when-to-use}

- 测试失败，但回溯信息无法揭示某个值为何错误
- 需要单步执行函数并观察集合的变化
- 长时间运行的进程（hermes gateway、tui_gateway）行为异常，且无法重启
- 事后调试：异常发生在类似生产环境的代码中，想检查崩溃点的局部变量
- 子进程 / 子任务（Python `_SlashWorker`、PTY 桥接工作进程）是实际出问题的地方

**不要用于：** `print()` / `logging.debug` 在一分钟内能解决的问题，或者 `pytest -vv --tb=long --showlocals` 已经能揭示的问题。

## pdb 快速参考 {#pdb-quick-reference}

在任何 pdb 提示符（`(Pdb)`）下：

| 命令 | 作用 |
|---|---|
| `h` / `h cmd` | 帮助 |
| `n` | 下一行（单步跳过） |
| `s` | 步入 |
| `r` | 从当前函数返回 |
| `c` | 继续执行 |
| `unt N` | 继续执行直到第 N 行 |
| `j N` | 跳转到第 N 行（仅限同一函数） |
| `l` / `ll` | 列出当前行附近的源码 / 整个函数 |
| `w` | 显示调用栈（where） |
| `u` / `d` | 在调用栈中向上 / 向下移动 |
| `a` | 打印当前函数的参数 |
| `p expr` / `pp expr` | 打印 / 漂亮打印表达式 |
| `display expr` | 每次停止时自动打印表达式 |
| `b file:line` | 设置断点 |
| `b func` | 在函数入口处设置断点 |
| `b file:line, cond` | 条件断点 |
| `cl N` | 清除断点 N |
| `tbreak file:line` | 一次性断点 |
| `!stmt` | 执行任意 Python 代码（包括赋值） |
| `interact` | 在当前作用域进入完整 Python REPL（Ctrl+D 退出） |
| `q` | 退出 |
`interact` 命令是最强大的——你可以导入任何东西，检查复杂对象，甚至调用会改变状态的方法。局部变量默认是只读的；在 `(Pdb)` 提示符下使用 `!x = 42` 来改变。

## 方案 1：本地断点 {#recipe-1-local-breakpoint}

最简单。编辑文件：

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- 在此处进入 pdb
    return result + y
```

正常运行代码。你会停在 `breakpoint()` 这一行，并且可以完全访问局部变量。

**提交前别忘了删除 `breakpoint()`。** 使用 `git diff` 或提交前 grep：
```bash
rg -n 'breakpoint\(\)' --type py
```

## 方案 2：在 pdb 下启动脚本（无需修改源码） {#recipe-2-launch-a-script-under-pdb-no-source-edits}

```bash
python -m pdb path/to/script.py arg1 arg2
# 停在脚本的第一行
(Pdb) b path/to/script.py:42
(Pdb) c
```

## 方案 3：调试 pytest 测试 {#recipe-3-debug-a-pytest-test}

hermes 测试运行器和 pytest 都支持这个：

```bash
# 在失败时（或任何抛出的异常时）进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb

# 在测试开始时进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py::test_name --trace

# 在回溯中显示局部变量（不进入 pdb）：
scripts/run_tests.sh tests/path/to/test_file.py --showlocals --tb=long
```

注意：`scripts/run_tests.sh` 默认使用 xdist（`-n 4`），而 pdb 在 xdist 下无法工作。添加 `-p no:xdist` 或使用 `-n 0` 运行单个测试：

```bash
scripts/run_tests.sh tests/foo_test.py::test_bar --pdb -p no:xdist
# 或者
source .venv/bin/activate
python -m pytest tests/foo_test.py::test_bar --pdb
```

这会绕过 hermetic-env 的保证——调试时没问题，但在推送前请重新在包装器下运行以确认。

## 方案 4：任何异常的事后调试 {#recipe-4-post-mortem-on-any-exception}

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

或者包装整个脚本：

```bash
python -m pdb -c continue script.py
# 当脚本崩溃时，pdb 会捕获它，你就进入了异常发生的帧
```

或者在 repl/jupyter 中设置全局钩子：

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

## 方案 5：使用 debugpy 远程调试（附加到正在运行的进程） {#recipe-5-remote-debug-with-debugpy-attach-to-running-process}

适用于长时间运行的进程：Hermes gateway、tui_gateway、守护进程、已经出现异常且无法干净重启的进程。

### 设置 {#setup}

```bash
source /home/bb/hermes-agent/.venv/bin/activate
pip install debugpy
```

### 模式 A：修改源码——进程在启动时等待调试器 {#pattern-a-source-edit-process-waits-for-debugger-at-launch}

在入口点顶部附近（或要调试的函数内部）添加：

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy 正在监听 5678，等待客户端...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()       # 可选：附加后立即暂停
```

启动进程；它会阻塞在 `wait_for_client()` 上。

### 模式 B：不修改源码——使用 `-m debugpy` 启动 {#pattern-b-no-source-edit-launch-with-m-debugpy}

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```
模块入口的等效命令：

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

### 模式 C：附加到正在运行的进程 {#pattern-c-attach-to-an-already-running-process}

需要目标环境中已安装 debugpy 并知道进程 PID：

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
# debugpy 会注入到该进程中。然后按下方方式附加客户端。
```

某些内核/安全配置会阻止基于 ptrace 的注入（`/proc/sys/kernel/yama/ptrace_scope`）。可通过以下命令修复：
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

### 从终端连接客户端 {#connecting-a-client-from-the-terminal}

最简单的终端侧 DAP 客户端是 VS Code CLI 或一个小脚本。在 Hermes 内部，你有两个实用的选择：

**选项 1：`debugpy` 自带的 CLI REPL** — 这不是官方功能，而是一个小巧的 DAP 客户端脚本：

```python
# /tmp/dap_client.py
import socket, json, itertools, time, sys

HOST, PORT = "127.0.0.1", 5678
s = socket.create_connection((HOST, PORT))
seq = itertools.count(1)

def send(msg):
    msg["seq"] = next(seq)
    body = json.dumps(msg).encode()
    s.sendall(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)

def recv():
    header = b""
    while b"\r\n\r\n" not in header:
        header += s.recv(1)
    length = int(header.decode().split("Content-Length:")[1].split("\r\n")[0].strip())
    body = b""
    while len(body) < length:
        body += s.recv(length - len(body))
    return json.loads(body)

send({"type": "request", "command": "initialize", "arguments": {"adapterID": "python"}})
print(recv())
send({"type": "request", "command": "attach", "arguments": {}})
print(recv())
send({"type": "request", "command": "setBreakpoints",
      "arguments": {"source": {"path": sys.argv[1]},
                    "breakpoints": [{"line": int(sys.argv[2])}]}})
print(recv())
send({"type": "request", "command": "configurationDone"})
# ... 循环读取事件并发送 continue/stepIn 等命令
```

这对于一次性自动化来说没问题，但作为交互式体验会很痛苦。

**选项 2：从 VS Code / Cursor / Zed 附加** — 如果用户打开了其中一个编辑器，可以添加一个 `launch.json`：

```json
{
  "name": "Attach to Hermes",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "127.0.0.1", "port": 5678 },
  "justMyCode": false,
  "pathMappings": [
    { "localRoot": "${workspaceFolder}", "remoteRoot": "/home/bb/hermes-agent" }
  ]
}
```

**选项 3：放弃 DAP，使用 `remote-pdb`** — 这通常才是你在终端 Agent 中真正想要的：

```bash
pip install remote-pdb
```

在你的代码中：
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # 阻塞直到连接
```

然后在终端中：
```bash
nc 127.0.0.1 4444
# 你会得到一个 (Pdb) 提示符，就像本地调试一样。
```

当 `debugpy` 的 DAP 协议过于复杂时，`remote-pdb` 是最简洁、对 Agent 友好的选择。只有当你确实需要 IDE 集成时才使用 `debugpy`。

## 调试 Hermes 特有的进程 {#debugging-hermes-specific-processes}

### 测试 {#tests}
参见配方 3。始终添加 `-p no:xdist` 或在不使用 xdist 的情况下运行单个测试。
### `run_agent.py` / CLI — 一次性运行 {#runagent-py-cli-one-shot}
最简单的方式：在可疑代码附近添加 `breakpoint()`，然后正常运行 `hermes`。控制权会在暂停点返回到你的终端。

### `tui_gateway` 子进程（由 `hermes --tui` 启动） {#tuigateway-subprocess-spawned-by-hermes-tui}
该 gateway 作为 Node TUI 的子进程运行。选项：

**A. 源码编辑 gateway：**
```python
# tui_gateway/server.py 靠近 serve() 顶部
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```
启动 `hermes --tui`。TUI 会显示为冻结状态（其后端正在等待）。附加一个客户端；当你执行 `continue` 时，执行会恢复。

**B. 在特定 handler 中使用 `remote-pdb`：**
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # 在你想要拦截的 RPC handler 中
```
从 TUI 触发对应的斜杠命令，然后在另一个终端中执行 `nc 127.0.0.1 4444`。

### `_SlashWorker` 子进程 {#slashworker-subprocess}
同样的模式——在 worker 的 `exec` 路径中使用 `remote-pdb` 配合 `set_trace()`。该 worker 在斜杠命令之间是持久的，因此第一次触发会阻塞直到你连接；后续的斜杠命令会正常通过，除非你重新启用。

### Gateway（`gateway/run.py`） {#gateway-gateway-run-py}
长期运行。在 handler 中使用 `remote-pdb`，或者如果你无论如何都要重启 gateway，则使用 `debugpy` 配合 `--wait-for-client`。

## 常见陷阱 {#common-pitfalls}

1. **pdb 在 pytest-xdist 下静默无反应。** 你不会看到提示符，测试只是挂起。始终使用 `-p no:xdist` 或 `-n 0`。

2. **`breakpoint()` 在 CI / 非 TTY 上下文中会挂起进程。** 本地安全；切勿提交。添加一个 pre-commit grep 作为安全网。

3. **`PYTHONBREAKPOINT=0`** 会禁用所有 `breakpoint()` 调用。如果你的断点未命中，检查环境变量：
   ```bash
   echo $PYTHONBREAKPOINT
   ```

4. **`debugpy.listen` 仅在你同时调用 `wait_for_client()` 时才会阻塞。** 没有它，执行会继续，你的第一个断点可能在客户端附加之前触发。

5. **在强化内核上附加到 PID 会失败。** `ptrace_scope=1`（Ubuntu 默认）只允许同一用户对子进程进行 ptrace。解决方法：`echo 0 > /proc/sys/kernel/yama/ptrace_scope`（需要 root）或从一开始就在 `debugpy` 下启动。

6. **线程。** `pdb` 只调试当前线程。对于多线程代码，使用 `debugpy`（线程感知的 DAP）或为每个线程设置 `threading.settrace()`。

7. **asyncio。** `pdb` 可以在协程中工作，但在 pdb 内部使用 `await` 需要 Python 3.13+，或者在旧版本上使用 `interact` 模式下的 `await`。对于 3.11/3.12，使用 `asyncio.run_coroutine_threadsafe` 技巧或通过 `asyncio.ensure_future` 进行基于 `!stmt` 的 await。

8. **`scripts/run_tests.sh` 会剥离凭据并设置 `HOME=&lt;tmpdir&gt;`。** 如果你的 bug 依赖于用户配置或真实的 API 密钥，它不会在包装器下重现。先用原始 `pytest` 调试以重现，然后在包装器下重新确认。

9. **Forking / 多进程。** pdb 不会跟随 fork。每个子进程需要自己的 `breakpoint()` 或 `set_trace()`。对于 Hermes subagents，一次调试一个进程。

## 验证清单 {#verification-checklist}

- [ ] 执行 `pip install debugpy` 后，确认：`python -c "import debugpy; print(debugpy.__version__)"`
- [ ] 对于远程调试，确认端口确实在监听：`ss -tlnp | grep 5678`
- [ ] 第一个断点实际命中（如果没有命中，很可能你设置了 `PYTHONBREAKPOINT=0`，你在 xdist 下，或者执行在附加之前已完成）
- [ ] `where` / `w` 显示预期的调用栈
- [ ] 调试后清理：已提交的代码中没有残留的 `breakpoint()` / `set_trace()`
  ```bash
  rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
  ```
## 一次性配方 {#one-shot-recipes}

**"为什么这个字典缺少一个键？"**
```python
# add above the KeyError site
breakpoint()
# then in pdb:
(Pdb) pp d
(Pdb) pp list(d.keys())
(Pdb) w                # how did we get here
```

**"这个测试单独通过，但在测试套件中失败。"**
```bash
scripts/run_tests.sh tests/the_test.py --pdb -p no:xdist
# But if it only fails WITH other tests:
source .venv/bin/activate
python -m pytest tests/ -x --pdb -p no:xdist
# Now it pdb-traps at the exact failing test after state accumulated.
```

**"我的异步处理器死锁了。"**
```python
# Add at handler entry
import remote_pdb; remote_pdb.set_trace(host="127.0.0.1", port=4444)
```
触发处理器。`nc 127.0.0.1 4444`，然后 `w` 查看挂起的帧，`!import asyncio; asyncio.all_tasks()` 查看还有哪些任务在等待。

**"对 Ink 子进程/子进程崩溃的事后调试。"**
```bash
PYTHONFAULTHANDLER=1 python -m pdb -c continue path/to/entrypoint.py
# On crash, pdb lands at the frame of the exception with full locals
```
