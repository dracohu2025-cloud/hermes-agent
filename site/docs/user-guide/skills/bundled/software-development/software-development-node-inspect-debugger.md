---
title: "Node Inspect Debugger — 调试 Node"
sidebar_label: "Node Inspect Debugger"
description: "调试 Node"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Node Inspect Debugger {#node-inspect-debugger}

通过 `--inspect` + Chrome DevTools 协议 CLI 调试 Node.js。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/node-inspect-debugger` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `debugging`, `nodejs`, `node-inspect`, `cdp`, `breakpoints`, `ui-tui` |
| 相关技能 | [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`python-debugpy`](/user-guide/skills/bundled/software-development/software-development-python-debugpy), [`debugging-hermes-tui-commands`](/user-guide/skills/bundled/software-development/software-development-debugging-hermes-tui-commands) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Node.js Inspect Debugger {#node-js-inspect-debugger}

## 概述 {#overview}

当 `console.log` 不够用时，从终端以编程方式驱动 Node 内置的 V8 检查器。你可以获得真正的断点、单步进入/跳过/跳出、调用栈遍历、本地/闭包作用域转储，以及在暂停帧中执行任意表达式求值。

两种工具，任选其一：

- **`node inspect`** — 内置，零安装，CLI REPL。最适合快速探查。
- **`ndb` / 通过 `chrome-remote-interface` 使用 CDP** — 可从 Node/Python 脚本化；当你需要自动化多个断点、跨运行收集状态，或从 Agent 循环中非交互式调试时，最为合适。

**优先使用 `node inspect`。** 它始终可用，且 REPL 速度很快。

## 何时使用 {#when-to-use}

- Node 测试失败，需要查看中间状态
- ui-tui 崩溃或行为异常，需要检查渲染前的 React/Ink 状态
- tui_gateway 子进程（`_SlashWorker`、PTY 桥接工作进程）行为异常
- 需要检查闭包中的某个值，而 `console.log` 在不修改代码的情况下无法访问
- 性能：附加到正在运行的进程以捕获 CPU 性能分析或堆快照

**不要用于：** `console.log` 在一分钟内就能解决的问题。基于断点的调试更重，只有在确实能带来收益时才使用。

## 快速参考：`node inspect` REPL {#quick-reference-node-inspect-repl}

在第一行暂停启动：

```bash
node inspect path/to/script.js
# 或使用 tsx
node --inspect-brk $(which tsx) path/to/script.ts
```

`debug>` 提示符接受以下命令：

| 命令 | 操作 |
|---|---|
| `c` 或 `cont` | 继续执行 |
| `n` 或 `next` | 单步跳过 |
| `s` 或 `step` | 单步进入 |
| `o` 或 `out` | 单步跳出 |
| `pause` | 暂停正在运行的代码 |
| `sb('file.js', 42)` | 在 file.js 第 42 行设置断点 |
| `sb(42)` | 在当前文件第 42 行设置断点 |
| `sb('functionName')` | 当函数被调用时中断 |
| `cb('file.js', 42)` | 清除断点 |
| `breakpoints` | 列出所有断点 |
| `bt` | 回溯（调用栈） |
| `list(5)` | 显示当前位置周围 5 行源代码 |
| `watch('expr')` | 每次暂停时求值表达式 |
| `watchers` | 显示监视的表达式 |
| `repl` | 进入当前作用域的 REPL（Ctrl+C 退出 REPL） |
| `exec expr` | 求值一次表达式 |
| `restart` | 重启脚本 |
| `kill` | 终止脚本 |
| `.exit` | 退出调试器 |
**在 `repl` 子模式下：** 输入任意 JS 表达式，包括访问局部变量/闭包变量。`Ctrl+C` 退出回到 `debug>`。

## 附加到正在运行的进程 {#attaching-to-a-running-process}

当进程已经在运行中时（例如一个长期运行的开发服务器或 TUI 网关）：

```bash
# 1. 发送 SIGUSR1 信号，在现有进程上启用检查器
kill -SIGUSR1 <pid>
# Node 输出：Debugger listening on ws://127.0.0.1:9229/<uuid>

# 2. 附加调试器 CLI
node inspect -p <pid>
# 或通过 URL
node inspect ws://127.0.0.1:9229/<uuid>
```

从一开始就启用检查器启动进程：

```bash
node --inspect script.js           # 监听 127.0.0.1:9229，保持运行
node --inspect-brk script.js       # 监听并在第一行暂停
node --inspect=0.0.0.0:9230 script.js   # 自定义 host:port
```

通过 tsx 使用 TypeScript：

```bash
node --inspect-brk --import tsx script.ts
# 或旧版 tsx
node --inspect-brk -r tsx/cjs script.ts
```

## 编程式 CDP（从终端编写脚本） {#programmatic-cdp-scripting-from-terminal}

当你想要自动化操作时——设置多个断点、捕获作用域状态、编写复现脚本——使用 `chrome-remote-interface`：

```bash
npm i -g chrome-remote-interface        # 或项目本地安装
# 启动目标进程：
node --inspect-brk=9229 target.js &
```

驱动脚本（保存为 `/tmp/cdp-debug.js`）：

```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;

  Debugger.paused(async ({ callFrames, reason }) => {
    const top = callFrames[0];
    console.log(`PAUSED: ${reason} @ ${top.url}:${top.location.lineNumber + 1}`);

    // 遍历作用域以获取局部变量
    for (const scope of top.scopeChain) {
      if (scope.type === 'local' || scope.type === 'closure') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId,
          ownProperties: true,
        });
        for (const p of result) {
          console.log(`  ${scope.type}.${p.name} =`, p.value?.value ?? p.value?.description);
        }
      }
    }

    // 在暂停的帧中计算表达式
    const { result } = await Debugger.evaluateOnCallFrame({
      callFrameId: top.callFrameId,
      expression: 'typeof state !== "undefined" ? JSON.stringify(state) : "n/a"',
    });
    console.log('state =', result.value ?? result.description);

    await Debugger.resume();
  });

  await Runtime.enable();
  await Debugger.enable();

  // 通过 URL 正则 + 行号设置断点
  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$',
    lineNumber: 119,       // 0 索引
    columnNumber: 0,
  });

  await Runtime.runIfWaitingForDebugger();
})();
```

运行它：

```bash
node /tmp/cdp-debug.js
```

Hermes 特定说明：`chrome-remote-interface` **不在** `ui-tui/package.json` 中。如果你不想污染项目，可以将其安装到一个临时位置：

```bash
mkdir -p /tmp/cdp-tools && cd /tmp/cdp-tools && npm i chrome-remote-interface
NODE_PATH=/tmp/cdp-tools/node_modules node /tmp/cdp-debug.js
```
## 调试 Hermes ui-tui {#debugging-hermes-ui-tui}

TUI 基于 Ink + tsx 构建。两种常见场景：

### 在开发环境下调试单个 Ink 组件 {#debugging-a-single-ink-component-under-dev}

`ui-tui/package.json` 中有 `npm run dev`（tsx --watch）。通过直接运行 tsx 来添加 `--inspect-brk`：

```bash
cd /home/bb/hermes-agent/ui-tui
npm run build    # 先构建一次 dist/，这样首次加载时无需转译
node --inspect-brk dist/entry.js
# 在另一个终端中：
node inspect -p <node pid>
```

然后在 `debug>` 提示符下：

```
sb('dist/app.js', 220)     # 或者在你怀疑有问题的渲染位置
cont
```

当暂停时，`repl` → 检查 `props`、state refs、`useInput` 处理函数的值等。

### 调试正在运行的 `hermes --tui` {#debugging-a-running-hermes-tui}

TUI 从 Python CLI 中启动 Node。最简单的方法：

```bash
# 1. 启动 TUI
hermes --tui &
TUI_PID=$(pgrep -f 'ui-tui/dist/entry' | head -1)

# 2. 在该 Node PID 上启用 inspector
kill -SIGUSR1 "$TUI_PID"

# 3. 找到 WS URL
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'

# 4. 附加
node inspect ws://127.0.0.1:9229/<uuid>
```

与 TUI 交互（在其窗口中输入）会继续推进执行；你的调试器可以在任何 `sb(...)` 处通过断点暂停它。

### 调试 `_SlashWorker` / PTY 子进程 {#debugging-slashworker-pty-child-processes}

这些是 Python 进程，不是 Node —— 请使用 `python-debugpy` 技能来调试它们。只有 Node 部分（Ink UI、tui_gateway 客户端、`ui-tui/` 下的 tsx 运行测试）使用此技能。

## 在调试器下运行 Vitest 测试 {#running-vitest-tests-under-the-debugger}

```bash
cd /home/bb/hermes-agent/ui-tui
# 运行单个测试文件，在入口处暂停
node --inspect-brk ./node_modules/vitest/vitest.mjs run --no-file-parallelism src/app/foo.test.tsx
```

在另一个终端中：`node inspect -p &lt;pid&gt;`，然后 `sb('src/app/foo.tsx', 42)`，`cont`。

使用 `--no-file-parallelism`（vitest）或 `--runInBand`（jest）以便只存在一个 worker —— 调试池子很痛苦。

## 堆快照与 CPU 性能分析（非交互式） {#heap-snapshots-cpu-profiles-non-interactive}

从上面的 CDP 驱动中，将 Debugger 替换为 `HeapProfiler` / `Profiler`：

```javascript
// 5 秒的 CPU 性能分析
await client.Profiler.enable();
await client.Profiler.start();
await new Promise(r => setTimeout(r, 5000));
const { profile } = await client.Profiler.stop();
require('fs').writeFileSync('/tmp/cpu.cpuprofile', JSON.stringify(profile));
// 在 Chrome DevTools → Performance 标签页中打开 /tmp/cpu.cpuprofile
```

```javascript
// 堆快照
await client.HeapProfiler.enable();
const chunks = [];
client.HeapProfiler.addHeapSnapshotChunk(({ chunk }) => chunks.push(chunk));
await client.HeapProfiler.takeHeapSnapshot({ reportProgress: false });
require('fs').writeFileSync('/tmp/heap.heapsnapshot', chunks.join(''));
```

## 常见陷阱 {#common-pitfalls}

1. **TS 源文件中的行号错误。** 断点命中的是生成的 JS，而不是 `.ts`。要么 (a) 在构建后的 `dist/*.js` 中设置断点，要么 (b) 启用 sourcemaps（`node --enable-source-maps`）并使用 `sb('src/app.tsx', N)` —— 但仅适用于遵循 sourcemaps 的 CDP 客户端。`node inspect` CLI 不支持。

2. **`--inspect` 与 `--inspect-brk` 的区别。** `--inspect` 启动 inspector 但不会暂停；如果你附加得太晚，脚本会越过你的第一个断点。当你需要在任何代码运行之前设置断点时，请使用 `--inspect-brk`。
3. **端口冲突。** 默认端口是 `9229`。如果多个 Node 进程都在调试，请使用 `--inspect=0`（随机端口），然后从 `/json/list` 读取实际 URL：
   ```bash
   curl -s http://127.0.0.1:9229/json/list   # 列出主机上所有可调试的目标
   ```

4. **子进程。** 父进程上的 `--inspect` 不会自动调试其子进程。使用 `NODE_OPTIONS='--inspect-brk' node parent.js` 可以将调试传播到每个子进程；注意它们都需要唯一的端口（当继承 `NODE_OPTIONS='--inspect'` 时，Node 会自动递增端口）。

5. **后台终止。** 如果在目标暂停时按 `Ctrl+C` 退出 `node inspect`，目标会保持暂停状态。要么先执行 `cont`，要么显式 `kill` 目标。

6. **通过 Agent 终端运行 `node inspect`。** 这是一个支持 PTY 的 REPL。在 Hermes 中，使用 `terminal(pty=true)` 或 `background=true` + `process(action='submit', data='...')` 启动它。非 PTY 前台模式适用于一次性命令，但不适用于交互式单步调试。

7. **安全性。** `--inspect=0.0.0.0:9229` 会暴露任意代码执行风险。除非你处于隔离网络，否则始终绑定到 `127.0.0.1`（默认值）。

## 验证清单 {#verification-checklist}

设置调试会话后，请验证：

- [ ] `curl -s http://127.0.0.1:9229/json/list` 返回的正是你期望的目标
- [ ] 第一个断点确实命中（如果没有命中，很可能你漏掉了 `--inspect-brk`，或者在执行完成后才附加）
- [ ] 暂停时的源码列表显示正确的文件（不匹配 = sourcemap 问题，参见陷阱 1）
- [ ] 在 `repl` 中执行 `exec process.pid` 返回你打算附加的 PID

## 一次性配方 {#one-shot-recipes}

**“为什么这个变量在第 X 行是 undefined？”**
```bash
node --inspect-brk script.js &
node inspect -p $!
# debug>
sb('script.js', X)
cont
# paused. Now:
repl
> myVariable
> Object.keys(this)
```

**“进入这个函数的调用路径是什么？”**
```
debug> sb('suspectFn')
debug> cont
# paused on entry
debug> bt
```

**“这个异步链卡住了——在哪里？”**
```
# 使用 --inspect（不带 -brk）启动，让它运行到卡住，然后：
debug> pause
debug> bt
# 现在你会看到卡住的帧
```
