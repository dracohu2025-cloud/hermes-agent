---
sidebar_position: 17
title: "通过 SSH / 远程主机进行 OAuth 认证"
description: "当 Hermes 运行在远程机器、容器或跳板机后面时，如何完成基于浏览器的 OAuth 认证（xAI、Spotify）"
---

<a id="oauth-over-ssh-remote-hosts"></a>
# 通过 SSH / 远程主机进行 OAuth 认证

部分 Hermes 提供商——目前是 **xAI Grok OAuth** 和 **Spotify**——使用 *环回重定向* OAuth 流程。认证服务器（xAI、Spotify）将你的浏览器重定向到 `http://127.0.0.1:&lt;port&gt;/callback`，这样由 `hermes auth ...` 命令启动的一个小型 HTTP 监听器就能获取授权码。

当 Hermes 和你的浏览器在同一台机器上时，这完全没问题。但一旦它们不在同一台机器上，就会出问题：你笔记本电脑的浏览器试图访问**你笔记本电脑**上的 `127.0.0.1`，但监听器绑定在**远程服务器**上的 `127.0.0.1`。

解决办法是一行 SSH 本地转发——**或者**，当你没有真正的 SSH 客户端（GCP Cloud Shell、GitHub Codespaces、EC2 Instance Connect、Gitpod、基于浏览器的 Web IDE）时，可以使用 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923) 中新增的 `--manual-paste` 标志。

<a id="tl-dr"></a>
## 快速上手

```bash
# 在你的本地机器（笔记本电脑）上，另开一个终端：
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 在远程机器上已有的 SSH 会话中：
hermes auth add xai-oauth --no-browser
# → Hermes 会打印一个授权 URL。在笔记本电脑的浏览器中打开它。
# → 你的浏览器会重定向到 127.0.0.1:56121/callback，隧道将请求转发给远程监听器，登录完成。
```

端口 `56121` 是 xAI OAuth 使用的。对于 Spotify，将其替换为 `43827`。Hermes 会在 `Waiting for callback on ...` 这一行打印它绑定的确切端口——从那里复制即可。

<a id="browser-only-remote-cloud-shell-codespaces-ec2-instance-connect"></a>
## 纯浏览器远程环境（Cloud Shell / Codespaces / EC2 Instance Connect）

如果你没有常规的 SSH 客户端——例如，你在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台中运行 Hermes——则无法使用上述 SSH 隧道。请改用 `--manual-paste`：

```bash
hermes auth add xai-oauth --manual-paste
# → Hermes 会打印一个授权 URL。在笔记本电脑的浏览器中打开它。
# → 在浏览器中批准。重定向到 127.0.0.1:56121/callback 会加载失败——这是预期行为。
# → 从失败页面的地址栏复制完整的 URL。
# → 在终端中粘贴到 "Callback URL:" 提示符处。
```

同样的标志也适用于 `hermes model --manual-paste`（用于集成模型选择器）。如果你不想粘贴整个 URL，只粘贴 `?code=...&state=...` 查询片段也是可以的。

Hermes 对两种路径使用**相同的 PKCE verifier、state 和 nonce**，因此上游 OAuth 流程在字节级别上是完全一致的——`--manual-paste` 纯粹是回调跳转的传输方式改变，并非安全降级。

<a id="which-providers-need-this"></a>
## 哪些提供商需要此操作

| 提供商 | 环回端口 | 需要隧道？ |
|----------|---------------|----------------|
| `xai-oauth`（Grok SuperGrok） | `56121` | 是，当 Hermes 在远程时 |
| Spotify | `43827` | 是，当 Hermes 在远程时 |
| `anthropic`（Claude Pro/Max） | 无 | 否——粘贴代码流程 |
| `openai-codex`（ChatGPT Plus/Pro） | 无 | 否——设备代码流程 |
| `minimax`、`nous-portal` | 无 | 否——设备代码流程 |
如果你的提供商不在表格中，则不需要隧道。

<a id="why-the-listener-can-t-just-bind-0-0-0-0"></a>
## 为什么监听器不能直接绑定 0.0.0.0

xAI 和 Spotify 都会根据白名单验证 `redirect_uri` 参数。两者都要求使用回环形式（`http://127.0.0.1:<确切端口>/callback`）。将监听器绑定到 `0.0.0.0` 或不同的端口会导致认证服务器因 `redirect_uri` 不匹配而拒绝请求。SSH 隧道可保持回环 URI 端到端不变。

<a id="step-by-step-single-ssh-hop"></a>
## 逐步操作：单次 SSH 跳转

<a id="1-start-the-tunnel-from-your-local-machine"></a>
### 1. 从本地机器启动隧道

```bash
# xAI Grok OAuth (端口 56121)
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# 或用于 Spotify (端口 43827)
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

`-N` 表示“不打开远程 shell，仅保持隧道打开”。在登录过程中请保持此终端运行。

<a id="2-in-a-separate-ssh-session-run-the-auth-command"></a>
### 2. 在另一个 SSH 会话中运行认证命令

```bash
ssh user@remote-host
hermes auth add xai-oauth --no-browser
# 或用于 Spotify：
# hermes auth add spotify --no-browser
```

Hermes 会检测到 SSH 会话，跳过浏览器自动打开，并打印出一个授权 URL 以及一行 `Waiting for callback on http://127.0.0.1:<端口>/callback`。

<a id="3-open-the-url-in-your-local-browser"></a>
### 3. 在本地浏览器中打开该 URL

从远程终端复制授权 URL，然后粘贴到你笔记本电脑的浏览器中。批准同意屏幕。认证服务器会重定向到 `http://127.0.0.1:<端口>/callback`。你的浏览器会命中隧道，请求被转发到远程监听器，Hermes 会打印 `Login successful!`。

看到成功行后，你可以关闭隧道（在第一个终端中按 Ctrl+C）。

<a id="step-by-step-through-a-jump-box"></a>
## 逐步操作：通过跳板机

如果你通过堡垒机/跳板机访问 Hermes，请使用 SSH 的内置 `-J`（ProxyJump）参数：

```bash
ssh -N -L 56121:127.0.0.1:56121 -J jump-user@jump-host user@final-host
```

这会通过跳板机串联一个 SSH 连接，而不会将回环端口暴露在跳板机本身。你笔记本电脑上的本地 `127.0.0.1:56121` 会直接隧道传输到最终远程主机上的 `127.0.0.1:56121`。

对于不支持 `-J` 的旧版 OpenSSH，使用长格式：

```bash
ssh -N \
    -o "ProxyCommand=ssh -W %h:%p jump-user@jump-host" \
    -L 56121:127.0.0.1:56121 \
    user@final-host
```

<a id="mosh-tmux-ssh-controlmaster"></a>
## Mosh、tmux、SSH ControlMaster

隧道是底层 SSH 连接的一个属性。如果你在通过 mosh 会话运行的 `tmux` 中启动 Hermes，mosh 的漫游不会携带 `-L` 转发。请单独打开一个**仅**用于 `-L` 隧道的普通 SSH 会话——这条连接在认证流程期间必须保持活动。你的交互式 mosh/tmux 会话可以继续正常运行 Hermes。

如果你使用 `ssh -o ControlMaster=auto`，多路复用连接上的端口转发会共享主连接的生命周期。如果隧道没有建立起来，请重启主连接：

```bash
ssh -O exit user@remote-host
ssh -N -L 56121:127.0.0.1:56121 user@remote-host
```

<a id="troubleshooting"></a>
## 故障排除

<a id="bind-127-0-0-1-56121-address-already-in-use"></a>
### `bind [127.0.0.1]:56121: Address already in use`

你笔记本电脑上的某个进程已在占用该端口。可能是前一个隧道未能正常关闭，或者本地 Hermes 也在监听该端口。找到并终止占用进程：
```bash
# macOS / Linux
lsof -iTCP:56121 -sTCP:LISTEN
kill <PID>
```

然后重试 `ssh -L` 命令。

<a id="could-not-establish-connection-we-couldn-t-reach-your-app-xai"></a>
### "Could not establish connection. We couldn't reach your app."（xAI）

当 xAI 的授权页面重定向到 `127.0.0.1:&lt;port&gt;/callback` 但未能到达监听器时，就会显示此信息。可能的原因包括：隧道未运行、端口错误、或者你使用了 Hermes 在之前运行中打印的端口（如果首选端口被占用，端口可能会自动递增——请始终读取最新的 `Waiting for callback on ...` 行）。

<a id="xai-authorization-timed-out-waiting-for-the-local-callback"></a>
### `xAI authorization timed out waiting for the local callback`

根本原因与上述相同——重定向从未返回。检查隧道是否仍存活（`ssh -N` 不显示输出，因此请查看你启动隧道的终端），必要时重启，然后重新运行 `hermes auth add xai-oauth --no-browser`。

<a id="tokens-land-in-the-wrong-hermes"></a>
### Token 落到了错误的 `~/.hermes` 目录下

Token 会被写入运行 `hermes auth add ...` 的 Linux 用户目录下。如果你的网关 / systemd 服务以其他用户身份运行（例如 `root` 或专用的 `hermes` 用户），请以**该**用户身份进行认证，以便 Token 落入其 `~/.hermes/auth.json` 文件中。使用 `sudo -u hermes -i` 或等效命令。

<a id="see-also"></a>
## 参考

- [xAI Grok OAuth](./xai-grok-oauth.md)
- [Spotify（`通过 SSH 运行`）](../user-guide/features/spotify.md#running-over-ssh--in-a-headless-environment)
- [SSH `-J` / ProxyJump（man 手册）](https://man.openbsd.org/ssh#J)
