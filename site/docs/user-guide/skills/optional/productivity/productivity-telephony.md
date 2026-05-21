---
title: "Telephony — 赋予 Hermes 电话能力，无需修改核心工具"
sidebar_label: "Telephony"
description: "赋予 Hermes 电话能力，无需修改核心工具"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

<a id="telephony"></a>
# Telephony

赋予 Hermes 电话能力，无需修改核心工具。配置并永久持有 Twilio 号码，发送和接收 SMS/MMS，直接拨打电话，以及通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/telephony` 安装 |
| 路径 | `optional-skills/productivity/telephony` |
| 版本 | `1.0.0` |
| 作者 | Nous Research |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `telephony`, `phone`, `sms`, `mms`, `voice`, `twilio`, `bland.ai`, `vapi`, `calling`, `texting` |
| 相关技能 | [`maps`](/user-guide/skills/bundled/productivity/productivity-maps), [`google-workspace`](/user-guide/skills/bundled/productivity/productivity-google-workspace), [`agentmail`](/user-guide/skills/optional/email/email-agentmail) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="telephony-numbers-calls-and-texts-without-core-tool-changes"></a>
# Telephony — 无需修改核心工具即可管理号码、通话和短信

这个可选技能赋予 Hermes 实用的电话能力，同时将电话功能排除在核心工具列表之外。

它附带一个辅助脚本 `scripts/telephony.py`，可以：
- 将提供商凭证保存到 `~/.hermes/.env`
- 搜索并购买 Twilio 电话号码
- 记住所拥有的号码以便后续会话使用
- 从所拥有的号码发送 SMS/MMS
- 轮询该号码的入站短信（无需 webhook 服务器）
- 使用 TwiML `&lt;Say&gt;` 或 `&lt;Play&gt;` 直接发起 Twilio 通话
- 将所拥有的 Twilio 号码导入 Vapi
- 通过 Bland.ai 或 Vapi 进行 AI 驱动外呼

<a id="what-this-solves"></a>
## 解决的问题

此技能旨在满足用户实际需要的电话操作任务：
- 外呼
- 发短信
- 拥有一个可重复使用的 Agent 号码
- 检查稍后到达该号码的消息
- 在会话之间保留该号码及相关 ID
- 为入站短信轮询和其他自动化任务提供面向未来的电话标识

它**不会**将 Hermes 变成一个实时入站电话网关。入站短信通过轮询 Twilio REST API 处理。这对许多工作流来说已经足够，包括通知和某些一次性代码获取，而无需添加核心 webhook 基础设施。

<a id="safety-rules-mandatory"></a>
## 安全规则 — 必须遵守

1. 在拨打电话或发送短信之前，务必确认。
2. 切勿拨打紧急号码。
3. 切勿将电话功能用于骚扰、垃圾信息、冒名顶替或任何非法行为。
4. 将第三方电话号码视为敏感操作数据：
   - 不要将它们保存到 Hermes 记忆体中
   - 除非用户明确要求，否则不要将它们包含在技能文档、摘要或后续笔记中
5. 可以持久化 **Agent 拥有的 Twilio 号码**，因为它是用户配置的一部分。
6. **VoIP 号码不保证** 适用于所有第三方双重认证流程。请谨慎使用，并明确告知用户预期。
<a id="decision-tree-which-service-to-use"></a>
## 决策树 — 应该用哪个服务？

用下面这个逻辑来代替硬编码的提供商路由：

<a id="1-i-want-hermes-to-own-a-real-phone-number"></a>
### 1）“我想让 Hermes 拥有一个真实的电话号码”
使用 **Twilio**。

原因：
- 购买和保留号码的最简单途径
- 最好的 SMS / MMS 支持
- 最简单的入站 SMS 轮询方案
- 未来处理入站 webhook 或电话呼叫的最清晰路径

使用场景：
- 之后接收短信
- 发送部署告警 / cron 通知
- 为 Agent 维护一个可复用的电话号码身份
- 之后尝试基于电话的认证流程

<a id="2-i-only-need-the-easiest-outbound-ai-phone-call-right-now"></a>
### 2）“我现在只需要最简单的出站 AI 电话”
使用 **Bland.ai**。

原因：
- 搭建最快
- 一个 API key 即可
- 无需先自己购买/导入号码

权衡：
- 灵活性较低
- 语音质量尚可，但不是最好

<a id="3-i-want-the-best-conversational-ai-voice-quality"></a>
### 3）“我想要最好的对话式 AI 语音质量”
使用 **Twilio + Vapi**。

原因：
- Twilio 提供你拥有的号码
- Vapi 提供更好的对话式 AI 通话质量和更多的语音/模型灵活性

推荐流程：
1. 购买/保存一个 Twilio 号码
2. 将其导入 Vapi
3. 保存返回的 `VAPI_PHONE_NUMBER_ID`
4. 使用 `ai-call --provider vapi`

<a id="4-i-want-to-call-with-a-custom-prerecorded-voice-message"></a>
### 4）“我想用自定义预录语音消息打电话”
使用带有公共音频 URL 的 **Twilio 直拨电话**。

原因：
- 播放自定义 MP3 的最简单方式
- 配合 Hermes 的 `text_to_speech` 以及公共文件托管或隧道效果很好

<a id="files-and-persistent-state"></a>
## 文件和持久状态

该 Skill 在两个位置持久化电话状态：

<a id="hermes-env"></a>
### `~/.hermes/.env`
用于长期有效的提供商凭证和拥有的号码 ID，例如：
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `TWILIO_PHONE_NUMBER_SID`
- `BLAND_API_KEY`
- `VAPI_API_KEY`
- `VAPI_PHONE_NUMBER_ID`
- `PHONE_PROVIDER`（AI 通话提供商：bland 或 vapi）

<a id="hermes-telephonystate-json"></a>
### `~/.hermes/telephony_state.json`
用于只属于该 Skill 且应在会话间持久化的状态，例如：
- 记住的默认 Twilio 号码 / SID
- 记住的 Vapi 电话号码 ID
- 上次入站消息的 SID/日期（用于收件箱轮询检查点）

这意味着：
- 下次加载该 Skill 时，`diagnose` 可以告诉你已配置的号码
- `twilio-inbox --since-last --mark-seen` 可以从上一个检查点继续

<a id="locate-the-helper-script"></a>
## 找到辅助脚本

安装此 Skill 后，这样定位脚本：

```bash
SCRIPT="$(find ~/.hermes/skills -path '*/telephony/scripts/telephony.py' -print -quit)"
```

如果 `SCRIPT` 为空，说明该 Skill 尚未安装。

<a id="install"></a>
## 安装

这是一个官方可选 Skill，所以请从 Skill 中心安装：

```bash
hermes skills search telephony
hermes skills install official/productivity/telephony
```

<a id="provider-setup"></a>
## 提供商设置

<a id="twilio-owned-number-sms-mms-direct-calls-inbound-sms-polling"></a>
### Twilio — 拥有的号码、SMS/MMS、直拨电话、入站 SMS 轮询

注册地址：
- https://www.twilio.com/try-twilio

然后将凭据保存到 Hermes：

```bash
python3 "$SCRIPT" save-twilio ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_auth_token_here
```

搜索可用号码：

```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 5
```

购买并记住一个号码：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

列出已拥有的号码：

```bash
python3 "$SCRIPT" twilio-owned
```

稍后将其中一个设为默认：

```bash
python3 "$SCRIPT" twilio-set-default "+17025551234" --save-env
# 或
python3 "$SCRIPT" twilio-set-default PNXXXXXXXXXXXXXXXXXXXXXXXXXXXX --save-env
```

<a id="bland-ai-easiest-outbound-ai-calling"></a>
### Bland.ai — 最简单的 AI 外呼方案

注册地址：
- https://app.bland.ai

保存配置：

```bash
python3 "$SCRIPT" save-bland your_bland_api_key --voice mason
```

<a id="vapi-better-conversational-voice-quality"></a>
### Vapi — 更优质的对话语音质量

注册地址：
- https://dashboard.vapi.ai

先保存 API 密钥：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key
```

将你拥有的 Twilio 号码导入 Vapi，并保存返回的电话号码 ID：

```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

如果你已经知道 Vapi 的电话号码 ID，可以直接保存：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key --phone-number-id vapi_phone_number_id_here
```

<a id="diagnose-current-state"></a>
## 诊断当前状态

随时查看该技能已知的信息：

```bash
python3 "$SCRIPT" diagnose
```

在后续会话中恢复工作时，请先执行此命令。

<a id="common-workflows"></a>
## 常见工作流

<a id="a-buy-an-agent-number-and-keep-using-it-later"></a>
### A. 购买一个 Agent 号码并稍后继续使用

1. 保存 Twilio 凭据：
```bash
python3 "$SCRIPT" save-twilio AC... auth_token_here
```

2. 搜索号码：
```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 10
```

3. 购买号码并将其保存到 `~/.hermes/.env` 和状态中：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

4. 下次会话时运行：
```bash
python3 "$SCRIPT" diagnose
```
这会显示已记住的默认号码和收件箱检查点状态。

<a id="b-send-a-text-from-the-agent-number"></a>
### B. 从 Agent 号码发送短信

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Your deployment completed successfully."
```

附带媒体文件：

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Here is the chart." --media-url "https://example.com/chart.png"
```

<a id="c-check-inbound-texts-later-with-no-webhook-server"></a>
### C. 稍后无需 Webhook 服务器即可检查收到的短信

轮询默认 Twilio 号码的收件箱：

```bash
python3 "$SCRIPT" twilio-inbox --limit 20
```

仅显示上次检查点之后到达的消息，并在阅读完毕后将检查点前移：

```bash
python3 "$SCRIPT" twilio-inbox --since-last --mark-seen
```

这是“下次加载技能时如何访问该号码收到的消息？”的主要答案。

<a id="d-make-a-direct-twilio-call-with-built-in-tts"></a>
### D. 使用内置 TTS 发起直接 Twilio 通话

```bash
python3 "$SCRIPT" twilio-call "+15551230000" --message "Hello! This is Hermes calling with your status update." --voice Polly.Joanna
```

<a id="e-call-with-a-prerecorded-custom-voice-message"></a>
### E. 使用预录 / 自定义语音消息进行通话

这是复用 Hermes 现有 `text_to_speech` 支持的主要路径。

适用场景：
- 希望通话使用 Hermes 配置的 TTS 语音，而非 Twilio `&lt;Say&gt;`
- 需要单向语音传递（简报、提醒、笑话、通知、状态更新）
- **不需要** 实时的对话式电话通话

单独生成或托管音频，然后：
```bash
python3 "$SCRIPT" twilio-call "+155****0000" --audio-url "https://example.com/briefing.mp3"
```

推荐的 Hermes TTS -> Twilio Play 工作流程：

1.  使用 Hermes `text_to_speech` 生成音频。
2.  将生成的 MP3 文件公开可访问。
3.  使用 `--audio-url` 发起 Twilio 电话呼叫。

示例 Agent 流程：
- 要求 Hermes 使用 `text_to_speech` 创建消息音频
- 如有需要，通过临时静态主机/隧道/对象存储 URL 暴露文件
- 使用 `twilio-call --audio-url ...` 通过电话发送

MP3 的良好托管选项：
- 临时的公共对象/存储 URL
- 指向本地静态文件服务器的短期隧道
- 电话运营商可以直接获取的任何现有 HTTPS URL

重要说明：
- Hermes TTS 适合预录的外呼消息
- Bland/Vapi **更适合实时对话式 AI 通话**，因为它们自己处理实时电话音频栈
- 此处的 Hermes STT/TTS 并未用作全双工电话会话引擎；要实现全双工通话，需要比本技能介绍的更复杂的流式/webhook 集成

<a id="f-navigate-a-phone-tree-ivr-with-twilio-direct-calling"></a>
### F. 通过 Twilio 直接拨号导航电话树/IVR

如果在通话接通后需要按键，请使用 `--send-digits`。
Twilio 将 `w` 解释为短暂等待。

```bash
python3 "$SCRIPT" twilio-call "+18005551234" --message "正在为您转接账单部门。" --send-digits "ww1w2w3"
```

这在转接给人工或发送简短状态消息之前，需要到达特定菜单分支时非常有用。

<a id="g-outbound-ai-phone-call-with-bland-ai"></a>
### G. 使用 Bland.ai 进行外呼 AI 电话

```bash
python3 "$SCRIPT" ai-call "+15551230000" "Call the dental office, ask for a cleaning appointment on Tuesday afternoon, and if they do not have Tuesday availability, ask for Wednesday or Thursday instead." --provider bland --voice mason --max-duration 3
```

检查状态：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland
```

通话结束后询问 Bland 分析问题：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland --analyze "Was the appointment confirmed?,What date and time?,Any special instructions?"
```

<a id="h-outbound-ai-phone-call-with-vapi-on-your-owned-number"></a>
### H. 使用您名下的号码通过 Vapi 进行外呼 AI 电话

1.  将您的 Twilio 号码导入 Vapi：
```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

2.  拨打电话：
```bash
python3 "$SCRIPT" ai-call "+15551230000" "You are calling to make a dinner reservation for two at 7:30 PM. If that is unavailable, ask for the nearest time between 6:30 and 8:30 PM." --provider vapi --max-duration 4
```

3.  检查结果：
```bash
python3 "$SCRIPT" ai-status <call_id> --provider vapi
```

<a id="suggested-agent-procedure"></a>
## 建议的 Agent 流程

当用户请求拨打电话或发送短信时：

1.  通过决策树确定适合的路径。
2.  如果配置状态不清晰，运行 `diagnose`。
3.  收集完整的任务细节。
4.  在拨号或发送短信前与用户确认。
5.  使用正确的命令。
6.  如有需要，轮询结果。
7.  总结结果，不要将第三方号码持久化到 Hermes 记忆中。
<a id="what-this-skill-still-does-not-do"></a>
## 该技能仍不支持的功能

- 实时接听来电
- 基于 webhook 的实时短信推送至 Agent 循环
- 保证支持任意第三方 2FA 提供商

这些功能需要的底层基础设施远超一个纯可选技能。

<a id="pitfalls"></a>
## 陷阱

- Twilio 试用账户和地区规则可能会限制你能呼叫或发送短信的对象。
- 某些服务会拒绝 VoIP 号码用于 2FA。
- `twilio-inbox` 轮询 REST API，并非即时推送。
- Vapi 外呼仍然依赖于一个有效的已导入号码。
- Bland 最简单，但音质不一定最好。
- 不要将任意第三方电话号码存储在 Hermes 记忆体中。

<a id="verification-checklist"></a>
## 验证清单

设置完成后，你应该能够仅凭此技能完成以下所有操作：

1. `diagnose` 显示提供者就绪状态和已记忆的状态
2. 搜索并购买一个 Twilio 号码
3. 将该号码持久化到 `~/.hermes/.env`
4. 从拥有的号码发送一条短信
5. 稍后轮询该号码的入站短信
6. 通过 Twilio 直接拨打电话
7. 通过 Bland 或 Vapi 发起 AI 通话

<a id="references"></a>
## 参考链接

- Twilio 电话号码：https://www.twilio.com/docs/phone-numbers/api
- Twilio 消息服务：https://www.twilio.com/docs/messaging/api/message-resource
- Twilio 语音服务：https://www.twilio.com/docs/voice/api/call-resource
- Vapi 文档：https://docs.vapi.ai/
- Bland.ai：https://app.bland.ai/
