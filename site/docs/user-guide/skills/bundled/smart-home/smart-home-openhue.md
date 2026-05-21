---
title: "Openhue — 通过 OpenHue CLI 控制 Philips Hue 灯、场景和房间"
sidebar_label: "Openhue"
description: "通过 OpenHue CLI 控制 Philips Hue 灯、场景和房间"
---

{/* 此页面由技能中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

<a id="openhue"></a>
# Openhue

通过 OpenHue CLI 控制 Philips Hue 灯、场景和房间。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/smart-home/openhue` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Smart-Home`, `Hue`, `Lights`, `IoT`, `Automation` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 看到的就是这些指令。
:::

<a id="openhue-cli"></a>
# OpenHue CLI

通过终端经 Hue Bridge 控制 Philips Hue 灯和场景。

<a id="prerequisites"></a>
## 前置条件

```bash
# Linux（预编译二进制）
curl -sL https://github.com/openhue/openhue-cli/releases/latest/download/openhue-linux-amd64 -o ~/.local/bin/openhue && chmod +x ~/.local/bin/openhue

# macOS
brew install openhue/cli/openhue-cli
```

首次运行需要按下 Hue Bridge 上的按钮进行配对。Bridge 必须与运行 Hermes 的机器处于同一本地网络中。

<a id="when-to-use"></a>
## 使用场景

- “打开/关闭灯”
- “调暗客厅灯光”
- “设置场景”或“电影模式”
- 控制特定的 Hue 房间、区域或单个灯泡
- 调节亮度、颜色或色温

<a id="common-commands"></a>
## 常用命令

<a id="list-resources"></a>
### 列出资源

```bash
openhue get light       # 列出所有灯
openhue get room        # 列出所有房间
openhue get scene       # 列出所有场景
```

<a id="control-lights"></a>
### 控制灯

```bash
# 打开/关闭
openhue set light "Bedroom Lamp" --on
openhue set light "Bedroom Lamp" --off

# 亮度（0-100）
openhue set light "Bedroom Lamp" --on --brightness 50

# 色温（暖到冷：153-500 微倒度）
openhue set light "Bedroom Lamp" --on --temperature 300

# 颜色（按名称或十六进制）
openhue set light "Bedroom Lamp" --on --color red
openhue set light "Bedroom Lamp" --on --rgb "#FF5500"
```

<a id="control-rooms"></a>
### 控制房间

```bash
# 关闭整个房间
openhue set room "Bedroom" --off

# 设置房间亮度
openhue set room "Bedroom" --on --brightness 30
```

<a id="scenes"></a>
### 场景

```bash
openhue set scene "Relax" --room "Bedroom"
openhue set scene "Concentrate" --room "Office"
```

<a id="quick-presets"></a>
## 快速预设

```bash
# 睡前（暖光调暗）
openhue set room "Bedroom" --on --brightness 20 --temperature 450

# 工作模式（明亮冷光）
openhue set room "Office" --on --brightness 100 --temperature 250

# 电影模式（昏暗）
openhue set room "Living Room" --on --brightness 10

# 全部关闭
openhue set room "Bedroom" --off
openhue set room "Office" --off
openhue set room "Living Room" --off
```

<a id="notes"></a>
## 注意事项

- Bridge 必须与运行 Hermes 的机器处于同一本地网络中
- 首次运行需要物理按下 Hue Bridge 上的按钮进行授权
- 颜色仅在支持彩光的灯泡上生效（不包括纯白型号）
- 灯名和房间名区分大小写——使用 `openhue get light` 检查确切名称
- 可与 cron 任务配合实现定时照明（例如睡前调暗、起床调亮）
