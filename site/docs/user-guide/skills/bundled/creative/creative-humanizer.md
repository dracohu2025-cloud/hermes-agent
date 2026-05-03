---
title: "Humanizer — 人性化文本：去除 AI 痕迹，注入真实语气"
sidebar_label: "Humanizer"
description: "人性化文本：去除 AI 痕迹，注入真实语气"
---

{/* 此页面由网站脚本 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Humanizer {#humanizer}

人性化文本：去除 AI 痕迹，注入真实语气。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/creative/humanizer` |
| 版本 | `2.5.1` |
| 作者 | Siqi Chen (@blader, https://github.com/blader/humanizer)，由 Hermes Agent 移植 |
| 许可证 | MIT |
| 标签 | `writing`, `editing`, `humanize`, `anti-ai-slop`, `voice`, `prose`, `text` |
| 相关技能 | [`songwriting-and-ai-music`](/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Humanizer：去除 AI 写作模式 {#humanizer-remove-ai-writing-patterns}

识别并去除 AI 生成文本的痕迹，使写作听起来自然且人性化。基于维基百科的“AI 写作迹象”指南（由 WikiProject AI Cleanup 维护），源自对数千个 AI 生成文本实例的观察。

**关键洞察：** 大语言模型使用统计算法来猜测接下来应该出现什么。结果往往倾向于统计上最可能的补全，这就是下面这些明显模式被嵌入的原因。

## 何时使用此技能 {#when-to-use-this-skill}

当用户要求以下内容时，加载此技能：
- “人性化”、“去 AI”、“去垃圾”或“去 ChatGPT”一段文本
- 重写某些内容，使其听起来不像是由大语言模型写的
- 编辑草稿（博客文章、论文、PR 描述、文档、备忘录、邮件、推文、简历要点）使其更自然
- 在写作中匹配他们的语气
- 在发布前检查文本中的 AI 痕迹

同时，在编写面向用户的散文时，也请将此技能应用于**你自己的**输出——发布说明、PR 描述、文档、长篇解释、摘要。Hermes 的默认语气已经去除了大部分这些痕迹，但一次专注的检查可以捕捉到漏网之鱼。

## 如何在 Hermes 中使用 {#how-to-use-it-in-hermes}

文本通常以三种方式之一到达：
1. **内联**——用户直接将文本粘贴到消息中。就地处理，回复重写后的内容。
2. **文件**——用户指向一个文件。使用 `read_file` 加载它，然后使用 `patch` 或 `write_file` 应用编辑。对于仓库中的 Markdown 文档，按章节进行有针对性的 `patch` 比重写整个文件更清晰。
3. **语气校准样本**——用户提供他们自己写作的额外样本（内联或通过文件路径），并要求你匹配它。先阅读样本，然后重写。请参阅下面的语气校准部分。

始终向用户展示重写后的内容。对于文件编辑，显示差异或更改的部分——不要静默覆盖。

## 你的任务 {#your-task}

当给定要人性化的文本时：

1. **识别 AI 模式**——扫描下面列出的 29 种模式。
2. **重写有问题的部分**——用自然的替代方案替换 AI 痕迹。
3. **保留含义**——保持核心信息不变。
4. **保持语气**——匹配预期的语气（正式、随意、技术性等）。如果提供了语气样本，则专门匹配它。
5. **注入灵魂**——不要仅仅去除不良模式，要注入实际的个性。请参阅下面的“个性与灵魂”。
6. **进行最后的反 AI 检查**——问自己：“是什么让下面的内容明显是 AI 生成的？”简要回答任何残留的痕迹，然后再次修改。
## 声音校准（可选） {#voice-calibration-optional}

如果用户提供了一份写作样例（他们自己之前的作品），在重写前先进行分析：

1. **先阅读样例。** 注意：
   - 句子长度模式（短促有力？长句流畅？混合型？）
   - 用词级别（随意？学术？介于两者之间？）
   - 如何开头段落（直接切入？先铺垫背景？）
   - 标点习惯（大量破折号？括号插入语？分号？）
   - 任何重复的短语或口头禅
   - 如何处理过渡（显式连接词？直接开始下一个要点？）

2. **在重写中匹配他们的声音。** 不要只是移除 AI 模式——而是用样例中的模式替换它们。如果他们写短句，不要写出长句。如果他们使用“东西”和“事情”，不要升级为“元素”和“组件”。

3. **当没有提供样例时，** 回退到默认行为（来自下方“个性与灵魂”部分的自然、多变、有主见的声音）。

### 如何提供样例 {#how-to-provide-a-sample}
- 内联：“Humanize this text. Here's a sample of my writing for voice matching: [sample]”
- 文件：“Humanize this text. Use my writing style from [file path] as a reference.”

## 个性与灵魂 {#personality-and-soul}

避免 AI 模式只完成了一半工作。无菌、无灵魂的写作和垃圾一样明显。好文字背后有一个真实的人。

### 无灵魂写作的迹象（即使技术上“干净”）： {#signs-of-soulless-writing-even-if-technically-clean}
- 每个句子长度和结构相同
- 没有观点，只是中立报道
- 不承认不确定性或矛盾情绪
- 在适当的时候不使用第一人称
- 没有幽默、没有锋芒、没有个性
- 读起来像维基百科文章或新闻稿

### 如何添加声音： {#how-to-add-voice}

**有观点。** 不要只是陈述事实——要对它们做出反应。“我真的不知道对此该怎么看”比中立地列出优缺点更有人性。

**变化节奏。** 短促有力的句子。然后是一些慢慢展开的长句。混合起来。

**承认复杂性。** 真正的人会有矛盾情绪。“这令人印象但也有点令人不安”胜过“这令人印象深刻”。

**在合适时使用“我”。** 第一人称并不不专业——它是诚实的。“我一直在思考…”或“让我在意的是…”标志着一个真实的人在思考。

**允许一些混乱。** 完美的结构让人感觉像算法。离题、插入语和不完整的想法是人性化的表现。

**具体描述感受。** 不是“这令人担忧”，而是“在凌晨3点，没有人在看的时候，Agent 们不停运转，这让人有些不安。”

### 之前（干净但无灵魂）： {#before-clean-but-soulless}
> 实验得出了有趣的结果。Agent 们生成了 300 万行代码。一些开发者印象深刻，而另一些则持怀疑态度。其影响尚不清楚。

### 之后（有脉搏）： {#after-has-a-pulse}
> 我真的不知道该怎么看待这个。300 万行代码，在人类大概睡着的时候生成的。一半的开发者社区在抓狂，另一半在解释为什么这并不算数。真相可能夹在中间某个无聊的地方——但我一直在想那些彻夜工作的 Agent 们。
## 内容模式 {#content-patterns}

### 1. 过度强调重要性、遗产和宏观趋势 {#1-undue-emphasis-on-significance-legacy-and-broader-trends}

**需警惕的词汇：** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

**问题：** LLM 写作会通过添加关于任意方面如何代表或贡献于更广泛主题的陈述，来夸大重要性。

**修改前：**
> 加泰罗尼亚统计局于1989年正式成立，标志着西班牙地区统计发展中的一个关键转折点。这一举措是西班牙全国范围内下放行政职能、加强区域治理的广泛运动的一部分。

**修改后：**
> 加泰罗尼亚统计局成立于1989年，旨在独立于西班牙国家统计局收集和发布地区统计数据。

### 2. 过度强调知名度和媒体报道 {#2-undue-emphasis-on-notability-and-media-coverage}

**需警惕的词汇：** independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence

**问题：** LLM 会强行向读者灌输知名度的说法，常常不加背景地罗列来源。

**修改前：**
> 她的观点曾被《纽约时报》、BBC、《金融时报》和《印度教徒报》引用。她在社交媒体上非常活跃，拥有超过50万粉丝。

**修改后：**
> 在2024年《纽约时报》的一次采访中，她认为人工智能监管应侧重于结果而非方法。

### 3. 以 -ing 结尾的肤浅分析 {#3-superficial-analyses-with-ing-endings}

**需警惕的词汇：** highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...

**问题：** AI 聊天机器人会在句子末尾添加现在分词（"-ing"）短语，以制造虚假的深度。

**修改前：**
> 寺庙的蓝、绿、金色调与该地区的自然美景相呼应，象征着德克萨斯州的矢车菊、墨西哥湾以及多样的德克萨斯景观，反映了社区与土地的深厚联系。

**修改后：**
> 寺庙使用了蓝、绿、金色。建筑师表示，选择这些颜色是为了呼应当地的矢车菊和墨西哥湾海岸。

### 4. 宣传和广告式语言 {#4-promotional-and-advertisement-like-language}

**需警惕的词汇：** boasts a, vibrant, rich (比喻义), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (比喻义), renowned, breathtaking, must-visit, stunning

**问题：** LLM 在保持中立语气方面存在严重问题，尤其是在涉及"文化遗产"主题时。

**修改前：**
> 阿拉马塔·拉亚·科博坐落在埃塞俄比亚贡德尔地区令人叹为观止的区域，是一座充满活力的城镇，拥有丰富的文化遗产和令人惊叹的自然美景。

**修改后：**
> 阿拉马塔·拉亚·科博是埃塞俄比亚贡德尔地区的一个城镇。
**之后：**
> 阿拉马塔·拉亚·科博是埃塞俄比亚贡德尔地区的一个小镇，以每周集市和18世纪的教堂而闻名。

### 5. 模糊归属与推诿用语 {#5-vague-attributions-and-weasel-words}

**需警惕的词汇：** 行业报告、观察人士称、专家认为、一些评论者指出、部分来源/出版物（引用很少时）

**问题：** AI聊天机器人将观点归因于缺乏具体来源的模糊权威。

**之前：**
> 由于其独特特征，浩来河引起了研究人员和环保人士的关注。专家认为它在区域生态系统中发挥着关键作用。

**之后：**
> 根据中国科学院2019年的一项调查，浩来河支持着几种特有鱼类。

### 6. 模板化的“挑战与前景”部分 {#6-outline-like-challenges-and-future-prospects-sections}

**需警惕的词汇：** 尽管……面临若干挑战……、尽管有这些挑战、挑战与遗产、未来展望

**问题：** 许多LLM生成的文章包含公式化的“挑战”部分。

**之前：**
> 尽管工业繁荣，科拉图尔面临着城市地区的典型挑战，包括交通拥堵和水资源短缺。尽管有这些挑战，凭借其战略位置和持续举措，科拉图尔继续作为金奈发展不可或缺的一部分蓬勃发展。

**之后：**
> 2015年后，随着三个新的IT园区开放，交通拥堵加剧。市政公司于2022年启动了雨水排水项目，以应对反复发生的洪水。

## 语言与语法模式 {#language-and-grammar-patterns}

### 7. 过度使用的“AI词汇” {#7-overused-ai-vocabulary-words}

**高频AI词汇：** 实际上、此外、与……一致、关键的、深入探讨、强调、持久的、增强、培养、获得、突出（动词）、相互作用、复杂/复杂性、关键（形容词）、格局（抽象名词）、关键性的、展示、织锦（抽象名词）、证明、强调（动词）、有价值的、充满活力的

**问题：** 这些词在2023年后的文本中出现频率远高于以往，且经常共现。

**之前：**
> 此外，索马里美食的一个显著特征是融入骆驼肉。意大利殖民影响的一个持久证明是当地烹饪格局中广泛接纳了面食，展示了这些菜肴如何融入传统饮食。

**之后：**
> 索马里美食还包括骆驼肉，被视为珍馐。意大利殖民时期引入的面食菜肴仍然常见，尤其在南方。

### 8. 避免使用“是”（系动词回避） {#8-avoidance-of-is-are-copula-avoidance}

**需警惕的词汇：** 作为/充当、拥有/以……为特色、提供 [一个]

**问题：** LLM用复杂的结构替代简单的系动词。

**之前：**
> 825画廊作为LAAA的当代艺术展览空间。该画廊设有四个独立空间，拥有超过3000平方英尺的面积。

**之后：**
> 825画廊是LAAA的当代艺术展览空间。该画廊有四个房间，总面积为3000平方英尺。

### 9. 否定平行结构与尾缀否定 {#9-negative-parallelisms-and-tailing-negations}
**问题：** 像 "Not only...but..." 或 "It's not just about..., it's..." 这样的结构被过度使用。同样被滥用的还有句子末尾的截断式否定片段，例如 "no guessing" 或 "no wasted motion"，它们本应写成真正的从句，却被生硬地贴在句尾。

**修改前：**
> 这不仅仅是节奏在人声下律动；它是侵略性和氛围的一部分。这不仅仅是一首歌，它是一种宣言。

**修改后：**
> 沉重的节拍增强了歌曲的攻击性。

**修改前（截断式否定）：**
> 选项来自所选项目，无需猜测。

**修改后：**
> 选项来自所选项目，无需强迫用户猜测。

### 10. 三法则的过度使用 {#10-rule-of-three-overuse}

**问题：** 大语言模型为了显得全面，强行将想法分成三组。

**修改前：**
> 该活动包括主题演讲、小组讨论和社交机会。与会者可以期待创新、灵感和行业洞察。

**修改后：**
> 该活动包括演讲和小组讨论。会议间隙还有非正式的社交时间。

### 11. 优雅变体（同义词循环） {#11-elegant-variation-synonym-cycling}

**问题：** AI 的重复惩罚机制会导致过度使用同义词替换。

**修改前：**
> 主角面临许多挑战。主人公必须克服障碍。核心人物最终取得胜利。英雄回到家中。

**修改后：**
> 主角面临许多挑战，但最终取得胜利并回到家中。

### 12. 虚假范围 {#12-false-ranges}

**问题：** 大语言模型使用 "从 X 到 Y" 的结构，但 X 和 Y 并不在一个有意义的尺度上。

**修改前：**
> 我们的宇宙之旅从大爆炸的奇点带到了宏大的宇宙网，从恒星的诞生与死亡带到了暗物质的神秘舞蹈。

**修改后：**
> 这本书涵盖了宇宙大爆炸、恒星形成以及关于暗物质的当前理论。

### 13. 被动语态与无主语片段 {#13-passive-voice-and-subjectless-fragments}

**问题：** 大语言模型经常隐藏动作执行者或完全省略主语，例如 "No configuration file needed" 或 "The results are preserved automatically." 当主动语态能使句子更清晰、更直接时，请重写这些句子。

**修改前：**
> 无需配置文件。结果会自动保留。

**修改后：**
> 你不需要配置文件。系统会自动保留结果。

## 风格模式 {#style-patterns}

### 14. 破折号过度使用 {#14-em-dash-overuse}

**问题：** 大语言模型使用破折号（—）的频率高于人类，模仿“有力”的销售文案。实际上，大多数破折号都可以用逗号、句号或括号更清晰地改写。

**修改前：**
> 这个术语主要由荷兰机构推广——而不是由人民自己。你不会说“荷兰，欧洲”作为地址——然而这种错误标签仍在继续——甚至在官方文件中。

**修改后：**
> 这个术语主要由荷兰机构推广，而不是由人民自己。你不会说“荷兰，欧洲”作为地址，然而这种错误标签仍在官方文件中继续。

### 15. 粗体过度使用 {#15-overuse-of-boldface}

**问题：** AI 聊天机器人机械地使用粗体强调短语。
**之前：**
> 它融合了 **OKRs（目标和关键结果）**、**KPIs（关键绩效指标）** 以及 **商业模式画布（BMC）** 和 **平衡计分卡（BSC）** 等可视化战略工具。

**之后：**
> 它融合了 OKRs、KPIs 以及商业模式画布和平衡计分卡等可视化战略工具。


### 16. 行内标题垂直列表 {#16-inline-header-vertical-lists}

**问题：** AI 输出的列表中，每项以加粗标题开头，后跟冒号。

**之前：**
> - **用户体验：** 通过全新的界面，用户体验得到了显著提升。
> - **性能：** 通过优化算法，性能得到了增强。
> - **安全性：** 通过端到端加密，安全性得到了加强。

**之后：**
> 本次更新改进了界面，通过优化算法加快了加载速度，并增加了端到端加密。


### 17. 标题中的首字母大写 {#17-title-case-in-headings}

**问题：** AI 聊天机器人会大写标题中的所有主要单词。

**之前：**
> ## Strategic Negotiations And Global Partnerships

**之后：**
> ## Strategic negotiations and global partnerships（战略谈判与全球合作伙伴关系）


### 18. 表情符号 {#18-emojis}

**问题：** AI 聊天机器人经常用表情符号装饰标题或列表项。

**之前：**
> 🚀 **发布阶段：** 产品将于第三季度发布
> 💡 **关键洞察：** 用户偏爱简洁
> ✅ **后续步骤：** 安排跟进会议

**之后：**
> 产品将于第三季度发布。用户研究显示用户偏爱简洁。下一步：安排跟进会议。


### 19. 弯引号 {#19-curly-quotation-marks}

**问题：** ChatGPT 使用弯引号（"..."）代替直引号（"..."）。

**之前：**
> 他说“项目按计划进行”，但其他人不同意。

**之后：**
> 他说"项目按计划进行"，但其他人不同意。


## 沟通模式 {#communication-patterns}

### 20. 协作式沟通痕迹 {#20-collaborative-communication-artifacts}

**需要注意的词汇：** 希望这有帮助、当然可以！、没问题！、你说得完全正确！、希望你...、请告知、以下是...

**问题：** 本应是聊天机器人回复的文字被当作内容粘贴进来。

**之前：**
> 以下是对法国大革命的概述。希望这对你有帮助！如果你希望我详细阐述任何部分，请告诉我。

**之后：**
> 法国大革命始于1789年，当时财政危机和粮食短缺引发了广泛动荡。


### 21. 知识截止日期免责声明 {#21-knowledge-cutoff-disclaimers}

**需要注意的词汇：** 截至 [日期]、根据我上次的训练更新、虽然具体细节有限/稀缺...、基于现有信息...

**问题：** AI 关于信息不完整的免责声明被留在了文本中。

**之前：**
> 虽然该公司的成立细节在现有可用资料中没有广泛记载，但它似乎是在20世纪90年代某个时候成立的。

**之后：**
> 根据公司注册文件，该公司成立于1994年。


### 22. 谄媚/奉承的语气 {#22-sycophantic-servile-tone}

**问题：** 过于积极、取悦他人的措辞。

**之前：**
> 好问题！你说得完全正确，这确实是一个复杂的话题。你关于经济因素的观点非常精彩。

**之后：**
> （原文未给出“之后”示例，此处保持空白或删除？根据文档结构，每个条目都有After，但此处原文只有Before。按照规则，保留结构，原文没有After，我们就不添加。但检查原文：最后一段只有Before，没有After。所以只输出Before内容，不加After。）
**之后：**
> 你提到的经济因素在这里是相关的。


## 填充词与回避性用语 {#filler-and-hedging}

### 23. 填充短语 {#23-filler-phrases}

**之前 → 之后：**
- "In order to achieve this goal" → "To achieve this"
- "Due to the fact that it was raining" → "Because it was raining"
- "At this point in time" → "Now"
- "In the event that you need help" → "If you need help"
- "The system has the ability to process" → "The system can process"
- "It is important to note that the data shows" → "The data shows"


### 24. 过度回避性用语 {#24-excessive-hedging}

**问题：** 对陈述过度限定。

**之前：**
> It could potentially possibly be argued that the policy might have some effect on outcomes.

**之后：**
> The policy may affect outcomes.


### 25. 泛泛的积极结论 {#25-generic-positive-conclusions}

**问题：** 模糊的乐观结尾。

**之前：**
> The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence. This represents a major step in the right direction.

**之后：**
> The company plans to open two more locations next year.


### 26. 连字符复合词过度使用 {#26-hyphenated-word-pair-overuse}

**需注意的词：** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end

**问题：** AI 会完美一致地给常见复合词加连字符。人类很少会统一加连字符，即使加了也不一致。不太常见或技术性的复合修饰语加连字符是可以的。

**之前：**
> The cross-functional team delivered a high-quality, data-driven report on our client-facing tools. Their decision-making process was well-known for being thorough and detail-oriented.

**之后：**
> The cross functional team delivered a high quality, data driven report on our client facing tools. Their decision making process was known for being thorough and detail oriented.


### 27. 说服性权威套话 {#27-persuasive-authority-tropes}

**需注意的短语：** The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter

**问题：** 大语言模型用这些短语假装在穿透噪音触及更深层的真相，但后面跟着的句子通常只是用额外的仪式感重述一个普通观点。

**之前：**
> The real question is whether teams can adapt. At its core, what really matters is organizational readiness.

**之后：**
> The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.


### 28. 路标式声明 {#28-signposting-and-announcements}

**需注意的短语：** Let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado

**问题：** 大语言模型会宣布它们将要做什么，而不是直接去做。这种元评论拖慢了写作节奏，给人一种教程脚本的感觉。

**之前：**
> Let's dive into how caching works in Next.js. Here's what you need to know.

**之后：**
> Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.
### 29. 碎片化标题 {#29-fragmented-headers}

**注意迹象：** 标题后面跟着一个单行段落，只是重复标题内容，然后才进入正文。

**问题：** 大语言模型经常在标题后添加一句泛泛的句子作为开场白。这通常毫无意义，只会让文章显得冗长。

**修改前：**
> ## 性能
>
> 速度很重要。
>
> 当用户遇到加载缓慢的页面时，他们会离开。

**修改后：**
> ## 性能
>
> 当用户遇到加载缓慢的页面时，他们会离开。

---

## 流程 {#process}

1. 仔细阅读输入文本（如果是文件，使用 `read_file`）。
2. 识别上述所有模式的出现位置。
3. 重写每个有问题的部分。
4. 确保修改后的文本：
   - 朗读起来自然流畅
   - 句子结构自然变化
   - 使用具体细节而非模糊表述
   - 保持与上下文相符的语气
   - 在适当的地方使用简单结构（is/are/has）
5. 提供一个拟人化草稿版本。
6. 自问：“下面这段文字为什么明显是 AI 生成的？”
7. 简要回答剩余的可疑特征（如果有）。
8. 自问：“现在让它看起来不像 AI 生成的。”
9. 提供最终版本（审核后修改）。
10. 如果文本来自文件，使用 `patch`（针对性修改）或 `write_file`（完全重写）应用编辑，并向用户展示修改内容。

## 输出格式 {#output-format}

提供：
1. 草稿重写
2. “下面这段文字为什么明显是 AI 生成的？”（简要要点）
3. 最终重写
4. 修改内容的简要总结（可选，如果有帮助）

## 完整示例 {#full-example}

**修改前（听起来像 AI 写的）：**
> 好问题！这里有一篇关于这个主题的文章。希望这能帮到你！
>
> AI 辅助编程作为大型语言模型变革潜力的持久证明，标志着软件开发演进中的一个关键时刻。在当今快速变化的技术格局中，这些突破性工具——处于研究与实践的交汇点——正在重塑工程师构思、迭代和交付的方式，突显了它们在现代工作流程中的关键作用。
>
> 其核心价值主张很明确：简化流程、增强协作、促进对齐。这不仅仅是自动补全；而是关于大规模释放创造力，确保组织在为用户提供无缝、直观且强大的体验的同时保持敏捷。该工具充当催化剂。该助手扮演合作伙伴。该系统作为创新的基础。
>
> 行业观察者指出，采用已从爱好者实验加速到企业级部署，从独立开发者扩展到跨职能团队。该技术曾被《纽约时报》、《连线》和《The Verge》报道。此外，生成文档、测试和重构的能力展示了 AI 如何有助于实现更好的结果，突显了自动化与人类判断之间复杂的相互作用。
>
> - 💡 **速度：** 代码生成显著加快，减少了摩擦并赋能开发者。
> - 🚀 **质量：** 通过改进训练提升了输出质量，有助于达到更高标准。
> - ✅ **采用：** 使用量持续增长，反映了更广泛的行业趋势。
>
> 虽然基于现有信息的具体细节有限，但可以认为这些工具可能产生一些积极影响。尽管存在新兴技术的典型挑战——包括幻觉、偏见和问责制——生态系统仍在蓬勃发展。为了充分实现这一潜力，团队必须遵循最佳实践。
>
> 总之，未来看起来一片光明。在我们继续这段追求卓越的旅程中，激动人心的时刻就在前方。如果你希望我展开任何部分，请告诉我！
**草稿改写：**
> AI 编码助手能加快某些任务的完成速度。谷歌在 2024 年的一项研究中发现，使用 Codex 的开发者完成简单函数的速度比对照组快 55%，但在调试或架构决策方面没有明显提升。
>
> 这些工具擅长处理模板代码：配置文件、测试脚手架、重复性重构。但它们不擅长判断自己何时出错。我曾批量接受过一些建议，这些代码能通过编译和 lint 检查，但最终做的事情却是错的，因为我停止了关注。
>
> 我在一家金融科技初创公司采访过的工程师 Mira 说，她使用 Copilot 就像“无聊代码的自动补全”，但会在提交前逐行审查。在另一家大型公司工作的资深开发者 Jake 则禁用了它，因为它不断从一个已弃用的内部库中推荐模式。
>
> 关于生产力的说法很难验证。GitHub 表示 Copilot 用户“接受了 30% 的建议”，但接受不等于正确，正确也不等于价值。2024 年的 Uplevel 研究发现，使用 AI 助手和没有使用的团队之间，在拉取请求吞吐量上没有统计上的显著差异。
>
> 这并不意味着这些工具没用。它们只是工具。它们不能取代判断力，也不能消除测试的必要性。如果没有测试，你就无法判断建议是否正确。

**为什么以下内容明显像是 AI 生成的？**
- 节奏还是太工整了（清晰的对比，均匀节奏的段落）。
- 列举的人物和引用的研究读起来像是合理但虚构的占位符，除非是真实且有来源的。
- 结尾部分有点口号化（"如果你没有测试..."），不像真人在说话。

**现在把它改得不像 AI 生成的。**
> AI 编码助手能让你在无聊的部分更快，但不是所有部分，绝对不是架构方面。
>
> 它们擅长模板代码：配置文件、测试脚手架、重复性重构。它们也擅长听起来正确但实际出错。我接受过一些建议，它们编译通过、通过 lint 检查，但仍然偏离了重点，因为我停止了关注。
>
> 我聊过的人大致分为两派。有些人把它当作杂事的自动补全，逐行审查。另一些人则在它不断推荐他们不想要的模式后禁用了它。两种做法感觉都合理。
>
> 生产力指标很模糊。GitHub 可以说 Copilot 用户“接受了 30% 的建议”，但接受不等于正确，正确也不等于价值。如果没有测试，你基本上就是在猜。

**作出的改动：**
- 去掉了聊天机器人式的用语（“好问题！”、“希望这有帮助！”、“请让我知道如果...”）
- 去掉了夸大其词（“证明”、“关键时刻”、“不断发展的格局”、“关键作用”）
- 去掉了推广语言（“开创性的”、“坐落于”、“无缝、直观且强大”）
- 去掉了模糊归属（“行业观察者”）
- 去掉了表面的-ing短语（“强调”、“突出”、“反映”、“贡献”）
- 去掉了否定并行句式（“不仅是X，还是Y”）
- 去掉了三点式模式与同义词循环（“催化剂/伙伴/基础”）
- 去掉了虚假范围（“从X到Y，从A到B”）
- 去掉了破折号、表情符号、加粗标题和弯引号
- 去掉了系动词回避（“作为”、“充当”、“表现为”），改用“是”
- 去掉了公式化的挑战段落（“尽管面临挑战……仍在蓬勃发展”）
- 去掉了知识截止日期的含糊措辞（“虽然具体细节有限……”）
- 去掉了过多的含糊用语（“可能可以被认为……也许有一些”）
- 去掉了填充短语和说服性框架（“为了”、“其核心是”）
- 去掉了泛泛的正面结论（“前景光明”、“激动人心的时代在前方”）
- 让语气更个人化，少一些“拼凑感”（节奏更变化，少一些占位符）
## 出处 {#attribution}

本技能移植自 [blader/humanizer](https://github.com/blader/humanizer)（MIT 许可证），而该库又基于 [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)，由 WikiProject AI Cleanup 维护。其中记录的规律来自对维基百科上数千个 AI 生成文本实例的观察。

原作者：Siqi Chen（[@blader](https://github.com/blader)）。原始仓库：https://github.com/blader/humanizer（版本 2.5.1）。已移植到 Hermes Agent，使用了 Hermes 原生工具引用（`read_file`、`patch`、`write_file`）以及何时加载该技能的指导说明；29 个模式、个性/灵魂部分及完整示例均自原文逐字保留。原始 MIT 许可证保存在与此 `SKILL.md` 同目录的 `LICENSE` 文件中。

维基百科的关键见解：“LLM 使用统计算法来猜测接下来应该出现什么。结果往往趋向于适用于最广泛情况的最具统计可能性的结果。”
