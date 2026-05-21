---
title: "Design Md — 编写/验证/导出 Google 的 DESIGN"
sidebar_label: "Design Md"
description: "编写/验证/导出 Google 的 DESIGN"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从 skill 的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页。 */}

<a id="design-md"></a>
# Design Md

编写/验证/导出 Google 的 DESIGN.md 令牌规范文件。

<a id="skill-metadata"></a>
## Skill 元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative/design-md` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `design`, `design-system`, `tokens`, `ui`, `accessibility`, `wcag`, `tailwind`, `dtcg`, `google` |
| 相关技能 | [`popular-web-designs`](/user-guide/skills/bundled/creative/creative-popular-web-designs), [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是在触发此技能时 Hermes 加载的完整技能定义。这是技能激活后 Agent 看到作为指令的内容。
:::

<a id="design-md-skill"></a>
# DESIGN.md 技能

DESIGN.md 是 Google 的开放规范（Apache-2.0，`google-labs-code/design.md`），用于向编码 Agent 描述视觉标识。一个文件包含：

- **YAML 前置元数据** — 机器可读的设计令牌（规范值）
- **Markdown 正文** — 人类可读的设计理由，按规范章节组织

令牌提供精确的值。正文告诉 Agent *为什么* 存在这些值以及如何使用。CLI（`npx @google/design.md`）可检查结构 + WCAG 对比度、对比版本差异、以及导出到 Tailwind 或 W3C DTCG JSON。

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

- 用户要求提供 DESIGN.md 文件、设计令牌或设计系统规范
- 用户希望在多个项目或工具间保持一致的 UI/品牌
- 用户粘贴现有的 DESIGN.md 并要求 lint、diff、导出或扩展它
- 用户要求将样式指南转换为 Agent 可消费的格式
- 用户希望对其调色板进行对比度 / WCAG 无障碍验证

若只需纯视觉灵感或布局示例，请改用 `popular-web-designs`。若需从头设计一次性 HTML 制品（原型、幻灯片、落地页、组件实验室）的*流程和品味*，请使用 `claude-design`。此技能针对的是*正式规范文件本身*。

<a id="file-anatomy"></a>
## 文件结构

```md
---
version: alpha
name: Heritage
description: Architectural minimalism meets journalistic gravitas.
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
---

## 概述

建筑极简主义遇上新闻庄重感……

## 颜色

- **主色 (#1A1C1E)：** 标题和核心文本的深墨色。
- **辅色 (#B8422E)：** “波士顿陶土”——交互的唯一驱动。
- **强调色 (#6C7278)：** 次要文本和边框。
- **中性色 (#F7F5F2)：** 背景底色。

## 排版

除小型全大写标签外，所有内容均使用 Public Sans……

## 组件

`button-primary` 是页面上唯一的高强调度动作……
```
<a id="token-types"></a>
## Token 类型

| 类型 | 格式 | 示例 |
|------|------|------|
| 颜色 | `#` + 十六进制 (sRGB) | `"#1A1C1E"` |
| 尺寸 | 数字 + 单位 (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| Token 引用 | `{path.to.token}` | `{colors.primary}` |
| 排版 | 包含 `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` 的对象 | 见上方 |

组件属性白名单：`backgroundColor`, `textColor`, `typography`,
`rounded`, `padding`, `size`, `height`, `width`。变体（hover, active,
pressed）是**独立的组件条目**，使用关联键名（如 `button-primary-hover`），而不是嵌套。

<a id="canonical-section-order"></a>
## 标准章节顺序

章节是可选的，但出现的章节**必须**按此顺序排列。重复的标题会导致文件被拒绝。

1. 概述（别名：品牌与风格）
2. 颜色
3. 排版
4. 布局（别名：布局与间距）
5. 高度与深度（别名：高度）
6. 形状
7. 组件
8. 注意事项

未知章节会保留，不会报错。未知的 token 名称如果值类型有效，也会被接受。未知的组件属性会产生警告。

<a id="workflow-authoring-a-new-design-md"></a>
## 工作流程：编写新的 DESIGN.md

1. **询问用户**（或推断）品牌调性、强调色和排版方向。如果用户提供了网站、图片或氛围描述，将其转换为上述 token 形式。
2. 在项目根目录下使用 `write_file` **写入 `DESIGN.md`**。始终包含 `name:` 和 `colors:`；其他章节可选但鼓励添加。
3. 在 `components:` 章节中**使用 token 引用**（`{colors.primary}`），而不是重复输入十六进制值。这样可以保持调色板单一来源。
4. **检查它**（见下方）。在返回之前修复所有损坏的引用或 WCAG 失败。
5. **如果用户已有项目**，同时在其旁边写入 Tailwind 或 DTCG 导出文件（`tailwind.theme.json`, `tokens.json`）。

<a id="workflow-lint-diff-export"></a>
## 工作流程：检查 / 比较 / 导出

CLI 是 `@google/design.md`（Node）。使用 `npx`——无需全局安装。

```bash
# 验证结构 + token 引用 + WCAG 对比度
npx -y @google/design.md lint DESIGN.md

# 比较两个版本，回归时失败（exit 1 = 回归）
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md

# 导出为 Tailwind 主题 JSON
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# 导出为 W3C DTCG（设计 Token 格式模块）JSON
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json

# 打印规格本身——在注入到 Agent 提示时很有用
npx -y @google/design.md spec --rules-only --format json
```

所有命令接受 `-` 作为标准输入。`lint` 在出错时返回 exit 1。如果需要结构化地报告发现，使用 `--format json` 标志并解析输出。

<a id="lint-rule-reference-what-the-7-rules-catch"></a>
### 检查规则参考（7 条规则捕获的内容）

- `broken-ref`（错误）——`{colors.missing}` 指向不存在的 token
- `duplicate-section`（错误）——相同的 `## 标题` 出现两次
- `invalid-color`, `invalid-dimension`, `invalid-typography`（错误）
- `wcag-contrast`（警告/信息）——组件的 `textColor` 与 `backgroundColor` 对比度对 WCAG AA（4.5:1）和 AAA（7:1）的满足情况
- `unknown-component-property`（警告）——超出上述白名单的属性
当用户关注无障碍性时，请在总结中明确说明这一点——WCAG 相关的发现是使用 CLI 最有力的理由。

<a id="pitfalls"></a>
## 陷阱

- **不要嵌套组件变体。** `button-primary.hover` 是错误的写法；正确的做法是使用同级键 `button-primary-hover`。
- **十六进制颜色必须用引号括起来的字符串。** 否则 YAML 会因 `#` 而报错，或异常截断类似 `#1A1C1E` 的值。
- **负的尺寸值也需要用引号。** `letterSpacing: -0.02em` 会被解析为 YAML 流式语法——请写成 `letterSpacing: "-0.02em"`。
- **区块顺序是强制的。** 如果用户以随机顺序给出段落文字，在保存前请将其重新排序以匹配规范列表。
- **`version: alpha` 是当前规范版本**（截至 2026 年 4 月）。该规范标记为 alpha——请注意破坏性变更。
- **令牌引用通过点路径解析。** `{colors.primary}` 有效；`{primary}` 无效。

<a id="spec-source-of-truth"></a>
## 规范真实来源

- 仓库：https://github.com/google-labs-code/design.md (Apache-2.0)
- CLI：npm 上的 `@google/design.md`
- 生成的 DESIGN.md 文件的许可证：取决于用户项目所使用的许可证；规范本身采用 Apache-2.0。
