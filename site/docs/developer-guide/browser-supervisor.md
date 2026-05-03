# Browser CDP Supervisor — 设计 {#browser-cdp-supervisor-design}

**状态：** 已发布（PR 14540）
**最后更新：** 2026-04-23
**作者：** @teknium1

## 问题 {#problem}

原生 JS 对话框（`alert`/`confirm`/`prompt`/`beforeunload`）和 iframe 是我们浏览器工具中最大的两个缺口：

1. **对话框会阻塞 JS 线程。** 页面上的任何操作都会停滞，直到对话框被处理。在此工作之前，Agent 无法知道对话框已打开——后续的工具调用会挂起或抛出模糊的错误。
2. **iframe 不可见。** Agent 可以在 DOM 快照中看到 iframe 节点，但无法在其中点击、输入或执行 eval——尤其是跨源（OOPIF）的 iframe，它们位于独立的 Chromium 进程中。

[PR #12550](https://github.com/NousResearch/hermes-agent/pull/12550) 提出了一个无状态的 `browser_dialog` 包装器。但这并不能解决检测问题——它只是在 Agent 已经（通过症状）知道对话框打开时，提供一个更干净的 CDP 调用。该 PR 已关闭，被取代。

## 后端能力矩阵（2026-04-23 实时验证） {#backend-capability-matrix-verified-live-2026-04-23}

使用一次性探测脚本，针对一个数据 URL 页面（该页面在主框架和同源 srcdoc iframe 中触发 alert，以及一个跨源 `https://example.com` iframe）进行测试：

| 后端 | 对话框检测 | 对话框响应 | 框架树 | 通过 `browser_cdp(frame_id=...)` 进行 OOPIF `Runtime.evaluate` |
|---|---|---|---|---|
| 本地 Chrome（`--remote-debugging-port`）/ `/browser connect` | ✓ | ✓ 完整工作流 | ✓ | ✓ |
| Browserbase | ✓（通过桥接） | ✓ 完整工作流（通过桥接） | ✓ | ✓（在真实跨源 iframe 上验证了 `document.title = "Example Domain"`） |
| Camofox | ✗ 无 CDP（仅 REST） | ✗ | 通过 DOM 快照部分支持 | ✗ |

**Browserbase 的响应机制。** Browserbase 的 CDP 代理内部使用 Playwright，并在约 10ms 内自动关闭原生对话框，因此 `Page.handleJavaScriptDialog` 无法跟上。为了解决这个问题，supervisor 通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个桥接脚本，该脚本用同步 XHR 覆盖 `window.alert`/`confirm`/`prompt`，指向一个魔法主机（`hermes-dialog-bridge.invalid`）。`Fetch.enable` 在这些 XHR 触及网络之前拦截它们——对话框变成了 supervisor 捕获的 `Fetch.requestPaused` 事件，而 `respond_to_dialog` 通过 `Fetch.fulfillRequest` 完成响应，返回一个注入脚本解码的 JSON 体。

最终结果：从页面的角度看，`prompt()` 仍然返回 Agent 提供的字符串。从 Agent 的角度看，无论哪种方式，都是相同的 `browser_dialog(action=...)` API。已在真实 Browserbase 会话上进行了端到端测试——4/4（alert/prompt/confirm-accept/confirm-dismiss）通过，包括值往返回页面 JS。

Camofox 在此 PR 中仍不受支持；计划在 `jo-inc/camofox-browser` 提交上游问题，请求一个对话框轮询端点。

## 架构 {#architecture}

### CDPSupervisor {#cdpsupervisor}

每个 Hermes `task_id` 对应一个在后台守护线程中运行的 `asyncio.Task`。持有一个到后端 CDP 端点的持久 WebSocket。维护以下内容：

- **对话框队列** — `List[PendingDialog]`，包含 `{id, type, message, default_prompt, session_id, opened_at}`
- **框架树** — `Dict[frame_id, FrameInfo]`，包含父级关系、URL、源、是否为跨源子会话
- **会话映射** — `Dict[session_id, SessionInfo]`，以便交互工具可以路由到正确的附加会话以进行 OOPIF 操作
- **近期控制台错误** — 最近 50 条错误的环形缓冲区（用于 PR 2 的诊断）
在附加时订阅：
- `Page.enable` — `javascriptDialogOpening`、`frameAttached`、`frameNavigated`、`frameDetached`
- `Runtime.enable` — `executionContextCreated`、`consoleAPICalled`、`exceptionThrown`
- `Target.setAutoAttach {autoAttach: true, flatten: true}` — 暴露子 OOPIF 目标；supervisor 在每个目标上启用 `Page`+`Runtime`

通过快照锁实现线程安全的状态访问；工具处理程序（同步）读取冻结的快照，无需等待。

### 生命周期 {#lifecycle}

- **启动：** `SupervisorRegistry.get_or_start(task_id, cdp_url)` — 由 `browser_navigate`、Browserbase 会话创建、`/browser connect` 调用。幂等。
- **停止：** 会话拆除或 `/browser disconnect`。取消 asyncio 任务，关闭 WebSocket，丢弃状态。
- **重新绑定：** 如果 CDP URL 发生变化（用户重新连接到新的 Chrome），停止旧的 supervisor 并重新开始——绝不跨端点复用状态。

### 对话框策略 {#dialog-policy}

可通过 `config.yaml` 中的 `browser.dialog_policy` 配置：

- **`must_respond`**（默认）— 捕获，在 `browser_snapshot` 中展示，等待显式调用 `browser_dialog(action=...)`。若 300 秒安全超时内无响应，则自动关闭并记录日志。防止有缺陷的 Agent 无限期卡住。
- `auto_dismiss` — 记录并立即关闭；Agent 事后通过 `browser_snapshot` 中的 `browser_state` 看到它。
- `auto_accept` — 记录并接受（对于 `beforeunload` 场景很有用，用户希望干净地离开页面）。

策略按任务设置；v1 中不支持按对话框覆盖。

## Agent 接口（PR 1） {#agent-surface-pr-1}

### 一个新工具 {#one-new-tool}

```
browser_dialog(action, prompt_text=None, dialog_id=None)
```

- `action="accept"` / `"dismiss"` → 响应指定的或唯一的待处理对话框（必填）
- `prompt_text=...` → 提供给 `prompt()` 对话框的文本
- `dialog_id=...` → 当多个对话框排队时消除歧义（罕见）

该工具仅用于响应。Agent 在调用前从 `browser_snapshot` 输出中读取待处理对话框。

### `browser_snapshot` 扩展 {#browsersnapshot-extension}

当附加了 supervisor 时，在现有快照输出中添加三个可选字段：

```json
{
  "pending_dialogs": [
    {"id": "d-1", "type": "alert", "message": "Hello", "opened_at": 1650000000.0}
  ],
  "recent_dialogs": [
    {"id": "d-1", "type": "alert", "message": "...", "opened_at": 1650000000.0,
     "closed_at": 1650000000.1, "closed_by": "remote"}
  ],
  "frame_tree": {
    "top": {"frame_id": "FRAME_A", "url": "https://example.com/", "origin": "https://example.com"},
    "children": [
      {"frame_id": "FRAME_B", "url": "about:srcdoc", "is_oopif": false},
      {"frame_id": "FRAME_C", "url": "https://ads.example.net/", "is_oopif": true, "session_id": "SID_C"}
    ],
    "truncated": false
  }
}
```

- **`pending_dialogs`**：当前阻塞页面 JS 线程的对话框。Agent 必须调用 `browser_dialog(action=...)` 来响应。在 Browserbase 上为空，因为它们的 CDP 代理会在约 10ms 内自动关闭。
- **`recent_dialogs`**：最多 20 个最近关闭的对话框的环形缓冲区，带有 `closed_by` 标签——`"agent"`（我们响应了）、`"auto_policy"`（本地 auto_dismiss/auto_accept）、`"watchdog"`（must_respond 超时触发）或 `"remote"`（浏览器/后端替我们关闭了，例如 Browserbase）。这样，Browserbase 上的 Agent 仍然能了解发生了什么。
- **`frame_tree`**：帧结构，包括跨源（OOPIF）子帧。上限为 30 条记录 + OOPIF 深度 2，以限制广告密集页面上的快照大小。当达到限制时，`truncated: true` 会显示；需要完整树的 Agent 可以使用 `browser_cdp` 配合 `Page.getFrameTree`。

这些新字段不会暴露新的工具 schema——Agent 直接读取它已经请求的快照。

### 可用性门控 {#availability-gating}

两个字段都依赖 `_browser_cdp_check`（Supervisor 仅在 CDP 端点可达时才能运行）。在 Camofox / 无后端会话中，对话框工具被隐藏，快照省略新字段——不会导致 schema 膨胀。

## 跨源 iframe 交互 {#cross-origin-iframe-interaction}

作为对话框检测工作的扩展，`browser_cdp(frame_id=...)` 通过 Supervisor 已连接的 WebSocket 使用 OOPIF 的子 `sessionId` 路由 CDP 调用（特别是 `Runtime.evaluate`）。Agent 从 `browser_snapshot.frame_tree.children[]` 中提取 `is_oopif=true` 的 frame_id，并将其传递给 `browser_cdp`。对于同源 iframe（没有专用 CDP 会话），Agent 改用顶层 `Runtime.evaluate` 的 `contentWindow`/`contentDocument`——当 `frame_id` 属于非 OOPIF 时，Supervisor 会返回一个指向该回退方案的错误。

在 Browserbase 上，这是 iframe 交互的唯一可靠路径——无状态 CDP 连接（每次 `browser_cdp` 调用时打开）会遇到签名 URL 过期，而 Supervisor 的长连接保持有效会话。

## Camofox（后续） {#camofox-follow-up}

计划针对 `jo-inc/camofox-browser` 提交 issue，添加：
- 每个会话的 Playwright `page.on('dialog', handler)`
- `GET /tabs/:tabId/dialogs` 轮询端点
- `POST /tabs/:tabId/dialogs/:id` 接受/关闭
- 帧树内省端点

## 涉及的文件（PR 1） {#files-touched-pr-1}

### 新增 {#new}

- `tools/browser_supervisor.py` — `CDPSupervisor`、`SupervisorRegistry`、`PendingDialog`、`FrameInfo`
- `tools/browser_dialog_tool.py` — `browser_dialog` 工具处理器
- `tests/tools/test_browser_supervisor.py` — 模拟 CDP WebSocket 服务器 + 生命周期/状态测试
- `website/docs/developer-guide/browser-supervisor.md` — 本文档

### 修改 {#modified}

- `toolsets.py` — 在 `browser`、`hermes-acp`、`hermes-api-server`、核心工具集中注册 `browser_dialog`（受 CDP 可达性门控）
- `tools/browser_tool.py`
  - `browser_navigate` 启动钩子：如果 CDP URL 可解析，则 `SupervisorRegistry.get_or_start(task_id, cdp_url)`
  - `browser_snapshot`（约第 1536 行）：将 Supervisor 状态合并到返回负载中
  - `/browser connect` 处理器：使用新端点重启 Supervisor
  - `_cleanup_browser_session` 中的会话拆除钩子
- `hermes_cli/config.py` — 在 `DEFAULT_CONFIG` 中添加 `browser.dialog_policy` 和 `browser.dialog_timeout_s`
- 文档：`website/docs/user-guide/features/browser.md`、`website/docs/reference/tools-reference.md`、`website/docs/reference/toolsets-reference.md`

## 非目标 {#non-goals}

- Camofox 的检测/交互（上游缺口；单独跟踪）
- 实时向用户流式传输对话框/帧事件（需要网关钩子）
- 跨会话持久化对话框历史（仅内存）
- 每个 iframe 的对话框策略（Agent 可以通过 `dialog_id` 表达）
- 替换 `browser_cdp`——它仍然作为长尾场景（cookies、视口、网络节流）的逃生舱口
## 测试 {#testing}

单元测试使用一个 asyncio 模拟 CDP 服务器，它实现了足够多的协议功能来覆盖所有状态转换：attach、enable、navigate、dialog fire、dialog dismiss、frame attach/detach、child target attach、session teardown。真实后端端到端测试（Browserbase + 本地 Chrome）为手动测试；2026-04-23 调查中的探测脚本保存在仓库中的 `scripts/browser_supervisor_e2e.py` 下，以便任何人在新的后端版本上重新验证。
