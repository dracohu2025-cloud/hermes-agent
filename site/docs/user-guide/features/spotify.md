<a id="spotify"></a>
# Spotify

Hermes 可以直接控制 Spotify——包括播放、队列、搜索、播放列表、已保存的曲目/专辑以及收听历史——通过 Spotify 官方 Web API 和 PKCE OAuth。Token 存储在 `~/.hermes/auth.json` 中，遇到 401 时会自动刷新；每个机器只需登录一次。

与 Hermes 内置的 OAuth 集成（Google、GitHub Copilot、Codex）不同，Spotify 要求每个用户注册自己的轻量级开发者应用。Spotify 不允许第三方提供任何人都能使用的公共 OAuth 应用。整个流程大约需要两分钟，`hermes auth spotify` 会一步步引导你完成。

<a id="prerequisites"></a>
## 前提条件

- 一个 Spotify 账户。**免费版**可用于搜索、播放列表、资料库和活动工具。**Premium** 版才支持播放控制（播放、暂停、跳过、拖拽、音量、添加到队列、转移播放）。
- 已安装并运行 Hermes Agent。
- 对于播放工具：需要一个**活跃的 Spotify Connect 设备**——至少在一个设备（手机、电脑、网页播放器、音箱）上打开 Spotify 应用，Web API 才有东西可控制。如果没有活跃设备，你会收到 `403 Forbidden` 并提示“没有活跃设备”；在任意设备上打开 Spotify 后重试。

<a id="setup"></a>
## 设置

<a id="one-shot-hermes-tools-or-first-run-setup"></a>
### 一键式：`hermes tools` 或首次运行设置

这是最快的方式。运行：

```bash
hermes tools
```

滚动到 `🎵 Spotify`，按空格键开启，然后按 `s` 保存。同样的开关也可以在首次运行 `hermes setup` / `hermes setup tools` 的流程中使用。Spotify 默认是手动开启的，因此在那里启用它会执行与 `hermes tools` 相同的提供者感知配置。

Hermes 会直接带你进入 OAuth 流程——如果你还没有 Spotify 应用，它会引导你当场创建一个。完成之后，工具集就在一步之内启用并认证了。

如果你更喜欢分开执行这些步骤（或者稍后重新认证），请使用下面的两步流程。

<a id="two-step-flow"></a>
### 两步流程

<a id="1-enable-the-toolset"></a>
#### 1. 启用工具集

```bash
hermes tools
```

开启 `🎵 Spotify`，保存，当内联向导打开时，忽略它（Ctrl+C）。工具集保持开启；只是推迟了认证步骤。

<a id="2-run-the-login-wizard"></a>
#### 2. 运行登录向导

```bash
hermes auth spotify
```

这 7 个 Spotify 工具只有在第一步之后才会出现在 Agent 的工具集中——它们默认是关闭的，这样不需要这些工具的用户就不会在每次 API 调用时附带额外的工具 schema。

如果没有设置 `HERMES_SPOTIFY_CLIENT_ID`，Hermes 会内联地引导你完成应用注册：

1. 在浏览器中打开 `https://developer.spotify.com/dashboard`
2. 打印需要粘贴到 Spotify“创建应用”表单中的确切值
3. 提示你输入拿到的 Client ID
4. 将其保存到 `~/.hermes/.env`，这样以后就可以跳过这一步
5. 直接进入 OAuth 授权流程

你批准后，Token 会写入 `~/.hermes/auth.json` 中的 `providers.spotify` 下。活跃的推理提供者**不会**改变——Spotify 认证与你使用的 LLM 提供者是独立的。

<a id="creating-the-spotify-app-what-the-wizard-asks-for"></a>
### 创建 Spotify 应用（向导要求的内容）

当仪表盘打开后，点击**创建应用**并填写：

| 字段 | 值 |
|-------|-------|
| 应用名称 | 任意（例如 `hermes-agent`） |
| 应用描述 | 任意（例如 `personal Hermes integration`） |
| 网站 | 留空 |
| 重定向 URI | `http://127.0.0.1:43827/spotify/callback` |
| 使用哪些 API/SDK？ | 勾选 **Web API** |
同意条款并点击 **Save**。在下一页点击 **Settings** → 复制 **Client ID** 并粘贴到 Hermes 提示中。这是 Hermes 唯一需要的值——PKCE 不使用客户端密钥。

<a id="running-over-ssh-in-a-headless-environment"></a>
### 通过 SSH / 在无头环境中运行

如果设置了 `SSH_CLIENT` 或 `SSH_TTY`，Hermes 会在向导步骤和 OAuth 步骤中跳过自动打开浏览器。复制 Hermes 打印的仪表盘 URL 和授权 URL，在本机浏览器中打开它们，然后正常继续——本地 HTTP 监听器仍然在远程主机的 `43827` 端口上运行。如果没有 SSH 本地转发，笔记本的浏览器无法访问远程的回环地址：

```bash
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

对于跳板机 / 堡垒机设置和其他陷阱（mosh、tmux、端口冲突），请参阅 [OAuth over SSH / Remote Hosts](../../guides/oauth-over-ssh.md)。

<a id="verify"></a>
## 验证

```bash
hermes auth status spotify
```

显示令牌是否存在以及访问令牌何时过期。刷新是自动的：当任何 Spotify API 调用返回 401 时，客户端会交换刷新令牌并重试一次。刷新令牌在 Hermes 重启后仍然保留，因此只有在 Spotify 账户设置中撤销应用或运行 `hermes auth logout spotify` 时才需要重新认证。

<a id="using-it"></a>
## 使用

登录后，Agent 可以访问 7 个 Spotify 工具。您可以自然地与 Agent 对话——它会选择合适的工具和操作。为了获得最佳行为，Agent 会加载一个配套技能，该技能教授规范的用法模式（单次搜索后播放、何时不要预检 `get_state` 等）。

```
> play some miles davis
> what am I listening to
> add this track to my Late Night Jazz playlist
> skip to the next song
> make a new playlist called "Focus 2026" and add the last three songs I played
> which of my saved albums are by Radiohead
> search for acoustic covers of Blackbird
> transfer playback to my kitchen speaker
```

<a id="tool-reference"></a>
### 工具参考

所有修改播放状态的操作都接受可选的 `device_id` 参数，用于指定目标设备。如果省略，Spotify 会使用当前活跃设备。

<a id="spotifyplayback"></a>
#### `spotify_playback`

控制并检查播放状态，还可以获取最近播放的历史记录。

| 操作 | 用途 | 需要 Premium? |
|--------|---------|----------|
| `get_state` | 完整的播放状态（曲目、设备、进度、随机播放/重复） | 否 |
| `get_currently_playing` | 仅当前曲目（如果返回 204 则返回空——见下方说明） | 否 |
| `play` | 开始/恢复播放。可选参数：`context_uri`, `uris`, `offset`, `position_ms` | 是 |
| `pause` | 暂停播放 | 是 |
| `next` / `previous` | 跳过曲目 | 是 |
| `seek` | 跳转到 `position_ms` | 是 |
| `set_repeat` | `state` = `track` / `context` / `off` | 是 |
| `set_shuffle` | `state` = `true` / `false` | 是 |
| `set_volume` | `volume_percent` = 0-100 | 是 |
| `recently_played` | 最后播放的曲目。可选参数 `limit`, `before`, `after`（Unix 毫秒时间戳） | 否 |

<a id="spotifydevices"></a>
#### `spotify_devices`

| 操作 | 用途 |
|--------|---------|
| `list` | 您账户可见的所有 Spotify Connect 设备 |
| `transfer` | 将播放转移到 `device_id`。可选 `play: true` 在转移时开始播放 |
<a id="home-assistant-managed-speakers"></a>
### Home Assistant 管理的音箱

如果 Home Assistant 管理的音箱已经支持 Spotify Connect（例如 Sonos、Echo、Nest 或其他支持 Connect 的音箱），只要 Spotify 能发现它们，它们就会自动出现在 `spotify_devices list` 中。对于这种路径，Hermes 不需要 Home Assistant ↔ Spotify 桥接——Spotify 本身就能处理设备路由。

你可以让 Hermes 通过音箱的显示名称来转移播放（例如“把 Spotify 转移到厨房音箱”），或者在编写脚本时调用 `spotify_devices list`，然后将确切的 `device_id` 传递给 `spotify_devices transfer`。如果音箱没有出现，请打开一次 Spotify 应用或音箱的 Spotify 集成，这样 Spotify 就会将其注册为活跃的 Connect 目标。

<a id="spotifyqueue"></a>
#### `spotify_queue`
| 操作 | 用途 | 需要 Premium？ |
|--------|---------|----------|
| `get` | 获取当前队列中的曲目 | 否 |
| `add` | 将 `uri` 追加到队列 | 是 |

<a id="spotifysearch"></a>
#### `spotify_search`
搜索目录。`query` 是必填项。可选参数：`types`（`track` / `album` / `artist` / `playlist` / `show` / `episode` 的数组）、`limit`、`offset`、`market`。

<a id="spotifyplaylists"></a>
#### `spotify_playlists`
| 操作 | 用途 | 必填参数 |
|--------|---------|---------------|
| `list` | 用户的播放列表 | — |
| `get` | 获取一个播放列表及其曲目 | `playlist_id` |
| `create` | 创建新播放列表 | `name`（可选 `description`、`public`、`collaborative`） |
| `add_items` | 添加曲目 | `playlist_id`、`uris`（可选 `position`） |
| `remove_items` | 移除曲目 | `playlist_id`、`uris`（可选 `snapshot_id`） |
| `update_details` | 重命名/编辑 | `playlist_id` + `name`、`description`、`public`、`collaborative` 中的任意一个 |

<a id="spotifyalbums"></a>
#### `spotify_albums`
| 操作 | 用途 | 必填参数 |
|--------|---------|---------------|
| `get` | 专辑元数据 | `album_id` |
| `tracks` | 专辑曲目列表 | `album_id` |

<a id="spotifylibrary"></a>
#### `spotify_library`
统一访问已保存的曲目和已保存的专辑。使用 `kind` 参数选择集合。

| 操作 | 用途 |
|--------|---------|
| `list` | 分页列出库内容 |
| `save` | 将 `ids` / `uris` 添加到库 |
| `remove` | 从库中移除 `ids` / `uris` |

必填：`kind` = `tracks` 或 `albums`，加上 `action`。

<a id="feature-matrix-free-vs-premium"></a>
### 功能矩阵：免费版 vs Premium

只读工具在免费账户上可用。任何会改变播放状态或队列的操作都需要 Premium。

| 免费版可用 | 需要 Premium |
|---------------|------------------|
| `spotify_search`（全部） | `spotify_playback` — play、pause、next、previous、seek、set_repeat、set_shuffle、set_volume |
| `spotify_playback` — get_state、get_currently_playing、recently_played | `spotify_queue` — add |
| `spotify_devices` — list | `spotify_devices` — transfer |
| `spotify_queue` — get | |
| `spotify_playlists`（全部） | |
| `spotify_albums`（全部） | |
| `spotify_library`（全部） | |

<a id="scheduling-spotify-cron"></a>
## 定时任务：Spotify + cron

由于 Spotify 工具是常规的 Hermes 工具，在 Hermes 会话中运行的 cron 任务可以按任何时间表触发播放。无需编写新代码。

<a id="morning-wake-up-playlist"></a>
### 早晨唤醒播放列表
```bash
hermes cron add \
  --name "morning-commute" \
  "0 7 * * 1-5" \
  "将播放转移到我的厨房音箱，并播放我的'通勤早晨'歌单。音量设为 40。开启随机播放。"
```

每个工作日上午 7 点会发生什么：
1. Cron 启动一个无头 Hermes 会话。
2. Agent 读取提示，调用 `spotify_devices list` 按名称找到“厨房音箱”，然后依次调用 `spotify_devices transfer` → `spotify_playback set_volume` → `spotify_playback set_shuffle` → `spotify_search` + `spotify_playback play`。
3. 音乐开始在目标音箱上播放。总成本：一个会话，几次工具调用，无需人工输入。

<a id="wind-down-at-night"></a>
### 夜间放松

```bash
hermes cron add \
  --name "wind-down" \
  "30 22 * * *" \
  "暂停 Spotify。然后将音量设为 20，这样明天我再次启动时声音不会太大。"
```

<a id="gotchas"></a>
### 注意事项

- **Cron 触发时必须有一个活跃的设备存在。** 如果没有运行中的 Spotify 客户端（手机/桌面/Connect 音箱），播放操作会返回 `403 no active device`。对于早晨歌单，技巧是定位到始终在线的设备（Sonos、Echo、智能音箱），而不是你的手机。
- **任何改变播放状态的操作都需要 Premium 账户** — 播放、暂停、跳过、音量、转移。只读的 cron 任务（例如定时“给我发送最近播放的曲目”）在免费账户上可以正常使用。
- **Cron agent 会继承你当前启用的工具集。** 必须在 `hermes tools` 中启用 Spotify，cron 会话才能看到 Spotify 工具。
- **Cron 任务以 `skip_memory=True` 运行**，因此它们不会写入你的记忆存储。

完整的 cron 参考文档：[Cron 任务](./cron)。

<a id="sign-out"></a>
## 退出登录

```bash
hermes auth logout spotify
```

从 `~/.hermes/auth.json` 中移除令牌。要同时清除应用配置，请从 `~/.hermes/.env` 中删除 `HERMES_SPOTIFY_CLIENT_ID`（以及你设置的 `HERMES_SPOTIFY_REDIRECT_URI`），或者重新运行向导。

要在 Spotify 端撤销应用授权，请访问[已连接到你的账户的应用](https://www.spotify.com/account/apps/)，然后点击**移除访问权限**。

<a id="troubleshooting"></a>
## 故障排除

**`403 Forbidden — Player command failed: No active device found`** — 你需要在至少一台设备上运行 Spotify。在手机、桌面或网页播放器上打开 Spotify 应用，播放任意曲目一秒钟以注册设备，然后重试。`spotify_devices list` 会显示当前可见的设备。

**`403 Forbidden — Premium required`** — 你使用的是免费账户，但尝试了改变播放状态的操作。请参考上面的功能矩阵。

**`get_currently_playing` 返回 `204 No Content`** — 当前没有任何设备在播放内容。这是 Spotify 的正常响应，不是错误；Hermes 会将其显示为带有说明的空结果（`is_playing: false`）。

**`INVALID_CLIENT: Invalid redirect URI`** — 你的 Spotify 应用设置中的重定向 URI 与 Hermes 使用的不匹配。默认值为 `http://127.0.0.1:43827/spotify/callback`。请将该地址添加到你的应用允许的重定向 URI 列表中，或者在 `~/.hermes/.env` 中将 `HERMES_SPOTIFY_REDIRECT_URI` 设置为你注册的地址。

**`429 Too Many Requests`** — Spotify 的速率限制。Hermes 会返回一个友好的错误提示；请等待一分钟再重试。如果问题持续存在，你可能在脚本中运行了过于密集的循环——Spotify 的配额大约每 30 秒重置一次。
**反复出现 `401 Unauthorized`** — 你的刷新令牌已被撤销（通常是因为你从账户中移除了该应用，或者该应用已被删除）。重新运行 `hermes auth spotify`。

**向导没有打开浏览器** — 如果你是通过 SSH 连接，或者在无图形界面的容器中，Hermes 会检测到并跳过自动打开。复制它打印的面板 URL 并手动打开。

<a id="advanced-custom-scopes"></a>
## 进阶：自定义权限范围

默认情况下，Hermes 会请求所有已提供工具所需的权限范围。如果你想限制访问权限，可以覆盖设置：

```bash
hermes auth spotify --scope "user-read-playback-state user-modify-playback-state playlist-read-private"
```

权限范围参考：[Spotify Web API 权限范围](https://developer.spotify.com/documentation/web-api/concepts/scopes)。如果你请求的权限范围少于某个工具所需，则该工具的调用将以 403 失败。

<a id="advanced-custom-client-id-redirect-uri"></a>
## 进阶：自定义客户端 ID / 重定向 URI

```bash
hermes auth spotify --client-id <id> --redirect-uri http://localhost:3000/callback
```

或者在 `~/.hermes/.env` 中永久设置：

```
HERMES_SPOTIFY_CLIENT_ID=<your_id>
HERMES_SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

重定向 URI 必须在你的 Spotify 应用设置中被列入允许列表。默认设置对绝大多数人来说都能正常工作——只有当端口 43827 被占用时才需要更改。

<a id="where-things-live"></a>
## 文件位置

| 文件 | 内容 |
|------|------|
| `~/.hermes/auth.json` → `providers.spotify` | 访问令牌、刷新令牌、过期时间、权限范围、重定向 URI |
| `~/.hermes/.env` | `HERMES_SPOTIFY_CLIENT_ID`，可选的 `HERMES_SPOTIFY_REDIRECT_URI` |
| Spotify 应用 | 属于你，位于 [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)；包含客户端 ID 和重定向 URI 允许列表 |
