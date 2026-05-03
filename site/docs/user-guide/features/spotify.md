# Spotify {#spotify}

Hermes 可以直接控制 Spotify —— 播放、队列、搜索、播放列表、已保存的曲目/专辑以及收听历史 —— 使用 Spotify 官方 Web API 和 PKCE OAuth。令牌存储在 `~/.hermes/auth.json` 中，遇到 401 时会自动刷新；每台机器只需登录一次。

与 Hermes 内置的 OAuth 集成（Google、GitHub Copilot、Codex）不同，Spotify 要求每个用户注册自己的轻量级开发者应用。Spotify 不允许第三方发布任何人都能使用的公共 OAuth 应用。整个过程大约需要两分钟，`hermes auth spotify` 会引导你完成。

## 前提条件 {#prerequisites}

- 一个 Spotify 账户。**免费版**可用于搜索、播放列表、资料库和活动工具。**Premium** 是播放控制（播放、暂停、跳过、快进/快退、音量、添加到队列、转移播放）所必需的。
- 已安装并运行 Hermes Agent。
- 对于播放工具：一个**活跃的 Spotify Connect 设备** —— Spotify 应用必须在至少一个设备（手机、桌面、网页播放器、音箱）上打开，这样 Web API 才有东西可以控制。如果没有活跃设备，你会收到 `403 Forbidden` 并提示“no active device”；在任何设备上打开 Spotify 然后重试。

## 设置 {#setup}

### 一键式：`hermes tools` {#one-shot-hermes-tools}

最快的方式。运行：

```bash
hermes tools
```

滚动到 `🎵 Spotify`，按空格键启用它，然后按 `s` 保存。Hermes 会直接带你进入 OAuth 流程 —— 如果你还没有 Spotify 应用，它会引导你当场创建一个。完成后，工具集在一次操作中既启用又完成了认证。

如果你更喜欢分开执行这些步骤（或者以后重新认证），请使用下面的两步流程。

### 两步流程 {#two-step-flow}

#### 1. 启用工具集 {#1-enable-the-toolset}

```bash
hermes tools
```

启用 `🎵 Spotify`，保存，当内联向导打开时，关闭它（Ctrl+C）。工具集保持开启状态；只有认证步骤被推迟。

#### 2. 运行登录向导 {#2-run-the-login-wizard}

```bash
hermes auth spotify
```

这 7 个 Spotify 工具只有在步骤 1 之后才会出现在 Agent 的工具集中 —— 它们默认是关闭的，这样不需要这些工具的用户就不会在每次 API 调用时发送额外的工具模式。

如果没有设置 `HERMES_SPOTIFY_CLIENT_ID`，Hermes 会引导你内联完成应用注册：

1. 在浏览器中打开 `https://developer.spotify.com/dashboard`
2. 打印出需要粘贴到 Spotify“创建应用”表单中的确切值
3. 提示你输入获取到的 Client ID
4. 将其保存到 `~/.hermes/.env`，这样以后运行就跳过这一步
5. 直接进入 OAuth 授权流程

授权后，令牌会写入 `~/.hermes/auth.json` 中的 `providers.spotify` 下。活跃的推理提供者**不会**改变 —— Spotify 认证独立于你的 LLM 提供者。

### 创建 Spotify 应用（向导要求的内容） {#creating-the-spotify-app-what-the-wizard-asks-for}

当仪表板打开时，点击 **Create app** 并填写：

| 字段 | 值 |
|-------|-------|
| App name | 任意（例如 `hermes-agent`） |
| App description | 任意（例如 `personal Hermes integration`） |
| Website | 留空 |
| Redirect URI | `http://127.0.0.1:43827/spotify/callback` |
| Which API/SDKs? | 勾选 **Web API** |
同意条款并点击**保存**。在下一页点击**设置** → 复制**Client ID**并粘贴到 Hermes 提示中。这是 Hermes 唯一需要的值——PKCE 不使用客户端密钥。

### 通过 SSH / 在无头环境中运行 {#running-over-ssh-in-a-headless-environment}

如果设置了 `SSH_CLIENT` 或 `SSH_TTY`，Hermes 会在向导和 OAuth 步骤中跳过自动打开浏览器。复制 Hermes 打印的仪表盘 URL 和授权 URL，在本地机器的浏览器中打开它们，然后正常进行——本地 HTTP 监听器仍在远程主机的 43827 端口上运行。如果需要通过 SSH 隧道访问，请转发该端口：`ssh -L 43827:127.0.0.1:43827 remote`。

## 验证 {#verify}

```bash
hermes auth status spotify
```

显示令牌是否存在以及访问令牌何时过期。刷新是自动的：当任何 Spotify API 调用返回 401 时，客户端会交换刷新令牌并重试一次。刷新令牌在 Hermes 重启后仍然存在，因此只有在 Spotify 账户设置中撤销应用或运行 `hermes auth logout spotify` 时才需要重新认证。

## 使用 {#using-it}

登录后，Agent 可以访问 7 个 Spotify 工具。你可以自然地与 Agent 对话——它会选择正确的工具和操作。为了获得最佳行为，Agent 会加载一个配套技能，该技能教授规范的使用模式（单次搜索然后播放、何时不预检 `get_state` 等）。

```
> 播放一些迈尔斯·戴维斯
> 我在听什么
> 将这首曲目添加到我的“深夜爵士”播放列表
> 跳到下一首歌
> 创建一个名为“Focus 2026”的新播放列表，并添加我最后播放的三首歌
> 我保存的专辑中哪些是电台司令的
> 搜索《黑鸟》的原声翻唱
> 将播放转移到我的厨房音箱
```

### 工具参考 {#tool-reference}

所有改变播放状态的操作都接受可选的 `device_id` 来定位特定设备。如果省略，Spotify 会使用当前活动设备。

#### `spotify_playback` {#spotifyplayback}
控制并检查播放状态，以及获取最近播放历史。

| 操作 | 用途 | 需要 Premium？ |
|--------|---------|----------|
| `get_state` | 完整播放状态（曲目、设备、进度、随机/重复） | 否 |
| `get_currently_playing` | 仅当前曲目（返回 204 时为空——见下文） | 否 |
| `play` | 开始/恢复播放。可选：`context_uri`、`uris`、`offset`、`position_ms` | 是 |
| `pause` | 暂停播放 | 是 |
| `next` / `previous` | 跳过曲目 | 是 |
| `seek` | 跳转到 `position_ms` | 是 |
| `set_repeat` | `state` = `track` / `context` / `off` | 是 |
| `set_shuffle` | `state` = `true` / `false` | 是 |
| `set_volume` | `volume_percent` = 0-100 | 是 |
| `recently_played` | 最后播放的曲目。可选 `limit`、`before`、`after`（Unix 毫秒） | 否 |

#### `spotify_devices` {#spotifydevices}
| 操作 | 用途 |
|--------|---------|
| `list` | 你的账户可见的所有 Spotify Connect 设备 |
| `transfer` | 将播放转移到 `device_id`。可选 `play: true` 在转移时开始播放 |

#### `spotify_queue` {#spotifyqueue}
| 操作 | 用途 | 需要 Premium？ |
|--------|---------|----------|
| `get` | 当前队列中的曲目 | 否 |
| `add` | 将 `uri` 追加到队列 | 是 |
#### `spotify_search` {#spotifysearch}
搜索目录。`query` 是必填项。可选参数：`types`（`track` / `album` / `artist` / `playlist` / `show` / `episode` 的数组）、`limit`、`offset`、`market`。

#### `spotify_playlists` {#spotifyplaylists}
| 操作 | 用途 | 必填参数 |
|--------|---------|---------------|
| `list` | 用户的播放列表 | — |
| `get` | 获取单个播放列表及其曲目 | `playlist_id` |
| `create` | 新建播放列表 | `name`（可选 `description`、`public`、`collaborative`） |
| `add_items` | 添加曲目 | `playlist_id`、`uris`（可选 `position`） |
| `remove_items` | 移除曲目 | `playlist_id`、`uris`（可选 `snapshot_id`） |
| `update_details` | 重命名/编辑 | `playlist_id` + `name`、`description`、`public`、`collaborative` 中的任意一个 |

#### `spotify_albums` {#spotifyalbums}
| 操作 | 用途 | 必填参数 |
|--------|---------|---------------|
| `get` | 专辑元数据 | `album_id` |
| `tracks` | 专辑曲目列表 | `album_id` |

#### `spotify_library` {#spotifylibrary}
统一访问已保存的曲目和已保存的专辑。通过 `kind` 参数选择集合。

| 操作 | 用途 |
|--------|---------|
| `list` | 分页列出库内容 |
| `save` | 将 `ids` / `uris` 添加到库 |
| `remove` | 从库中移除 `ids` / `uris` |

必填：`kind` = `tracks` 或 `albums`，外加 `action`。

### 功能矩阵：免费版 vs Premium {#feature-matrix-free-vs-premium}

只读工具在免费账户上可用。任何修改播放或队列的操作都需要 Premium。

| 免费版可用 | 需要 Premium |
|---------------|------------------|
| `spotify_search`（全部） | `spotify_playback` — play、pause、next、previous、seek、set_repeat、set_shuffle、set_volume |
| `spotify_playback` — get_state、get_currently_playing、recently_played | `spotify_queue` — add |
| `spotify_devices` — list | `spotify_devices` — transfer |
| `spotify_queue` — get | |
| `spotify_playlists`（全部） | |
| `spotify_albums`（全部） | |
| `spotify_library`（全部） | |

## 定时任务：Spotify + cron {#scheduling-spotify-cron}

由于 Spotify 工具是常规的 Hermes 工具，在 Hermes 会话中运行的 cron 作业可以按任何时间表触发播放。无需编写新代码。

### 早晨唤醒播放列表 {#morning-wake-up-playlist}

```bash
hermes cron add \
  --name "morning-commute" \
  "0 7 * * 1-5" \
  "将播放转移到我的厨房音箱，并开始播放我的'Morning Commute'播放列表。音量设为40。开启随机播放。"
```

每个工作日上午7点会发生什么：
1. Cron 启动一个无头 Hermes 会话。
2. Agent 读取提示，调用 `spotify_devices list` 按名称找到“厨房音箱”，然后 `spotify_devices transfer` → `spotify_playback set_volume` → `spotify_playback set_shuffle` → `spotify_search` + `spotify_playback play`。
3. 音乐在目标音箱上开始播放。总成本：一个会话，几次工具调用，无需人工输入。

### 夜间放松 {#wind-down-at-night}

```bash
hermes cron add \
  --name "wind-down" \
  "30 22 * * *" \
  "暂停 Spotify。然后将音量设为20，这样明天再次启动时声音不会太大。"
```

### 注意事项 {#gotchas}

- **cron 触发时必须存在一个活跃设备。** 如果没有运行中的 Spotify 客户端（手机/桌面/Connect 音箱），播放操作会返回 `403 no active device`。对于早晨播放列表，技巧是定位一个始终在线的设备（Sonos、Echo、智能音箱），而不是你的手机。
- **任何修改播放的操作都需要 Premium** — play、pause、skip、volume、transfer。只读的 cron 作业（例如定时“给我发送最近播放的曲目”）在免费版上可以正常工作。
- **cron agent 继承你当前启用的工具集。** 必须在 `hermes tools` 中启用 Spotify，cron 会话才能看到 Spotify 工具。
- **cron 作业以 `skip_memory=True` 运行**，因此它们不会写入你的记忆存储。
完整 cron 参考：[Cron Jobs](./cron)。

## 退出登录 {#sign-out}

```bash
hermes auth logout spotify
```

从 `~/.hermes/auth.json` 中移除令牌。如需同时清除应用配置，可从 `~/.hermes/.env` 中删除 `HERMES_SPOTIFY_CLIENT_ID`（以及你设置的 `HERMES_SPOTIFY_REDIRECT_URI`），或重新运行向导。

若要在 Spotify 侧撤销应用，请访问[已关联账号的应用](https://www.spotify.com/account/apps/)，然后点击 **REMOVE ACCESS**。

## 故障排除 {#troubleshooting}

**`403 Forbidden — Player command failed: No active device found`** — 你需要在至少一台设备上运行 Spotify。打开手机、桌面或网页版 Spotify 应用，播放任意曲目片刻以注册设备，然后重试。`spotify_devices list` 会显示当前可见的设备。

**`403 Forbidden — Premium required`** — 你使用的是免费帐户，却尝试执行会改变播放状态的操作。请参考上方的功能矩阵。

**`get_currently_playing` 返回 `204 No Content`** — 当前没有任何设备在播放内容。这是 Spotify 的正常响应，并非错误；Hermes 会将其解释为空结果（`is_playing: false`）。

**`INVALID_CLIENT: Invalid redirect URI`** — Spotify 应用设置中的重定向 URI 与 Hermes 使用的 URI 不匹配。默认值为 `http://127.0.0.1:43827/spotify/callback`。请将其添加到应用的允许重定向 URI 列表中，或者在 `~/.hermes/.env` 中设置 `HERMES_SPOTIFY_REDIRECT_URI` 为你注册的 URI。

**`429 Too Many Requests`** — Spotify 的速率限制。Hermes 会返回一条友好的错误信息；请等待一分钟再重试。如果持续出现，你可能在脚本中运行了过于密集的循环——Spotify 的配额大约每 30 秒重置一次。

**`401 Unauthorized` 反复出现** — 你的刷新令牌已被撤销（通常是因为你从帐户中移除了该应用，或应用已被删除）。请重新运行 `hermes auth spotify`。

**向导未自动打开浏览器** — 如果你通过 SSH 连接或处于没有显示器的容器中，Hermes 会检测到并跳过自动打开。请复制它打印的控制台 URL 并手动打开。

## 进阶：自定义权限范围 {#advanced-custom-scopes}

默认情况下，Hermes 会请求所有已提供工具所需的权限范围。如需限制访问权限，可按如下方式覆盖：

```bash
hermes auth spotify --scope "user-read-playback-state user-modify-playback-state playlist-read-private"
```

权限范围参考：[Spotify Web API scopes](https://developer.spotify.com/documentation/web-api/concepts/scopes)。如果你请求的权限范围少于某个工具所需的范围，该工具的调用将返回 403 错误。

## 进阶：自定义客户端 ID / 重定向 URI {#advanced-custom-client-id-redirect-uri}

```bash
hermes auth spotify --client-id <id> --redirect-uri http://localhost:3000/callback
```

或者将其永久设置到 `~/.hermes/.env` 中：

```
HERMES_SPOTIFY_CLIENT_ID=<your_id>
HERMES_SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

重定向 URI 必须在 Spotify 应用设置的白名单中。默认值适用于绝大多数场景——仅在端口 43827 被占用时才需要修改。

## 文件存放位置 {#where-things-live}

| 文件 | 内容 |
|------|------|
| `~/.hermes/auth.json` → `providers.spotify` | 访问令牌、刷新令牌、过期时间、权限范围、重定向 URI |
| `~/.hermes/.env` | `HERMES_SPOTIFY_CLIENT_ID`，可选的 `HERMES_SPOTIFY_REDIRECT_URI` |
| Spotify 应用 | 由你在 [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) 拥有；包含客户端 ID 和重定向 URI 白名单 |
