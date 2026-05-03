---
title: "Pokemon Player — 通过无头模拟器 + RAM 读取玩宝可梦"
sidebar_label: "Pokemon Player"
description: "通过无头模拟器 + RAM 读取玩宝可梦"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Pokemon Player {#pokemon-player}

通过无头模拟器 + RAM 读取玩宝可梦。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/gaming/pokemon-player` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

<a id="pokemon-player"></a>
# Pokemon Player

使用 `pokemon-agent` 包通过无头模拟玩宝可梦游戏。

## 何时使用 {#when-to-use}
- 用户说“玩宝可梦”、“开始宝可梦”、“宝可梦游戏”
- 用户询问关于宝可梦红、蓝、黄、火红等版本
- 用户想观看 AI 玩宝可梦
- 用户提到 ROM 文件（.gb、.gbc、.gba）

## 启动流程 {#startup-procedure}

### 1. 首次设置（克隆、虚拟环境、安装） {#1-first-time-setup-clone-venv-install}
仓库是 GitHub 上的 NousResearch/pokemon-agent。克隆它，然后设置 Python 3.10+ 虚拟环境。使用 uv（推荐，速度更快）创建虚拟环境并以可编辑模式安装包，同时安装 pyboy 额外依赖。如果 uv 不可用，则回退到 python3 -m venv + pip。

在这台机器上，它已经设置在 /home/teknium/pokemon-agent，并且虚拟环境已就绪——只需 cd 到该目录并执行 source .venv/bin/activate。

你还需要一个 ROM 文件。向用户索要他们的 ROM。在这台机器上，该目录下有一个 roms/pokemon_red.gb 文件。
**切勿下载或提供 ROM 文件**——始终向用户索要。

### 2. 启动游戏服务器 {#2-start-the-game-server}
在 pokemon-agent 目录内，激活虚拟环境后，运行 pokemon-agent serve，使用 --rom 指向 ROM，--port 指定为 9876。在后台运行（加 &）。
要从存档恢复，添加 --load-state 并指定存档名称。
等待 4 秒启动，然后用 GET /health 验证。

### 3. 为用户设置实时仪表盘 {#3-set-up-live-dashboard-for-user-to-watch}
通过 localhost.run 使用 SSH 反向隧道，让用户可以在浏览器中查看仪表盘。连接 ssh，将本地端口 9876 转发到远程端口 80，目标为 nokey@localhost.run。将输出重定向到日志文件，等待 10 秒，然后从日志中 grep 出 .lhr.life 的 URL。将 URL 加上 /dashboard/ 后缀提供给用户。
隧道 URL 每次都会变化——如果重启，请给用户新的 URL。

## 存档与读档 {#save-and-load}

### 何时存档 {#when-to-save}
- 每 15-20 个游戏回合
- **始终**在道馆战、劲敌遭遇或危险战斗前
- 进入新城镇或迷宫前
- 任何你不确定的行动前

### 如何存档 {#how-to-save}
POST /save，附带描述性名称。好的例子：
before_brock、route1_start、mt_moon_entrance、got_cut

### 如何读档 {#how-to-load}
POST /load，附带存档名称。

### 列出可用存档 {#list-available-saves}
GET /saves 返回所有已保存的状态。

### 在服务器启动时加载 {#loading-on-server-startup}
启动服务器时使用 --load-state 标志自动加载存档。这比启动后通过 API 加载更快。

## 游戏循环 {#the-gameplay-loop}

### 步骤 1：观察——检查状态并截图 {#step-1-observe-check-state-and-take-a-screenshot}
GET /state 获取位置、HP、战斗、对话信息。
GET /screenshot 并保存到 /tmp/pokemon.png，然后使用 vision_analyze。
**始终同时执行这两步**——RAM 状态提供数字，视觉提供空间感知。
### 步骤 2：定向（ORIENT） {#step-2-orient}
- 屏幕上有对话/文字 → 推进对话
- 处于战斗中 → 战斗或逃跑
- 队伍受伤 → 前往宝可梦中心
- 靠近目标 → 小心导航

### 步骤 3：决策（DECIDE） {#step-3-decide}
优先级：对话 > 战斗 > 回复 > 剧情目标 > 训练 > 探索

### 步骤 4：行动（ACT）—— 最多移动 2-4 步，然后重新检查 {#step-4-act-move-2-4-steps-max-then-re-check}
POST /action 带一个简短动作列表（2-4 个动作，而不是 10-15 个）。

### 步骤 5：验证（VERIFY）—— 每次移动序列后截图 {#step-5-verify-screenshot-after-every-move-sequence}
截图并使用 vision_analyze 确认你移动到了预期的位置。这是**最重要的步骤**。没有视觉你**一定会**迷路。

### 步骤 6：用 PKM: 前缀将进度记录到记忆中 {#step-6-record-progress-to-memory-with-pkm-prefix}

### 步骤 7：定期保存 {#step-7-save-periodically}

## 动作参考 {#action-reference}
- press_a — 确认、对话、选择
- press_b — 取消、关闭菜单
- press_start — 打开游戏菜单
- walk_up/down/left/right — 移动一格
- hold_b_N — 按住 B 键 N 帧（用于快速跳过文字）
- wait_60 — 等待约 1 秒（60 帧）
- a_until_dialog_end — 重复按 A 直到对话结束

## 经验中的关键提示 {#critical-tips-from-experience}

### 持续使用视觉（USE VISION CONSTANTLY） {#use-vision-constantly}
- 每移动 2-4 步截一次图
- RAM 状态能告诉你位置和血量，但**不能**告诉你周围有什么
- 悬崖、栅栏、路牌、建筑门、NPC —— 只能通过截图看到
- 向视觉模型提出具体问题：“我北边一格是什么？”
- 卡住时，先截图再乱试方向

### 传送门过图需要额外等待时间 {#warp-transitions-need-extra-wait-time}
穿过门或楼梯时，过图动画中屏幕会变黑。你必须等待动画完成。在每次门/楼梯传送后，额外加入 2-3 个 wait_60 动作。如果不等待，位置数据会变得过时，你会以为自己还在旧地图。

### 建筑出口陷阱 {#building-exit-trap}
当走出建筑时，你会直接出现在门**正前方**。如果向北走，你会直接走回建筑内。**始终**先向左或向右移动 2 格侧移，然后再朝你打算的方向走。

### 对话处理 {#dialog-handling}
第一代游戏文字是一字一字缓慢滚动的。要快速通过对话，按住 B 120 帧然后按 A。根据需要重复。按住 B 键能让文字以最快速度显示，然后按 A 推进到下一行。a_until_dialog_end 动作会检查 RAM 对话标志，但这个标志并不能捕捉到所有文字状态。如果对话卡住了，改用手动 hold_b + press_a 模式，并通过截图验证。

### 悬崖是单向的 {#ledges-are-one-way}
悬崖（小断崖）只能向下（南）跳，不能向上（北）爬。如果向北被悬崖挡住，你必须向左或向右绕过去。用视觉识别缺口的方向，明确向视觉模型提问。

### 导航策略 {#navigation-strategy}
- 每次移动 2-4 步，然后截图检查位置
- 进入新区域时立即截图以定方位
- 向视觉模型提问“到[目的地]该往哪个方向？”
- 如果尝试 3+ 次仍卡住，拍照并完全重新评估
- 不要一次发送 10-15 步移动——你会跑过头或卡住

### 从野生战斗中逃跑 {#running-from-wild-battles}
在战斗菜单中，逃跑（RUN）在右下角。从默认光标位置（FIGHT，左上角）到达那里：先按下再按右将光标移到 RUN，然后按 A。配合按住 B 键快速跳过文字/动画。
### 对战 (FIGHT) {#battling-fight}
在战斗菜单中，FIGHT 位于左上角（默认光标位置）。
按 A 进入招式选择，再次按 A 使用第一个招式。
然后按住 B 加速跳过攻击动画和文本。

## 战斗策略 {#battle-strategy}

### 决策树 {#decision-tree}
1. 想抓？→ 削弱后投掷精灵球
2. 野生精灵不需要？→ 逃跑
3. 有属性优势？→ 使用效果拔群的招式
4. 没有优势？→ 使用最强的同系加成招式
5. HP 较低？→ 交换或使用药水

### 第一代属性相克表（关键对战） {#gen-1-type-chart-key-matchups}
- 水克制火、地面、岩石
- 火克制草、虫、冰
- 草克制水、地面、岩石
- 电克制水、飞行
- 地面克制火、电、岩石、毒
- 超能克制格斗、毒（在第一代中非常强势！）

### 第一代特性 {#gen-1-quirks}
- 特殊能力值 = 特殊招式的攻击和防御两者
- 超能属性过于强大（幽灵招式有bug）
- 暴击基于速度能力值
- 缠绕/绑紧阻止对手行动
- 聚气bug：降低暴击率而非提高

## 记忆约定 {#memory-conventions}
| 前缀 | 用途 | 示例 |
|--------|---------|---------|
| PKM:OBJECTIVE | 当前目标 | 从常青市商店取包裹 |
| PKM:MAP | 导航知识 | 常青市：商店在东北面 |
| PKM:STRATEGY | 战斗/队伍计划 | 在小霞之前需要草系 |
| PKM:PROGRESS | 里程碑追踪 | 击败劲敌，前往常青市 |
| PKM:STUCK | 卡住情况 | y=28 处的悬崖，向右走绕过 |
| PKM:TEAM | 队伍笔记 | 杰尼龟 Lv6，撞击+摇尾巴 |

## 进度里程碑 {#progression-milestones}
- 选择初始宝可梦
- 从常青市商店交付包裹，获得图鉴
- 岩石徽章 — 小刚（岩石）→ 使用水/草
- 瀑布徽章 — 小霞（水）→ 使用草/电
- 雷电徽章 — 马志士（电）→ 使用地面
- 彩虹徽章 — 艾莉佳（草）→ 使用火/冰/飞行
- 灵魂徽章 — 阿桔（毒）→ 使用地面/超能
- 沼泽徽章 — 娜姿（超能）→ 最难的道馆
- 火山徽章 — 夏伯（火）→ 使用水/地面
- 大地徽章 — 坂木（地面）→ 使用水/草/冰
- 四天王 → 冠军！

## 停止游戏 {#stopping-play}
1. 通过 POST /save 以描述性名称保存游戏
2. 用 PKM:PROGRESS 更新记忆
3. 告诉用户：“游戏已保存为 [name]！说‘play pokemon’可继续。”
4. 终止服务器和隧道后台进程

## 注意事项 {#pitfalls}
- 切勿下载或提供 ROM 文件
- 不要连续发送超过 4-5 个动作而不检查视野
- 从建筑出来后，在向北走之前务必先侧移
- 在门/楼梯传送后，始终添加 wait_60 x2-3
- 通过 RAM 检测对话不可靠 — 请用截图确认
- 在危险遭遇之前保存
- 隧道 URL 每次重启都会变化
