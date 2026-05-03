---
title: "Meme Generation — 通过选择模板并使用 Pillow 叠加文本来生成真实的梗图"
sidebar_label: "Meme Generation"
description: "通过选择模板并使用 Pillow 叠加文本来生成真实的梗图"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Meme Generation {#meme-generation}

通过选择模板并使用 Pillow 叠加文本来生成真实的梗图。生成实际的 .png 格式梗图文件。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/meme-generation` 安装 |
| 路径 | `optional-skills/creative/meme-generation` |
| 版本 | `2.0.0` |
| 作者 | adanaleycio |
| 许可证 | MIT |
| 标签 | `creative`, `memes`, `humor`, `images` |
| 相关技能 | [`ascii-art`](/user-guide/skills/bundled/creative/creative-ascii-art), `generative-widgets` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="meme-generation"></a>
# Meme Generation

根据主题生成实际的梗图。选择模板、编写字幕，并渲染出带有文字叠加的真实 .png 文件。

## 何时使用 {#when-to-use}

- 用户要求你制作或生成一个梗图
- 用户想要一个关于特定主题、情境或槽点的梗图
- 用户说“把这个做成梗图”或类似的话

## 可用模板 {#available-templates}

该脚本支持**约 100 个流行的 imgflip 模板**（按名称或 ID），外加 10 个经过手动调整文字位置的精选模板。

### 精选模板（自定义文字位置） {#curated-templates-custom-text-placement}

| ID | 名称 | 字段 | 最佳用途 |
|----|------|--------|----------|
| `this-is-fine` | This is Fine | top, bottom | 混乱、否认 |
| `drake` | Drake Hotline Bling | reject, approve | 拒绝/偏好 |
| `distracted-boyfriend` | Distracted Boyfriend | distraction, current, person | 诱惑、优先级变化 |
| `two-buttons` | Two Buttons | left, right, person | 两难选择 |
| `expanding-brain` | Expanding Brain | 4 levels | 升级的讽刺 |
| `change-my-mind` | Change My Mind | statement | 争议观点 |
| `woman-yelling-at-cat` | Woman Yelling at Cat | woman, cat | 争论 |
| `one-does-not-simply` | One Does Not Simply | top, bottom | 看似简单实则困难的事 |
| `grus-plan` | Gru's Plan | step1-3, realization | 适得其反的计划 |
| `batman-slapping-robin` | Batman Slapping Robin | robin, batman | 否决糟糕的想法 |

### 动态模板（来自 imgflip API） {#dynamic-templates-from-imgflip-api}

任何不在精选列表中的模板都可以通过名称或 imgflip ID 使用。这些模板会获得智能的默认文字位置（2 字段为顶部/底部，3 个以上字段均匀分布）。使用以下命令搜索：
```bash
python "$SKILL_DIR/scripts/generate_meme.py" --search "disaster"
```

## 操作步骤 {#procedure}

### 模式 1：经典模板（默认） {#mode-1-classic-template-default}

1. 理解用户的主题，识别核心动态（混乱、两难、偏好、讽刺等）
2. 选择最匹配的模板。使用“最佳用途”列，或使用 `--search` 搜索。
3. 为每个字段编写简短的字幕（每个字段最多 8-12 个词，越短越好）。
4. 找到技能的脚本目录：
   ```
   SKILL_DIR=$(dirname "$(find ~/.hermes/skills -path '*/meme-generation/SKILL.md' 2>/dev/null | head -1)")
   ```
5. 运行生成器：
   ```bash
   python "$SKILL_DIR/scripts/generate_meme.py" <template_id> /tmp/meme.png "caption 1" "caption 2" ...
   ```
6. 使用 `MEDIA:/tmp/meme.png` 返回图片
### 模式 2：自定义 AI 图片（当 `image_generate` 可用时） {#mode-2-custom-ai-image-when-imagegenerate-is-available}

当没有合适的经典模板，或者用户想要原创内容时使用此模式。

1.  先写好文字（caption）。
2.  使用 `image_generate` 创建一个与梗图概念匹配的场景。**不要**在图片提示词中包含任何文字——文字将由脚本添加。只描述视觉场景。
3.  从 `image_generate` 的结果 URL 中找到生成的图片路径。如果需要，将其下载到本地路径。
4.  使用 `--image` 运行脚本以叠加文字，选择一种模式：
    -   **叠加**（文字直接显示在图片上，白色带黑色轮廓）：
        ```bash
        python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png /tmp/meme.png "顶部文字" "底部文字"
        ```
    -   **黑条**（上下黑条配白色文字——更干净，始终可读）：
        ```bash
        python "$SKILL_DIR/scripts/generate_meme.py" --image /path/to/scene.png --bars /tmp/meme.png "顶部文字" "底部文字"
        ```
    当图片内容繁杂/细节丰富，文字直接叠加难以阅读时，使用 `--bars`。
5.  **使用视觉能力验证**（如果 `vision_analyze` 可用）：检查结果是否美观：
    ```
    vision_analyze(image_url="/tmp/meme.png", question="文字是否清晰易读且位置恰当？这个梗图在视觉上有效吗？")
    ```
    如果视觉模型指出问题（文字难以阅读、位置不佳等），尝试另一种模式（在叠加和黑条之间切换）或重新生成场景。
6.  使用 `MEDIA:/tmp/meme.png` 返回图片。

## 示例 {#examples}

**"凌晨两点调试生产环境"：**
```bash
python generate_meme.py this-is-fine /tmp/meme.png "服务器着火了" "没事的"
```

**"在睡觉和再看一集之间做选择"：**
```bash
python generate_meme.py drake /tmp/meme.png "睡够8小时" "凌晨3点再看一集"
```

**"周一早晨的几个阶段"：**
```bash
python generate_meme.py expanding-brain /tmp/meme.png "设一个闹钟" "设5个闹钟" "睡过所有闹钟" "在床上工作"
```

## 列出模板 {#listing-templates}

要查看所有可用模板：
```bash
python generate_meme.py --list
```

## 常见陷阱 {#pitfalls}

-   保持文字简短。长文字的梗图看起来很糟糕。
-   确保文字参数的数量与模板的字段数量匹配。
-   选择符合笑话结构的模板，而不仅仅是主题匹配。
-   不要生成仇恨、辱骂或针对个人的内容。
-   脚本在首次下载后会将模板图片缓存到 `scripts/.cache/` 目录。

## 验证 {#verification}

如果满足以下条件，则输出正确：
-   在输出路径创建了一个 `.png` 文件
-   文字在模板上清晰易读（白色带黑色轮廓）
-   笑话成立——文字与模板的预期结构匹配
-   文件可以通过 `MEDIA:` 路径交付
