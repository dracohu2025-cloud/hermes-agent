---
sidebar_position: 10
title: "皮肤与主题"
description: "使用内置和用户自定义的皮肤来定制 Hermes CLI 的外观"
---

# 皮肤与主题

皮肤控制着 Hermes CLI 的**视觉呈现**：横幅颜色、旋转器表情和动词、响应框标签、品牌文本以及工具活动前缀。

对话风格和视觉风格是两个独立的概念：

- **个性**改变 Agent 的语气和措辞。
- **皮肤**改变 CLI 的外观。

## 更换皮肤

```bash
/skin                # 显示当前皮肤并列出可用皮肤
/skin ares           # 切换到内置皮肤
/skin mytheme        # 切换到自定义皮肤（位于 ~/.hermes/skins/mytheme.yaml）
```

或者在 `~/.hermes/config.yaml` 中设置默认皮肤：

```yaml
display:
  skin: default
```

## 内置皮肤

| 皮肤 | 描述 | Agent 品牌 |
|------|-------------|----------------|
| `default` | 经典 Hermes — 金色与可爱风格 | `Hermes Agent` |
| `ares` | 战神主题 — 深红与青铜色 | `Ares Agent` |
| `mono` | 单色 — 简洁的灰度 | `Hermes Agent` |
| `slate` | 冷蓝色 — 面向开发者 | `Hermes Agent` |
| `poseidon` | 海神主题 — 深蓝与海沫色 | `Poseidon Agent` |
| `sisyphus` | 西西弗斯主题 — 朴素的灰度，带有坚持感 | `Sisyphus Agent` |
| `charizard` | 火山主题 — 焦橙色与余烬色 | `Charizard Agent` |

## 皮肤可定制的内容

| 区域 | 配置键 |
|------|------|
| 横幅 + 响应颜色 | `colors.banner_*`, `colors.response_border` |
| 旋转器动画 | `spinner.waiting_faces`, `spinner.thinking_faces`, `spinner.thinking_verbs`, `spinner.wings` |
| 品牌文本 | `branding.agent_name`, `branding.welcome`, `branding.response_label`, `branding.prompt_symbol` |
| 工具活动前缀 | `tool_prefix` |

## 自定义皮肤

在 `~/.hermes/skins/` 目录下创建 YAML 文件。用户皮肤会从内置的 `default` 皮肤继承缺失的值。

```yaml
name: cyberpunk
description: 霓虹终端主题

colors:
  banner_border: "#FF00FF"
  banner_title: "#00FFFF"
  banner_accent: "#FF1493"

spinner:
  thinking_verbs: ["jacking in", "decrypting", "uploading"]
  wings:
    - ["⟨⚡", "⚡⟩"]

branding:
  agent_name: "Cyber Agent"
  response_label: " ⚡ Cyber "

tool_prefix: "▏"
```

## 操作说明

- 内置皮肤从 `hermes_cli/skin_engine.py` 加载。
- 未知的皮肤会自动回退到 `default`。
- `/skin` 命令会立即更新当前会话的活动 CLI 主题。