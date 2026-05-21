---
title: "Meme Generation — 选取模板并用 Pillow 叠加文本，生成真实的梗图"
sidebar_label: "Meme Generation"
description: "选取模板并用 Pillow 叠加文本，生成真实的梗图"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="meme-generation"></a>
# 梗图生成

通过选取模板并用 Pillow 叠加文本，生成真实的梗图。能够产出实际的 .png 梗图文件。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/meme-generation` 安装 |
| 路径 | `optional-skills/creative/meme-generation` |
| 版本 | `2.0.0` |
| 作者 | adanaleycio |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `creative`, `memes`, `humor`, `images` |
| 相关技能 | [`ascii-art`](/user-guide/skills/bundled/creative/creative-ascii-art), `generative-widgets` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是该技能触发时 Hermes 加载的完整技能定义。这就是技能激活时 agent 看到的指令。
:::

# 梗图生成

根据某个主题生成实际的梗图。选取模板，撰写说明文字，并渲染出带有文本叠加的真实 .png 文件。

<a id="when-to-use"></a>
## 使用时机

- 用户要求你制作或生成一个梗图
- 用户想要关于某个特定主题、情境或烦恼的梗图
- 用户说“把这个做成梗图”或类似的话

<a id="available-templates"></a>
## 可用模板

该脚本支持**大约 100 个流行的 imgflip 模板**（通过名称或 ID），外加 10 个经过文本位置手动调优的精选模板。

<a id="curated-templates-custom-text-placement"></a>
### 精选模板（自定义文本位置）

| ID | 名称 | 字段 | 最佳用途 |
|----|------|--------|----------|
| `this-is-fine` | This is Fine | top, bottom | 混乱、否认 |
| `drake` | Drake Hotline Bling | reject, approve | 拒绝/偏好 |
| `distracted-boyfriend` | Distracted Boyfriend | distraction, current, person | 诱惑、优先级转移 |
| `two-buttons` | Two Buttons | left, right, person | 两难选择 |
| `expanding-brain` | Expanding Brain | 4 levels | 渐进的讽刺 |
| `change-my-mind` | Change My Mind | statement | 热点话题 |
| `woman-yelling-at-cat` | Woman Yelling at Cat | woman, cat | 争吵 |
| `one-does-not-simply` | One Does Not Simply | top, bottom | 表面简单实则困难的事情 |
| `grus-plan` | Gru's Plan | step1-3, realization | 适得其反的计划 |
| `batman-slapping-robin` | Batman Slapping Robin | robin, batman | 扼杀坏主意 |

<a id="dynamic-templates-from-imgflip-api"></a>
### 动态模板（来自 imgflip API）

任何不在精选列表中的模板都可以通过名称或 imgflip ID 使用。这些模板会获得智能的默认文本位置（2 字段的为顶部/底部，3 字段及以上的均匀间距）。搜索命令：

```bash
python "$SKILL_DIR/scripts/generate_meme.py" --search "disaster"
```

<a id="procedure"></a>
## 操作步骤

<a id="mode-1-classic-template-default"></a>
### 模式 1：经典模板（默认）

1. 阅读用户的主题，识别核心动态（混乱、两难、偏好、讽刺等）
2. 选取最匹配的模板。使用“最佳用途”列，或通过 `--search` 搜索。
3. 为每个字段撰写简短的说明文字（每个字段最多 8-12 个单词，越短越好）。
4. 找到技能脚本目录：
   ```
   SKILL_DIR=$(dirname "$(find ~/.hermes/skills -path '*/meme-generation/SKILL.md' 2>/dev/null | head -1)")
   ```
5. 运行生成器：
   ```bash
   python "$SKILL_DIR/scripts/generate_meme.py" <template_id> /tmp/meme.png "caption 1" "caption 2" ...
   ```
6. 使用 `MEDIA:/tmp/meme.png` 返回图片。
<a id="mode-2-custom-ai-image-when-imagegenerate-is-available"></a>
### 模式 2：自定义 AI 图片（当 `image_generate` 可用时）

当没有合适的经典模板，或者用户想要原创内容时使用此模式。

1.  先写好文字。
2.  使用 `image_generate` 创建一个与梗图概念匹配的场景。**不要**在图片提示词中包含任何文字——文字将由脚本添加。只描述视觉场景。
3.  从 `image_generate` 的结果 URL 中找到生成的图片路径。如果需要，将其下载到本地路径。
4.  使用 `--image` 运行脚本以叠加文字，并选择一种模式：
    -   **叠加**（文字直接显示在图片上，白色带黑色轮廓）：
        ```bash
        python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png /tmp/meme.png "顶部文字" "底部文字"
        ```
    -   **黑条**（图片上方/下方有黑色条带，白色文字——更干净，始终可读）：
        ```bash
        python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png --bars /tmp/meme.png "顶部文字" "底部文字"
        ```
    当图片内容繁杂/细节丰富，文字直接叠加难以阅读时，使用 `--bars`。
5.  **使用视觉能力验证**（如果 `vision_analyze` 可用）：检查结果是否美观：
    ```
    vision_analyze(image_url="/tmp/meme.png", question="文字是否清晰易读且位置恰当？这个梗图在视觉上有效吗？")
    ```
    如果视觉模型指出问题（文字难以阅读、位置不佳等），请尝试另一种模式（在叠加和黑条之间切换）或重新生成场景。
6.  使用 `MEDIA:/tmp/meme.png` 返回图片。

<a id="examples"></a>
## 示例

**"凌晨两点调试生产环境"：**
```bash
python generate_meme.py this-is-fine /tmp/meme.png "服务器着火了" "没事，问题不大"
```

**"在睡觉和再看一集之间做选择"：**
```bash
python generate_meme.py drake /tmp/meme.png "睡够8小时" "凌晨3点再看一集"
```

**"周一早晨的几个阶段"：**
```bash
python generate_meme.py expanding-brain /tmp/meme.png "设一个闹钟" "设五个闹钟" "闹钟全睡过" "在床上办公"
```

<a id="listing-templates"></a>
## 列出模板

要查看所有可用模板：
```bash
python generate_meme.py --list
```

<a id="pitfalls"></a>
## 注意事项

-   文字要**简短**。长文字的梗图看起来很糟糕。
-   确保文字参数的数量与模板的字段数量匹配。
-   选择符合笑话结构的模板，而不仅仅是主题匹配。
-   不要生成仇恨、辱骂或针对个人的内容。
-   脚本在首次下载后会将模板图片缓存到 `scripts/.cache/` 目录。

<a id="verification"></a>
## 验证

满足以下条件则输出正确：
-   在输出路径创建了一个 `.png` 文件
-   模板上的文字清晰易读（白色带黑色轮廓）
-   笑话成立——文字与模板的预期结构匹配
-   文件可以通过 `MEDIA:` 路径交付
