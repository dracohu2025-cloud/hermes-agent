---
title: "Pokemon Player — 通过无头模拟器 + RAM 读取玩宝可梦"
sidebar_label: "Pokemon Player"
description: "通过无头模拟器 + RAM 读取玩宝可梦"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="pokemon-player"></a>
# Pokemon Player

通过无头模拟器 + RAM 读取玩宝可梦。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/gaming/pokemon-player` |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Pokemon Player

使用 `pokemon-agent` 包通过无头模拟玩宝可梦游戏。

<a id="when-to-use"></a>
## 何时使用
- 用户说“玩宝可梦”、“开始宝可梦”、“宝可梦游戏”
- 用户询问关于宝可梦红、蓝、黄、火红等
- 用户想观看 AI 玩宝可梦
- 用户提到 ROM 文件（.gb, .gbc, .gba）

<a id="startup-procedure"></a>
## 启动流程

<a id="1-first-time-setup-clone-venv-install"></a>
### 1. 首次设置（克隆、虚拟环境、安装）
仓库是 GitHub 上的 NousResearch/pokemon-agent。克隆它，然后
设置一个 Python 3.10+ 虚拟环境。使用 uv（推荐，速度更快）
创建虚拟环境并以可编辑模式安装包，附带
pyboy 额外依赖。如果 uv 不可用，则回退到 python3 -m venv + pip。

在这台机器上，它已经设置在 /home/teknium/pokemon-agent
并已准备好虚拟环境——只需 cd 到那里并 source .venv/bin/activate。

你还需要一个 ROM 文件。向用户索要他们的。在这台机器上，
该目录下有一个 roms/pokemon_red.gb。
永远不要下载或提供 ROM 文件——始终询问用户。

<a id="2-start-the-game-server"></a>
### 2. 启动游戏服务器
在 pokemon-agent 目录内，激活虚拟环境后，运行
pokemon-agent serve，使用 --rom 指向 ROM，--port 9876。
在后台运行，加上 &。
要从存档恢复，添加 --load-state 并指定存档名称。
等待 4 秒启动，然后用 GET /health 验证。

<a id="3-set-up-live-dashboard-for-user-to-watch"></a>
### 3. 设置用户可观看的实时仪表盘
通过 localhost.run 使用 SSH 反向隧道，让用户可以在
浏览器中查看仪表盘。使用 ssh 连接，将本地端口 9876 转发到
远程端口 80，地址为 nokey@localhost.run。将输出重定向
到日志文件，等待 10 秒，然后 grep 日志查找 .lhr.life
URL。将 URL 加上 /dashboard/ 后缀提供给用户。
隧道 URL 每次都会变化——如果重启，给用户新的 URL。

<a id="save-and-load"></a>
## 保存与加载

<a id="when-to-save"></a>
### 何时保存
- 每 15-20 回合游戏操作
- 在道馆战、劲敌遭遇或危险战斗之前务必保存
- 进入新城镇或地下城之前
- 在任何你不确定的操作之前

<a id="how-to-save"></a>
### 如何保存
POST /save 并附带一个描述性名称。好的例子：
before_brock, route1_start, mt_moon_entrance, got_cut

<a id="how-to-load"></a>
### 如何加载
POST /load 并附带存档名称。

<a id="list-available-saves"></a>
### 列出可用存档
GET /saves 返回所有已保存的状态。

<a id="loading-on-server-startup"></a>
### 在服务器启动时加载
启动服务器时使用 --load-state 标志自动加载存档。
这比启动后通过 API 加载更快。

<a id="the-gameplay-loop"></a>
## 游戏循环

<a id="step-1-observe-check-state-and-take-a-screenshot"></a>
### 第 1 步：观察——检查状态并截图
GET /state 获取位置、HP、战斗、对话。
GET /screenshot 并保存到 /tmp/pokemon.png，然后使用 vision_analyze。
始终同时执行这两步——RAM 状态提供数字，视觉提供空间感知。
<a id="step-2-orient"></a>
### 第二步：定位
- 屏幕上出现对话/文字 → 推进对话
- 战斗中 → 战斗或逃跑
- 队伍受伤 → 前往宝可梦中心
- 靠近目标 → 小心导航

<a id="step-3-decide"></a>
### 第三步：决策
优先级：对话 > 战斗 > 治疗 > 剧情目标 > 训练 > 探索

<a id="step-4-act-move-2-4-steps-max-then-re-check"></a>
### 第四步：行动——最多移动 2–4 步，然后重新检查
向 `/action` 发送一个短动作列表（2–4 个动作，不要 10–15 个）。

<a id="step-5-verify-screenshot-after-every-move-sequence"></a>
### 第五步：验证——每次移动序列后截图
截取屏幕截图并用 `vision_analyze` 确认你移动到了预期位置。这是**最重要的一步**。没有视觉反馈，你**绝对会**迷路。

<a id="step-6-record-progress-to-memory-with-pkm-prefix"></a>
### 第六步：用 `PKM:` 前缀记录进度到记忆

<a id="step-7-save-periodically"></a>
### 第七步：定期保存

<a id="action-reference"></a>
## 动作参考
- `press_a` — 确认、对话、选择
- `press_b` — 取消、关闭菜单
- `press_start` — 打开游戏菜单
- `walk_up/down/left/right` — 移动一格
- `hold_b_N` — 按住 B 键 N 帧（用于加速跳过文字）
- `wait_60` — 等待约 1 秒（60 帧）
- `a_until_dialog_end` — 重复按 A 直到对话结束

<a id="critical-tips-from-experience"></a>
## 来自经验的关键提示

<a id="use-vision-constantly"></a>
### 持续使用视觉
- 每移动 2–4 步截屏一次
- RAM 状态告诉你位置和血量，但**不会**告诉你周围有什么
- 悬崖、栅栏、路牌、建筑门、NPC——只有截图才能看到
- 向视觉模型提出具体问题：“我北边一格是什么？”
- 卡住时，先截图，再随机方向

<a id="warp-transitions-need-extra-wait-time"></a>
### 传送/切换地图需要额外等待
当穿过门或楼梯时，地图切换过程中屏幕会变黑。你必须等待它完成。任何门/楼梯传送后，添加 2–3 个 `wait_60` 动作。如果不等待，位置信息会变得陈旧，你会以为自己还在旧地图中。

<a id="building-exit-trap"></a>
### 出建筑物陷阱
从建筑物出来时，你会直接出现在**门的前方**。如果向北走，你会直接走回建筑物内。**一定要先侧移**：向左或向右走 2 格，然后再朝目标方向前进。

<a id="dialog-handling"></a>
### 对话处理
第一代游戏文字滚动速度很慢，一个字母一个字母地显示。要快速跳过对话，按住 B 键 120 帧，然后按 A。根据需要重复。按住 B 可以让文字以最快速度显示，然后按 A 进入下一行。`a_until_dialog_end` 动作会检查 RAM 中的对话标志，但这个标志**并不能覆盖所有**文字状态。如果对话似乎卡住了，改用手动 `hold_b + press_a` 模式，并通过截图验证。

<a id="ledges-are-one-way"></a>
### 悬崖是单向的
悬崖（小岩壁）只能向下跳（南），永远不能向上爬（北）。如果向北走的路上被悬崖挡住，你必须向左或向右绕过去。使用视觉判断缺口在哪一侧，明确地向视觉模型提问。

<a id="navigation-strategy"></a>
### 导航策略
- 每次移动 2–4 步，然后截图确认位置
- 进入新区域时，立即截图以定位
- 向视觉模型提问“去 [目的地] 往哪个方向？”
- 如果尝试 3 次以上仍未前进，截图并重新全面评估
- 不要连续发送 10–15 个移动——你会过头或卡住

<a id="running-from-wild-battles"></a>
### 从野生对战中逃跑
在对战菜单中，**逃跑**（RUN）在右下角。要从默认光标位置（**FIGHT**，左上角）到达那里：先按**下**再按**右**将光标移到 RUN，然后按 A。配合按住 B 键加速跳过文字/动画。
<a id="battling-fight"></a>
### 对战（FIGHT）
在战斗菜单中，FIGHT 选项位于左上角（默认光标位置）。
按 A 进入招式选择，再次按 A 使用第一个招式。
然后按住 B 键可快速跳过攻击动画和文本。

<a id="battle-strategy"></a>
## 战斗策略

<a id="decision-tree"></a>
### 决策树
1. 想捕捉？ → 削弱后投掷精灵球
2. 野生精灵不需要？ → 逃跑
3. 有属性优势？ → 使用效果拔群的招式
4. 没有优势？ → 使用最强的同属性攻击加成（STAB）招式
5. 血量低？ → 替换精灵或使用伤药

<a id="gen-1-type-chart-key-matchups"></a>
### 第一世代属性克制表（关键对阵）
- 水克制火、地面、岩石
- 火克制草、虫、冰
- 草克制水、地面、岩石
- 电克制水、飞行
- 地面克制火、电、岩石、毒
- 超能力克制格斗、毒（在第一世代中占主导地位！）

<a id="gen-1-quirks"></a>
### 第一世代特性
- 特殊能力值 = 同时影响特殊招式的攻击与防御
- 超能力属性过强（幽灵招式有 bug）
- 暴击基于速度能力值
- 缠绕/紧束技能使对手无法行动
- 集气 bug：降低暴击率而非提升

<a id="memory-conventions"></a>
## 记忆约定
| 前缀 | 用途 | 示例 |
|--------|---------|---------|
| PKM:OBJECTIVE | 当前目标 | 从常青市商店拿到包裹 |
| PKM:MAP | 导航知识 | 常青市：商店在东北方向 |
| PKM:STRATEGY | 战斗/队伍计划 | 在小霞之前需要草属性精灵 |
| PKM:PROGRESS | 里程碑追踪器 | 击败劲敌，前往常青市 |
| PKM:STUCK | 卡关情况 | 在 y=28 处的悬崖向右走可绕过 |
| PKM:TEAM | 队伍笔记 | 杰尼龟 Lv6，撞击 + 摇尾巴 |

<a id="progression-milestones"></a>
## 进度里程碑
- 选择初始精灵
- 从常青市商店送达包裹，获得图鉴
- 灰色徽章 — 小刚（岩石）→ 使用水/草属性
- 蓝色徽章 — 小霞（水）→ 使用草/电属性
- 电击徽章 — 马志士（电）→ 使用地面属性
- 彩虹徽章 — 莉佳（草）→ 使用火/冰/飞行属性
- 灵魂徽章 — 阿桔（毒）→ 使用地面/超能力属性
- 沼泽徽章 — 娜姿（超能力）→ 最难的道馆
- 火山徽章 — 夏伯（火）→ 使用水/地面属性
- 大地徽章 — 坂木（地面）→ 使用水/草/冰属性
- 四天王 → 冠军！

<a id="stopping-play"></a>
## 停止游戏
1. 通过 POST /save 用描述性名称保存游戏
2. 用 PKM:PROGRESS 更新记忆
3. 告知用户：“游戏已保存为 [名称]！说‘play pokemon’即可继续。”
4. 关闭服务器和隧道后台进程

<a id="pitfalls"></a>
## 注意事项
- 绝不下载或提供 ROM 文件
- 每次检查画面后，最多执行 4-5 个动作
- 离开建筑后往北走之前，务必先侧移一步
- 经过门/楼梯传送后，务必添加 wait_60 x2-3
- 通过 RAM 检测对话不可靠——请用截图确认
- 在遇到危险战斗前务必保存
- 每次重启隧道后，隧道 URL 都会变化
