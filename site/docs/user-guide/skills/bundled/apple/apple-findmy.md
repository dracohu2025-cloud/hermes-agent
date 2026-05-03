---
title: "Findmy — 通过 FindMy 追踪 Apple 设备/AirTags"
sidebar_label: "Findmy"
description: "通过 FindMy 追踪 Apple 设备/AirTags"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Findmy {#findmy}

通过 macOS 上的 FindMy.app 追踪 Apple 设备/AirTags。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/findmy` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `FindMy`、`AirTag`、`location`、`tracking`、`macOS`、`Apple` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Find My (Apple) {#find-my-apple}

通过 macOS 上的 FindMy.app 追踪 Apple 设备和 AirTags。由于 Apple 没有为 FindMy 提供 CLI，本技能使用 AppleScript 打开应用，并通过屏幕截图读取设备位置。

## 前置条件 {#prerequisites}

- **macOS**，已安装 Find My 应用并登录 iCloud
- 设备/AirTags 已在 Find My 中注册
- 终端已获得屏幕录制权限（系统设置 → 隐私与安全性 → 屏幕录制）
- **可选但推荐**：安装 `peekaboo` 以获得更好的 UI 自动化体验：`brew install steipete/tap/peekaboo`

## 何时使用 {#when-to-use}

- 用户询问“我的 [设备/猫/钥匙/包] 在哪里？”
- 追踪 AirTag 位置
- 检查设备位置（iPhone、iPad、Mac、AirPods）
- 随时间监控宠物或物品的移动（AirTag 巡逻路线）

## 方法 1：AppleScript + 截图（基础） {#method-1-applescript-screenshot-basic}

### 打开 FindMy 并导航 {#open-findmy-and-navigate}

```bash
# Open Find My app
osascript -e 'tell application "FindMy" to activate'

# Wait for it to load
sleep 3

# Take a screenshot of the Find My window
screencapture -w -o /tmp/findmy.png
```

然后使用 `vision_analyze` 读取截图：
```
vision_analyze(image_url="/tmp/findmy.png", question="What devices/items are shown and what are their locations?")
```

### 切换标签页 {#switch-between-tabs}

```bash
# Switch to Devices tab
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Devices" of toolbar 1 of window 1
    end tell
end tell'

# Switch to Items tab (AirTags)
osascript -e '
tell application "System Events"
    tell process "FindMy"
        click button "Items" of toolbar 1 of window 1
    end tell
end tell'
```

## 方法 2：Peekaboo UI 自动化（推荐） {#method-2-peekaboo-ui-automation-recommended}

如果已安装 `peekaboo`，使用它进行更可靠的 UI 交互：

```bash
# Open Find My
osascript -e 'tell application "FindMy" to activate'
sleep 3

# Capture and annotate the UI
peekaboo see --app "FindMy" --annotate --path /tmp/findmy-ui.png

# Click on a specific device/item by element ID
peekaboo click --on B3 --app "FindMy"

# Capture the detail view
peekaboo image --app "FindMy" --path /tmp/findmy-detail.png
```

然后使用视觉分析：
```
vision_analyze(image_url="/tmp/findmy-detail.png", question="What is the location shown for this device/item? Include address and coordinates if visible.")
```

## 工作流：随时间追踪 AirTag 位置 {#workflow-track-airtag-location-over-time}
用于监控 AirTag（例如追踪猫咪的巡逻路线）：

```bash
# 1. Open FindMy to Items tab
osascript -e 'tell application "FindMy" to activate'
sleep 3

# 2. Click on the AirTag item (stay on page — AirTag only updates when page is open)

# 3. Periodically capture location
while true; do
    screencapture -w -o /tmp/findmy-$(date +%H%M%S).png
    sleep 300  # Every 5 minutes
done
```

通过视觉能力分析每张截图以提取坐标，然后合成路线图。

## 限制 {#limitations}

- FindMy **没有 CLI 或 API** —— 必须使用 UI 自动化
- 只有当 FindMy 页面处于活跃显示状态时，AirTags 才会更新位置
- 定位精度取决于 FindMy 网络中附近 Apple 设备的参与
- 截屏需要“屏幕录制”权限
- AppleScript UI 自动化在不同 macOS 版本间可能失效

## 规则 {#rules}

1. 跟踪 AirTags 时，保持 FindMy 应用在前台（最小化后位置更新会停止）
2. 使用 `vision_analyze` 读取截图内容 —— 不要尝试解析像素
3. 对于持续跟踪，使用 cron 定时任务定期截屏并记录位置
4. 尊重隐私 —— 只追踪用户自己拥有的设备/物品
