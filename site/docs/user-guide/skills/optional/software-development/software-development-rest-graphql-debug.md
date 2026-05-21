---
title: "Rest Graphql Debug — 调试 REST/GraphQL API：状态码、认证、模式、再现"
sidebar_label: "Rest Graphql Debug"
description: "调试 REST/GraphQL API：状态码、认证、模式、再现"
---

{/* 此页面由网址 scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

<a id="rest-graphql-debug"></a>
# Rest Graphql Debug

调试 REST/GraphQL API：状态码、认证、模式、再现。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/software-development/rest-graphql-debug` 安装 |
| 路径 | `optional-skills/software-development/rest-graphql-debug` |
| 版本 | `1.2.0` |
| 作者 | eren-karakus0 |
| 许可证 | MIT |
| 标签 | `api`, `rest`, `graphql`, `http`, `debugging`, `testing`, `curl`, `integration` |
| 相关技能 | [`systematic-debugging`](/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`test-driven-development`](/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

<a id="reference-full-skill-md"></a>
## 参考：完整 SKILL.md

:::info
以下是在此技能被触发时 Hermes 加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="api-testing-debugging"></a>
# API 测试与调试

通过 Hermes 工具驱动 REST 和 GraphQL 诊断 — 使用 `terminal` 执行 `curl`，使用 `execute_code` 执行 Python 的 `requests`，使用 `web_extract` 查阅供应商文档。在猜测修复方案之前，先隔离出出错的层。

<a id="when-to-use"></a>
## 何时使用

- API 返回意外的状态码或响应体
- 认证失败（刷新令牌后出现 401/403，OAuth，API 密钥）
- 在 Postman 中正常，但在代码中失败
- Webhook / 回调集成调试
- 构建或审查 API 集成测试
- 速率限制或分页问题

以下情况跳过：UI 渲染、数据库查询调优、DNS/防火墙基础设施（升级处理）。

<a id="core-principle"></a>
## 核心原则

**先隔离层，再修复。** 200 OK 可能隐藏着错误的数据。500 可能掩盖了一个字符的认证拼写错误。按顺序逐一排查；永远不要跳过某一步。

```
1. 连接性       → 能否正常访问主机？
1.5 超时        → 是连接慢还是读取慢？
2. TLS/SSL      → 证书是否有效且受信任？
3. 认证         → 凭据是否正确且未过期？
4. 请求格式     → 载荷结构是否与服务器期望一致？
5. 响应解析     → 我们的代码是否接受了返回的内容？
6. 语义         → 数据是否如我们假设的那样？
```

<a id="5-minute-quickstart"></a>
## 5 分钟快速入门

<a id="rest-via-terminal"></a>
### 通过终端调试 REST

```python
# 详细显示请求/响应交换
terminal('curl -v https://api.example.com/users/1')

# 带 JSON 的 POST
terminal("""curl -X POST https://api.example.com/users \\
  -H 'Content-Type: application/json' \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"name":"test","email":"test@example.com"}'""")

# 仅查看响应头
terminal('curl -sI https://api.example.com/health')

# 美化打印 JSON
terminal('curl -s https://api.example.com/users | python3 -m json.tool')
```

<a id="graphql-via-terminal"></a>
### 通过终端调试 GraphQL

```python
terminal("""curl -X POST https://api.example.com/graphql \\
  -H 'Content-Type: application/json' \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"query":"{ user(id: 1) { name email } }"}'""")
```

**GraphQL 陷阱：** 即使查询失败，服务器也常常返回 HTTP 200。无论状态码如何，始终检查 `errors` 字段：

--- END DOCUMENT CHUNK ---
```python
execute_code('''
import os, requests
resp = requests.post(
    "https://api.example.com/graphql",
    json={"query": "{ user(id: 1) { name email } }"},
    headers={"Authorization": f"Bearer {os.environ['TOKEN']}"},
    timeout=10,
)
data = resp.json()
if data.get("errors"):
    for err in data["errors"]:
        print(f"GraphQL error: {err['message']} (path: {err.get('path')})")
print(data.get("data"))
''')
```

<a id="python-requests-via-executecode"></a>
### Python (requests) via execute_code

```python
execute_code('''
import requests
resp = requests.get(
    "https://api.example.com/users/1",
    headers={"Authorization": "Bearer <TOKEN>"},
    timeout=(3.05, 30),  # (connect, read)
)
print(resp.status_code, dict(resp.headers))
print(resp.text[:500])
''')
```

<a id="layered-debug-flow"></a>
## 分层调试流程

<a id="step-1-connectivity"></a>
### 第 1 步 — 连通性

```python
terminal('nslookup api.example.com')
terminal('curl -v --connect-timeout 5 https://api.example.com/health')
```

故障场景：DNS 解析失败、防火墙阻断、需要 VPN、缺少代理。

<a id="step-1-5-timeouts"></a>
### 第 1.5 步 — 超时

区分 *无法到达* 和 *能到达但很慢*：

```python
terminal('''curl -w "dns:%{time_namelookup}s connect:%{time_connect}s tls:%{time_appconnect}s ttfb:%{time_starttransfer}s total:%{time_total}s\\n" \\
  -o /dev/null -s https://api.example.com/endpoint''')
```

在 Python 中，始终传递一个元组超时——`requests` 没有默认值，会永久挂起：

```python
execute_code('''
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
try:
    requests.get(url, timeout=(3.05, 30))
except ConnectTimeout:
    print("Cannot reach host — DNS, firewall, VPN")
except ReadTimeout:
    print("Connected but server is slow")
''')
```

诊断：`time_connect` 高说明网络/防火墙问题；`time_starttransfer` 高但 `time_connect` 低说明服务器响应慢。

<a id="step-2-tls-ssl"></a>
### 第 2 步 — TLS/SSL

```python
terminal('curl -vI https://api.example.com 2>&1 | grep -E "SSL|subject|expire|issuer"')
```

故障场景：证书过期、自签名证书、主机名不匹配、缺少 CA 包。仅临时调试时可使用 `-k`，切勿在代码中使用。

<a id="step-3-authentication"></a>
### 第 3 步 — 认证

```python
# Token 有效性检查
terminal('curl -s -o /dev/null -w "%{http_code}\\n" -H "Authorization: Bearer $TOKEN" https://api.example.com/me')

# 解码 JWT 的 exp 声明 — 正确处理 base64url 填充
execute_code('''
import json, base64, os
tok = os.environ["TOKEN"]
payload = tok.split(".")[1]
payload += "=" * (-len(payload) % 4)
print(json.dumps(json.loads(base64.urlsafe_b64decode(payload)), indent=2))
''')
```

检查清单：
- Token 过期？(JWT 中的 `exp` 声明)
- 认证方案正确？Bearer vs Basic vs Token vs `X-Api-Key`
- 环境正确？生产环境用了预发环境的 key 是经典错误
- API key 在 header 还是 query 参数中 (`?api_key=…`)？

<a id="step-4-request-format"></a>
### 第 4 步 — 请求格式

```python
terminal("""curl -v -X POST https://api.example.com/endpoint \\
  -H 'Content-Type: application/json' \\
  -d '{"key":"value"}' 2>&1""")
```

**Content-Type 与 body 不匹配——静默的 415/400 错误：**

```python
# 错误 — data= 发送的是表单编码，但 header 声明为 JSON
requests.post(url, data='{"k":"v"}', headers={"Content-Type": "application/json"})

# 正确 — json= 自动设置 header 并序列化
requests.post(url, json={"k": "v"})

# 错误 — Accept 声明 XML，代码却调用 .json()
requests.get(url, headers={"Accept": "text/xml"})

# 正确 — 让 requests 自动构建带 boundary 的 multipart
requests.post(url, files={"file": open("doc.pdf", "rb")})
```
Common: form-encoded vs JSON, missing required fields, wrong HTTP method, unencoded query params.

<a id="step-5-response-parsing"></a>
### 步骤 5 — 响应解析

在调用 `.json()` 前始终检查 content-type：

```python
execute_code('''
import requests
resp = requests.post(url, json=payload, timeout=10)
print(f"status={resp.status_code}")
print(f"headers={dict(resp.headers)}")
ct = resp.headers.get("Content-Type", "")
if "application/json" in ct:
    print(resp.json())
else:
    print(f"unexpected content-type {ct!r}, body={resp.text[:500]!r}")
''')
```

常见失败：期望 JSON 却得到 HTML 错误页面、空响应体、错误字符集。

<a id="step-6-semantic-validation"></a>
### 步骤 6 — 语义验证

解析没有报错——但数据本身*正确*吗？

- `"status": "active"` 的含义是否与你代码中理解的一致？
- 响应中的 ID 是否与请求的 ID 匹配？
- 时间戳是否在预期的时区？
- 分页返回的是全部结果，还是只返回了第一页？

<a id="http-status-playbook"></a>
## HTTP 状态码速查手册

<a id="401-unauthorized-credentials-missing-or-invalid"></a>
### 401 Unauthorized — 凭据缺失或无效

1. `Authorization` 请求头是否真的存在？（用 `curl -v` 确认）
2. Token 是否正确且未过期？
3. 认证方案是否正确？（`Bearer` vs `Basic` vs `Token`）
4. 某些 API 使用查询参数（`?api_key=…`）而不是请求头。

<a id="403-forbidden-authenticated-but-not-authorized"></a>
### 403 Forbidden — 已认证但无权限

1. Token 是否具有所需的 scope/权限？
2. 资源是否属于另一个账号？
3. IP 白名单是否拦截了你？
4. 浏览器环境中的 CORS？（检查 `Access-Control-Allow-Origin`）

<a id="404-not-found-resource-doesn-t-exist-or-url-is-wrong"></a>
### 404 Not Found — 资源不存在或 URL 错误

1. 路径是否正确？（尾部斜杠、拼写错误、版本前缀）
2. 资源 ID 是否存在？
3. API 版本是否正确（`/v1/` vs `/v2/`）？
4. 基础 URL 是否正确（staging vs prod）？

<a id="409-conflict-state-collision"></a>
### 409 Conflict — 状态冲突

1. 资源已存在（重复创建）？
2. 过期的 `ETag` / `If-Match`？
3. 另一个进程同时修改？

<a id="422-unprocessable-entity-valid-json-invalid-data"></a>
### 422 Unprocessable Entity — JSON 格式正确，但数据无效

错误体中通常会指明出错字段。检查：
- 字段类型（string vs int，日期格式）
- 必需 vs 可选
- 枚举值是否在允许范围内

<a id="429-too-many-requests-rate-limited"></a>
### 429 Too Many Requests — 被限速

检查 `Retry-After` 和 `X-RateLimit-*` 响应头。指数退避：

```python
execute_code('''
import time, requests

def with_backoff(method, url, **kwargs):
    for attempt in range(5):
        resp = requests.request(method, url, **kwargs)
        if resp.status_code != 429:
            return resp
        wait = int(resp.headers.get("Retry-After", 2 ** attempt))
        time.sleep(wait)
    return resp
''')
```

<a id="5xx-server-side-usually-not-your-fault"></a>
### 5xx — 服务端错误，通常不是你导致的

- **500** — 服务器 Bug。捕获关联 ID，向服务提供商提交。
- **502** — 上游服务宕机。退避 + 重试。
- **503** — 过载 / 维护。查看状态页面。
- **504** — 上游超时。减少 payload 或增大超时时间。

所有 5xx：退避时加入随机抖动，持续告警。

<a id="pagination-idempotency"></a>
## 分页与幂等性

**分页。** 确认你获取了*所有*结果。留意 `next_cursor`、`next_page`、`total_count`。两种模式：
- Offset 偏移量（`?limit=100&offset=200`）—— 简单，但数据变动时可能跳过条目。
- Cursor 游标（`?cursor=abc123`）—— 推荐用于实时或大数据集。
**幂等性。** 对于非幂等操作（POST），发送 `Idempotency-Key: &lt;uuid&gt;`，以便重试时不会重复计费/重复创建。支付和订单类操作强制要求。

<a id="contract-validation"></a>
## 契约验证

在契约漂移影响到生产环境之前就将其捕获：

```python
execute_code('''
import requests

def validate_user(data: dict) -> list[str]:
    errors = []
    required = {"id": int, "email": str, "created_at": str}
    for field, expected in required.items():
        if field not in data:
            errors.append(f"missing field: {field}")
        elif not isinstance(data[field], expected):
            errors.append(f"{field}: want {expected.__name__}, got {type(data[field]).__name__}")
    return errors

resp = requests.get(f"{BASE}/users/1", headers=HEADERS, timeout=10)
issues = validate_user(resp.json())
if issues:
    print(f"contract violations: {issues}")
''')
```

在 API 升级、集成新的第三方服务时，或在 CI 烟雾测试中执行。

<a id="correlation-ids"></a>
## 关联 ID

始终捕获提供方的请求 ID —— 这是联系供应商支持的最快途径：

```python
execute_code('''
import requests
resp = requests.post(url, json=payload, headers=headers, timeout=10)
request_id = (
    resp.headers.get("X-Request-Id")
    or resp.headers.get("X-Trace-Id")
    or resp.headers.get("CF-Ray")  # Cloudflare
)
if resp.status_code >= 400:
    print(f"failed status={resp.status_code} req_id={request_id} ts={resp.headers.get('Date')}")
''')
```

**供应商 bug 报告模板：**

```
Endpoint:    POST /api/v1/orders
Request ID:  req_abc123xyz
Timestamp:   2026-03-17T14:30:00Z
Status:      500
Expected:    201 with order object
Actual:      500 {"error":"internal server error"}
Repro:       curl -X POST … (auth: <REDACTED>)
```

<a id="regression-test-template"></a>
## 回归测试模板

将其放入 `tests/` 目录，并通过 `terminal('pytest tests/test_api_smoke.py -v')` 运行：

```python
import os, requests, pytest

BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com")
TOKEN    = os.environ.get("API_TOKEN", "")
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}

class TestAPISmoke:
    def test_health(self):
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200

    def test_list_users_returns_array(self):
        resp = requests.get(f"{BASE_URL}/users", headers=HEADERS, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data.get("data", data), list)

    def test_get_user_required_fields(self):
        resp = requests.get(f"{BASE_URL}/users/1", headers=HEADERS, timeout=10)
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            user = resp.json()
            assert "id" in user and "email" in user

    def test_invalid_auth_returns_401(self):
        resp = requests.get(
            f"{BASE_URL}/users",
            headers={"Authorization": "Bearer invalid-token"},
            timeout=10,
        )
        assert resp.status_code == 401
```

<a id="security"></a>
## 安全

<a id="token-handling"></a>
### Token 处理
- 绝不要记录完整的 token。使用脱敏形式：`Bearer &lt;REDACTED&gt;`。
- 绝不要在脚本中硬编码 token。从环境变量（`os.environ["API_TOKEN"]`）或 `~/.hermes/.env` 中读取。
- 如果 token 出现在日志、错误消息或 git 历史中，立即轮换。
<a id="safe-logging"></a>
### 安全日志记录

```python
def redact_auth(headers: dict) -> dict:
    sensitive = {"authorization", "x-api-key", "cookie", "set-cookie"}
    return {k: ("<REDACTED>" if k.lower() in sensitive else v) for k, v in headers.items()}
```

<a id="leak-checklist"></a>
### 泄漏检查清单

- [ ] **URL 中的凭据。** 查询字符串中的 API 密钥会出现在服务器日志、浏览器历史记录和引用标头中——请使用标头。
- [ ] **错误响应中的个人身份信息（PII）。** `404 on /users/123` 不应泄露用户是否存在（枚举攻击）。
- [ ] **生产环境中的堆栈跟踪。** 500 错误不应暴露文件路径、框架版本。
- [ ] **内部主机名/IP。** `10.x.x.x`、`internal-api.corp.local` 出现在错误主体中。
- [ ] **Token 被回显。** 某些 API 会在错误详情中包含认证 token。请确认它们不会这样做。
- [ ] **冗余的 `Server` / `X-Powered-By`。** 堆栈信息泄露。注意在安全审查中处理。

<a id="hermes-tool-patterns"></a>
## Hermes Tool 模式

<a id="terminal-for-curl-dig-openssl"></a>
### terminal — 用于 curl、dig、openssl

```python
terminal('curl -sI https://api.example.com')
terminal('openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null 2>/dev/null | openssl x509 -noout -dates')
```

<a id="executecode-for-multi-step-python-flows"></a>
### execute_code — 用于多步骤 Python 流程

当调试包含 auth → fetch → paginate → validate 的 span 时，使用 `execute_code`。变量在脚本执行期间持久存在，结果打印到标准输出，不会在上下文中产生 token 垃圾信息：

```python
execute_code('''
import os, requests

token = os.environ["API_TOKEN"]
base  = "https://api.example.com"
H     = {"Authorization": f"Bearer {token}"}

# 1. 认证
me = requests.get(f"{base}/me", headers=H, timeout=10)
print(f"auth {me.status_code}")

# 2. 分页
all_users, cursor = [], None
while True:
    params = {"cursor": cursor} if cursor else {}
    r = requests.get(f"{base}/users", headers=H, params=params, timeout=10)
    body = r.json()
    all_users.extend(body["data"])
    cursor = body.get("next_cursor")
    if not cursor:
        break
print(f"users={len(all_users)}")
''')
```

<a id="webextract-for-vendor-api-docs"></a>
### web_extract — 用于供应商 API 文档

拉取你正在调试的端点的规范，而不是瞎猜：

```python
web_extract(urls=["https://docs.example.com/api/v1/users"])
```

<a id="delegatetask-for-full-crud-test-sweeps"></a>
### delegate_task — 用于完整的 CRUD 测试扫描

```python
delegate_task(
    goal="测试 /api/v1/users 的所有 CRUD 端点",
    context="""
遵循 rest-graphql-debug 技能（optional-skills/software-development/rest-graphql-debug）。
基础 URL：https://api.example.com
认证：Bearer token 来自 API_TOKEN 环境变量。

对于每个 HTTP 动词（POST、GET、PATCH、DELETE）：
  - 正常路径：验证状态码 + 响应结构
  - 错误情况：400、404、422
  - 对任何失败记录一个可复现的 curl 命令（脱敏 token）

输出：每个端点的通过/失败状态 + 失败时的关联 ID。
""",
    toolsets=["terminal", "file"],
)
```

<a id="output-format"></a>
## 输出格式

报告发现时，使用以下格式：

```
## 发现
Endpoint: POST /api/v1/users
Status:   422 Unprocessable Entity
Req ID:   req_abc123xyz

## 复现步骤
curl -X POST https://api.example.com/api/v1/users \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <REDACTED>' \
  -d '{"name":"test"}'

## 根因
缺少必填字段 `email`。服务器在处理前验证拒绝。

## 修复
-d '{"name":"test","email":"test@example.com"}'
```
<a id="related"></a>
## 相关

- `systematic-debugging` — 一旦隔离了出错的 API 层，就可以对代码进行根因分析
- `test-driven-development` — 在发布修复之前先编写回归测试
