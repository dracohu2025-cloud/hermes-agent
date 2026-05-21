---
title: "Spotify — Spotify：播放、搜索、队列、管理播放列表和设备"
sidebar_label: "Spotify"
description: "Spotify：播放、搜索、队列、管理播放列表和设备"
---

{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="spotify"></a>
# Spotify

Spotify：播放、搜索、队列、管理播放列表和设备。

<a id="skill-metadata"></a>
## Skill 元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/spotify` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `spotify`, `music`, `playback`, `playlists`, `media` |
| 相关 skill | [`gif-search`](/user-guide/skills/bundled/media/media-gif-search) |

<a id="reference-full-skill-md"></a>
## 参考：完整版 SKILL.md

:::info
以下是当该 skill 被触发时 Hermes 加载的完整 skill 定义。这是 Agent 在 skill 激活时看到的指令。
:::

# Spotify

通过 Hermes Spotify 工具集（7 个工具）控制用户的 Spotify 账户。设置指南：https://hermes-agent.nousresearch.com/docs/user-guide/features/spotify

<a id="when-to-use-this-skill"></a>
## 何时使用此 skill

用户说出类似“播放 X”、“暂停”、“跳过”、“排队 X”、“正在播放什么”、“搜索 X”、“添加到我的 X 播放列表”、“创建一个播放列表”、“保存到我的资料库”等语句时。

<a id="the-7-tools"></a>
## 7 个工具

- `spotify_playback` — 播放、暂停、下一首、上一首、跳转、设置重复模式、设置随机播放、设置音量、获取状态、获取当前播放内容、最近播放
- `spotify_devices` — 列出、转移
- `spotify_queue` — 获取、添加
- `spotify_search` — 搜索目录
- `spotify_playlists` — 列出、获取、创建、添加项目、移除项目、更新详情
- `spotify_albums` — 获取、曲目列表
- `spotify_library` — 使用 `kind: "tracks"|"albums"` 列出/保存/移除

修改播放状态的操作需要 Spotify Premium；搜索/资料库/播放列表操作在免费版上可用。

<a id="canonical-patterns-minimize-tool-calls"></a>
## 规范模式（最小化工具调用）

<a id="play-artist-track-album"></a>
### “播放 &lt;艺术家/曲目/专辑>”
一次搜索，然后通过 URI 播放。除非用户要求选项，否则不要循环遍历搜索结果并逐一描述。

```
spotify_search({"query": "miles davis kind of blue", "types": ["album"], "limit": 1})
→ 获得专辑 URI spotify:album:1weenld61qoidwYuZ1GESA
spotify_playback({"action": "play", "context_uri": "spotify:album:1weenld61qoidwYuZ1GESA"})
```

对于“播放一些 &lt;艺术家>”（没有具体歌曲），优先使用 `types: ["artist"]` 并播放艺术家上下文 URI —— Spotify 会自动智能随机播放。如果用户说“这首歌”或“那个曲目”，搜索 `types: ["track"]` 并传递 `uris: [track_uri]` 来播放。

<a id="what-s-playing-what-am-i-listening-to"></a>
### “正在播放什么？”/“我在听什么？”
单次调用 —— 不要在 get_currently_playing 之后再链式调用 get_state。

```
spotify_playback({"action": "get_currently_playing"})
```

如果返回 204/空（`is_playing: false`），告诉用户当前没有播放内容。不要重试。

<a id="pause-skip-volume-50"></a>
### “暂停”/“跳过”/“音量 50”
直接操作，无需先检查状态。

```
spotify_playback({"action": "pause"})
spotify_playback({"action": "next"})
spotify_playback({"action": "set_volume", "volume_percent": 50})
```

<a id="add-to-my-playlist-name-playlist"></a>
### “添加到我的 &lt;播放列表名称> 播放列表”
1. `spotify_playlists list` 按名称找到播放列表 ID
2. 获取曲目 URI（从当前播放内容或搜索获得）
3. 使用 `playlist_id` 和 URIs 调用 `spotify_playlists add_items`
```
spotify_playlists({"action": "list"})
→ found "Late Night Jazz" = 37i9dQZF1DX4wta20PHgwo
spotify_playback({"action": "get_currently_playing"})
→ current track uri = spotify:track:0DiWol3AO6WpXZgp0goxAV
spotify_playlists({"action": "add_items",
                   "playlist_id": "37i9dQZF1DX4wta20PHgwo",
                   "uris": ["spotify:track:0DiWol3AO6WpXZgp0goxAV"]})
```

<a id="create-a-playlist-called-x-and-add-the-last-3-songs-i-played"></a>
### "创建一个名为 X 的播放列表并添加我最近播放的 3 首歌"
```
spotify_playback({"action": "recently_played", "limit": 3})
spotify_playlists({"action": "create", "name": "Focus 2026"})
→ got playlist_id back in response
spotify_playlists({"action": "add_items", "playlist_id": <id>, "uris": [<3 uris>]})
```

<a id="save-unsave-is-this-saved"></a>
### "保存 / 取消保存 / 是否已保存？"
使用带有正确 `kind` 的 `spotify_library`。

```
spotify_library({"kind": "tracks", "action": "save", "uris": ["spotify:track:..."]})
spotify_library({"kind": "albums", "action": "list", "limit": 50})
```

<a id="transfer-playback-to-my-device"></a>
### "将播放转移到我的 &lt;device>"
```
spotify_devices({"action": "list"})
→ pick the device_id by matching name/type
spotify_devices({"action": "transfer", "device_id": "<id>", "play": true})
```

<a id="critical-failure-modes"></a>
## 关键故障模式

**`403 Forbidden — No active device found`** 出现在任何播放操作上，意味着 Spotify 没有在运行。告诉用户："请先在手机/桌面/网页播放器上打开 Spotify，播放任意曲目一秒钟，然后重试。" 不要盲目重试工具调用——结果仍会失败。你可以调用 `spotify_devices list` 确认；返回空列表表示没有活跃设备。

**`403 Forbidden — Premium required`** 表示用户使用的是免费版，并试图修改播放状态。不要重试；告诉用户此操作需要 Premium。读取操作仍然有效（搜索、播放列表、音乐库、get_state）。

**`get_currently_playing` 返回 `204 No Content`** 不是错误——表示当前没有播放任何内容。工具返回 `is_playing: false`。直接报告给用户即可。

**`429 Too Many Requests`** = 速率限制。等待后重试一次。如果持续出现，说明你在循环调用——请停止。

**重试后出现 `401 Unauthorized`** —— 刷新令牌已失效。告诉用户重新运行 `hermes auth spotify`。

<a id="uri-and-id-formats"></a>
## URI 和 ID 格式

Spotify 使用三种可互换的 ID 格式。工具全部接受并归一化：

- URI：`spotify:track:0DiWol3AO6WpXZgp0goxAV`（推荐）
- URL：`https://open.spotify.com/track/0DiWol3AO6WpXZgp0goxAV`
- Bare ID：`0DiWol3AO6WpXZgp0goxAV`

不确定时，使用完整的 URI。搜索结果会在 `uri` 字段返回 URI——直接传入即可。

实体类型：`track`、`album`、`artist`、`playlist`、`show`、`episode`。请为操作使用正确的类型——`spotify_playback.play` 配合 `context_uri` 期望 album/playlist/artist；`uris` 期望一个 track URI 数组。

<a id="what-not-to-do"></a>
## 不要做的事情

- **不要在每次操作前调用 `get_state`。** Spotify 接受直接播放/暂停/跳过，无需预检。只有当用户询问"正在播放什么"或你需要推断设备/曲目时，才检查状态。
- **除非被要求，不要描述搜索结果。** 如果用户说"播放 X"，搜索、获取顶部 URI、直接播放。如果不对，用户会听到并知道。
- **不要在 `403 Premium required` 或 `403 No active device` 时重试。** 这些错误在用户采取行动前是永久性的。
- **不要使用 `spotify_search` 按名称查找播放列表** —— 这会搜索公开的 Spotify 目录。用户播放列表来自 `spotify_playlists list`。
- **不要在 `spotify_library` 中将 `kind: "tracks"` 与专辑 URI 混用**（反之亦然）。工具会归一化 ID，但 API 端点不同。
