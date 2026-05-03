---
title: "Gitnexus Explorer"
sidebar_label: "Gitnexus Explorer"
description: "使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Gitnexus Explorer {#gitnexus-explorer}

使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/research/gitnexus-explorer` 安装 |
| 路径 | `optional-skills/research/gitnexus-explorer` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `gitnexus`, `code-intelligence`, `knowledge-graph`, `visualization` |
| 相关技能 | [`native-mcp`](/user-guide/skills/bundled/mcp/mcp-native-mcp), [`codebase-inspection`](/user-guide/skills/bundled/github/github-codebase-inspection) |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

<a id="gitnexus-explorer"></a>
# GitNexus Explorer

将任意代码库索引为知识图谱，并提供交互式 Web UI，用于探索符号、调用链、聚类和执行流。通过 Cloudflare 隧道实现远程访问。

## 何时使用 {#when-to-use}

- 用户希望直观地探索代码库的架构
- 用户请求某个仓库的知识图谱/依赖关系图
- 用户希望与他人分享交互式代码库浏览器

## 前提条件 {#prerequisites}

- **Node.js**（v18+）— GitNexus 和代理所需
- **git** — 仓库必须包含 `.git` 目录
- **cloudflared** — 用于隧道（如果缺失，会自动安装到 `~/.local/bin`）

## 规模警告 {#size-warning}

Web UI 会在浏览器中渲染所有节点。约 5000 个文件以下的仓库运行良好。大型仓库（3 万以上节点）会变得缓慢或导致浏览器标签页崩溃。CLI/MCP 工具在任何规模下都能正常工作——只有 Web 可视化有此限制。

## 步骤 {#steps}

### 1. 克隆并构建 GitNexus（一次性设置） {#1-clone-and-build-gitnexus-one-time-setup}

```bash
GITNEXUS_DIR="${GITNEXUS_DIR:-$HOME/.local/share/gitnexus}"

if [ ! -d "$GITNEXUS_DIR/gitnexus-web/dist" ]; then
  git clone https://github.com/abhigyanpatwari/GitNexus.git "$GITNEXUS_DIR"
  cd "$GITNEXUS_DIR/gitnexus-shared" && npm install && npm run build
  cd "$GITNEXUS_DIR/gitnexus-web" && npm install
fi
```

### 2. 修补 Web UI 以支持远程访问 {#2-patch-the-web-ui-for-remote-access}

Web UI 默认使用 `localhost:4747` 进行 API 调用。将其修补为同源访问，以便通过隧道/代理正常工作：

**文件：`$GITNEXUS_DIR/gitnexus-web/src/config/ui-constants.ts`**
将：
```typescript
export const DEFAULT_BACKEND_URL = 'http://localhost:4747';
```
改为：
```typescript
export const DEFAULT_BACKEND_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? window.location.origin : 'http://localhost:4747';
```

**文件：`$GITNEXUS_DIR/gitnexus-web/vite.config.ts`**
在 `server: { }` 块内添加 `allowedHosts: true`（仅在以开发模式而非生产构建运行时需要）：
```typescript
server: {
    allowedHosts: true,
    // ... 现有配置
},
```
然后构建生产包：
```bash
cd "$GITNEXUS_DIR/gitnexus-web" && npx vite build
```

### 3. 索引目标仓库 {#3-index-the-target-repo}

```bash
cd /path/to/target-repo
npx gitnexus analyze --skip-agents-md
rm -rf .claude/    # 移除 Claude Code 专用产物
```

添加 `--embeddings` 可启用语义搜索（速度较慢——耗时从秒级变为分钟级）。

索引文件存放在仓库内的 `.gitnexus/` 目录下（已自动加入 .gitignore）。

### 4. 创建代理脚本 {#4-create-the-proxy-script}

将以下内容写入文件（例如 `$GITNEXUS_DIR/proxy.mjs`）。该脚本会提供生产环境 Web UI，并将 `/api/*` 请求代理到 GitNexus 后端——同源访问，无跨域问题，无需 sudo，无需 nginx。

```javascript
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const API_PORT = parseInt(process.env.API_PORT || '4747');
const DIST_DIR = process.argv[2] || './dist';
const PORT = parseInt(process.argv[3] || '8888');

const MIME = {
  '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.wasm': 'application/wasm',
};

function proxyToApi(req, res) {
  const opts = {
    hostname: '127.0.0.1', port: API_PORT,
    path: req.url, method: req.method, headers: req.headers,
  };
  const proxy = http.request(opts, (upstream) => {
    res.writeHead(upstream.statusCode, upstream.headers);
    upstream.pipe(res, { end: true });
  });
  proxy.on('error', () => { res.writeHead(502); res.end('后端不可用'); });
  req.pipe(proxy, { end: true });
}

function serveStatic(req, res) {
  let filePath = path.join(DIST_DIR, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
  if (!fs.existsSync(filePath)) filePath = path.join(DIST_DIR, 'index.html');
  const ext = path.extname(filePath);
  const mime = MIME[ext] || 'application/octet-stream';
  try {
    const data = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': mime, 'Cache-Control': 'public, max-age=3600' });
    res.end(data);
  } catch { res.writeHead(404); res.end('未找到'); }
}

http.createServer((req, res) => {
  if (req.url.startsWith('/api')) proxyToApi(req, res);
  else serveStatic(req, res);
}).listen(PORT, () => console.log(`GitNexus 代理运行在 http://localhost:${PORT}`));
```

### 5. 启动服务 {#5-start-the-services}

```bash
# 终端 1：GitNexus 后端 API
npx gitnexus serve &

# 终端 2：代理（Web UI + API 共用同一端口）
node "$GITNEXUS_DIR/proxy.mjs" "$GITNEXUS_DIR/gitnexus-web/dist" 8888 &
```

验证：执行 `curl -s http://localhost:8888/api/repos` 应返回已索引的仓库列表。

### 6. 使用 Cloudflare 隧道（可选——用于远程访问） {#6-tunnel-with-cloudflare-optional-for-remote-access}

```bash
# 如需则安装 cloudflared（无需 sudo）
if ! command -v cloudflared &>/dev/null; then
  mkdir -p ~/.local/bin
  curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    -o ~/.local/bin/cloudflared
  chmod +x ~/.local/bin/cloudflared
  export PATH="$HOME/.local/bin:$PATH"
fi

# 启动隧道（--config /dev/null 避免与现有命名隧道冲突）
cloudflared tunnel --config /dev/null --url http://localhost:8888 --no-autoupdate --protocol http2
```
隧道 URL（例如 `https://random-words.trycloudflare.com`）会输出到 stderr。
分享它——任何拥有该链接的人都可以浏览图谱。

### 7. 清理 {#7-cleanup}

```bash
# 停止服务
pkill -f "gitnexus serve"
pkill -f "proxy.mjs"
pkill -f cloudflared

# 从目标仓库中移除索引
cd /path/to/target-repo
npx gitnexus clean
rm -rf .claude/
```

## 注意事项 {#pitfalls}

- **cloudflared 必须使用 `--config /dev/null`**，如果用户在 `~/.cloudflared/config.yml` 中已有命名的隧道配置。不加此参数时，配置中的全匹配入口规则会对所有快速隧道请求返回 404。

- **隧道必须使用生产构建。** Vite 开发服务器默认会阻止非 localhost 的主机（`allowedHosts`）。使用生产构建 + Node 代理可以完全避免此问题。

- **Web UI 不会创建 `.claude/` 或 `CLAUDE.md`。** 这些文件由 `npx gitnexus analyze` 创建。使用 `--skip-agents-md` 可以抑制 markdown 文件，然后使用 `rm -rf .claude/` 清理其余部分。这些是 Claude Code 的集成功能，Hermes Agent 用户不需要。

- **浏览器内存限制。** Web UI 会将整个图谱加载到浏览器内存中。文件数超过 5000 的仓库可能会变得卡顿。超过 30000 个文件则很可能导致标签页崩溃。

- **嵌入是可选的。** `--embeddings` 启用语义搜索，但在大型仓库上需要几分钟时间。快速浏览时可以跳过；如果你希望通过 AI 聊天面板进行自然语言查询，则可以添加此选项。

- **多仓库支持。** `gitnexus serve` 会服务所有已索引的仓库。索引多个仓库后，只需启动一次 serve，Web UI 即可让你在它们之间切换。
