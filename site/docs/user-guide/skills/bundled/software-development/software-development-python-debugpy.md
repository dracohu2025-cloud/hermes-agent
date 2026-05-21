---
title: "Python Debugpy — 调试 Python：pdb REPL + debugpy 远程 (DAP)"
sidebar_label: "Python Debugpy"
description: "调试 Python：pdb REPL + debugpy 远程 (DAP)"
---

{/* 此页面通过 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="python-debugpy"></a>
# Python Debugpy

调试 Python：pdb REPL + debugpy 远程 (DAP)。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 默认安装 |
| 路径 | `skills/software-development/python-debugpy` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `debugging`, `python`, `pdb`, `debugpy`, `breakpoints`, `dap`, `post-mortem` |
| 相关技能 | [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`node-inspect-debugger`](/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), [`debugging-hermes-tui-commands`](/user-guide/skills/bundled/software-development/software-development-debugging-hermes-tui-commands) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 所看到的指令。
:::

<a id="python-debugger-pdb-debugpy"></a>
# Python 调试器（pdb + debugpy）

<a id="overview"></a>
## 概览

共三种工具，根据场景选用：

| 工具 | 适用场景 |
|---|---|
| **`breakpoint()` + pdb** | 本地、交互式、最简单。在源码中添加 `breakpoint()`，正常运行，即可在该行获得一个 REPL。 |
| **`python -m pdb`** | 以 pdb 启动现有脚本，无需修改源码。适合快速探试。 |
| **`debugpy`** | 远程 / 无头 / “附加到正在运行的进程”。使用 DAP 协议，可通过终端脚本调用，适用于长期运行的进程（网关、守护进程、PTY 子进程）。 |

**先从 `breakpoint()` 开始。** 这是成本最低的方式。

<a id="when-to-use"></a>
## 何时使用

- 测试失败，但回溯信息无法揭示某个值为何错误
- 需要逐步执行函数，观察集合的变化
- 长期运行的进程（hermes gateway、tui_gateway）行为异常，且无法重启
- 事后调试：在生产环境代码中触发了异常，你想在崩溃位置检查局部变量
- 子进程 / 子任务（Python `_SlashWorker`、PTY 桥接 worker）才是真正的 bug 所在

**不要用于：** 用 `print()` / `logging.debug` 一分钟就能解决的问题，或通过 `pytest -vv --tb=long --showlocals` 已经能揭示的问题。

<a id="pdb-quick-reference"></a>
## pdb 快速参考

在任何 pdb 提示符（`(Pdb)`）下：

| 命令 | 操作 |
|---|---|
| `h` / `h cmd` | 帮助 |
| `n` | 下一步（步过） |
| `s` | 单步进入 |
| `r` | 从当前函数返回 |
| `c` | 继续 |
| `unt N` | 继续执行直到第 N 行 |
| `j N` | 跳转到第 N 行（仅限同一函数） |
| `l` / `ll` | 列出当前行周围的源码 / 完整函数 |
| `w` | 查看当前位置（堆栈跟踪） |
| `u` / `d` | 在堆栈中上移 / 下移 |
| `a` | 打印当前函数的参数 |
| `p expr` / `pp expr` | 打印 / 漂亮打印表达式 |
| `display expr` | 每次停止时自动打印表达式 |
| `b file:line` | 设置断点 |
| `b func` | 在函数入口处中断 |
| `b file:line, cond` | 条件断点 |
| `cl N` | 清除断点 N |
| `tbreak file:line` | 一次性断点 |
| `!stmt` | 执行任意 Python 代码（包括赋值） |
| `interact` | 进入当前作用域的全功能 Python REPL（Ctrl+D 退出） |
| `q` | 退出 |
`interact` 命令最为强大——你可以导入任何东西、检查复杂对象，甚至调用会修改状态的方法。局部变量默认只读；在 `(Pdb)` 提示符下使用 `!x = 42` 即可修改。

<a id="recipe-1-local-breakpoint"></a>
## 方案 1：本地断点

最简单。编辑文件：

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- 在这里进入 pdb
    return result + y
```

正常运行代码。程序会在 `breakpoint()` 行停下来，你可以完全访问局部变量。

**记得在提交前删除 `breakpoint()`。** 使用 `git diff` 或提交前的 grep 检查：
```bash
rg -n 'breakpoint\(\)' --type py
```

<a id="recipe-2-launch-a-script-under-pdb-no-source-edits"></a>
## 方案 2：在 pdb 下启动脚本（无需修改源码）

```bash
python -m pdb path/to/script.py arg1 arg2
# 停在脚本第一行
(Pdb) b path/to/script.py:42
(Pdb) c
```

<a id="recipe-3-debug-a-pytest-test"></a>
## 方案 3：调试 pytest 测试

hermes 测试运行器和 pytest 都支持此功能：

```bash
# 失败时（或抛出任何异常时）进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb

# 在测试开始时进入 pdb：
scripts/run_tests.sh tests/path/to/test_file.py::test_name --trace

# 显示回溯中的局部变量（不进入 pdb）：
scripts/run_tests.sh tests/path/to/test_file.py --showlocals --tb=long
```

注意：`scripts/run_tests.sh` 默认使用 xdist（`-n 4`），而 pdb 在 xdist 下无法工作。请添加 `-p no:xdist`，或者使用 `-n 0` 运行单个测试：

```bash
scripts/run_tests.sh tests/foo_test.py::test_bar --pdb -p no:xdist
# 或者
source .venv/bin/activate
python -m pytest tests/foo_test.py::test_bar --pdb
```

这会绕过封闭环境保障——对调试来说是好的，但在推送前应重新在包装器下运行以确认。

<a id="recipe-4-post-mortem-on-any-exception"></a>
## 方案 4：任何异常的事后调试

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
# 当脚本崩溃时，pdb 会捕获异常，你会停在异常发生的帧
```

或者在 repl/jupyter 中设置全局钩子：

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

<a id="recipe-5-remote-debug-with-debugpy-attach-to-running-process"></a>
## 方案 5：使用 debugpy 远程调试（附加到运行中的进程）

适用于长生命周期的进程：Hermes gateway、tui_gateway、守护进程、已经在异常行为且无法干净重启的进程。

<a id="setup"></a>
### 设置

```bash
source /home/bb/hermes-agent/.venv/bin/activate
pip install debugpy
```

<a id="pattern-a-source-edit-process-waits-for-debugger-at-launch"></a>
### 模式 A：修改源码——进程启动时等待调试器

在入口点附近（或要调试的函数内部）添加：

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy 监听在 5678 端口，等待客户端连接...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()       # 可选：连接成功后立即暂停
```

启动进程；它会阻塞在 `wait_for_client()`。

<a id="pattern-b-no-source-edit-launch-with-m-debugpy"></a>
### 模式 B：无需修改源码——使用 `-m debugpy` 启动

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```
模块入口的等价命令：

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

<a id="pattern-c-attach-to-an-already-running-process"></a>
### 模式 C：附加到已运行的进程

需要知道目标环境中已预装 debugpy 及其 PID：

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
# debugpy 会注入到进程内部，然后按下面方式连接客户端。
```

某些内核/安全配置会阻止基于 ptrace 的注入（`/proc/sys/kernel/yama/ptrace_scope`）。通过以下命令修复：
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

<a id="connecting-a-client-from-the-terminal"></a>
### 从终端连接客户端

最简单的终端侧 DAP 客户端是 VS Code CLI 或一个小脚本。在 Hermes 内部，你有两个实用的选择：

**选项 1：`debugpy` 自带的 CLI REPL** —— 这并非官方功能，而是一个精简的 DAP 客户端脚本：

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
# ... 循环读取事件并发送 continue/stepIn 等
```

这种方式适合一次性自动化，但作为交互式用户体验则很痛苦。

**选项 2：从 VS Code / Cursor / Zed 附加** —— 如果用户打开了其中一个编辑器，可以添加一个 `launch.json`：

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

**选项 3：放弃 DAP，使用 `remote-pdb`** —— 这通常是终端 Agent 真正需要的：

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
# 你会看到一个 (Pdb) 提示符，就像本地调试一样。
```

当 `debugpy` 的 DAP 协议过于重量级时，`remote-pdb` 是更简洁、对 Agent 更友好的选择。只有在确实需要 IDE 集成时才使用 `debugpy`。

<a id="debugging-hermes-specific-processes"></a>
## 调试 Hermes 相关进程

<a id="tests"></a>
### 测试
请参见配方 3。始终添加 `-p no:xdist` 或不使用 xdist 运行单个测试。
<a id="runagent-py-cli-one-shot"></a>
### `run_agent.py` / CLI — 一次性执行
最简单的方法：在可疑代码附近加上 `breakpoint()`，然后正常运行 `hermes`。控制权会在暂停点返回到你的终端。

<a id="tuigateway-subprocess-spawned-by-hermes-tui"></a>
### `tui_gateway` 子进程（由 `hermes --tui` 启动）
该网关作为 Node TUI 的子进程运行。选项：

**A. 源码编辑网关：**
```python
# tui_gateway/server.py 靠近 serve() 顶部的位置
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```
启动 `hermes --tui`。TUI 会看起来卡住（其后端正在等待）。连接一个客户端；当你执行 `continue` 时，执行会恢复。

**B. 在特定处理程序中使用 `remote-pdb`：**
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # 在你想要拦截的 RPC 处理程序中
```
从 TUI 触发对应的斜杠命令，然后在另一个终端中执行 `nc 127.0.0.1 4444`。

<a id="slashworker-subprocess"></a>
### `_SlashWorker` 子进程
同样的模式 — 在 worker 的 `exec` 路径中使用 `remote-pdb` 和 `set_trace()`。worker 在斜杠命令之间是持久的，因此第一次触发会阻塞直到你连接；后续的斜杠命令会正常通过，除非你重新启用。

<a id="gateway-gateway-run-py"></a>
### 网关（`gateway/run.py`）
长期运行。在处理程序中使用 `remote-pdb`，或者如果你无论如何都要重启网关，使用带 `--wait-for-client` 的 `debugpy`。

<a id="common-pitfalls"></a>
## 常见陷阱

1. **pdb 在 pytest-xdist 下静默地什么都不做。** 你不会看到提示符，测试只是挂起。始终使用 `-p no:xdist` 或 `-n 0`。

2. **`breakpoint()` 在 CI / 非 TTY 环境中会挂起进程。** 本地安全，但绝不要提交。添加一个 pre-commit grep 作为安全网。

3. **`PYTHONBREAKPOINT=0`** 会禁用所有 `breakpoint()` 调用。如果你的断点没有命中，检查环境变量：
   ```bash
   echo $PYTHONBREAKPOINT
   ```

4. **`debugpy.listen` 仅在你同时调用 `wait_for_client()` 时才会阻塞。** 没有它，执行会继续，你的第一个断点可能在客户端连接之前触发。

5. **在强化内核上附加到 PID 会失败。** `ptrace_scope=1`（Ubuntu 默认）只允许同一用户对子进程进行 ptrace。解决方法：`echo 0 > /proc/sys/kernel/yama/ptrace_scope`（需要 root 权限）或从一开始就在 `debugpy` 下启动。

6. **线程。** `pdb` 只调试当前线程。对于多线程代码，使用 `debugpy`（线程感知的 DAP）或为每个线程设置 `threading.settrace()`。

7. **asyncio。** `pdb` 在协程中工作，但在 pdb 内部使用 `await` 需要 Python 3.13+，或在旧版本上使用 `interact` 模式下的 `await`。对于 3.11/3.12，使用 `asyncio.run_coroutine_threadsafe` 技巧或通过 `asyncio.ensure_future` 进行基于 `!stmt` 的 await。

8. **`scripts/run_tests.sh` 会剥离凭据并设置 `HOME=&lt;tmpdir&gt;`。** 如果你的 bug 依赖于用户配置或真实的 API 密钥，它在包装器下不会复现。先用原始 `pytest` 调试以复现，然后在包装器下重新确认。

9. **Forking / 多进程。** pdb 不会跟随 fork。每个子进程需要自己的 `breakpoint()` 或 `set_trace()`。对于 Hermes subagents，一次调试一个进程。

<a id="verification-checklist"></a>
## 验证检查清单

- [ ] 在 `pip install debugpy` 之后，确认：`python -c "import debugpy; print(debugpy.__version__)"`
- [ ] 对于远程调试，确认端口确实在监听：`ss -tlnp | grep 5678`
- [ ] 第一个断点实际命中（如果没有，你可能设置了 `PYTHONBREAKPOINT=0`，正在 xdist 下运行，或者在附加之前执行已完成）
- [ ] `where` / `w` 显示预期的调用栈
- [ ] 调试后清理：提交的代码中没有残留的 `breakpoint()` / `set_trace()`
  ```bash
  rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
  ```
<a id="one-shot-recipes"></a>
## 一次性配方

**"为什么这个字典缺少一个键？"**
```python
# add above the KeyError site
breakpoint()
# then in pdb:
(Pdb) pp d
(Pdb) pp list(d.keys())
(Pdb) w                # how did we get here
```

**"这个测试单独运行能通过，但放在测试套件里就会失败。"**
```bash
scripts/run_tests.sh tests/the_test.py --pdb -p no:xdist
# But if it only fails WITH other tests:
source .venv/bin/activate
python -m pytest tests/ -x --pdb -p no:xdist
# Now it pdb-traps at the exact failing test after state accumulated.
```

**"我的异步处理程序死锁了。"**
```python
# Add at handler entry
import remote_pdb; remote_pdb.set_trace(host="127.0.0.1", port=4444)
```
触发处理程序。执行 `nc 127.0.0.1 4444`，然后输入 `w` 查看挂起的帧，输入 `!import asyncio; asyncio.all_tasks()` 查看还有哪些任务处于等待状态。

**"对 Ink 子进程 / 子进程中的崩溃进行事后调试。"**
```bash
PYTHONFAULTHANDLER=1 python -m pdb -c continue path/to/entrypoint.py
# On crash, pdb lands at the frame of the exception with full locals
```
