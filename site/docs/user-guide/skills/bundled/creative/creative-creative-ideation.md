---
title: "创意构思 — 通过创意约束生成项目点子"
sidebar_label: "创意构思"
description: "通过创意约束生成项目点子"
---

{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="ideation"></a>
# 创意构思

通过创意约束生成项目点子。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| Source | 捆绑（默认安装） |
| Path | `skills/creative/creative-ideation` |
| Version | `1.0.0` |
| Author | SHL0MS |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `Creative`, `Ideation`, `Projects`, `Brainstorming`, `Inspiration` |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。技能激活后，Agent 将以此为指令。
:::

<a id="creative-ideation"></a>
# 创意构思

<a id="when-to-use"></a>
## 使用时机

当用户说“我想做个东西”、“给我个项目点子”、“我好无聊”、“我该做什么”、“给我点灵感”，或任何类似“我有工具但没方向”的表达时使用。适用于代码、艺术、硬件、写作、工具以及任何可制作的东西。

通过创意约束生成项目点子。约束 + 方向 = 创造力。

<a id="how-it-works"></a>
## 工作原理

1. **从下方约束库中选取一个约束**——随机选取，或与用户的领域/心情相匹配
2. **宽泛地解释它**——一个编码提示可以变成硬件项目，一个艺术提示可以变成 CLI 工具
3. **生成 3 个具体的项目点子**，满足该约束
4. **如果用户选中一个，就把它做出来**——创建项目、编写代码、发布它

<a id="the-rule"></a>
## 规则

每个提示都要尽可能宽泛地解释。“这包括 X 吗？”→ 是的。提示提供方向和适度约束。如果没有这两者，就没有创造力。

<a id="constraint-library"></a>
## 约束库

<a id="for-developers"></a>
### 面向开发者

**解决你自己的痛点：**
构建你这周希望存在的工具。少于 50 行。今天就发布它。

**把烦人的事自动化：**
你的工作流中最乏味的部分是什么？用脚本解决它。花两小时解决一个每天耗费你五分钟的问题。

**本应存在的 CLI 工具：**
想一个你希望可以输入的命令。`git undo-that-thing-i-just-did`。`docker why-is-this-broken`。`npm explain-yourself`。现在把它做出来。

**只需胶水，别无新意：**
完全使用现有的 API、库和数据集来制作东西。唯一的原创贡献是你如何将它们连接起来。

**弗兰肯斯坦周：**
拿一个做 X 的东西，让它做 Y。一个播放音乐的 git 仓库。一个生成诗歌的 Dockerfile。一个发送赞美消息的 cron 任务。

**减法：**
在代码库崩溃之前，你能移除多少内容？将一个工具剥离到最小可行功能。不断删除，直到只剩下精髓。

**高概念，低投入：**
一个深刻的想法，懒散地执行。概念要出色，实现只需一个下午。如果花更长时间，说明你想得太复杂了。

<a id="for-makers-artists"></a>
### 面向制作者与艺术家

**明目张胆地复制某个东西：**
挑选一个你欣赏的东西——工具、艺术作品、界面。从零开始重现它。学习就存在于你的版本和他们的版本之间的差距之中。
**One million of something:**
一百万既多也不多。一百万像素就是一张1MB的照片；一百万次API调用只是一个周二的量。任何东西一旦达到百万级别，规模带来的趣味就出现了。

**Make something that dies:**
一个每天少一个功能的网站；一个会遗忘的聊天机器人；一个倒计时到零的页面。一次关于腐朽、消亡或放手的练习。

**Do a lot of math:**
生成式几何、shader golf、数学艺术、计算折纸。是时候重新学习一下反正弦是什么了。

<a id="for-anyone"></a>
### 面向任何人

**Text is the universal interface:**
构建一个文本是唯一交互方式的东西。没有按钮，没有图形，只有文字输入和文字输出。文本几乎可以进出所有事物。

**Start at the punchline:**
想一句好笑的句子。然后反向推导，把它做成真实的东西。“我教会了我的温控器来PUA我”——然后把它搭建出来。

**Hostile UI:**
故意让某样东西用起来很痛苦。一个需要满足47个条件的密码输入框；所有标签都在说谎的表单；会评判你命令的CLI。

**Take two:**
回想一个旧项目。从头再做一遍，不要看原版。看看你思考方式发生了什么变化。

参见 `references/full-prompt-library.md`，获取横跨沟通、规模、哲学、转型等领域的30余个额外约束。

<a id="matching-constraints-to-users"></a>
## 按用户匹配约束条件

| 用户说 | 从中挑选 |
|--------|----------|
| “我想做点什么”（没有方向） | 随机——任意约束 |
| “我在学 [语言]” | 直接模仿某个东西，自动化烦人的事 |
| “我想要点奇怪的东西” | 敌意UI，弗兰肯斯坦周，从笑点开始 |
| “我想要点有用的东西” | 解决自己的痒点，本应存在的CLI，自动化烦人的事 |
| “我想要点漂亮的东西” | 做大量数学，一百万级别的东西 |
| “我累了” | 高概念低投入，做个会消亡的东西 |
| “周末项目” | 除了胶水没有新东西，从笑点开始 |
| “我想要挑战” | 一百万级别的东西，减法，重做一次 |

<a id="output-format"></a>
## 输出格式

```
## Constraint: [Name]
> [The constraint, one sentence]

### Ideas

1. **[One-line pitch]**
   [2-3 sentences: what you'd build and why it's interesting]
   ⏱ [weekend / week / month] • 🔧 [stack]

2. **[One-line pitch]**
   [2-3 sentences]
   ⏱ ... • 🔧 ...

3. **[One-line pitch]**
   [2-3 sentences]
   ⏱ ... • 🔧 ...
```

<a id="example"></a>
## 示例

```
## Constraint: The CLI tool that should exist
> Think of a command you've wished you could type. Now build it.

### Ideas

1. **`git whatsup` — show what happened while you were away**
   Compares your last active commit to HEAD and summarizes what changed,
   who committed, and what PRs merged. Like a morning standup from your repo.
   ⏱ weekend • 🔧 Python, GitPython, click

2. **`explain 503` — HTTP status codes for humans**
   Pipe any status code or error message and get a plain-English explanation
   with common causes and fixes. Pulls from a curated database, not an LLM.
   ⏱ weekend • 🔧 Rust or Go, static dataset

3. **`deps why &lt;package&gt;` — why is this in my dependency tree**
   Traces a transitive dependency back to the direct dependency that pulled
   it in. Answers "why do I have 47 copies of lodash" in one command.
   ⏱ weekend • 🔧 Node.js, npm/yarn lockfile parsing
```
用户选择一项后，开始构建——创建项目、编写代码、迭代。

<a id="attribution"></a>
## 参考致谢

约束方法灵感来源于 [wttdotm.com/prompts.html](https://wttdotm.com/prompts.html)。针对软件开发与通用创意思维进行了改编和扩展。
