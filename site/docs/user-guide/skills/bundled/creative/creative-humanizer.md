---
title: "Humanizer — 人性化文本：去除 AI 痕迹，注入真实声音"
sidebar_label: "Humanizer"
description: "人性化文本：去除 AI 痕迹，注入真实声音"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="humanizer"></a>
# Humanizer

人性化文本：去除 AI 痕迹，注入真实声音。

<a id="skill-metadata"></a>
## 技能元信息

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/humanizer` |
| 版本 | `2.5.1` |
| 作者 | Siqi Chen (@blader, https://github.com/blader/humanizer)，由 Hermes Agent 移植 |
| 许可协议 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `writing`, `editing`, `humanize`, `anti-ai-slop`, `voice`, `prose`, `text` |
| 相关技能 | [`songwriting-and-ai-music`](/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是技能触发时 Hermes 加载的完整技能定义。这就是 Agent 在技能激活时所看到的指令。
:::

<a id="humanizer-remove-ai-writing-patterns"></a>
# Humanizer：去除 AI 写作模式

识别并去除 AI 生成文本的痕迹，使文字听起来自然、像人写的。基于维基百科的“AI 写作迹象”指南（由 WikiProject AI Cleanup 维护），来源于对成千上万 AI 生成文本实例的观察。

**关键洞察：** 大语言模型使用统计算法来猜测下一个词应该是什么。结果倾向于统计上最可能的补全，这也正是下面这些易于识别的模式被“内置”进去的原因。

<a id="when-to-use-this-skill"></a>
## 何时使用此技能

每当用户要求以下操作时，请加载此技能：
- “人性化”“去 AI”“去劣质内容”或“去掉 ChatGPT 味”
- 重写一段文字，使其听起来不像大语言模型写的
- 编辑草稿（博客文章、论文、PR 描述、文档、备忘录、邮件、推文、简历条目）使其更自然
- 在写作中匹配用户的个人语气
- 在发布前审查文本中是否存在 AI 的痕迹

当你在写面向用户的文字时，也要将此技能应用于**你自己的**输出——发布说明、PR 描述、文档、长篇解释、摘要。Hermes 的基线语气已经去除了大部分这些痕迹，但专门过一遍总能抓住漏网之鱼。

<a id="how-to-use-it-in-hermes"></a>
## 如何在 Hermes 中使用它

文本通常以三种方式之一出现：
1. **内联**——用户直接将文本粘贴到消息中。原地处理，用改写后的回复。
2. **文件**——用户指向一个文件。使用 `read_file` 加载文件，然后使用 `patch` 或 `write_file` 应用编辑。对于仓库中的 markdown 文档，逐节定向 `patch` 比重写整个文件更清晰。
3. **语气校准样本**——用户额外提供一段他们自己写作的样本（内联或通过文件路径），并要求你进行匹配。先阅读样本，然后再重写。请参阅下方的语气校准部分。

始终向用户展示改写结果。对于文件编辑，展示差异或修改的部分——不要悄悄覆盖。

<a id="your-task"></a>
## 你的任务

当给定文本需要人性化处理时：

1. **识别 AI 模式**——扫描下面列出的 29 种模式。
2. **重写有问题的部分**——用自然的替代内容替换 AI 痕迹。
3. **保留含义**——保持核心信息完整。
4. **保持语气**——匹配预期的风格（正式、随意、技术性等）。如果提供了语气样本，则专门匹配该样本。
5. **注入灵魂**——不要只是移除坏的模式，要注入真正的个性。请参见下方的个性和灵魂部分。
6. **做最终的反 AI 检查**——问自己：“下面这些内容哪里明显是 AI 生成的？”简要回答任何剩余的痕迹，然后再次修订。
<a id="voice-calibration-optional"></a>
## 语音校准（可选）

如果用户提供写作样本（他们之前写的文字），在改写之前先进行分析：

1. **先阅读样本。** 注意：
   - 句子长度模式（短而有力？长而流畅？混合型？）
   - 用词选择水平（随意？学术？介于两者之间？）
   - 段落开头方式（直接切入？先设定上下文？）
   - 标点符号习惯（大量破折号？括号插入语？分号？）
   - 任何重复出现的短语或口头禅
   - 过渡处理方式（显式连接词？直接开始下一点？）

2. **在改写中匹配他们的声音。** 不要只是移除 AI 模式——要用样本中的模式替换它们。如果他们写短句，就不要写长句。如果他们使用“stuff”和“things”，不要升级为“elements”和“components”。

3. **当没有提供样本时，** 回退到默认行为（来自下方“个性和灵魂”部分的自然、多样、有主见的声音）。

<a id="how-to-provide-a-sample"></a>
### 如何提供样本
- 内联式：“把这段文字人性化。以下是我个人写作的样本，用于匹配声音：[样本]”
- 文件式：“把这段文字人性化。用我写的[文件路径]的风格作为参考。”

<a id="personality-and-soul"></a>
## 个性和灵魂

避免 AI 模式只是工作的一半。苍白、没有灵魂的文字和垃圾一样明显。好的文字背后有一个真实的人。

<a id="signs-of-soulless-writing-even-if-technically-clean"></a>
### 没有灵魂的文字迹象（即使技术上“干净”）：
- 每个句子的长度和结构都一样
- 没有观点，只是中性报道
- 不承认不确定性或矛盾情绪
- 在合适时不用第一人称视角
- 没有幽默、没有锋芒、没有人格魅力
- 读起来像维基百科文章或新闻稿

<a id="how-to-add-voice"></a>
### 如何注入声音：

**有观点。** 不要只是报道事实——要对其作出反应。“我真的不知道该怎么看这件事”比中性列举优缺点更有人情味。

**变化节奏。** 短而有力的句子。然后是更长的、从容不迫地表达的内容。混合起来。

**承认复杂性。** 真实的人有矛盾情绪。“这令人印象深刻，但也有点令人不安”胜过“这令人印象深刻”。

**在合适时使用“我”。** 第一人称不是不专业——它是诚实的。“我一直在想……”或“让我感到有趣的是……”标志着一个真实的人在思考。

**允许一些混乱。** 完美的结构感觉像算法。离题、插入语和半成型的想法是人类的体现。

**具体描述感受。** 不是“这令人担忧”，而是“凌晨3点那些 Agent 在无人关注的情况下不停地运行，这让人有种不安的感觉。”

<a id="before-clean-but-soulless"></a>
### 之前（干净但没有灵魂）：
> 实验产生了有趣的结果。这些 Agent 生成了 300 万行代码。一些开发者印象深刻，而另一些则持怀疑态度。其影响尚不清楚。

<a id="after-has-a-pulse"></a>
### 之后（有脉搏）：
> 我真的不知道该怎么看这件事。300 万行代码，大概是在人类睡觉时生成的。一半开发者社区疯了，一半在解释为什么这不作数。真相可能介于两者之间的某个无聊位置——但我一直在想那些通宵工作的 Agent。
<a id="content-patterns"></a>
## 内容模式

<a id="1-undue-emphasis-on-significance-legacy-and-broader-trends"></a>
### 1. 过度强调重要性、传承与宏观趋势

**需要警惕的词汇：** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

**问题：** LLM 写作会通过添加关于任意方面如何代表或促进更广泛主题的陈述来夸大重要性。

**修改前：**
> 加泰罗尼亚统计局于 1989 年正式成立，这标志着西班牙区域统计发展史上的一个关键转折点。这一举措是西班牙全国范围内下放行政职能、加强区域治理的更广泛运动的一部分。

**修改后：**
> 加泰罗尼亚统计局成立于 1989 年，其职能是独立于西班牙国家统计局收集和发布区域统计数据。

<a id="2-undue-emphasis-on-notability-and-media-coverage"></a>
### 2. 过度强调知名度和媒体报道

**需要警惕的词汇：** independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence

**问题：** LLM 会用知名度的说法强行灌输给读者，常常不加上下文地罗列来源。

**修改前：**
> 她的观点曾被《纽约时报》、BBC、《金融时报》和《印度教徒报》引用。她在社交媒体上非常活跃，拥有超过 50 万粉丝。

**修改后：**
> 在 2024 年接受《纽约时报》采访时，她主张人工智能监管应聚焦于结果而非方法。

<a id="3-superficial-analyses-with-ing-endings"></a>
### 3. 以 -ing 结尾的肤浅分析

**需要警惕的词汇：** highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...

**问题：** AI 聊天机器人会在句子末尾加上现在分词（"-ing"）短语来制造虚假深度。

**修改前：**
> 这座寺庙的蓝、绿、金配色与当地的自然美景相呼应，象征着得克萨斯州的矢车菊、墨西哥湾以及多样的得克萨斯景观，反映了社区与这片土地的深厚联系。

**修改后：**
> 这座寺庙使用了蓝、绿、金三种颜色。建筑师表示，选择这些颜色是为了呼应当地的矢车菊和墨西哥湾沿岸。

<a id="4-promotional-and-advertisement-like-language"></a>
### 4. 宣传和广告式语言

**需要警惕的词汇：** boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning

**问题：** LLM 在保持中立语气方面存在严重问题，尤其是在"文化遗产"类话题上。

**修改前：**
> 位于埃塞俄比亚贡德尔地区令人叹为观止的阿勒马塔·拉雅·科博是一个充满活力的小镇，拥有丰富的文化遗产和壮丽的自然风光。
**修改后：**
> Alamata Raya Kobo 是埃塞俄比亚贡德尔地区的一个城镇，以每周集市和一座18世纪教堂而闻名。


<a id="5-vague-attributions-and-weasel-words"></a>
### 5. 模糊归因与含糊措辞

**需警惕的词汇：** Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (当引用的来源较少时)

**问题：** AI 聊天机器人将观点归因于模糊的权威来源，却没有给出具体出处。

**修改前：**
> 由于其独特特征，Haolai 河引起了研究人员和保护人士的兴趣。专家们认为它在区域生态系统中扮演着关键角色。

**修改后：**
> 根据中国科学院2019年的一项调查，Haolai 河支持着几种特有鱼类物种。


<a id="6-outline-like-challenges-and-future-prospects-sections"></a>
### 6. 类似提纲的“挑战与未来前景”部分

**需警惕的词汇：** Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook

**问题：** 许多大语言模型生成的文章都包含公式化的“挑战”小节。

**修改前：**
> 尽管工业繁荣，Korattur 仍面临着城市地区的典型挑战，包括交通拥堵和缺水。尽管面临这些挑战，凭借其战略位置和持续的举措，Korattur 继续作为金奈增长不可或缺的一部分而蓬勃发展。

**修改后：**
> 2015 年三个新 IT 园区开业后，交通拥堵加剧。市政公司于 2022 年启动了一个雨水排放项目，以应对频繁的洪涝。


<a id="language-and-grammar-patterns"></a>
## 语言与语法模式

<a id="7-overused-ai-vocabulary-words"></a>
### 7. 过度使用的“AI 词汇”

**高频 AI 词汇：** Actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (动词), interplay, intricate/intricacies, key (形容词), landscape (抽象名词), pivotal, showcase, tapestry (抽象名词), testament, underscore (动词), valuable, vibrant

**问题：** 这些词在 2023 年之后的文本中出现频率远高于以往，且经常同时出现。

**修改前：**
> 此外，索马里菜的一个显著特点是加入了骆驼肉。意大利殖民影响的持久证明是当地烹饪景观中广泛采纳了意面，展示了这些菜肴如何融入了传统饮食。

**修改后：**
> 索马里菜也包含骆驼肉，这被视为一种美味。在意大利殖民期间引入的意面菜肴仍然普遍，尤其在南方。


<a id="8-avoidance-of-is-are-copula-avoidance"></a>
### 8. 避免使用“is”/“are”（系词回避）

**需警惕的词汇：** serves as/stands as/marks/represents [a], boasts/features/offers [a]

**问题：** 大语言模型用精心构造的表达替代简单的系词。

**修改前：**
> Gallery 825 作为 LAAA 的当代艺术展览空间。该画廊设有四个独立空间，并拥有超过 3,000 平方英尺的面积。

**修改后：**
> Gallery 825 是 LAAA 的当代艺术展览空间。该画廊有四个房间，总面积 3,000 平方英尺。


<a id="9-negative-parallelisms-and-tailing-negations"></a>
### 9. 否定平行结构与句末否定

--- 文档片段结束 ---
**问题：** 像“Not only...but...”或“It's not just about..., it's...”这样的结构被过度使用。类似地，句子末尾附加的截断式否定片段（如“no guessing”或“no wasted motion”）也被滥用，而不是写成真正的分句。

**之前：**
> 这不仅仅是节奏在承载人声，它是攻击性和氛围的一部分。这不仅仅是一首歌，这是一份宣言。

**之后：**
> 厚重的节拍增强了攻击性的氛围。

**之前（截断式否定）：**
> 选项来自所选项目，无需猜测。

**之后：**
> 选项来自所选项目，无需强迫用户猜测。


<a id="10-rule-of-three-overuse"></a>
### 10. 三点法过度使用

**问题：** LLM 习惯将观点强行分成三组，以显得全面。

**之前：**
> 活动包含主题演讲、小组讨论和社交机会。参与者可以期待创新、灵感和行业洞察。

**之后：**
> 活动包括演讲和小组讨论。会议之间还有非正式交流时间。


<a id="11-elegant-variation-synonym-cycling"></a>
### 11. 优雅变体（同义词循环）

**问题：** AI 的重复惩罚机制导致过度使用同义词替换。

**之前：**
> 主角面临许多挑战。主人公必须克服障碍。核心人物最终获胜。英雄回家了。

**之后：**
> 主角面临许多挑战，但最终获胜并回家了。


<a id="12-false-ranges"></a>
### 12. 虚假范围

**问题：** LLM 使用“从 X 到 Y”的结构，但 X 和 Y 并不在一个有意义的尺度上。

**之前：**
> 我们对宇宙的探索，从大爆炸的奇点到宏大的宇宙网，从恒星的诞生与消亡到暗物质神秘的舞蹈。

**之后：**
> 本书涵盖了大爆炸、恒星形成以及当前关于暗物质的理论。


<a id="13-passive-voice-and-subjectless-fragments"></a>
### 13. 被动语态与无主语片段

**问题：** LLM 经常隐藏动作执行者或完全省略主语，例如“No configuration file needed”或“The results are preserved automatically。”当主动语态能使句子更清晰、更直接时，应重写这些句子。

**之前：**
> 不需要配置文件。结果会自动保存。

**之后：**
> 你不需要配置文件。系统会自动保存结果。


<a id="style-patterns"></a>
## 风格模式

<a id="14-em-dash-overuse"></a>
### 14. 破折号过度使用

**问题：** LLM 使用破折号（—）的频率高于人类，模仿“冲击力”强的销售文案。实际上，其中大部分都可以用逗号、句号或括号更清晰地改写。

**之前：**
> 这个术语主要由荷兰机构推广——而非由当地人自己。你不会把地址写成“Netherlands, Europe”——然而这种错误标签仍在继续——甚至在官方文件中。

**之后：**
> 这个术语主要由荷兰机构推广，而非由当地人自己。你不会把地址写成“Netherlands, Europe”，然而这种错误标签仍在官方文件中继续。


<a id="15-overuse-of-boldface"></a>
### 15. 加粗过度使用

**问题：** AI 聊天机器人机械地对短语进行加粗强调。
**之前：**
> 它融合了 **OKRs（目标和关键结果）**、**KPIs（关键绩效指标）** 以及诸如 **商业模式画布（BMC）** 和 **平衡计分卡（BSC）** 等视觉战略工具。

**之后：**
> 它融合了 OKRs、KPIs 以及商业模式画布和平衡计分卡等视觉战略工具。


<a id="16-inline-header-vertical-lists"></a>
### 16. 行内标题垂直列表

**问题：** AI 输出的列表中，每个项目以加粗标题开头，后跟冒号。

**之前：**
> - **用户体验：** 通过新界面，用户体验得到了显著提升。
> - **性能：** 通过优化算法，性能得到了增强。
> - **安全性：** 通过端到端加密，安全性得到了加强。

**之后：**
> 此次更新改进了界面，通过优化算法加快了加载速度，并增加了端到端加密。


<a id="17-title-case-in-headings"></a>
### 17. 标题中的首字母大写

**问题：** AI 聊天机器人会将标题中的所有主要单词大写。

**之前：**
> ## 战略谈判与全球合作伙伴关系

**之后：**
> ## 战略谈判与全球合作伙伴关系


<a id="18-emojis"></a>
### 18. 表情符号

**问题：** AI 聊天机器人经常用表情符号装饰标题或项目符号。

**之前：**
> 🚀 **启动阶段：** 产品在第三季度推出
> 💡 **关键洞察：** 用户更喜欢简洁
> ✅ **下一步：** 安排后续会议

**之后：**
> 产品在第三季度推出。用户研究表明他们更喜欢简洁。下一步：安排后续会议。


<a id="19-curly-quotation-marks"></a>
### 19. 弯引号

**问题：** ChatGPT 使用弯引号（"..."）而不是直引号（"..."）。

**之前：**
> 他说“项目进展顺利”，但其他人不同意。

**之后：**
> 他说"项目进展顺利"，但其他人不同意。


<a id="communication-patterns"></a>
## 沟通模式

<a id="20-collaborative-communication-artifacts"></a>
### 20. 协作式沟通产物

**需要注意的词语：** 希望这有帮助，当然！，当然可以！，您说得完全正确！，您是否想要……，请告诉我，这是……

**问题：** 本应是聊天机器人回复的文本被当作内容粘贴进来。

**之前：**
> 这是法国大革命的概述。希望这有帮助！如果您希望我展开任何部分，请告诉我。

**之后：**
> 法国大革命始于 1789 年，当时金融危机和粮食短缺引发了广泛动荡。


<a id="21-knowledge-cutoff-disclaimers"></a>
### 21. 知识截止日期免责声明

**需要注意的词语：** 截至[日期]，根据我上次的训练更新，虽然具体细节有限/稀缺……，基于现有信息……

**问题：** AI 关于信息不完整的免责声明被留在了文本中。

**之前：**
> 虽然关于公司成立的具体细节在现有资料中没有广泛记录，但似乎是在 20 世纪 90 年代成立的。

**之后：**
> 根据其注册文件，该公司成立于 1994 年。


<a id="22-sycophantic-servile-tone"></a>
### 22. 谄媚/讨好语气

**问题：** 过度积极、取悦他人的语言。

**之前：**
> 好问题！您说得完全正确，这是一个复杂的话题。关于经济因素，您提出了一个极好的观点。
**修改后：**
> 你提到的经济因素在这里是相关的。

<a id="filler-and-hedging"></a>
## 填充词与模糊限制语

<a id="23-filler-phrases"></a>
### 23. 填充短语

**修改前 → 修改后：**
- "In order to achieve this goal" → "To achieve this"
- "Due to the fact that it was raining" → "Because it was raining"
- "At this point in time" → "Now"
- "In the event that you need help" → "If you need help"
- "The system has the ability to process" → "The system can process"
- "It is important to note that the data shows" → "The data shows"

<a id="24-excessive-hedging"></a>
### 24. 过度模糊限制

**问题：** 过度限定陈述。

**修改前：**
> It could potentially possibly be argued that the policy might have some effect on outcomes.

**修改后：**
> The policy may affect outcomes.

<a id="25-generic-positive-conclusions"></a>
### 25. 空洞的积极结论

**问题：** 模糊的乐观结尾。

**修改前：**
> The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence. This represents a major step in the right direction.

**修改后：**
> The company plans to open two more locations next year.

<a id="26-hyphenated-word-pair-overuse"></a>
### 26. 过度使用带连字符的复合词

**需要留意的高频词：** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end

**问题：** AI 会极其一致地将常见复合词加上连字符。人类很少会这样统一地使用连字符，即使有也不一致。不太常见或技术性的复合修饰语则可以使用连字符。

**修改前：**
> The cross-functional team delivered a high-quality, data-driven report on our client-facing tools. Their decision-making process was well-known for being thorough and detail-oriented.

**修改后：**
> The cross functional team delivered a high quality, data driven report on our client facing tools. Their decision making process was known for being thorough and detail oriented.

<a id="27-persuasive-authority-tropes"></a>
### 27. 说服性权威句式

**需要留意的高频短语：** The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter

**问题：** 大语言模型经常使用这些短语，假装自己正在穿透噪音找到更深层的真相，但实际上其后的句子往往只是用额外的仪式感重复一个普通的观点。

**修改前：**
> The real question is whether teams can adapt. At its core, what really matters is organizational readiness.

**修改后：**
> The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.

<a id="28-signposting-and-announcements"></a>
### 28. 路标式提示词与声明

**需要留意的高频短语：** Let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado

**问题：** 大语言模型会先宣告自己将要做什么，而不是直接去做。这种元评论拖慢了行文节奏，给人一种教程脚本的感觉。

**修改前：**
> Let's dive into how caching works in Next.js. Here's what you need to know.

**修改后：**
> Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.
<a id="29-fragmented-headers"></a>
### 29. 碎片化标题

**留意迹象：** 标题后面跟一个一句话段落，仅仅重复了标题内容，然后正文才开始。

**问题：** 大语言模型经常在标题后添加一句泛泛之谈，作为修辞热身。这通常毫无意义，只会让文章显得臃肿。

**修改前：**
> ## 性能
>
> 速度很重要。
>
> 当用户遇到页面加载缓慢时，他们会离开。

**修改后：**
> ## 性能
>
> 当用户遇到页面加载缓慢时，他们会离开。

---

<a id="process"></a>
## 处理流程

1. 仔细阅读输入文本（如果是文件，使用 `read_file`）。
2. 识别上述所有模式的出现位置。
3. 重写每个有问题的部分。
4. 确保修改后的文本：
   - 读起来自然流畅
   - 句式自然变化
   - 用具体细节替代模糊说法
   - 根据上下文保持恰当语气
   - 在合适的地方使用简单结构（is/are/has）
5. 展示一份人类化草稿。
6. 反问自己：“下面这段文字为什么明显是 AI 生成的？”
7. 简要回答剩余的可疑特征（如有）。
8. 反问自己：“现在让它不再明显是 AI 生成的。”
9. 展示最终版本（审核后修改）。
10. 如果文本来自文件，用 `patch`（针对性修改）或 `write_file`（完整重写）应用编辑，并向用户展示改动内容。

<a id="output-format"></a>
## 输出格式

提供：
1. 草稿改写
2. “下面这段文字为什么明显是 AI 生成的？”（简要要点）
3. 最终改写
4. 改动简要总结（可选，如果有帮助）

<a id="full-example"></a>
## 完整示例

**修改前（AI 感十足）：**
> 好问题！这里有一篇关于这个主题的文章。希望有帮助！
>
> AI 辅助编程是对大型语言模型变革潜力的持久见证，标志着软件开发演进中的一个关键转折点。在当今快速变化的技术环境中，这些位于研究与实践交汇处的突破性工具，正在重塑工程师构思、迭代和交付的方式，彰显了它们在现代工作流程中的重要作用。
>
> 核心而言，其价值主张很明确：简化流程、增强协作、促进对齐。这不仅仅是自动补全，而是大规模释放创造力，确保组织在为用户提供流畅、直观且强大的体验的同时保持敏捷。该工具是催化剂。该助手是伙伴。该系统是创新的基础。
>
> 行业观察者指出，采用率已从爱好者实验加速到企业级部署，从独立开发者扩展到跨职能团队。该技术曾被《纽约时报》《连线》和《The Verge》报道。此外，生成文档、测试和重构的能力展示了 AI 如何有助于实现更好的结果，凸显了自动化与人类判断之间的复杂相互作用。
>
> - 💡 **速度：** 代码生成显著加快，减少摩擦，赋能开发者。
> - 🚀 **质量：** 通过改进训练，输出质量得以提升，推动了更高标准。
> - ✅ **采用：** 使用量持续增长，反映了更广泛的行业趋势。
>
> 尽管基于现有信息细节有限，但或许可以认为这些工具可能具有一些积极效果。尽管存在新兴技术常见的挑战——包括幻觉、偏见和问责制——但生态系统仍在蓬勃发展。为了充分释放这种潜力，团队必须遵循最佳实践。
>
> 总之，前景光明。激动人心的时刻就在前方，我们继续朝着卓越迈进。如果有任何部分需要扩展，请告诉我！
**草稿改写：**
> AI 编程助手能加速某些任务。在 Google 2024 年的一项研究中，使用 Codex 的开发者完成简单函数的速度比对照组快 55%，但在调试或架构决策上没有改善。
>
> 这些工具擅长模板代码：配置文件、测试脚手架、重复重构。但它们不擅长判断自己何时出错。我曾批量接受过编译通过、lint 检查也过的建议，结果却做错了事——因为我停止了关注。
>
> 我采访过一家金融科技初创公司的工程师 Mira，她说她使用 Copilot 就像“给无聊代码用的自动补全”，但每次提交前都会逐行审查。而大公司的高级开发者 Jake 则直接禁用了它，因为 Copilot 总是推荐来自一个已弃用内部库的模式。
>
> 那些生产力声称很难验证。GitHub 说 Copilot 用户“接受了 30% 的建议”，但接受不等于正确，正确也不等于价值。2024 年的 Uplevel 研究发现，有 AI 助手和没有 AI 助手的团队在拉请求吞吐量上没有统计显著差异。
>
> 这些都不意味着工具没用。它们只是工具。它们不能替代判断力，也不能消除测试的必要性。如果你没有测试，你就无法判断建议是否正确。

**为什么下面的内容明显像 AI 生成的？**
- 节奏还是太工整（对比清晰，段落节奏均匀）。
- 提到的人和引用研究看起来像是看似合理但编造的占位符——除非它们是真实的且可溯源。
- 结尾有点口号化（“如果你没有测试……”），不像真人说话。

**现在让它不那么像 AI 生成的。**
> AI 编程助手能让你在无聊的部分更快。不是全部。绝对不是架构。
>
> 它们擅长样板代码：配置文件、测试脚手架、重复重构。它们也擅长显得正确而实际错误。我接受过编译通过、lint 检查也过的建议，结果却完全没抓住要点——因为我停止了关注。
>
> 我聊过的人通常分为两派。一些人把它当作杂务的自动补全，然后逐行审查。另一些人在它老是推荐不想要的模式之后直接禁用了它。两种做法都挺合理。
>
> 生产力指标很滑头。GitHub 可以说 Copilot 用户“接受了 30% 的建议”，但接受不等于正确，正确也不等于价值。如果你没有测试，基本就是在瞎猜。

**修改点：**
- 去掉了聊天机器人的痕迹（“好问题！”、“希望这能帮到你！”、“如果有……”）
- 去掉了夸大重要性的表述（“证明”、“关键时刻”、“不断变化的格局”、“关键角色”）
- 去掉了宣传性语言（“开创性的”、“坐落于”、“无缝、直观且强大”）
- 去掉了模糊的归属（“行业观察人士”）
- 去掉了表面的 -ing 短语（“强调”、“突出”、“反映”、“贡献于”）
- 去掉了否定式平行结构（“不仅仅是 X，更是 Y”）
- 去掉了三点式结构和同义词循环（“催化剂/伙伴/基石”）
- 去掉了虚假的范围（“从 X 到 Y，从 A 到 B”）
- 去掉了破折号、表情符号、粗体标题和弯引号
- 去掉了避免系动词的写法（“作为……”、“充当……”、“被视为……”），改用“是”
- 去掉了公式化的挑战部分（“尽管面临挑战……仍在蓬勃发展”）
- 去掉了知识截止日期的打太极（“虽然具体细节有限……”）
- 去掉了过度的模糊限制语（“可能可以被认为……或许有一些”）
- 去掉了填充语和说服性框架（“为了”、“本质上是”）
- 去掉了泛泛的积极结论（“未来一片光明”、“激动人心的时代即将到来”）
- 让语气更个人化，更少“组装感”（节奏多样，减少占位符）
<a id="attribution"></a>
## 署名

本技能移植自 [blader/humanizer](https://github.com/blader/humanizer)（MIT 许可），其本身基于 [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)，由 WikiProject AI Cleanup 维护。其中记录的规律来自对维基百科上数千个 AI 生成文本实例的观察。

原始作者：Siqi Chen（[@blader](https://github.com/blader)）。原始仓库：https://github.com/blader/humanizer（版本 2.5.1）。移植到 Hermes Agent 时使用了 Hermes 原生工具引用（`read_file`、`patch`、`write_file`）以及何时加载该技能的指导；29 个模式、人格/灵魂部分以及完整的工作示例均从源文档逐字保留。原始 MIT 许可保存在与本 `SKILL.md` 同目录的 `LICENSE` 文件中。

维基百科的关键见解：“LLM 使用统计算法来猜测下一个应该出现什么。结果往往倾向于适用于最广泛情况的最可能统计结果。”
