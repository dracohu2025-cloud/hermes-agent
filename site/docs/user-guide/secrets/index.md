<a id="secrets"></a>
# Secrets

Hermes 可以在进程启动时从外部密钥管理器拉取 API 密钥，而不是将它们存储在 `~/.hermes/.env` 中。密钥管理器的引导令牌存放在 `.env` 里；其他所有提供商的密钥（OpenAI、Anthropic、OpenRouter 等）都可以保留在管理器中并进行集中轮换。

已支持：

- [Bitwarden Secrets Manager](./bitwarden) — `bws` CLI，按需安装，免费版即可使用。

更多后端（Vault、AWS Secrets Manager、1Password CLI）很容易通过相同的接口添加——只需在 `agent/secret_sources/` 目录下添加一个模块和一个 CLI 处理器即可。如果你有特定的需求，可以提交请求。
