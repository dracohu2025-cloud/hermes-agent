---
sidebar_position: 16
title: "LSP — 语义诊断"
description: "将真实的语言服务器（pyright、gopls、rust-analyzer 等）接入到 write_file 和 patch 使用的写入后 lint 检查中。"
---

<a id="language-server-protocol-lsp"></a>
# 语言服务器协议（LSP）

Hermes 会以后台子进程的方式运行完整的语言服务器——pyright、gopls、rust-analyzer、typescript-language-server、clangd 等 20 多种——并将其语义诊断结果输入到 `write_file` 和 `patch` 使用的写入后 lint 检查中。Agent 编辑文件时，它看到的正是此次编辑引入的错误——不仅是语法错误，还包括语言服务器检测到的 **类型错误、未定义名称、缺失导入以及项目范围的语义问题**。

这是顶级编码 Agent 所使用的同一套架构。Hermes 自带运行，无需编辑器宿主、无需安装插件、也无需管理单独的守护进程。

<a id="when-lsp-runs"></a>
## LSP 何时运行

LSP 以 **git 工作区检测** 为门控条件。当 Agent 的工作目录（或正在编辑的文件）位于某个 git 仓库内时，LSP 会针对该工作区运行。两者都不在 git 仓库中时，LSP 保持休眠状态——这对于消息网关等场景很有用，此时当前工作目录是用户的主目录，没有项目需要诊断。

检查是分层的：首先是进程内语法检查（微秒级），语法无误后再进行 LSP 诊断。不稳定或缺失的语言服务器绝不会导致写入失败——每条 LSP 失败路径都会静默回退到纯语法检查结果。

具体来说，每次成功的 `write_file` 或 `patch` 操作都会：

1. Hermes 捕获文件当前诊断的基线。
2. 执行写入操作。
3. 重新查询语言服务器，过滤掉基线中已有的诊断，仅呈现新的诊断。

Agent 会看到类似下面的输出：

```
{
  "bytes_written": 42,
  "dirs_created": false,
  "lint": {"status": "ok", "output": ""},
  "lsp_diagnostics": "LSP diagnostics introduced by this edit:\n<diagnostics file=\"/path/to/foo.py\">\nERROR [42:5] Cannot find name 'foo' [reportUndefinedVariable] (Pyright)\nERROR [50:1] Argument of type \"str\" is not assignable to \"int\" [reportArgumentType] (Pyright)\n</diagnostics>"
}
```

`lint` 字段携带语法检查结果（微秒级进程内解析，通过 `ast.parse`、`json.loads` 等完成）；`lsp_diagnostics` 字段携带来自真实语言服务器的语义诊断结果。两个通道，独立信号——Agent 看到的可能是：语法干净但存在语义问题的文件，表现为 `lint: ok` 加上填充了内容的 `lsp_diagnostics`。

<a id="supported-languages"></a>
## 支持的语言

| 语言 | 服务器 | 自动安装 |
|----------|--------|--------------|
| Python | `pyright-langserver` | npm |
| TypeScript / JavaScript / JSX / TSX | `typescript-language-server` | npm |
| Vue | `@vue/language-server` | npm |
| Svelte | `svelte-language-server` | npm |
| Astro | `@astrojs/language-server` | npm |
| Go | `gopls` | `go install` |
| Rust | `rust-analyzer` | manual (rustup) |
| C / C++ | `clangd` | manual (LLVM) |
| Bash / Zsh | `bash-language-server` | npm |
| YAML | `yaml-language-server` | npm |
| Lua | `lua-language-server` | manual (GitHub releases) |
| PHP | `intelephense` | npm |
| OCaml | `ocaml-lsp` | manual (opam) |
| Dockerfile | `dockerfile-language-server-nodejs` | npm |
| Terraform | `terraform-ls` | manual |
| Dart | `dart language-server` | manual (dart sdk) |
| Haskell | `haskell-language-server` | manual (ghcup) |
| Julia | `julia` + LanguageServer.jl | manual |
| Clojure | `clojure-lsp` | manual |
| Nix | `nixd` | manual |
| Zig | `zls` | manual |
| Gleam | `gleam lsp` | manual (gleam install) |
| Elixir | `elixir-ls` | manual |
| Prisma | `prisma language-server` | manual |
| Kotlin | `kotlin-language-server` | manual |
| Java | `jdtls` | manual |
对于“手动”条目，通过适合该语言的工具链管理器（rustup、ghcup、opam、brew……）安装服务器。Hermes 会自动检测 `PATH` 或 `&lt;HERMES_HOME&gt;/lsp/bin/` 中的二进制文件。

少数服务器是与 npm 不会自动拉取的对等依赖一起安装的。目前的情况是 `typescript-language-server`，它需要从同一个 `node_modules` 树中可导入的 `typescript` SDK——当你运行 `hermes lsp install typescript` 或首次使用时自动安装触发时，Hermes 会同时安装这两个包。

<a id="cli"></a>
## CLI

```
hermes lsp status          # 服务状态 + 每服务器安装状态
hermes lsp list            # 注册表，可选 --installed-only
hermes lsp install <id>    # 主动安装一个服务器
hermes lsp install-all     # 尝试所有已知配方的服务器
hermes lsp restart         # 关闭正在运行的客户端
hermes lsp which <id>      # 打印解析出的二进制路径
```

`hermes lsp status` 是最好的起点——它显示哪些语言今天能获得语义诊断，哪些需要安装二进制文件。

<a id="configuration"></a>
## 配置

默认配置适用于典型设置；如果二进制文件已在 `PATH` 上，则无需设置任何内容。

```yaml
# config.yaml
lsp:
  # 主开关。禁用会跳过整个子系统——不会产生服务器，不会运行后台事件循环。
  enabled: true

  # 每次写入后等待诊断的时间。
  wait_mode: document      # "document" 或 "full"
  wait_timeout: 5.0

  # 如何处理缺失的服务器二进制文件。
  #   auto    — 通过 npm/pip/go install 安装到 <HERMES_HOME>/lsp/bin
  #   manual  — 仅使用已在 PATH 上的二进制文件
  install_strategy: auto

  # 每服务器覆盖（均为可选）。
  servers:
    pyright:
      disabled: false
      command: ["/abs/path/to/pyright-langserver", "--stdio"]
      env: { PYRIGHT_LOG_LEVEL: "info" }
      initialization_options:
        python:
          analysis:
            typeCheckingMode: "strict"
    typescript:
      disabled: true       # 即使扩展名匹配也跳过 TS
```

<a id="per-server-keys"></a>
### 每服务器键

* `disabled: true` — 即使其扩展名与文件匹配，也完全跳过此服务器。
* `command: [bin, ...args]` — 固定自定义二进制路径。绕过自动安装。
* `env: {KEY: value}` — 传递给生成的进程的额外环境变量。
* `initialization_options: {...}` — 合并到 `initialize` 握手中发送的 LSP `initializationOptions` 负载中。特定于服务器；请查阅语言服务器的文档。

<a id="installation-locations"></a>
## 安装位置

当 `install_strategy: auto` 时，Hermes 将二进制文件安装到 `&lt;HERMES_HOME&gt;/lsp/bin/`。NPM 包位于 `&lt;HERMES_HOME&gt;/lsp/node_modules/`，bin 符号链接在上一级目录。Go 二进制文件来自 `go install`，其中 `GOBIN` 指向暂存目录。

任何内容都不会安装到 `/usr/local/`、`~/.local/` 或其他共享位置——暂存目录完全由 Hermes 拥有，当你重置配置文件时会被移除。

<a id="performance-characteristics"></a>
## 性能特征

LSP 服务器在首次使用时**懒启动**。在从未遇到过 `.py` 流量的项目中编辑 Python 文件会启动 pyright；大多数服务器的启动需要 1-3 秒（rust-analyzer 在冷项目上可能需要 10 秒以上）。同一工作区中的后续编辑会重用正在运行的服务器。
LSP 层在干净写入（无诊断输出时）会增加几毫秒延迟。当产生诊断时，等待预算为 `wait_timeout` 秒——通常对于 pyright/tsserver，服务器在几十毫秒内响应；对于正处索引中的 rust-analyzer，则需要几秒。

服务器在 Hermes 进程的整个生命周期内保持存活。没有空闲超时回收机制——每次写入都重新启动服务器索引的成本远高于保持守护进程。

<a id="disabling"></a>
## 禁用

在 `config.yaml` 中设置 `lsp.enabled: false` 可禁用整个子系统。写入后检查会回退到进程内语法检查（Python 使用 `ast.parse`，JSON 使用 `json.loads` 等），这部分与早期版本无异。

若要只禁用单个语言而不禁用整个层：

```yaml
lsp:
  servers:
    rust-analyzer:
      disabled: true
```

<a id="troubleshooting"></a>
## 故障排查

**`hermes lsp status` 显示服务器状态为 "missing"**

可执行文件不在 PATH 中，也不在 `&lt;HERMES_HOME&gt;/lsp/bin/` 目录下。运行 `hermes lsp install &lt;server_id&gt;` 尝试自动安装，或通过该语言的标准工具链手动安装二进制文件。

**`hermes lsp status` 中的 `Backend warnings` 部分**

某些服务器实际上只是一个薄包装器，它将真正的诊断任务委托给外部 CLI——它们可以正常启动并接受请求，但当 sidecar 二进制文件缺失时，永远不会输出错误。最常见的情况是 `bash-language-server`，它将诊断委托给 `shellcheck`。当 `hermes lsp status` 显示 `Backend warnings` 部分时，请通过操作系统包管理器安装指定的工具：

```
apt install shellcheck      # Debian / Ubuntu
brew install shellcheck     # macOS
scoop install shellcheck    # Windows
```

同样的警告也会在服务器启动时记录一次到 `~/.hermes/logs/agent.log` 中。

**服务器启动但从不返回诊断**

检查 `~/.hermes/logs/agent.log` 中的 `[agent.lsp.client]` 条目——语言服务器的 stderr 和协议错误都会记录在这里。某些服务器（尤其是 rust-analyzer）需要完成全项目索引后才能输出每个文件的诊断；服务器启动后的第一次编辑可能完成且无诊断，后续编辑才会正常输出。

**服务器崩溃**

崩溃的服务器会被加入损坏集合，在本会话中不再重试。运行 `hermes lsp restart` 可清除该集合；下一次编辑时会重新启动服务器。

**编辑不在任何 git 仓库中的文件**

根据设计，LSP 仅在 git 仓库内运行。如果项目尚未初始化，请运行 `git init` 以启用 LSP 诊断。否则将回退到进程内纯语法检查。
