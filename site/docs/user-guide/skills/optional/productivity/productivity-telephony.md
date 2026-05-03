---
title: "Telephony — 在不修改核心工具的前提下，为 Hermes 赋予电话能力"
sidebar_label: "Telephony"
description: "在不修改核心工具的前提下，为 Hermes 赋予电话能力"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Telephony {#telephony}

在不修改核心工具的前提下，为 Hermes 赋予电话能力。可以申请并持久化一个 Twilio 号码，发送和接收 SMS/MMS，直接拨打电话，以及通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/telephony` 安装 |
| 路径 | `optional-skills/productivity/telephony` |
| 版本 | `1.0.0` |
| 作者 | Nous Research |
| 许可证 | MIT |
| 标签 | `telephony`, `phone`, `sms`, `mms`, `voice`, `twilio`, `bland.ai`, `vapi`, `calling`, `texting` |
| 相关技能 | [`maps`](/user-guide/skills/bundled/productivity/productivity-maps), [`google-workspace`](/user-guide/skills/bundled/productivity/productivity-google-workspace), [`agentmail`](/user-guide/skills/optional/email/email-agentmail) |

## 参考：完整的 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，Agent 会将其视为指令。
:::

# Telephony — 无需修改核心工具即可处理号码、通话和短信 {#telephony-numbers-calls-and-texts-without-core-tool-changes}

这个可选技能为 Hermes 提供了实用的电话能力，同时将电话功能排除在核心工具列表之外。

它附带一个辅助脚本 `scripts/telephony.py`，可以：
- 将提供商凭证保存到 `~/.hermes/.env`
- 搜索并购买一个 Twilio 电话号码
- 记住该拥有的号码，以便后续会话使用
- 从拥有的号码发送 SMS / MMS
- 轮询该号码的入站短信，无需 webhook 服务器
- 使用 TwiML `&lt;Say&gt;` 或 `&lt;Play&gt;` 直接进行 Twilio 通话
- 将拥有的 Twilio 号码导入 Vapi
- 通过 Bland.ai 或 Vapi 进行 AI 外呼

## 解决的问题 {#what-this-solves}

此技能旨在覆盖用户实际需要的电话任务：
- 外呼
- 发短信
- 拥有一个可复用的 Agent 号码
- 稍后检查发送到该号码的消息
- 在会话之间保留该号码及相关 ID
- 为入站短信轮询和其他自动化提供面向未来的电话身份

它**不会**将 Hermes 变成一个实时的入站电话网关。入站短信通过轮询 Twilio REST API 处理。这对于许多工作流（包括通知和某些一次性验证码获取）来说已经足够，且无需添加核心 webhook 基础设施。

## 安全规则 — 必须遵守 {#safety-rules-mandatory}

1. 在拨打电话或发送短信之前，务必先确认。
2. 切勿拨打紧急号码。
3. 切勿将电话功能用于骚扰、垃圾信息、冒充他人或任何非法行为。
4. 将第三方电话号码视为敏感操作数据：
   - 不要将其保存到 Hermes 记忆
   - 除非用户明确要求，否则不要将其包含在技能文档、摘要或后续笔记中
5. 可以持久化**Agent 拥有的 Twilio 号码**，因为这是用户配置的一部分。
6. **不保证** VoIP 号码能用于所有第三方双因素认证流程。请谨慎使用，并明确告知用户预期。
## 决策树 — 该用哪个服务？ {#decision-tree-which-service-to-use}

请使用以下逻辑，而不是硬编码的提供商路由：

### 1) "我希望 Hermes 拥有一个真实的电话号码" {#1-i-want-hermes-to-own-a-real-phone-number}
使用 **Twilio**。

原因：
- 购买和保留号码的最简单途径
- 最佳的 SMS / MMS 支持
- 最简单的入站 SMS 轮询方案
- 未来接入入站 webhook 或呼叫处理的最清晰路径

使用场景：
- 稍后接收短信
- 发送部署告警 / cron 通知
- 为 Agent 维护一个可复用的电话身份
- 后续尝试基于电话的身份验证流程

### 2) "我现在只需要最简单的出站 AI 电话呼叫" {#2-i-only-need-the-easiest-outbound-ai-phone-call-right-now}
使用 **Bland.ai**。

原因：
- 设置最快
- 一个 API 密钥即可
- 无需先自行购买/导入号码

权衡：
- 灵活性较低
- 语音质量尚可，但不是最佳

### 3) "我想要最好的对话式 AI 语音质量" {#3-i-want-the-best-conversational-ai-voice-quality}
使用 **Twilio + Vapi**。

原因：
- Twilio 提供你拥有的号码
- Vapi 提供更好的对话式 AI 呼叫质量和更多的语音/模型灵活性

推荐流程：
1. 购买/保存一个 Twilio 号码
2. 将其导入 Vapi
3. 保存返回的 `VAPI_PHONE_NUMBER_ID`
4. 使用 `ai-call --provider vapi`

### 4) "我想用自定义预录语音消息拨打电话" {#4-i-want-to-call-with-a-custom-prerecorded-voice-message}
使用带有公共音频 URL 的 **Twilio 直接呼叫**。

原因：
- 播放自定义 MP3 的最简单方式
- 与 Hermes `text_to_speech` 配合良好，再加上公共文件托管或隧道

## 文件和持久化状态 {#files-and-persistent-state}

该技能在两个位置持久化电话状态：

### `~/.hermes/.env` {#hermes-env}
用于长期有效的提供商凭证和拥有的号码 ID，例如：
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `TWILIO_PHONE_NUMBER_SID`
- `BLAND_API_KEY`
- `VAPI_API_KEY`
- `VAPI_PHONE_NUMBER_ID`
- `PHONE_PROVIDER`（AI 呼叫提供商：bland 或 vapi）

### `~/.hermes/telephony_state.json` {#hermes-telephonystate-json}
用于仅技能自身使用、且应在会话间持久化的状态，例如：
- 记住的默认 Twilio 号码 / SID
- 记住的 Vapi 电话号码 ID
- 用于收件箱轮询检查点的最后一条入站消息 SID/日期

这意味着：
- 下次加载该技能时，`diagnose` 可以告诉你已配置了哪个号码
- `twilio-inbox --since-last --mark-seen` 可以从上一个检查点继续

## 定位辅助脚本 {#locate-the-helper-script}

安装此技能后，按如下方式定位脚本：

```bash
SCRIPT="$(find ~/.hermes/skills -path '*/telephony/scripts/telephony.py' -print -quit)"
```

如果 `SCRIPT` 为空，则表示该技能尚未安装。

## 安装 {#install}

这是一个官方可选技能，请从技能中心安装：

```bash
hermes skills search telephony
hermes skills install official/productivity/telephony
```

## 提供商设置 {#provider-setup}

### Twilio — 拥有的号码、SMS/MMS、直接呼叫、入站 SMS 轮询 {#twilio-owned-number-sms-mms-direct-calls-inbound-sms-polling}

在以下地址注册：
- https://www.twilio.com/try-twilio

然后将凭证保存到 Hermes：

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

稍后将其中一个设为默认号码：

```bash
python3 "$SCRIPT" twilio-set-default "+17025551234" --save-env
# 或
python3 "$SCRIPT" twilio-set-default PNXXXXXXXXXXXXXXXXXXXXXXXXXXXX --save-env
```

### Bland.ai — 最简单的出站 AI 通话 {#bland-ai-easiest-outbound-ai-calling}

注册地址：
- https://app.bland.ai

保存配置：

```bash
python3 "$SCRIPT" save-bland your_bland_api_key --voice mason
```

### Vapi — 更好的对话语音质量 {#vapi-better-conversational-voice-quality}

注册地址：
- https://dashboard.vapi.ai

先保存 API 密钥：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key
```

将你拥有的 Twilio 号码导入 Vapi，并保留返回的电话号码 ID：

```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

如果你已经知道 Vapi 的电话号码 ID，可以直接保存：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key --phone-number-id vapi_phone_number_id_here
```

## 诊断当前状态 {#diagnose-current-state}

随时检查技能已掌握的信息：

```bash
python3 "$SCRIPT" diagnose
```

在后续会话中恢复工作时，请先运行此命令。

## 常见工作流 {#common-workflows}

### A. 购买一个 Agent 号码并后续继续使用 {#a-buy-an-agent-number-and-keep-using-it-later}

1. 保存 Twilio 凭据：
```bash
python3 "$SCRIPT" save-twilio AC... auth_token_here
```

2. 搜索号码：
```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 10
```

3. 购买号码并保存到 `~/.hermes/.env` 及状态中：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

4. 下次会话时，运行：
```bash
python3 "$SCRIPT" diagnose
```
这将显示已记住的默认号码和收件箱检查点状态。

### B. 从 Agent 号码发送短信 {#b-send-a-text-from-the-agent-number}

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Your deployment completed successfully."
```

带附件：

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Here is the chart." --media-url "https://example.com/chart.png"
```

### C. 稍后检查入站短信（无需 Webhook 服务器） {#c-check-inbound-texts-later-with-no-webhook-server}

轮询默认 Twilio 号码的收件箱：

```bash
python3 "$SCRIPT" twilio-inbox --limit 20
```

仅显示上次检查点之后到达的消息，并在阅读完毕后推进检查点：

```bash
python3 "$SCRIPT" twilio-inbox --since-last --mark-seen
```

这是对“下次加载技能时如何访问号码收到的消息？”这一问题的核心回答。

### D. 使用内置 TTS 发起直接 Twilio 通话 {#d-make-a-direct-twilio-call-with-built-in-tts}

```bash
python3 "$SCRIPT" twilio-call "+15551230000" --message "Hello! This is Hermes calling with your status update." --voice Polly.Joanna
```

### E. 使用预录/自定义语音消息进行通话 {#e-call-with-a-prerecorded-custom-voice-message}

这是复用 Hermes 现有 `text_to_speech` 支持的主要路径。

在以下场景使用：
- 你希望通话使用 Hermes 配置的 TTS 语音，而非 Twilio 的 `&lt;Say&gt;`
- 你希望进行单向语音传递（简报、提醒、笑话、状态更新）
- 你**不需要**实时对话式通话

请单独生成或托管音频，然后：

--- END DOCUMENT CHUNK ---
```bash
python3 "$SCRIPT" twilio-call "+155****0000" --audio-url "https://example.com/briefing.mp3"
```

推荐的 Hermes TTS → Twilio Play 工作流程：

1. 使用 Hermes `text_to_speech` 生成音频。
2. 将生成的 MP3 文件设置为可公开访问。
3. 使用 `--audio-url` 发起 Twilio 通话。

示例 Agent 流程：
- 让 Hermes 用 `text_to_speech` 创建消息音频
- 如果需要，通过临时静态主机/隧道/对象存储 URL 暴露文件
- 使用 `twilio-call --audio-url ...` 通过电话发送

MP3 的合适托管选项：
- 临时公共对象/存储 URL
- 指向本地静态文件服务器的短期隧道
- 电话提供商可以直接获取的任何现有 HTTPS URL

重要提示：
- Hermes TTS 非常适合预录的外呼消息
- Bland/Vapi 更适合**实时对话式 AI 通话**，因为它们自己处理实时电话音频栈
- 这里并未将 Hermes STT/TTS 单独用作全双工电话对话引擎；那需要比本技能所介绍的更重的流式/webhook 集成

### F. 通过 Twilio 直接呼叫导航电话树/IVR {#f-navigate-a-phone-tree-ivr-with-twilio-direct-calling}

如果需要在通话接通后按键，请使用 `--send-digits`。
Twilio 将 `w` 解释为短暂等待。

```bash
python3 "$SCRIPT" twilio-call "+18005551234" --message "正在连接至账单部门。" --send-digits "ww1w2w3"
```

这在转接给人工或发送简短状态消息之前，用于到达特定菜单分支时非常有用。

### G. 使用 Bland.ai 进行外呼 AI 电话 {#g-outbound-ai-phone-call-with-bland-ai}

```bash
python3 "$SCRIPT" ai-call "+15551230000" "致电牙科诊所，预约周二下午的洗牙服务；如果周二没有空位，则询问周三或周四。" --provider bland --voice mason --max-duration 3
```

检查状态：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland
```

通话完成后向 Bland 询问分析问题：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland --analyze "预约是否确认？,日期和时间是什么？,是否有特殊说明？"
```

### H. 使用 Vapi 通过自有号码进行外呼 AI 电话 {#h-outbound-ai-phone-call-with-vapi-on-your-owned-number}

1. 将你的 Twilio 号码导入 Vapi：
```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

2. 发起通话：
```bash
python3 "$SCRIPT" ai-call "+15551230000" "你正在致电预订两人晚餐，时间为晚上 7:30。如果该时间不可用，请询问晚上 6:30 到 8:30 之间最近的时间。" --provider vapi --max-duration 4
```

3. 检查结果：
```bash
python3 "$SCRIPT" ai-status <call_id> --provider vapi
```

## 建议的 Agent 流程 {#suggested-agent-procedure}

当用户要求拨打电话或发送短信时：

1. 通过决策树确定适合的路径。
2. 如果配置状态不明确，运行 `diagnose`。
3. 收集完整的任务细节。
4. 在拨号或发送短信前与用户确认。
5. 使用正确的命令。
6. 如果需要，轮询结果。
7. 总结结果，不要将第三方号码持久化到 Hermes 记忆中。
## 该技能目前仍不支持的功能 {#what-this-skill-still-does-not-do}

- 实时接听来电
- 基于 webhook 的实时短信推送至 agent loop
- 对任意第三方 2FA 提供商的保证支持

这些功能需要比纯可选技能更复杂的基础设施。

## 注意事项 {#pitfalls}

- Twilio 试用账户和地区规则可能会限制可呼叫或发送短信的对象。
- 某些服务会拒绝使用 VoIP 号码进行 2FA。
- `twilio-inbox` 通过轮询 REST API 实现，并非即时推送。
- Vapi 外呼仍依赖于拥有有效的导入号码。
- Bland 最简单，但音质不一定最好。
- 不要将任意第三方电话号码存储在 Hermes 内存中。

## 验证清单 {#verification-checklist}

完成设置后，你应该能够仅凭此技能完成以下所有操作：

1. `diagnose` 显示提供商就绪状态和已记忆的状态
2. 搜索并购买一个 Twilio 号码
3. 将该号码持久化到 `~/.hermes/.env`
4. 从拥有的号码发送短信
5. 稍后轮询该号码的接收短信
6. 发起直接 Twilio 呼叫
7. 通过 Bland 或 Vapi 发起 AI 呼叫

## 参考链接 {#references}

- Twilio 电话号码：https://www.twilio.com/docs/phone-numbers/api
- Twilio 消息服务：https://www.twilio.com/docs/messaging/api/message-resource
- Twilio 语音：https://www.twilio.com/docs/voice/api/call-resource
- Vapi 文档：https://docs.vapi.ai/
- Bland.ai：https://app.bland.ai/
