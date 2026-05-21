---
title: "Pinggy Tunnel — 通过 SSH 使用 Pinggy 零安装本地隧道"
sidebar_label: "Pinggy Tunnel"
description: "通过 SSH 使用 Pinggy 零安装本地隧道"
---

{/* 本页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="pinggy-tunnel"></a>
# Pinggy Tunnel

通过 SSH 使用 Pinggy 零安装本地隧道。

<a id="skill-metadata"></a>
## Skill 元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/devops/pinggy-tunnel` 安装 |
| 路径 | `optional-skills/devops/pinggy-tunnel` |
| 版本 | `0.1.0` |
| 作者 | Teknium (teknium1), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Pinggy`, `Tunnel`, `Networking`, `SSH`, `Webhook`, `Localhost` |
| 相关技能 | `cloudflared-quick-tunnel`, [`webhook-subscriptions`](/user-guide/skills/bundled/devops/devops-webhook-subscriptions) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是当该技能被触发时，Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="pinggy-tunnel-skill"></a>
# Pinggy Tunnel 技能

使用 Pinggy SSH 反向隧道将本地服务（开发服务器、webhook 接收器、MCP 端点、演示应用）暴露到公网。无需安装守护进程 —— 用户自带的 SSH 客户端连接到 `a.pinggy.io:443`，Pinggy 返回一个公共的 HTTP/HTTPS URL。

免费版：60 分钟隧道、随机子域名、无需注册。专业版（$3/月）是可选功能，需要 token。

<a id="when-to-use"></a>
## 何时使用

- 用户要求“把这个本地服务暴露出去”、“分享我的开发服务器”、“让这个 URL 对外可访问”、“隧道端口 N”、“为 webhook 获取一个公网 URL”
- 在本地任务期间需要接收 webhook 回调（Stripe、GitHub、Discord、AgentMail）
- 临时分享一个 HTTP 演示（MCP 服务器、Ollama/vLLM 端点、仪表盘）给远程方
- 主机上有 SSH 但没有 `cloudflared` / `ngrok` 二进制程序，安装它们有点大材小用

如果主机已经配置了 `cloudflared`，建议优先使用 `cloudflared-quick-tunnel` 技能 —— Cloudflare 快速隧道不会在 60 分钟后过期。

<a id="prerequisites"></a>
## 前提条件

- `ssh` 已存在于 PATH 中（`ssh -V`）。Linux、macOS 和 Windows 10+ 默认自带。无需其他安装。
- 在隧道启动前，有一个本地服务在 `127.0.0.1:&lt;port&gt;` 上监听。Pinggy 会返回 URL，但在本地服务启动之前，访问会返回 502。

可选：

- `PINGGY_TOKEN` 环境变量，用于付费专业版功能（持久子域名、自定义域名、多隧道、无 60 分钟限制）。免费版不需要凭据。

<a id="quick-reference"></a>
## 快速参考

```bash
# 端口 8000 的纯 HTTP/HTTPS 隧道（免费版）
ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R0:localhost:8000 free@a.pinggy.io

# TCP 隧道（数据库、原始 SSH 等）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:5432 tcp@a.pinggy.io

# TLS 隧道（Pinggy 无法解密 —— 你自己在服务端提供证书）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:443 tls@a.pinggy.io

# 基础认证门（b:user:pass）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "b:admin:secret+free@a.pinggy.io"

# Bearer token 门（k:token）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "k:mysecrettoken+free@a.pinggy.io"

# IP 白名单（w:CIDR）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "w:203.0.113.0/24+free@a.pinggy.io"

# 启用 CORS + 强制 HTTPS 重定向
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "co+x:https+free@a.pinggy.io"

# 专业版（持久 URL，无 60 分钟限制）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 "$PINGGY_TOKEN+a.pinggy.io"
```
<a id="procedure-start-a-tunnel-and-get-the-url"></a>
## 步骤 — 启动隧道并获取 URL

模型应使用 `terminal` 工具。隧道在整个共享期间必须保持存活，因此请将其作为后台进程运行，并从 stdout 中解析出公网 URL。

<a id="1-confirm-a-local-origin-is-up"></a>
### 1. 确认本地服务已启动

```bash
curl -sI http://127.0.0.1:8000/ | head -1
# 期望 HTTP/1.x 200（或任何非连接被拒绝的响应）
```

如果还没有任何服务在监听，请先启动它（例如 `python3 -m http.server 8000 --bind 127.0.0.1`）。Pinggy 会愉快地返回一个指向空地址的 URL——在本地服务启动之前，用户看到的是 502。

<a id="2-launch-the-tunnel-as-a-background-process"></a>
### 2. 将隧道作为后台进程启动

使用 `terminal(background=True)` 并将输出捕获到日志文件（Pinggy 先在 stdout 上打印 URL，然后保持连接打开）：

```bash
LOG=/tmp/pinggy-8000.log
nohup ssh -p 443 \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -R0:localhost:8000 free@a.pinggy.io \
    > "$LOG" 2>&1 &
echo $! > /tmp/pinggy-8000.pid
```

`StrictHostKeyChecking=no` + `UserKnownHostsFile=/dev/null` 跳过了首次运行的主机密钥提示。`ServerAliveInterval=30` 可防止 SSH 会话因空闲 NAT 而断开。

<a id="3-parse-the-url-out-of-the-log"></a>
### 3. 从日志中解析出 URL

```bash
sleep 4
grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/pinggy-8000.log | head -1
```

预期输出如下：

```
You are not authenticated.
Your tunnel will expire in 60 minutes.
http://yqycl-98-162-69-48.a.free.pinggy.link
https://yqycl-98-162-69-48.a.free.pinggy.link
```

将 `https://...pinggy.link` URL 交给用户。

<a id="4-verify"></a>
### 4. 验证

```bash
curl -sI https://<the-url>/ | head -3
# 期望 200/302/或本地服务实际返回的任何状态码
```

如果收到 `502 Bad Gateway`，说明 SSH 会话已建立但本地服务未在监听——请先修复步骤 1。

<a id="5-teardown"></a>
### 5. 清理

```bash
kill "$(cat /tmp/pinggy-8000.pid)"
# 或者，如果 pid 文件丢失了：
pkill -f 'ssh -p 443 .* free@a\.pinggy\.io'
```

如果你有来自 `terminal(background=True)` 的 `session_id`，请优先使用 `process(action='kill', session_id=...)`。

<a id="access-control-via-username-keywords"></a>
## 通过用户名关键词进行访问控制

Pinggy 将控制标志堆叠在 SSH 用户名中，以 `+` 分隔。当参数中包含 `+` 时，始终将整个 `user@host` 参数用引号括起来：

| 关键词 | 效果 |
|--------|------|
| `b:user:pass` | HTTP Basic 身份验证门 |
| `k:token` | Bearer 令牌头门（`Authorization: Bearer &lt;token&gt;`） |
| `w:CIDR` | IP 白名单（单个 IP 或 CIDR，可重复） |
| `co` | 添加 `Access-Control-Allow-Origin: *`（跨域） |
| `x:https` | 强制 HTTPS — 自动将 HTTP 重定向到 HTTPS |
| `a:Name:Value` | 添加请求头 |
| `u:Name:Value` | 更新请求头 |
| `r:Name` | 移除请求头 |
| `qr` | 将 URL 的二维码打印到 stdout（方便移动端分享） |

可自由组合：`"b:admin:secret+co+x:https+free@a.pinggy.io"`。

<a id="web-debugger-optional"></a>
## Web 调试器（可选）

Pinggy 可以将入站流量镜像到 `localhost:4300` 以便检查。在 SSH 命令中添加一个本地转发：
```bash
ssh -p 443 -L4300:localhost:4300 -R0:localhost:8000 free@a.pinggy.io
```

然后在浏览器中打开 `http://localhost:4300` 即可实时查看请求/响应对。

<a id="pitfalls"></a>
## 注意事项

- **免费版硬性限制 60 分钟。** SSH 会话在 60 分钟时自动终止，URL 失效。如需更长的共享时间，请使用 `PINGGY_TOKEN`（Pro 版）或用 shell 循环自动重启（注意免费版每次重启 URL 会变化）。
- **免费版 URL 随机生成，重启后改变。** 不要将其加入书签或粘贴到配置文件中。每次重新从日志中解析。
- **免费版同时只能有一个隧道，按源 IP 限制。** 在相同机器上启动第二个隧道通常会杀死第一个。Pro 版无此限制。
- **用户名中的 `+` 必须加引号。** 裸写 `ssh ... b:admin:secret+free@a.pinggy.io` 在 bash 中可以工作，但在那些将 `+` 特殊处理或通过编程方式拼接的 shell 中会出错。请始终用双引号包裹。
- **没有访问控制标志时，不要通过隧道传输敏感内容。** 裸 HTTP 隧道能被任何知道 URL 的人访问。对非公开服务请使用 `b:`、`k:` 或 `w:`。
- **`process(action='log')` 可能无法捕获 SSH 横幅输出。** Pinggy 先打印 URL，然后 SSH 会话进入交互模式。始终将输出重定向到日志文件，并直接对文件执行 `grep`——与 `cloudflared-quick-tunnel` 的模式相同。
- **首次运行时会提示确认主机密钥。** 默认 OpenSSH 配置会要求用户接受 Pinggy 的主机密钥。无人值守运行时务必传递 `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null`。
- **TCP 和 TLS 隧道返回的是 `&lt;subdomain&gt;.a.pinggy.online:&lt;port&gt;` 形式，而不是 https URL。** 需要用不同的正则表达式（`tcp://` 加端口号）解析。不要假设所有 Pinggy 隧道都是 HTTP。
- **Pro 版将 token 作为用户名，而不是标志。** 使用 `"$PINGGY_TOKEN+a.pinggy.io"`（不要 `free@`）。如果有 token，还可以加上 `:persistent` 获得固定子域名——参见 `pinggy.io/docs/`。

<a id="recipes"></a>
## 实践方案

将本地源服务与 Pinggy 隧道组合的典型模式。每个方案独立完整——启动本地源、启动隧道、解析 URL、交回给用户。

<a id="recipe-1-receive-a-webhook-callback"></a>
### 方案 1 — 接收 Webhook 回调

当外部服务（Stripe、GitHub、Discord、AgentMail 等）需要在本地任务期间向一个可公开访问的 URL 发起 POST 请求时使用。

```bash
# 1. 简易捕获服务器：每个请求追加到 /tmp/webhook-hits.log
cat >/tmp/webhook-server.py <<'PY'
import http.server, json, datetime, pathlib
LOG = pathlib.Path("/tmp/webhook-hits.log")
class H(http.server.BaseHTTPRequestHandler):
    def _capture(self):
        n = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        rec = {"t": datetime.datetime.utcnow().isoformat(), "path": self.path,
               "method": self.command, "headers": dict(self.headers), "body": body}
        with LOG.open("a") as f: f.write(json.dumps(rec) + "\n")
        self.send_response(200); self.send_header("content-type","application/json")
        self.end_headers(); self.wfile.write(b'{"ok":true}\n')
    def do_GET(self): self._capture()
    def do_POST(self): self._capture()
    def log_message(self,*a,**k): pass
http.server.HTTPServer(("127.0.0.1", 18080), H).serve_forever()
PY
nohup python3 /tmp/webhook-server.py >/tmp/webhook-server.log 2>&1 &
echo $! >/tmp/webhook-server.pid

# 2. 隧道——用 bearer token 作为门禁，防止随意人员污染捕获日志
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:18080 "k:$(openssl rand -hex 12)+free@a.pinggy.io" \
    >/tmp/webhook-pinggy.log 2>&1 &
echo $! >/tmp/webhook-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/webhook-pinggy.log | head -1)
echo "Webhook URL: $URL"

# 3. Agent 工作时，观察请求的到达情况
tail -f /tmp/webhook-hits.log
```
将 `$URL` 交给需要调用你的服务。关闭：`kill $(cat /tmp/webhook-server.pid) $(cat /tmp/webhook-pinggy.pid)`。

<a id="recipe-2-expose-an-mcp-server-over-http-sse"></a>
### 配方 2 — 通过 HTTP/SSE 暴露 MCP 服务器

当远程 MCP 客户端（另一台机器上的 Claude Desktop、队友的编辑器等）需要访问本地机器上运行的 MCP 服务器时使用。仅适用于支持 HTTP 传输的 MCP 服务器——stdio 模式下的服务器无法通过隧道实现。

```bash
# 1. 以 HTTP 模式启动 MCP 服务器（示例：在端口 8765 上运行的 FastMCP 服务器）
nohup python3 my_mcp_server.py --transport http --port 8765 \
    >/tmp/mcp-server.log 2>&1 &
echo $! >/tmp/mcp-server.pid

# 2. 使用 Bearer 令牌建立隧道 — MCP 流量不应暴露在公网
TOKEN=$(openssl rand -hex 16)
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:8765 "k:$TOKEN+free@a.pinggy.io" \
    >/tmp/mcp-pinggy.log 2>&1 &
echo $! >/tmp/mcp-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/mcp-pinggy.log | head -1)
echo "MCP URL: $URL"
echo "Bearer token: $TOKEN"
```

远程客户端通过 `Authorization: Bearer $TOKEN` 连接到 `$URL`。Hermes 原生的 MCP 客户端配置：`{"transport": "http", "url": "&lt;URL&gt;", "headers": {"Authorization": "Bearer &lt;TOKEN&gt;"}}`。

<a id="recipe-3-expose-a-local-llm-endpoint-ollama-vllm-llama-cpp"></a>
### 配方 3 — 暴露本地 LLM 端点（Ollama / vLLM / llama.cpp）

将本地模型共享给远程调用者（另一个 Agent、手机、队友）。Ollama 监听 `:11434`，vLLM 和 llama.cpp 通常监听 `:8000`。

```bash
# 前置条件：模型服务器已在 127.0.0.1:11434 上运行（Ollama 默认）
TOKEN=$(openssl rand -hex 16)
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:11434 "k:$TOKEN+co+free@a.pinggy.io" \
    >/tmp/llm-pinggy.log 2>&1 &
echo $! >/tmp/llm-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/llm-pinggy.log | head -1)
echo "Endpoint: $URL"
echo "Token:    $TOKEN"

# 验证
curl -s "$URL/api/tags" -H "Authorization: Bearer $TOKEN" | head
```

`co` 启用 CORS，以便浏览器调用者可以访问端点。如果只有后端调用者，请去掉 `co`。对于兼容 OpenAI 的 vLLM/llama.cpp 端点，调用者使用基础 URL `$URL/v1` 并附带 `Authorization: Bearer $TOKEN`——但请注意，Pinggy 不会对请求体进行任何剔除或替换，因此模型服务器本身会看到 Pinggy 的令牌；本地服务器应配置为忽略认证（它已在 `127.0.0.1` 上），让 Pinggy 负责访问控制。

<a id="recipe-4-share-a-dev-server-with-a-one-shot-password"></a>
### 配方 4 — 使用一次性密码共享开发服务器

这是“让队友快速戳一下我运行的应用”的最快模式。随机密码，只打印一次，按 Ctrl-C 即关闭。

```bash
PASS=$(openssl rand -base64 12 | tr -d '+/=' | head -c 12)
echo "Dev server password: $PASS"
ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:3000 "b:dev:$PASS+co+x:https+free@a.pinggy.io"
# URL 会打印到终端。分享 URL + 密码。按 Ctrl-C 关闭。
```
`b:dev:$PASS` 用 HTTP Basic 认证保护该 URL。`x:https` 强制启用 TLS。`co` 为 SPA 前端添加 CORS。

<a id="verification"></a>
## 验证

```bash
# 端到端：启动一个简单的源服务器，建立隧道，访问它，最后清理
python3 -m http.server 18000 --bind 127.0.0.1 >/tmp/origin.log 2>&1 &
ORIGIN_PID=$!

nohup ssh -p 443 \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -R0:localhost:18000 free@a.pinggy.io >/tmp/pinggy-verify.log 2>&1 &
SSH_PID=$!

sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/pinggy-verify.log | head -1)
echo "URL: $URL"
curl -sI "$URL/" | head -1

kill "$SSH_PID" "$ORIGIN_PID"
```

预期结果：得到一个 `pinggy.link` 的 URL，并且 curl 头部返回 `HTTP/2 200`。
