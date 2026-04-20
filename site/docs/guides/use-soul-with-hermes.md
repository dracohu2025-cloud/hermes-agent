---
sidebar_position: 7
title: "在 Hermes 中使用 SOUL.md"
description: "如何使用 SOUL.md 塑造 Hermes Agent 的默认语气，哪些内容属于该文件，以及它与 AGENTS.md 和 /personality 的区别"
---

# 在 Hermes 中使用 SOUL.md {#use-soul-md-with-hermes}

`SOUL.md` 是你的 Hermes 实例的**核心身份**。它是系统提示词（system prompt）中的第一项内容——它定义了 Agent 是谁、如何说话以及避讳什么。

如果你希望 Hermes 在每次对话时都表现得像同一个助手，或者你想用自己的设定完全替换 Hermes 的人格，那么就应该使用这个文件。

## SOUL.md 的用途 {#what-soul-md-is-for}

在 `SOUL.md` 中定义：
- 语气（tone）
- 性格（personality）
- 沟通风格
- Hermes 表现得直接还是温和
- Hermes 在风格上应该避免什么
- Hermes 如何处理不确定性、分歧和模糊性

简而言之：
- `SOUL.md` 关乎 Hermes 是谁以及 Hermes 如何说话

## SOUL.md 不适用的场景 {#what-soul-md-is-not-for}

不要将其用于：
- 特定仓库的代码规范
- 文件路径
- 命令
- 服务端口
- 架构说明
- 项目工作流指令

这些内容属于 `AGENTS.md`。

一个简单的原则：
- 如果它适用于所有地方，放在 `SOUL.md`
- 如果它只属于某个特定项目，放在 `AGENTS.md`

## 文件位置 {#where-it-lives}

Hermes 现在仅为当前实例使用全局 SOUL 文件：

```text
~/.hermes/SOUL.md
```

如果你使用自定义的主目录运行 Hermes，路径则为：

```text
$HERMES_HOME/SOUL.md
```

## 首次运行行为 {#first-run-behavior}

如果 `SOUL.md` 尚不存在，Hermes 会自动为你生成一个初始的 `SOUL.md`。

这意味着大多数用户在开始时就拥有一个可以立即阅读和编辑的真实文件。

重要提示：
- 如果你已经有了 `SOUL.md`，Hermes 不会覆盖它
- 如果文件存在但为空，Hermes 不会从中向提示词添加任何内容

## Hermes 如何使用它 {#how-hermes-uses-it}

当 Hermes 启动会话时，它会从 `HERMES_HOME` 读取 `SOUL.md`，扫描是否存在提示词注入（prompt-injection）模式，根据需要进行截断，并将其作为 **Agent 身份**（系统提示词的第 1 槽位）。这意味着 SOUL.md 会完全替换内置的默认身份文本。

如果 SOUL.md 缺失、为空或无法加载，Hermes 将回退到内置的默认身份。

文件内容不会被添加任何包装语言。内容本身至关重要——请按照你希望 Agent 思考和说话的方式来编写。

## 第一次修改建议 {#a-good-first-edit}

如果你不想做太多改动，只需打开文件并修改几行，让它感觉更像你。

例如：

```markdown
你表现得直接、冷静且技术严谨。
比起礼貌的客套，更看重实质内容。
当一个想法很糟糕时，请明确指出。
除非深层细节有用，否则保持回答简洁。
```

仅此一点就能显著改变 Hermes 给人的感觉。

## 风格示例 {#example-styles}

### 1. 务实的工程师 {#1-pragmatic-engineer}

```markdown
你是一位务实的高级工程师。
你更关心正确性和操作现实，而不是听起来很厉害。

## 风格
- 说话直接
- 除非复杂度需要深度，否则保持简洁
- 如果某个想法很烂，直接说出来
- 相比理想化的抽象，更倾向于实际的权衡

## 避免
- 谄媚
- 夸大其词的语言
- 过度解释显而易见的事情
```

### 2. 研究伙伴 {#2-research-partner}

```markdown
你是一位深思熟虑的研究合作者。
你充满好奇心，对不确定性保持诚实，并对不寻常的想法感到兴奋。

## 风格
- 探索各种可能性，不假装确定
- 区分推测与证据
- 当想法空间定义不足时，提出澄清性问题
- 相比浅显的完整性，更倾向于概念的深度
```

### 3. 老师 / 讲解者 {#3-teacher-explainer}

```markdown
你是一位耐心的技术教师。
你关心的是理解，而不是表现。

## 风格
- 讲解清晰
- 在有帮助时使用例子
- 除非用户有所表示，否则不要预设对方已有相关知识
- 从直觉出发构建到细节
```

### 4. 严厉的评审者 {#4-tough-reviewer}

```markdown
你是一位严谨的评审者。
你很公正，但不会软化重要的批评。

## 风格
- 直接指出薄弱的假设
- 相比和谐，优先考虑正确性
- 明确说明风险和权衡
- 相比模糊的外交辞令，更倾向于直率的清晰
```

## 什么是一个强大的 SOUL.md？ {#what-makes-a-strong-soul-md}

强大的 `SOUL.md` 具备以下特点：
- 稳定
- 广泛适用
- 语气具体
- 不堆砌临时指令

弱小的 `SOUL.md` 则是：
- 充斥着项目细节
- 自相矛盾
- 试图微观管理每一个回复的形状
- 大多是像“要乐于助人”和“要清晰”之类的通用废话

Hermes 已经尝试做到乐于助人和清晰了。`SOUL.md` 应该增加真实的性格和风格，而不是重申显而易见的默认设置。

## 建议结构 {#suggested-structure}

你不需要标题，但标题会有所帮助。

一个效果良好的简单结构：

```markdown
# 身份 (Identity)
Hermes 是谁。

# 风格 (Style)
Hermes 听起来应该是什么样的。

# 避免 (Avoid)
Hermes 不应该做什么。

# 默认行为 (Defaults)
当出现模糊情况时，Hermes 应该如何表现。
```

## SOUL.md vs /personality {#soul-md-vs-personality}

这两者是互补的。

使用 `SOUL.md` 作为你持久的基准。
使用 `/personality` 进行临时的模式切换。

示例：
- 你的默认 SOUL 是务实且直接的
- 然后在某个会话中，你使用 `/personality teacher`
- 稍后你切换回来，而无需更改你的基础性格文件

## SOUL.md vs AGENTS.md {#soul-md-vs-agents-md}

这是最常见的错误。

### 放入 SOUL.md 的内容 {#put-this-in-soul-md}
- “说话直接。”
- “避免夸大其词。”
- “除非深度有帮助，否则倾向于简短回答。”
- “当用户错误时予以反驳。”

### 放入 AGENTS.md 的内容 {#put-this-in-agents-md}
- “使用 pytest，不要用 unittest。”
- “前端代码位于 `frontend/` 目录下。”
- “永远不要直接编辑 migration 文件。”
- “API 运行在 8000 端口。”

## 如何编辑 {#how-to-edit-it}

```bash
nano ~/.hermes/SOUL.md
```

或者

```bash
vim ~/.hermes/SOUL.md
```

然后重启 Hermes 或开始新会话。

## 实践工作流 {#a-practical-workflow}

1. 从生成的默认文件开始
2. 删掉任何感觉不符合你想要语气的内内容
3. 添加 4–8 行明确定义语气和默认行为的内容
4. 与 Hermes 聊一会儿
5. 根据仍然感觉不对劲的地方进行调整

这种迭代方法比尝试一次性设计出完美的人格效果更好。

## 故障排除 {#troubleshooting}

### 我编辑了 SOUL.md 但 Hermes 听起来还是老样子 {#i-edited-soul-md-but-hermes-still-sounds-the-same}

检查：
- 你编辑的是 `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md`
- 而不是某个仓库本地的 `SOUL.md`
- 文件不是空的
- 编辑后重启了会话
- 没有 `/personality` 覆盖层在主导结果

### Hermes 忽略了我 SOUL.md 的部分内容 {#hermes-is-ignoring-parts-of-my-soul-md}

可能的原因：
- 更高优先级的指令覆盖了它
- 文件中包含相互矛盾的指导
- 文件太长被截断了
- 部分文本类似于提示词注入内容，可能被扫描器拦截或修改

### 我的 SOUL.md 变得太针对特定项目了 {#my-soul-md-became-too-project-specific}

将项目指令移至 `AGENTS.md`，保持 `SOUL.md` 专注于身份和风格。

## 相关文档 {#related-docs}

- [性格与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)
- [配置](/user-guide/configuration)
- [提示与最佳实践](/guides/tips)
