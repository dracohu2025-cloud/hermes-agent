---
sidebar_position: 7
title: "网关内部机制"
description: "消息网关如何启动、授权用户、路由会话以及投递消息"
---

# 网关内部机制

消息网关是一个长期运行的进程，负责将 Hermes 连接到外部平台。

关键文件：

- `gateway/run.py`
- `gateway/config.py`
- `gateway/session.py`
- `gateway/delivery.py`
- `gateway/pairing.py`
- `gateway/channel_directory.py`
- `gateway/hooks.py`
- `gateway/mirror.py`
- `gateway/platforms/*`

## 核心职责

网关进程负责：

- 从 `.env`、`config.yaml` 和 `gateway.json` 加载配置
- 启动平台适配器
- 授权用户
- 将传入事件路由到会话
- 维护每个聊天会话的连续性
- 将消息分派给 `AIAgent`
- 运行定时任务和后台维护任务
- 将输出镜像/主动投递到配置的频道

## 配置来源

网关采用多源配置模型：

- 环境变量
- `~/.hermes/gateway.json`
- 从 `~/.hermes/config.yaml` 中选取的桥接值

## 会话路由

`gateway/session.py` 和 `GatewayRunner` 协同工作，将传入消息映射到活跃的会话 ID。

会话键的生成可能取决于：

- 平台
- 用户/聊天身份
- 线程/主题身份
- 特定于平台的特殊路由行为

## 授权层级

网关可以通过以下方式授权：

- 平台允许列表
- 网关全局允许列表
- 私信配对流程
- 显式允许所有设置

配对支持在 `gateway/pairing.py` 中实现。

## 投递路径

外发投递由 `gateway/delivery.py` 处理，它知道如何：

- 投递到主频道
- 解析显式目标
- 将部分远程投递镜像回本地历史记录/会话跟踪

## 钩子

网关事件通过 `gateway/hooks.py` 触发钩子回调。钩子是本地受信任的 Python 代码，可以观察或扩展网关生命周期事件。

## 后台维护

网关还运行维护任务，例如：

- 定时任务
- 缓存刷新
- 会话过期检查
- 重置/过期前的主动内存刷新

## 与 Honcho 的交互

当启用 Honcho 时，网关会保持持久的 Honcho 管理器与会话生命周期以及平台特定的会话键对齐。

### 会话路由

Honcho 工具（`honcho_profile`、`honcho_search`、`honcho_context`、`honcho_conclude`）需要在正确的用户 Honcho 会话上执行。在多用户网关中，`tools/honcho_tools.py` 中的进程全局模块状态是不够的——多个会话可能同时处于活动状态。

解决方案是通过调用链传递会话上下文：

```
AIAgent._invoke_tool()
  → handle_function_call(honcho_manager=..., honcho_session_key=...)
    → registry.dispatch(**kwargs)
      → _handle_honcho_*(args, **kw)
        → _resolve_session_context(**kw)   # 优先使用显式 kwargs，其次才是模块全局变量
```

`honcho_tools.py` 中的 `_resolve_session_context()` 首先检查 kwargs 中是否存在 `honcho_manager` 和 `honcho_session_key`，如果不存在，则回退到模块全局的 `_session_manager` / `_session_key`（用于 CLI 模式，该模式下只有一个会话）。

### 内存刷新生命周期

当会话被重置、恢复或过期时，网关会在丢弃上下文之前刷新记忆。刷新过程会创建一个临时的 `AIAgent`，其配置如下：

- `session_id` 设置为旧会话的 ID（以便正确加载对话记录）
- `honcho_session_key` 设置为网关会话键（以便 Honcho 写入正确的位置）
- 向 `run_conversation()` 传递 `sync_honcho=False`（以便合成的刷新轮次不会写回 Honcho 的对话历史记录）

刷新完成后，任何排队的 Honcho 写入都会被清空，并且该会话键对应的网关级 Honcho 管理器将被关闭。

## 相关文档

- [会话存储](./session-storage.md)
- [定时任务内部机制](./cron-internals.md)
- [ACP 内部机制](./acp-internals.md)
