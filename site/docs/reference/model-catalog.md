---
sidebar_position: 11
title: 模型目录
description: 远程托管的清单文件，驱动 OpenRouter 和 Nous Portal 的精选模型选择列表。
---

# 模型目录 {#model-catalog}

Hermes 从托管在文档站点旁的 JSON 清单文件中获取 **OpenRouter** 和 **Nous Portal** 的精选模型列表。这样维护者无需发布新的 `hermes-agent` 版本即可更新选择列表。

当清单文件不可达（离线、网络被屏蔽、托管故障）时，Hermes 会静默回退到 CLI 自带的仓库内快照。该清单永远不会破坏选择器——最坏情况下，你看到的是安装版本所捆绑的列表。

## 实时清单 URL {#live-manifest-url}

```
https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
```

每次合并到 `main` 分支时，通过现有的 `deploy-site.yml` GitHub Pages 流水线发布。数据源位于仓库的 `website/static/api/model-catalog.json`。

## 结构 {#schema}

```json
{
  "version": 1,
  "updated_at": "2026-04-25T22:00:00Z",
  "metadata": {},
  "providers": {
    "openrouter": {
      "metadata": {},
      "models": [
        {"id": "moonshotai/kimi-k2.6", "description": "recommended", "metadata": {}},
        {"id": "openai/gpt-5.4",       "description": ""}
      ]
    },
    "nous": {
      "metadata": {},
      "models": [
        {"id": "anthropic/claude-opus-4.7"},
        {"id": "moonshotai/kimi-k2.6"}
      ]
    }
  }
}
```

字段说明：

- **`version`** — 整数型结构版本。未来结构升级时会递增此值；Hermes 会拒绝无法理解的版本，并回退到硬编码快照。
- **`metadata`** — 清单、提供商和模型级别的自由格式字典。可包含任意键。Hermes 会忽略未知字段，因此你可以添加注释（如 `"tier": "paid"`、`"tags": [...]` 等），而无需协调结构变更。
- **`description`** — 仅用于 OpenRouter。驱动选择器徽章文本（`"recommended"`、`"free"` 或空）。Nous Portal 不使用此字段——免费层限制由 Portal 的定价端点实时确定。
- **定价和上下文长度**不在清单中。这些信息在获取时来自实时提供商 API（`/v1/models` 端点、models.dev）。

## 获取行为 {#fetch-behavior}

| 时机 | 行为 |
|---|---|
| `/model` 或 `hermes model` | 如果磁盘缓存过期则获取，否则使用缓存 |
| 磁盘缓存未过期（< TTL） | 无网络请求 |
| 网络故障且有缓存 | 静默回退到缓存，记录一行日志 |
| 网络故障且无缓存 | 静默回退到仓库内快照 |
| 清单未通过结构验证 | 视为不可达 |

缓存位置：`~/.hermes/cache/model_catalog.json`。

## 配置 {#config}

```yaml
model_catalog:
  enabled: true
  url: https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
  ttl_hours: 24
  providers: {}
```

设置 `enabled: false` 可完全禁用远程获取，始终使用仓库内快照。

### 按提供商覆盖 URL {#per-provider-override-urls}

第三方可以使用相同结构自行托管自己的精选列表。将提供商指向自定义 URL：

```yaml
model_catalog:
  providers:
    openrouter:
      url: https://example.com/my-openrouter-curation.json
```

覆盖清单只需填充它关心的提供商块。其他提供商将继续通过主 URL 解析。
## 更新清单 {#updating-the-manifest}

维护者：

```bash
# 从仓库内的硬编码列表重新生成（在编辑 hermes_cli/models.py 中的 OPENROUTER_MODELS 或 _PROVIDER_MODELS["nous"] 后，保持清单同步）
python scripts/build_model_catalog.py
```

然后将生成的变更通过 PR 提交到 `website/static/api/model-catalog.json` 并合并到 `main` 分支。文档站点会在合并后自动部署，新清单将在几分钟内生效。

你也可以直接手动编辑 JSON 文件，以进行不属于仓库内快照的细粒度元数据变更——生成脚本仅提供便利，并非唯一的事实来源。
