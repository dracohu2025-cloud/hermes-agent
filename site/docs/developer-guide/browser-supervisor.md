<a id="browser-cdp-supervisor-design"></a>
# 浏览器 CDP 管理器 — 设计

**状态：** 已发布（PR 14540）
**最后更新：** 2026-04-23
**作者：** @teknium1

<a id="problem"></a>
## 问题

原生 JS 对话框（`alert`/`confirm`/`prompt`/`beforeunload`）和 iframe 是浏览器工具集中最大的两个缺口：

1. **对话框会阻塞 JS 线程。** 页面上的任何操作都会卡住，直到对话框被处理。在此之前，Agent 无法知道有对话框打开——后续工具调用要么挂起，要么抛出含义模糊的错误。
2. **iframe 不可见。** Agent 可以在 DOM 快照中看到 iframe 节点，但无法在其中点击、输入或执行 eval——尤其是跨源（OOPIF）的 iframe，它们运行在独立的 Chromium 进程中。

[PR #12550](https://github.com/NousResearch/hermes-agent/pull/12550) 曾提出一种无状态的 `browser_dialog` 封装。但那并不能解决检测问题——它只是当 Agent 已经（通过症状）知道对话框已打开时，更干净地调用 CDP。该 PR 已被关闭，并被本方案取代。

<a id="backend-capability-matrix-verified-live-2026-04-23"></a>
## 后端能力矩阵（2026-04-23 实时验证）

使用一次性探针脚本对 data-URL 页面进行测试，该页面在主框架和同源 srcdoc iframe 中触发 alert，另加一个跨源 `https://example.com` iframe：

| 后端 | 对话框检测 | 对话框响应 | 框架树 | 通过 `browser_cdp(frame_id=...)` 对 OOPIF 进行 `Runtime.evaluate` |
|---|---|---|---|---|
| 本地 Chrome（`--remote-debugging-port`）/ `/browser connect` | ✓ | ✓ 完整工作流 | ✓ | ✓ |
| Browserbase | ✓（通过桥接） | ✓ 完整工作流（通过桥接） | ✓ | ✓（在真实跨源 iframe 上验证了 `document.title = "Example Domain"`） |
| Camofox | ✗ 没有 CDP（仅 REST） | ✗ | 通过 DOM 快照部分支持 | ✗ |

**Browserbase 的响应机制。** Browserbase 的 CDP 代理内部使用 Playwright，会在约 10ms 内自动关闭原生对话框，因此 `Page.handleJavaScriptDialog` 无法及时介入。为了解决这个问题，管理器通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个桥接脚本，该脚本将 `window.alert`/`confirm`/`prompt` 重写为发送到魔幻主机（`hermes-dialog-bridge.invalid`）的同步 XHR。`Fetch.enable` 会拦截这些 XHR，让它们不会触及网络——对话框变成管理器捕获到的 `Fetch.requestPaused` 事件，而 `respond_to_dialog` 通过 `Fetch.fulfillRequest` 发送一个 JSON 体（由注入脚本解码）来完成响应。

最终效果：从页面的角度看，`prompt()` 仍然返回 Agent 提供的字符串。从 Agent 的角度看，无论哪种后端，使用的都是相同的 `browser_dialog(action=...)` API。已在真实的 Browserbase 会话中进行了端到端测试——4/4（alert/prompt/confirm-accept/confirm-dismiss）全部通过，包括值回传回页面 JS。

Camofox 在本 PR 中仍不受支持；计划后续在 `jo-inc/camofox-browser` 提交上游问题，请求添加对话框轮询端点。

<a id="architecture"></a>
## 架构

<a id="cdpsupervisor"></a>
### CDPSupervisor

每个 Hermes `task_id` 对应一个运行在后台守护线程中的 `asyncio.Task`。持有一个到后端 CDP 端点的持久 WebSocket 连接。维护以下内容：

- **对话框队列** — `List[PendingDialog]`，包含 `{id, type, message, default_prompt, session_id, opened_at}`
- **框架树** — `Dict[frame_id, FrameInfo]`，包含父级关系、URL、源、是否为跨源子会话
- **会话映射** — `Dict[session_id, SessionInfo]`，使交互工具能够将操作路由到正确的附加会话，以执行 OOPIF 操作
- **近期控制台错误** — 最近 50 条错误的环形缓冲区（用于 PR 2 的诊断）
订阅 attach 时：
- `Page.enable` — `javascriptDialogOpening`、`frameAttached`、`frameNavigated`、`frameDetached`
- `Runtime.enable` — `executionContextCreated`、`consoleAPICalled`、`exceptionThrown`
- `Target.setAutoAttach {autoAttach: true, flatten: true}` — 暴露子页面 OOPIF 目标；supervisor 在每个子页面上启用 `Page`+`Runtime`

通过快照锁实现线程安全的状态访问；工具处理程序（同步）直接读取冻结的快照，无需等待。

<a id="lifecycle"></a>
### 生命周期

- **启动：** `SupervisorRegistry.get_or_start(task_id, cdp_url)` — 由 `browser_navigate`、Browserbase 会话创建、`/browser connect` 调用。幂等操作。
- **停止：** 会话拆除或 `/browser disconnect`。取消 asyncio 任务，关闭 WebSocket，丢弃状态。
- **重绑定：** 如果 CDP URL 发生变化（用户重新连接到新的 Chrome），停止旧的 supervisor 并重新启动——绝不跨端点复用状态。

<a id="dialog-policy"></a>
### 对话框策略

可通过 `config.yaml` 在 `browser.dialog_policy` 下配置：

- **`must_respond`**（默认）— 捕获，在 `browser_snapshot` 中展示，等待显式调用 `browser_dialog(action=...)`。如果超过 300 秒安全超时仍未响应，则自动关闭并记录日志。防止有 bug 的 agent 永久卡住。
- `auto_dismiss` — 记录后立即关闭；agent 事后通过 `browser_snapshot` 中的 `browser_state` 看到。
- `auto_accept` — 记录并接受（适用于 `beforeunload`，用户希望干净地离开页面）。

策略按任务设定；v1 中不支持按对话框单独覆盖。

<a id="agent-surface-pr-1"></a>
## Agent 接口（PR 1）

<a id="one-new-tool"></a>
### 一个新工具

```
browser_dialog(action, prompt_text=None, dialog_id=None)
```

- `action="accept"` / `"dismiss"` → 响应指定的或唯一的待处理对话框（必填）
- `prompt_text=...` → 向 `prompt()` 对话框提供的文本
- `dialog_id=...` → 当多个对话框排队时用于区分（少见）

该工具仅用于响应。Agent 在调用前从 `browser_snapshot` 输出中读取待处理对话框。

<a id="browsersnapshot-extension"></a>
### `browser_snapshot` 扩展

当 supervisor 附着时，向现有快照输出添加三个可选字段：

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

- **`pending_dialogs`**：当前阻塞页面 JS 线程的对话框。Agent 必须调用 `browser_dialog(action=...)` 来响应。在 Browserbase 上为空，因为它们的 CDP 代理会在约 10ms 内自动关闭对话框。
- **`recent_dialogs`**：最多 20 个最近关闭的对话框的环形缓冲区，带有 `closed_by` 标签 —— `"agent"`（我们响应的）、`"auto_policy"`（本地 auto_dismiss/auto_accept 策略）、`"watchdog"`（must_respond 超时触发）或 `"remote"`（浏览器/后端主动关闭，例如 Browserbase）。即使在 Browserbase 上，Agent 也能通过此字段了解发生了什么。
- **`frame_tree`**：帧结构，包含跨源（OOPIF）子帧。  
  上限为 30 条记录 + OOPIF 深度 2，以限制广告繁重页面的快照大小。当达到限制时，`truncated: true` 会显示出来；需要完整树的 Agent 可以使用 `browser_cdp` 配合 `Page.getFrameTree`。

  所有这些都不需要新的工具模式——Agent 读取它已经请求的快照。

<a id="availability-gating"></a>
### 可用性门控

两种模式都依赖 `_browser_cdp_check`（只有在 CDP 端点可达时 Supervisor 才能运行）。在 Camofox / 无后端会话中，对话框工具被隐藏，快照省略新字段——不会使模式膨胀。

<a id="cross-origin-iframe-interaction"></a>
## 跨源 iframe 交互

作为对话框检测工作的扩展，`browser_cdp(frame_id=...)` 通过 Supervisor 已连接的 WebSocket，使用 OOPIF 的子 `sessionId` 路由 CDP 调用（特别是 `Runtime.evaluate`）。Agent 从 `browser_snapshot.frame_tree.children[]`（其中 `is_oopif=true`）中选取 `frame_id`，并传递给 `browser_cdp`。对于同源 iframe（没有专用 CDP 会话），Agent 使用顶层 `Runtime.evaluate` 中的 `contentWindow`/`contentDocument` 代替——当 `frame_id` 属于非 OOPIF 时，Supervisor 会显示一个指向该回退的错误。

在 Browserbase 上，这是与 iframe 交互的唯一可靠路径——无状态的 CDP 连接（每次 `browser_cdp` 调用打开）会遇到签名 URL 过期，而 Supervisor 的长连接保持有效会话。

<a id="camofox-follow-up"></a>
## Camofox（后续）

计划对 `jo-inc/camofox-browser` 提出 Issue，增加：
- 每个会话的 Playwright `page.on('dialog', handler)`
- `GET /tabs/:tabId/dialogs` 轮询端点
- `POST /tabs/:tabId/dialogs/:id` 接受/拒绝
- 帧树自省端点

<a id="files-touched-pr-1"></a>
## 涉及的文件（PR 1）

<a id="new"></a>
### 新增

- `tools/browser_supervisor.py` — `CDPSupervisor`、`SupervisorRegistry`、`PendingDialog`、`FrameInfo`
- `tools/browser_dialog_tool.py` — `browser_dialog` 工具处理器
- `tests/tools/test_browser_supervisor.py` — 模拟 CDP WebSocket 服务器 + 生命周期/状态测试
- `website/docs/developer-guide/browser-supervisor.md` — 本文档

<a id="modified"></a>
### 修改

- `toolsets.py` — 在 `browser`、`hermes-acp`、`hermes-api-server`、核心工具集中注册 `browser_dialog`（基于 CDP 可达性门控）
- `tools/browser_tool.py`
  - `browser_navigate` 启动钩子：如果 CDP URL 可解析，则 `SupervisorRegistry.get_or_start(task_id, cdp_url)`
  - `browser_snapshot`（大约第 1536 行）：将 Supervisor 状态合并到返回负载中
  - `/browser connect` 处理器：用新端点重启 Supervisor
  - `_cleanup_browser_session` 中的会话拆除钩子
- `hermes_cli/config.py` — 向 `DEFAULT_CONFIG` 添加 `browser.dialog_policy` 和 `browser.dialog_timeout_s`
- 文档：`website/docs/user-guide/features/browser.md`、`website/docs/reference/tools-reference.md`、`website/docs/reference/toolsets-reference.md`

<a id="non-goals"></a>
## 非目标

- Camofox 的检测/交互（上游缺口；单独跟踪）
- 将对话框/帧事件实时流式传输给用户（需要网关钩子）
- 跨会话持久化对话框历史（仅内存）
- 每个 iframe 的对话框策略（Agent 可以通过 `dialog_id` 表达）
- 替换 `browser_cdp`——它仍然是长尾场景（cookies、视口、网络限速）的逃生舱
<a id="testing"></a>
## 测试

单元测试使用一个 asyncio 模拟 CDP 服务器，它能够支持协议中足够的部分，
以覆盖所有状态转换：attach（连接）、enable（启用）、navigate（导航）、dialog fire（触发对话框）、
dialog dismiss（关闭对话框）、frame attach/detach（框架附加/分离）、child target attach（子目标附加）、session teardown（会话拆除）。
真实后端 E2E（Browserbase + 本地 Chromium 系列浏览器）为手动测试——通过
`/browser connect` 连接到一个正在运行的 Chromium 系列浏览器，然后执行上述对话框/框架
测试用例。
