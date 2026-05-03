---
title: "Spotify — Spotify：播放、搜索、队列、管理播放列表和设备"
sidebar_label: "Spotify"
description: "Spotify：播放、搜索、队列、管理播放列表和设备"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Spotify {#spotify}

Spotify：播放、搜索、队列、管理播放列表和设备。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/spotify` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `spotify`、`music`、`playback`、`playlists`、`media` |
| 相关技能 | [`gif-search`](/user-guide/skills/bundled/media/media-gif-search) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="spotify"></a>
# Spotify

通过 Hermes Spotify 工具集（7 个工具）控制用户的 Spotify 账户。设置指南：https://hermes-agent.nousresearch.com/docs/user-guide/features/spotify

## 何时使用此技能 {#when-to-use-this-skill}

用户说出类似“播放 X”、“暂停”、“跳过”、“把 X 加入队列”、“正在播放什么”、“搜索 X”、“添加到我的 X 播放列表”、“创建一个播放列表”、“保存到我的资料库”等语句时。

## 7 个工具 {#the-7-tools}

- `spotify_playback` — 播放、暂停、下一首、上一首、跳转、设置重复模式、设置随机播放、设置音量、获取状态、获取当前播放、最近播放
- `spotify_devices` — 列出、转移
- `spotify_queue` — 获取、添加
- `spotify_search` — 搜索目录
- `spotify_playlists` — 列出、获取、创建、添加项目、移除项目、更新详情
- `spotify_albums` — 获取、曲目
- `spotify_library` — 使用 `kind: "tracks"|"albums"` 列出/保存/移除

改变播放状态的操作需要 Spotify Premium；搜索/资料库/播放列表操作在免费版上可用。

## 规范模式（最小化工具调用） {#canonical-patterns-minimize-tool-calls}

### “播放 &lt;艺术家/曲目/专辑&gt;” {#play-artist-track-album}
一次搜索，然后通过 URI 播放。除非用户要求选项，否则不要循环遍历搜索结果并逐一描述。

```
spotify_search({"query": "miles davis kind of blue", "types": ["album"], "limit": 1})
→ 得到专辑 URI spotify:album:1weenld61qoidwYuZ1GESA
spotify_playback({"action": "play", "context_uri": "spotify:album:1weenld61qoidwYuZ1GESA"})
```

对于“播放一些 &lt;艺术家&gt;”（没有具体歌曲），优先使用 `types: ["artist"]` 并播放艺术家上下文 URI——Spotify 会处理智能随机播放。如果用户说“那首歌”或“那个曲目”，搜索 `types: ["track"]` 并传递 `uris: [track_uri]` 来播放。

### “正在播放什么？”/“我在听什么？” {#what-s-playing-what-am-i-listening-to}
单次调用——不要在 `get_currently_playing` 之后链式调用 `get_state`。

```
spotify_playback({"action": "get_currently_playing"})
```

如果返回 204/空（`is_playing: false`），告诉用户没有在播放。不要重试。

### “暂停”/“跳过”/“音量 50” {#pause-skip-volume-50}
直接操作，无需预先检查。

```
spotify_playback({"action": "pause"})
spotify_playback({"action": "next"})
spotify_playback({"action": "set_volume", "volume_percent": 50})
```

### “添加到我的 &lt;播放列表名称&gt; 播放列表” {#add-to-my-playlist-name-playlist}
1. 使用 `spotify_playlists list` 按名称查找播放列表 ID
2. 获取曲目 URI（从当前播放或搜索）
3. 使用 `spotify_playlists add_items` 传入 playlist_id 和 URIs
```
spotify_playlists({"action": "list"})
→ found "Late Night Jazz" = 37i9dQZF1DX4wta20PHgwo
spotify_playback({"action": "get_currently_playing"})
→ current track uri = spotify:track:0DiWol3AO6WpXZgp0goxAV
spotify_playlists({"action": "add_items",
                   "playlist_id": "37i9dQZF1DX4wta20PHgwo",
                   "uris": ["spotify:track:0DiWol3AO6WpXZgp0goxAV"]})
```

### "创建一个名为 X 的歌单，并把我最近播放的 3 首歌加进去" {#create-a-playlist-called-x-and-add-the-last-3-songs-i-played}
```
spotify_playback({"action": "recently_played", "limit": 3})
spotify_playlists({"action": "create", "name": "Focus 2026"})
→ got playlist_id back in response
spotify_playlists({"action": "add_items", "playlist_id": <id>, "uris": [<3 uris>]})
```

### "保存 / 取消保存 / 这个保存了吗？" {#save-unsave-is-this-saved}
使用 `spotify_library` 并指定正确的 `kind`。

```
spotify_library({"kind": "tracks", "action": "save", "uris": ["spotify:track:..."]})
spotify_library({"kind": "albums", "action": "list", "limit": 50"})
```

### "将播放转移到我的 &lt;device&gt;" {#transfer-playback-to-my-device}
```
spotify_devices({"action": "list"})
→ pick the device_id by matching name/type
spotify_devices({"action": "transfer", "device_id": "<id>", "play": true})
```

## 关键失败模式 {#critical-failure-modes}

**`403 Forbidden — No active device found`** 出现在任何播放操作上，意味着 Spotify 没有在任何地方运行。告诉用户："请先在手机/桌面/网页播放器上打开 Spotify，随便播放一首歌一秒钟，然后重试。" 不要盲目重试工具调用——它会以同样的方式失败。你可以调用 `spotify_devices list` 来确认；如果列表为空，则表示没有活跃设备。

**`403 Forbidden — Premium required`** 意味着用户使用的是免费版，并试图修改播放状态。不要重试；告诉他们此操作需要 Premium 订阅。读取操作仍然有效（搜索、歌单、资料库、获取状态）。

**`get_currently_playing` 返回 `204 No Content`** 不是错误——它表示当前没有播放任何内容。该工具会返回 `is_playing: false`。只需向用户报告即可。

**`429 Too Many Requests`** = 速率限制。等待并重试一次。如果持续发生，说明你在循环调用——请停止。

**重试后出现 `401 Unauthorized`** — 刷新令牌已失效。告诉用户重新运行 `hermes auth spotify`。

## URI 和 ID 格式 {#uri-and-id-formats}

Spotify 使用三种可互换的 ID 格式。这些工具都接受这三种格式并进行标准化：

- URI: `spotify:track:0DiWol3AO6WpXZgp0goxAV`（推荐）
- URL: `https://open.spotify.com/track/0DiWol3AO6WpXZgp0goxAV`
- Bare ID: `0DiWol3AO6WpXZgp0goxAV`

如有疑问，请使用完整的 URI。搜索结果会在 `uri` 字段中返回 URI——直接传递这些 URI 即可。

实体类型：`track`、`album`、`artist`、`playlist`、`show`、`episode`。为操作使用正确的类型——`spotify_playback.play` 配合 `context_uri` 时，期望的是 album/playlist/artist；`uris` 期望的是一个 track URI 数组。

## 不要做什么 {#what-not-to-do}

- **不要在每次操作前都调用 `get_state`。** Spotify 无需预检即可接受播放/暂停/跳过。只有当用户询问"正在播放什么"或者你需要推理设备/曲目时，才检查状态。
- **除非被问到，否则不要描述搜索结果。** 如果用户说"播放 X"，就搜索、获取顶部 URI、播放。如果不对，他们自己会听到。
- **不要在 `403 Premium required` 或 `403 No active device` 时重试。** 这些错误在用户采取行动之前是永久性的。
- **不要使用 `spotify_search` 按名称查找歌单**——那会搜索公共的 Spotify 目录。用户的歌单来自 `spotify_playlists list`。
- **不要在 `spotify_library` 中将 `kind: "tracks"` 与专辑 URI 混用**（反之亦然）。该工具会标准化 ID，但 API 端点不同。
