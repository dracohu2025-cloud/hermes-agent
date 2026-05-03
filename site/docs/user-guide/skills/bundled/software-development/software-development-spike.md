---
title: "Spike — 在正式构建前通过一次性实验验证想法"
sidebar_label: "Spike"
description: "在正式构建前通过一次性实验验证想法"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Spike {#spike}

在正式构建前通过一次性实验验证想法。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/spike` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可证 | MIT |
| 标签 | `spike`, `prototype`, `experiment`, `feasibility`, `throwaway`, `exploration`, `research`, `planning`, `mvp`, `proof-of-concept` |
| 相关技能 | [`sketch`](/user-guide/skills/bundled/creative/creative-sketch), [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`plan`](/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="spike"></a>
# Spike

当用户希望在真正投入构建之前**试探一个想法**时使用此技能——验证可行性、比较不同方案，或揭示那些仅靠研究无法回答的未知因素。Spike 本质上是可丢弃的。一旦它们完成了使命，就可以扔掉。

当用户说出类似“让我试试这个”、“我想看看 X 是否可行”、“把这个 spike 出来”、“在我投入 Y 之前”、“快速原型 Z”、“这到底可不可能？”或“比较 A 和 B”时，加载此技能。

## 何时不应使用此技能 {#when-not-to-use-this}

- 答案可以从文档或阅读代码中得知——只需做研究，不要构建
- 工作是生产路径——改用 `writing-plans` / `plan`
- 想法已经过验证——直接跳到实现

## 如果用户安装了完整的 GSD 系统 {#if-the-user-has-the-full-gsd-system-installed}

如果 `gsd-spike` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），当用户需要完整的 GSD 工作流时，优先使用 **`gsd-spike`**：持久化的 `.planning/spikes/` 状态、跨会话的 MANIFEST 追踪、Given/When/Then 判定格式，以及与 GSD 其他部分集成的提交模式。本技能是面向没有（或不想要）完整系统的用户的轻量级独立版本。

## 核心方法 {#core-method}

无论规模大小，每个 spike 都遵循以下循环：

```
分解  →  研究  →  构建  →  判定
   ↑__________________________________________↓
                  根据发现迭代
```

### 1. 分解 {#1-decompose}

将用户的想法拆解为 **2-5 个独立的可行性问题**。每个问题就是一个 spike。以表格形式呈现，使用 Given/When/Then 框架：

| # | Spike | 验证内容 (Given/When/Then) | 风险 |
|---|-------|----------------------------|------|
| 001 | websocket-streaming | 给定一个 WS 连接，当 LLM 流式输出 token 时，客户端接收到的数据块延迟 &lt; 100ms | 高 |
| 002a | pdf-parse-pdfjs | 给定一个多页 PDF，当使用 pdfjs 解析时，可提取出结构化文本 | 中 |
| 002b | pdf-parse-camelot | 给定一个多页 PDF，当使用 camelot 解析时，可提取出结构化文本 | 中 |
**Spike 类型：**
- **standard** — 一种方法回答一个问题
- **comparison** — 同一个问题，不同方法（共享编号，字母后缀 `a`/`b`/`c`）

**好的 spike 问题：** 具有可观察输出的具体可行性。
**不好的 spike 问题：** 过于宽泛，没有可观察输出，或者只是“阅读关于 X 的文档”。

**按风险排序。** 最有可能推翻想法的 spike 先执行。如果困难部分行不通，那么为简单部分做原型就没有意义。

**跳过分解** 仅当用户已经确切知道他们想要 spike 什么并明确说明时。然后将他们的想法作为一个单独的 spike 来处理。

### 2. 对齐（针对多 spike 想法） {#2-align-for-multi-spike-ideas}

展示 spike 表格。询问：“按此顺序全部构建，还是需要调整？” 在你编写任何代码之前，让用户删除、重新排序或重新定义。

### 3. 调研（每个 spike，在构建之前） {#3-research-per-spike-before-building}

Spike 并非无需调研——你需要调研足够的信息以选择正确的方法，然后再构建。每个 spike：

1. **简要说明。** 2-3 句话：这个 spike 是什么，为什么重要，关键风险。
2. **列出竞争方法** 如果确实存在选择：

   | 方法 | 工具/库 | 优点 | 缺点 | 状态 |
   |----------|-------------|------|------|--------|
   | ... | ... | ... | ... | 维护中 / 已废弃 / 测试版 |

3. **选择一个。** 说明原因。如果有 2 个或以上方法可信，则在 spike 内构建快速变体。
4. **跳过调研** 对于没有外部依赖的纯逻辑。

使用 Hermes 工具进行调研步骤：

- `web_search("python websocket streaming libraries 2025")` — 查找候选
- `web_extract(urls=["https://websockets.readthedocs.io/..."])` — 阅读实际文档（返回 markdown）
- `terminal("pip show websockets | grep Version")` — 检查项目虚拟环境中已安装的内容

对于没有文档页面的库，通过 `read_file` 克隆并阅读其 `README.md` / `examples/`。Context7 MCP（如果用户已配置）也是一个很好的来源 — `mcp_*_resolve-library-id` 然后 `mcp_*_query-docs`。

### 4. 构建 {#4-build}

每个 spike 一个目录。保持独立。

<!-- ascii-guard-ignore -->
```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
├── 002a-pdf-parse-pdfjs/
│   ├── README.md
│   └── parse.js
└── 002b-pdf-parse-camelot/
    ├── README.md
    └── parse.py
```
<!-- ascii-guard-ignore-end -->

**倾向于用户能够与之交互的东西。** 当唯一的输出是一行写着“它工作了”的日志时，spike 就失败了。用户想要 *感受* spike 在运行。默认选择，按偏好顺序：

1. 一个可运行的 CLI，接受输入并打印可观察输出
2. 一个演示行为的最小 HTML 页面
3. 一个带有一个端点的小型 Web 服务器
4. 一个使用可识别断言来测试问题的单元测试

**深度优先于速度。** 永远不要在运行一次快乐路径后就宣布“它工作了”。测试边缘情况。跟进令人惊讶的发现。只有当调查是诚实的时，结论才可信。

**避免** 除非 spike 特别需要：复杂的包管理、构建工具/打包器、Docker、环境文件、配置系统。将所有内容硬编码——这只是一个 spike。
**构建一个 spike** — 典型的工具序列：

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python3 main.py")
# 观察输出，迭代。
```

**并行比较 spike（002a / 002b）— 委托。** 当两种方法可以并行运行，且都需要真正的工程（而非 10 行原型）时，使用 `delegate_task` 进行分发：

```
delegate_task(tasks=[
    {"goal": "构建 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "构建 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

每个子 Agent 返回自己的结论；由你撰写对比结果。

### 5. 结论 {#5-verdict}

每个 spike 的 `README.md` 以如下内容结尾：

```markdown
## 结论：VALIDATED | PARTIAL | INVALIDATED

### 有效部分
- ...

### 无效部分
- ...

### 意外发现
- ...

### 对实际构建的建议
- ...
```

**VALIDATED** = 核心问题得到了肯定的回答，并有证据支持。
**PARTIAL** = 在约束条件 X、Y、Z 下可行——请记录这些条件。
**INVALIDATED** = 由于某个原因不可行。这仍然是一次成功的 spike。

## 比较 spike {#comparison-spikes}

当两种方法回答同一个问题（002a / 002b）时，**背靠背**构建它们，然后在最后进行直接对比：

```markdown
## 直接对比：pdfjs vs camelot

| 维度 | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| 提取质量 | 9/10 结构化 | 7/10 仅表格 |
| 搭建复杂度 | npm install，1 行 | pip + ghostscript |
| 100 页 PDF 性能 | 3 秒 | 18 秒 |
| 处理旋转文本 | 否 | 是 |

**胜出者：** 针对我们的用例，pdfjs 胜出。如果后续需要以表格优先的提取，则选择 camelot。
```

## 前沿模式（选择下一个要 spike 的内容） {#frontier-mode-picking-what-to-spike-next}

如果 spike 已经存在，用户问“接下来应该 spike 什么？”，请遍历现有目录，寻找：

- **集成风险** — 两个已验证的 spike 触及同一资源，但独立测试过
- **数据交接** — spike A 的输出被假定与 spike B 的输入兼容，但从未验证
- **愿景中的空白** — 假设但未验证的能力
- **替代方法** — 针对 PARTIAL 或 INVALIDATED spike 的不同角度

以 Given/When/Then 的形式提出 2-4 个候选方案。让用户选择。

## 输出 {#output}

- 在仓库根目录创建 `spikes/`（如果用户使用 GSD 约定，则创建 `.planning/spikes/`）
- 每个 spike 一个目录：`NNN-descriptive-name/`
- 每个 spike 的 `README.md` 包含问题、方法、结果、结论
- 代码保持一次性使用——一个需要花 2 天“清理以用于生产”的 spike 就是糟糕的 spike

## 归属 {#attribution}

改编自 GSD（Get Shit Done）项目的 `/gsd-spike` 工作流 — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统提供持久化的 spike 状态、MANIFEST 跟踪以及与更广泛的规范驱动开发管线的集成；使用 `npx get-shit-done-cc --hermes --global` 安装。
