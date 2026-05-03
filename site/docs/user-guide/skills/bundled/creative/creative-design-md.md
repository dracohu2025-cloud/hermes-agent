---
title: "Design Md — 编写/验证/导出 Google 的 DESIGN"
sidebar_label: "Design Md"
description: "编写/验证/导出 Google 的 DESIGN"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Design Md {#design-md}

编写/验证/导出 Google 的 DESIGN.md 令牌规范文件。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/design-md` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 标签 | `design`, `design-system`, `tokens`, `ui`, `accessibility`, `wcag`, `tailwind`, `dtcg`, `google` |
| 相关技能 | [`popular-web-designs`](/user-guide/skills/bundled/creative/creative-popular-web-designs), [`claude-design`](/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/user-guide/skills/bundled/creative/creative-architecture-diagram) |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# DESIGN.md 技能 {#design-md-skill}

DESIGN.md 是 Google 的开放规范（Apache-2.0，`google-labs-code/design.md`），用于向编码 Agent 描述视觉标识。一个文件结合了：

- **YAML 前置元数据** — 机器可读的设计令牌（规范值）
- **Markdown 正文** — 人类可读的设计理由，按规范章节组织

令牌提供精确值。散文告诉 Agent *为什么* 这些值存在以及如何应用它们。CLI（`npx @google/design.md`）检查结构 + WCAG 对比度，比较版本间的回归问题，并导出为 Tailwind 或 W3C DTCG JSON。

## 何时使用此技能 {#when-to-use-this-skill}

- 用户要求提供 DESIGN.md 文件、设计令牌或设计系统规范
- 用户希望在多个项目或工具之间保持一致的 UI/品牌
- 用户粘贴现有的 DESIGN.md 并要求检查、比较差异、导出或扩展它
- 用户要求将样式指南移植为 Agent 可消费的格式
- 用户希望对其调色板进行对比度 / WCAG 无障碍验证

如果只是需要纯粹的视觉灵感或布局示例，请改用 `popular-web-designs`。如果是从头设计一次性 HTML 制品（原型、演示文稿、落地页、组件实验室）时的 *流程和品味*，请使用 `claude-design`。此技能针对的是 *正式的规范文件本身*。

## 文件结构 {#file-anatomy}

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

## Overview

Architectural Minimalism meets Journalistic Gravitas...

## Colors

- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Tertiary (#B8422E):** "Boston Clay" — the sole driver for interaction.

## Typography

Public Sans for everything except small all-caps labels...

## Components

`button-primary` is the only high-emphasis action on a page...
```
## Token 类型 {#token-types}

| 类型 | 格式 | 示例 |
|------|------|------|
| 颜色 | `#` + 十六进制 (sRGB) | `"#1A1C1E"` |
| 尺寸 | 数字 + 单位 (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| Token 引用 | `{path.to.token}` | `{colors.primary}` |
| 排版 | 包含 `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` 的对象 | 见上方 |

组件属性白名单：`backgroundColor`, `textColor`, `typography`,
`rounded`, `padding`, `size`, `height`, `width`。变体（hover、active、
pressed）是**独立的组件条目**，使用相关的键名
（`button-primary-hover`），而非嵌套。

## 规范章节顺序 {#canonical-section-order}

章节是可选的，但已存在的章节必须按此顺序出现。重复的
标题会导致文件被拒绝。

1. 概述（别名：品牌与风格）
2. 颜色
3. 排版
4. 布局（别名：布局与间距）
5. 层级与深度（别名：层级）
6. 形状
7. 组件
8. 注意事项

未知章节会被保留，不会报错。未知的 token 名称如果值类型有效则会被接受。未知的组件属性会产生警告。

## 工作流：编写新的 DESIGN.md {#workflow-authoring-a-new-design-md}

1. **询问用户**（或推断）品牌调性、强调色和排版方向。如果他们提供了网站、图片或氛围，将其转换为上述 token 形状。
2. **在项目根目录下**使用 `write_file` 编写 `DESIGN.md`。始终包含 `name:` 和 `colors:`；其他章节可选但鼓励添加。
3. **在 `components:` 部分使用 token 引用**（`{colors.primary}`），而不是重新输入十六进制值。这样保持调色板单一来源。
4. **检查它**（见下文）。在返回之前修复任何损坏的引用或 WCAG 失败。
5. **如果用户已有项目**，还要在文件旁边编写 Tailwind 或 DTCG 导出文件（`tailwind.theme.json`, `tokens.json`）。

## 工作流：lint / diff / 导出 {#workflow-lint-diff-export}

CLI 是 `@google/design.md`（Node）。使用 `npx` — 无需全局安装。

```bash
# 验证结构 + token 引用 + WCAG 对比度
npx -y @google/design.md lint DESIGN.md

# 比较两个版本，回归时失败（exit 1 = 回归）
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md

# 导出为 Tailwind 主题 JSON
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# 导出为 W3C DTCG（设计 Token 格式模块）JSON
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json

# 打印规范本身 — 在注入到 Agent 提示时很有用
npx -y @google/design.md spec --rules-only --format json
```

所有命令都接受 `-` 作为标准输入。`lint` 在出错时返回 exit 1。如果需要以结构化方式报告发现，请使用 `--format json` 标志并解析输出。

### Lint 规则参考（7 条规则捕获的内容） {#lint-rule-reference-what-the-7-rules-catch}

- `broken-ref`（错误）— `{colors.missing}` 指向不存在的 token
- `duplicate-section`（错误）— 同一个 `## Heading` 出现两次
- `invalid-color`, `invalid-dimension`, `invalid-typography`（错误）
- `wcag-contrast`（警告/信息）— 组件 `textColor` 与 `backgroundColor` 的比率，对照 WCAG AA（4.5:1）和 AAA（7:1）
- `unknown-component-property`（警告）— 超出上述白名单
当用户关注无障碍访问时，请在你的摘要中明确说明——WCAG 相关发现是使用 CLI 的最具分量的理由。

## 注意事项 {#pitfalls}

- **不要嵌套组件变体。** `button-primary.hover` 是错误的；正确的做法是将 `button-primary-hover` 作为同级键。
- **十六进制颜色必须用引号括起来的字符串。** 否则 YAML 会被 `#` 卡住，或异常截断类似 `#1A1C1E` 的值。
- **负维度值也需要引号。** `letterSpacing: -0.02em` 会解析为 YAML 流——请写成 `letterSpacing: "-0.02em"`。
- **区块顺序是强制的。** 如果用户提供的文本顺序是杂乱的，保存前请将其重新排序，使之匹配标准列表。
- **`version: alpha` 是当前规范版本**（截至 2026 年 4 月）。该规范标记为 alpha——请注意破坏性变更。
- **令牌引用通过点分隔路径解析。** `{colors.primary}` 有效；`{primary}` 无效。

## 规范权威来源 {#spec-source-of-truth}

- 仓库：https://github.com/google-labs-code/design.md（Apache-2.0）
- CLI：npm 上的 `@google/design.md`
- 生成的 DESIGN.md 文件许可：由用户项目决定；规范本身是 Apache-2.0。
