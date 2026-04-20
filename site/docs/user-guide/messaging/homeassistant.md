---
title: Home Assistant
description: 通过 Home Assistant 集成，使用 Hermes Agent 控制您的智能家居。
sidebar_label: Home Assistant
sidebar_position: 5
---

# Home Assistant 集成 {#home-assistant-integration}

Hermes Agent 通过两种方式与 [Home Assistant](https://www.home-assistant.io/) 集成：

1. **网关平台 (Gateway platform)** — 通过 WebSocket 订阅实时状态变化并响应事件。
2. **智能家居工具 (Smart home tools)** — 四个可供 LLM 调用的工具，用于通过 REST API 查询和控制设备。

## 设置 {#setup}

### 1. 创建长期访问令牌 (Long-Lived Access Token) {#1-create-a-long-lived-access-token}

1. 打开您的 Home Assistant 实例。
2. 进入 **个人资料** (点击侧边栏您的名字)。
3. 滚动到 **长期访问令牌** 部分。
4. 点击 **创建令牌**，命名为 "Hermes Agent" 之类的名称。
5. 复制该令牌。

### 2. 配置环境变量 {#2-configure-environment-variables}

```bash
# 添加到 ~/.hermes/.env

# 必填：您的长期访问令牌
HASS_TOKEN=your-long-lived-access-token

# 选填：HA URL (默认: http://homeassistant.local:8123)
HASS_URL=http://192.168.1.100:8123
```

:::info
当设置了 `HASS_TOKEN` 时，`homeassistant` 工具集会自动启用。网关平台和设备控制工具都通过这一个令牌激活。
:::

### 3. 启动网关 {#3-start-the-gateway}

```bash
hermes gateway
```

Home Assistant 将作为一个已连接的平台，与其他消息平台（Telegram、Discord 等）一起显示。

## 可用工具 {#available-tools}

Hermes Agent 注册了四个用于智能家居控制的工具：

### `ha_list_entities` {#halistentities}

列出 Home Assistant 实体，可选择按域 (domain) 或区域 (area) 进行过滤。

**参数：**
- `domain` *(可选)* — 按实体域过滤：`light`、`switch`、`climate`、`sensor`、`binary_sensor`、`cover`、`fan`、`media_player` 等。
- `area` *(可选)* — 按区域/房间名称过滤（匹配友好名称）：`living room`、`kitchen`、`bedroom` 等。

**示例：**
```
列出客厅里的所有灯
```

返回实体 ID、状态和友好名称。

### `ha_get_state` {#hagetstate}

获取单个实体的详细状态，包括所有属性（亮度、颜色、温度设定点、传感器读数等）。

**参数：**
- `entity_id` *(必填)* — 要查询的实体，例如 `light.living_room`、`climate.thermostat`、`sensor.temperature`。

**示例：**
```
climate.thermostat 当前的状态是什么？
```

返回：状态、所有属性、最后更改/更新的时间戳。

### `ha_list_services` {#halistservices}

列出可用的服务（动作）以进行设备控制。显示可以在每种设备类型上执行哪些操作以及它们接受哪些参数。

**参数：**
- `domain` *(可选)* — 按域过滤，例如 `light`、`climate`、`switch`。

**示例：**
```
温控设备 (climate) 有哪些可用服务？
```

### `ha_call_service` {#hacallservice}

调用 Home Assistant 服务来控制设备。

**参数：**
- `domain` *(必填)* — 服务域：`light`、`switch`、`climate`、`cover`、`media_player`、`fan`、`scene`、`script`。
- `service` *(必填)* — 服务名称：`turn_on`、`turn_off`、`toggle`、`set_temperature`、`set_hvac_mode`、`open_cover`、`close_cover`、`set_volume_level`。
- `entity_id` *(可选)* — 目标实体，例如 `light.living_room`。
- `data` *(可选)* — JSON 对象形式的附加参数。

**示例：**

```
打开客厅的灯
→ ha_call_service(domain="light", service="turn_on", entity_id="light.living_room")
```

```
将温控器设置为加热模式，温度 22 度
→ ha_call_service(domain="climate", service="set_temperature",
    entity_id="climate.thermostat", data={"temperature": 22, "hvac_mode": "heat"})
```

```
将客厅灯光设置为蓝色，亮度 50%
→ ha_call_service(domain="light", service="turn_on",
    entity_id="light.living_room", data={"brightness": 128, "color_name": "blue"})
```

## 网关平台：实时事件 {#gateway-platform-real-time-events}

Home Assistant 网关适配器通过 WebSocket 连接并订阅 `state_changed` 事件。当设备状态发生变化且符合您的过滤器时，它会作为消息转发给 Agent。

### 事件过滤 {#event-filtering}

:::warning 必须配置
默认情况下，**不会转发任何事件**。您必须配置 `watch_domains`、`watch_entities` 或 `watch_all` 中的至少一项才能接收事件。如果没有过滤器，启动时会记录警告，并且所有状态更改都会被静默丢弃。
:::

在 `~/.hermes/config.yaml` 的 Home Assistant 平台 `extra` 部分配置 Agent 可以看到的事件：

```yaml
platforms:
<a id="required-configuration"></a>
  homeassistant:
    enabled: true
    extra:
      watch_domains:
        - climate
        - binary_sensor
        - alarm_control_panel
        - light
      watch_entities:
        - sensor.front_door_battery
      ignore_entities:
        - sensor.uptime
        - sensor.cpu_usage
        - sensor.memory_usage
      cooldown_seconds: 30
```

| 设置 | 默认值 | 描述 |
|---------|---------|-------------|
| `watch_domains` | *(无)* | 仅监听这些实体域（例如 `climate`、`light`、`binary_sensor`） |
| `watch_entities` | *(无)* | 仅监听这些特定的实体 ID |
| `watch_all` | `false` | 设置为 `true` 以接收**所有**状态更改（对于大多数设置不推荐） |
| `ignore_entities` | *(无)* | 始终忽略这些实体（在域/实体过滤器之前应用） |
| `cooldown_seconds` | `30` | 同一实体的事件之间的最小间隔秒数 |

:::tip
建议从一组核心域开始 —— `climate`、`binary_sensor` 和 `alarm_control_panel` 涵盖了最实用的自动化场景。根据需要再添加更多。使用 `ignore_entities` 来屏蔽 CPU 温度或运行时间计数器等高频变动的传感器。
:::

### 事件格式化 {#event-formatting}

状态更改会根据域被格式化为易于理解的消息：

| 域 (Domain) | 格式 |
|--------|--------|
| `climate` | "HVAC 模式从 'off' 变为 'heat' (当前: 21, 目标: 23)" |
| `sensor` | "从 21°C 变为 22°C" |
| `binary_sensor` | "已触发 (triggered)" / "已清除 (cleared)" |
| `light`, `switch`, `fan` | "已打开" / "已关闭" |
| `alarm_control_panel` | "警报状态从 'armed_away' 变为 'triggered'" |
| *(其他)* | "从 'old' 变为 'new'" |

### Agent 响应 {#agent-responses}

来自 Agent 的出站消息将作为 **Home Assistant 持久通知**（通过 `persistent_notification.create`）送达。这些消息会出现在 HA 通知面板中，标题为 "Hermes Agent"。

### 连接管理 {#connection-management}

- **WebSocket** 带有 30 秒心跳检测，用于实时事件。
- **自动重连** 机制，退避策略为：5s → 10s → 30s → 60s。
- **REST API** 用于出站通知（独立会话以避免 WebSocket 冲突）。
- **授权** — HA 事件始终是经过授权的（不需要用户白名单，因为 `HASS_TOKEN` 已对连接进行了身份验证）。

## 安全性 {#security}

Home Assistant 工具强制执行安全限制：

:::warning 已屏蔽的域
以下服务域被**屏蔽**，以防止在 HA 主机上执行任意代码：

- `shell_command` — 任意 Shell 命令
<a id="blocked-domains"></a>
- `command_line` — 执行命令的传感器/开关
- `python_script` — 脚本化的 Python 执行
- `pyscript` — 更广泛的脚本集成
- `hassio` — 插件控制、主机关闭/重启
- `rest_command` — 来自 HA 服务器的 HTTP 请求（SSRF 向量）

尝试调用这些域中的服务将返回错误。
:::

实体 ID 会根据模式 `^[a-z_][a-z0-9_]*\.[a-z0-9_]+$` 进行验证，以防止注入攻击。

## 自动化示例 {#example-automations}

### 早晨例程 {#morning-routine}

```
用户：开始我的早晨例程

Agent：
1. ha_call_service(domain="light", service="turn_on",
     entity_id="light.bedroom", data={"brightness": 128})
2. ha_call_service(domain="climate", service="set_temperature",
     entity_id="climate.thermostat", data={"temperature": 22})
3. ha_call_service(domain="media_player", service="turn_on",
     entity_id="media_player.kitchen_speaker")
```

### 安全检查 {#security-check}

```
用户：家里安全吗？

Agent：
1. ha_list_entities(domain="binary_sensor")
     → 检查门窗传感器
2. ha_get_state(entity_id="alarm_control_panel.home")
     → 检查警报状态
3. ha_list_entities(domain="lock")
     → 检查门锁状态
4. 报告："所有门窗已关闭，警报处于离家布防状态，所有门锁已上锁。"
```

### 响应式自动化（通过网关事件） {#reactive-automation-via-gateway-events}
当作为网关平台连接时，Agent 可以对事件做出反应：

```
[Home Assistant] Front Door: triggered (was cleared)

Agent 自动执行：
1. ha_get_state(entity_id="binary_sensor.front_door")
2. ha_call_service(domain="light", service="turn_on",
     entity_id="light.hallway")
3. 发送通知："Front door opened. Hallway lights turned on."
```
