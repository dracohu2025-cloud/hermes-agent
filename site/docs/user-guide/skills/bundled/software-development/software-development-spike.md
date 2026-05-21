---
title: "Spike — 在正式构建之前，用一次性实验验证想法"
sidebar_label: "Spike"
description: "在正式构建之前，用一次性实验验证想法"
---

{/* 此页面由 scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="spike"></a>
# Spike

在正式构建之前，用一次性实验验证想法。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/software-development/spike` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `spike`, `prototype`, `experiment`, `feasibility`, `throwaway`, `exploration`, `research`, `planning`, `mvp`, `proof-of-concept` |
| 相关技能 | [`sketch`](/user-guide/skills/bundled/creative/creative-sketch), [`writing-plans`](/user-guide/skills/bundled/software-development/software-development-writing-plans), [`subagent-driven-development`](/user-guide/skills/bundled/software-development/software-development-subagent-driven-development), [`plan`](/user-guide/skills/bundled/software-development/software-development-plan) |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是该技能触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Spike

当用户希望在正式投入构建之前**试探一个想法**时使用此技能——验证可行性、比较不同方案，或者揭示那些靠研究无法回答的未知问题。Spike 在设计上就是一次性的。一旦它们完成了使命，就可以丢弃。

当用户说出类似“让我试试这个”、“我想看看 X 是否可行”、“把这个 spike 一下”、“在我决定用 Y 之前”、“快速做一个 Z 的原型”、“这到底能不能行？”或“比较 A 和 B”等话语时，加载此技能。

<a id="when-not-to-use-this"></a>
## 何时不应使用

- 答案可以通过文档或阅读代码获知——只需做研究，不要构建
- 工作属于生产路径——改用 `writing-plans` / `plan`
- 想法已经验证过——直接进入实现

<a id="if-the-user-has-the-full-gsd-system-installed"></a>
## 如果用户安装了完整的 GSD 系统

如果 `gsd-spike` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），当用户希望使用完整的 GSD 工作流时，应优先选择 **`gsd-spike`**：持久化的 `.planning/spikes/` 状态、跨会话的 MANIFEST 追踪、Given/When/Then 结论格式，以及与 GSD 其他部分集成的提交模式。此技能是面向没有（或不想要）完整系统的用户的轻量独立版本。

<a id="core-method"></a>
## 核心方法

无论规模大小，每个 spike 都遵循此循环：

```
分解  →  研究  →  构建  →  结论
   ↑__________________________________________↓
                  根据发现迭代
```

<a id="1-decompose"></a>
### 1. 分解

将用户的想法拆解为 **2-5 个独立的可行性问题**。每个问题就是一个 spike。用表格呈现，并采用 Given/When/Then 框架：

| # | Spike | 验证内容（Given/When/Then） | 风险 |
|---|-------|----------------------------|------|
| 001 | websocket-streaming | 给定一个 WS 连接，当 LLM 流式输出 token 时，客户端接收到的每个 chunk 小于 100ms | 高 |
| 002a | pdf-parse-pdfjs | 给定一个多页 PDF，当使用 pdfjs 解析时，可以提取出结构化文本 | 中 |
| 002b | pdf-parse-camelot | 给定一个多页 PDF，当使用 camelot 解析时，可以提取出结构化文本 | 中 |
**技术调研类型：**
- **标准型** — 用单一方法回答一个问题
- **比较型** — 同一个问题，不同方法（共享编号，字母后缀 `a`/`b`/`c`）

**好的技术调研问题：** 具体的可行性，结果可观察。
**不好的技术调研问题：** 过于宽泛，没有可观察的输出，或者只是“阅读 X 的文档”。

**按风险排序。** 最有可能否定想法的技术调研应该最先进行。如果难题走不通，没必要先给容易的部分做原型。

**跳过分解** 只有当用户已经确切知道他们要调研什么并且明确说出来时才跳过。然后将他们的想法作为一个单一技术调研。

<a id="2-align-for-multi-spike-ideas"></a>
### 2. 对齐（针对多技术调研的想法）

展示技术调研表格。问：“按这个顺序全部构建，还是调整？” 让用户在你写任何代码之前，先删除、重新排序或重新框定。

<a id="3-research-per-spike-before-building"></a>
### 3. 调研（每个技术调研，在构建之前）

技术调研并非不做研究——你需要调研到足够选择正确方法，然后再构建。每个技术调研：

1. **简述。** 2-3 句话：这个技术调研是什么、为什么重要、关键风险。
2. **列出竞争方案**（如果有真正的选择）：

   | 方法 | 工具/库 | 优点 | 缺点 | 状态 |
   |----------|-------------|------|------|--------|
   | ... | ... | ... | ... | 维护中 / 已废弃 / Beta |

3. **选一个。** 说明原因。如果 2 个以上都可信，在技术调研内构建快速变体。
4. **跳过调研**（对于没有外部依赖的纯逻辑）。

调研步骤使用 Hermes 工具：

- `web_search("python websocket streaming libraries 2025")` — 查找候选方案
- `web_extract(urls=["https://websockets.readthedocs.io/..."])` — 阅读实际文档（返回 markdown）
- `terminal("pip show websockets | grep Version")` — 检查项目 venv 中已安装的版本

对于没有文档页面的库，通过 `read_file` 克隆并阅读其 `README.md` / `examples/`。Context7 MCP（如果用户已配置）也是很好的来源——`mcp_*_resolve-library-id` 然后 `mcp_*_query-docs`。

<a id="4-build"></a>
### 4. 构建

每个技术调研一个目录。保持独立。

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

**偏向于用户可以交互的方式。** 当技术调研的唯一输出是显示“它工作了”的日志行时，它就失败了。用户想*感受*技术调研的效果。默认选择，按偏好顺序：

1. 一个可运行的 CLI，接受输入并打印可观察输出
2. 一个演示行为的最小 HTML 页面
3. 一个只有一个端点的小型 Web 服务器
4. 一个单元测试，用可识别的断言来验证问题

**深度优先于速度。** 绝不要在跑通一次 happy-path 后就宣布“它工作了”。测试边界情况。跟随意外的发现。只有当调研是诚实的，结论才可信。

**避免**（除非技术调研特别需要）：复杂的包管理、构建工具/打包器、Docker、环境变量文件、配置系统。把所有东西硬编码——这只是个技术调研。
**构建一个 spike** — 典型的工具序列：

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python3 main.py")
# 观察输出，迭代。
```

**并行对比 spike（002a / 002b）— 委托。** 当两种方法可以并行运行，且都需要真正的工程实现（而非 10 行原型）时，使用 `delegate_task` 进行分发：

```
delegate_task(tasks=[
    {"goal": "构建 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "构建 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

每个子 Agent 返回自己的结论；你负责撰写最终对比。

<a id="5-verdict"></a>
### 5. 结论

每个 spike 的 `README.md` 以如下内容结尾：

```markdown
## 结论：VALIDATED | PARTIAL | INVALIDATED

### 有效部分
- ...

### 无效部分
- ...

### 意外发现
- ...

### 对正式构建的建议
- ...
```

**VALIDATED** = 核心问题得到了肯定回答，并有证据支持。
**PARTIAL** = 在 X、Y、Z 约束条件下可行——请记录这些条件。
**INVALIDATED** = 由于某个原因不可行。这仍然是一次成功的 spike。

<a id="comparison-spikes"></a>
## 对比 spike

当两种方法回答同一个问题（002a / 002b）时，**依次**构建它们，然后在最后进行直接对比：

```markdown
## 直接对比：pdfjs vs camelot

| 维度 | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| 提取质量 | 9/10 结构化 | 7/10 仅表格 |
| 搭建复杂度 | npm install，1 行 | pip + ghostscript |
| 100 页 PDF 性能 | 3 秒 | 18 秒 |
| 处理旋转文本 | 否 | 是 |

**胜出者：** 针对我们的用例是 pdfjs。如果后续需要以表格优先的提取，则选择 camelot。
```

<a id="frontier-mode-picking-what-to-spike-next"></a>
## 前沿模式（选择下一个要 spike 的内容）

如果 spike 已经存在，用户问“接下来我应该 spike 什么？”，请遍历现有目录并查找：

- **集成风险** — 两个已验证的 spike 涉及同一资源，但独立测试过
- **数据交接** — spike A 的输出被假定与 spike B 的输入兼容，但从未验证
- **愿景中的空白** — 假设具备但未验证的能力
- **替代方案** — 针对 PARTIAL 或 INVALIDATED spike 的不同角度

以 Given/When/Then 格式提出 2-4 个候选方案。让用户选择。

<a id="output"></a>
## 输出

- 在仓库根目录创建 `spikes/`（如果用户使用 GSD 约定，则创建 `.planning/spikes/`）
- 每个 spike 一个目录：`NNN-descriptive-name/`
- 每个 spike 的 `README.md` 包含问题、方法、结果、结论
- 代码保持一次性使用——一个需要花 2 天“清理以用于生产”的 spike 就是失败的 spike

<a id="attribution"></a>
## 归属

改编自 GSD（Get Shit Done）项目的 `/gsd-spike` 工作流 — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统提供持久化的 spike 状态、MANIFEST 跟踪，以及与更广泛的规范驱动开发管线的集成；使用 `npx get-shit-done-cc --hermes --global` 安装。
