from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DOCS_ROOT = REPO_ROOT / "website" / "docs"
TARGET_DOCS_ROOT = REPO_ROOT / "site" / "docs"
TRANSLATABLE_SUFFIXES = {".md", ".json"}

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


MARKDOWN_SYSTEM_PROMPT = """你是一名专业的软件文档翻译编辑。

请把英文 Docusaurus Markdown/MDX 文档完整翻译成简体中文，并严格遵守下面规则：

1. 不得遗漏任何内容，段落、标题、表格、提示框、列表、引用、HTML/JSX 块都要保留。
2. 保持原始文档结构不变，标题层级、段落顺序、表格行数、链接目标、锚点、相对路径都不能改。
3. YAML frontmatter 的键名必须原样保留，只翻译用户可见的值，比如 title、description。
4. 代码块内容默认原样保留，不翻译命令、路径、环境变量、代码、JSON/YAML/TOML 配置项，也不要改代码块语言标记。
5. 行内代码、文件路径、命令名、模型名、品牌名、产品名、API 名称保持英文。
6. Mermaid、DOT、ASCII 图、HTML 标签、JSX 语法、注释标记、admonition 语法（:::tip 等）必须保留可用。
7. 凡是英文原文里明确写了 Agent 或 Agents，默认保留为 Agent 或 Agents，不要翻成“代理”。例如 AI Agent、Hermes Agent、sub-agents、agent loop 这类场景都优先保留 Agent。只有在原文明显指网络 proxy 时，才使用“代理”。
8. 中文风格要通俗易懂、自然、不端着，避免翻译腔，避免使用“落盘”“收口”等黑话，也不要频繁使用“不是……而是……”这种句式。
9. 输出只能是翻译后的文档正文，不要补充解释，不要加“以下是翻译”之类的话。
"""


MARKDOWN_USER_TEMPLATE = """请翻译下面这篇 Hermes Agent 文档。

额外要求：
- 保持所有 Markdown 结构、链接、锚点、代码块数量与原文一致。
- 如果原文包含 HTML/JSX 标签，只翻译其中对用户可见的文本，不要破坏标签或属性。
- 表格结构必须完全保留。
- 文档面向中文开发者，但要尽量好懂。
- 遇到 Agent 或 Agents 时，优先保留 Agent / Agents，不要随手翻成“代理”。

文档路径：{path}

--- BEGIN DOCUMENT ---
{content}
--- END DOCUMENT ---
"""


MARKDOWN_CHUNK_TEMPLATE = """请翻译下面这篇 Hermes Agent 文档的其中一个片段。

额外要求：
- 这是第 {chunk_index} / {chunk_total} 个片段，请只输出这个片段对应的中文内容。
- 保持所有 Markdown 结构、链接、锚点、代码块数量与原文一致。
- 如果原文包含 HTML/JSX 标签，只翻译其中对用户可见的文本，不要破坏标签或属性。
- 表格结构必须完全保留。
- 文档面向中文开发者，但要尽量好懂。
- 遇到 Agent 或 Agents 时，优先保留 Agent / Agents，不要随手翻成“代理”。

文档路径：{path}

--- BEGIN DOCUMENT CHUNK ---
{content}
--- END DOCUMENT CHUNK ---
"""


JSON_SYSTEM_PROMPT = """你是一名专业的软件文档本地化编辑。

请把输入的 JSON 文档翻译成简体中文，并严格遵守下面规则：

1. 输出必须是合法 JSON，不能添加任何解释性文本。
2. JSON 的键名、层级结构、数组长度、数字、布尔值、null、对象顺序都必须保持不变。
3. 只翻译用户可见的字符串值，比如 label、title、description、caption。
4. 命令、路径、环境变量、URL、模型名、品牌名、API 名称默认保持英文。
5. 凡是英文原文里明确写了 Agent 或 Agents，默认保留为 Agent 或 Agents，不要翻成“代理”。只有在原文明显指网络 proxy 时，才使用“代理”。
6. 中文要自然、好懂，不要端着，不要使用“落盘”“收口”等黑话，也不要频繁使用“不是……而是……”这种句式。
"""


JSON_USER_TEMPLATE = """请翻译下面这个 Hermes Agent 文档相关的 JSON 文件。

文档路径：{path}

--- BEGIN JSON ---
{content}
--- END JSON ---
"""


def find_api_key() -> str:
    candidates = (
        os.getenv("HERMES_DOCS_TRANSLATION_API_KEY"),
        os.getenv("OPENROUTER_API_KEY"),
        os.getenv("ANTHROPIC_AUTH_TOKEN"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("KIMI_API_KEY"),
    )
    for value in candidates:
        if value and value.strip():
            return value.strip()
    raise RuntimeError(
        "No translation API key found. Set HERMES_DOCS_TRANSLATION_API_KEY, "
        "OPENROUTER_API_KEY, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_API_KEY, or KIMI_API_KEY."
    )


def find_base_url() -> str | None:
    candidates = (
        os.getenv("HERMES_DOCS_TRANSLATION_BASE_URL"),
        os.getenv("OPENROUTER_BASE_URL"),
        os.getenv("ANTHROPIC_BASE_URL"),
        os.getenv("KIMI_BASE_URL"),
    )
    for value in candidates:
        if value and value.strip():
            return value.strip()
    return None


def resolve_transport(base_url: str | None, explicit: str | None) -> str:
    if explicit:
        return explicit

    lowered = (base_url or "").lower()
    if "openrouter.ai" in lowered or "/api/v1" in lowered:
        return "openai"
    return "anthropic"


def build_client(transport: str, api_key: str, base_url: str | None):
    if transport == "anthropic":
        from agent.anthropic_adapter import build_anthropic_client

        return build_anthropic_client(api_key, base_url)

    from openai import OpenAI

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def count_headings(text: str) -> int:
    return len(re.findall(r"(?m)^#{1,6}\s", text))


def count_fences(text: str) -> int:
    return text.count("```")


def count_admonitions(text: str) -> int:
    return len(re.findall(r"(?m)^:::[a-zA-Z]+", text))


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text

    match = re.match(r"^---\n.*?\n---\n", text, flags=re.DOTALL)
    if not match:
        return "", text

    return match.group(0), text[match.end():]


def extract_frontmatter_lines(frontmatter: str) -> list[str]:
    if not frontmatter:
        return []
    lines = frontmatter.splitlines()
    if len(lines) < 3 or lines[0] != "---" or lines[-1] != "---":
        return []
    return lines[1:-1]


def extract_frontmatter_keys(frontmatter: str) -> list[str]:
    keys: list[str] = []
    for line in extract_frontmatter_lines(frontmatter):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*.*$", line)
        if match:
            keys.append(match.group(1))
    return keys


TRANSLATABLE_FRONTMATTER_KEYS = {"title", "description", "sidebar_label"}


def collect_frontmatter_line_map(frontmatter: str) -> dict[str, str]:
    line_map: dict[str, str] = {}
    for line in extract_frontmatter_lines(frontmatter):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*.*$", line)
        if match:
            line_map[match.group(1)] = line
    return line_map


def collect_partial_frontmatter_line_map(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None

    after_open = text[len("---\n") :]
    lines = after_open.splitlines()
    line_map: dict[str, str] = {}
    consumed = 0

    for line in lines:
        if not line.strip():
            consumed += 1
            break
        match = re.match(r"^([A-Za-z0-9_-]+):\s*.*$", line)
        if not match:
            break
        line_map[match.group(1)] = line
        consumed += 1

    if not line_map:
        return None

    body_lines = lines[consumed:]
    body = "\n".join(body_lines).lstrip("\n")
    if text.endswith("\n") and body and not body.endswith("\n"):
        body += "\n"
    return line_map, body


def repair_translated_frontmatter(source_frontmatter: str, translated: str) -> str:
    if not source_frontmatter:
        return translated

    translated_frontmatter, _ = split_frontmatter(translated)
    source_lines = extract_frontmatter_lines(source_frontmatter)
    if not source_lines:
        return translated

    translated_line_map: dict[str, str] = {}
    body = translated

    if translated_frontmatter:
        translated_line_map = collect_frontmatter_line_map(translated_frontmatter)
        body = translated[len(translated_frontmatter) :]
    else:
        partial = collect_partial_frontmatter_line_map(translated)
        if partial is not None:
            translated_line_map, body = partial

    rebuilt_lines: list[str] = []
    for source_line in source_lines:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*.*$", source_line)
        if not match:
            rebuilt_lines.append(source_line)
            continue
        key = match.group(1)
        if key in TRANSLATABLE_FRONTMATTER_KEYS and key in translated_line_map:
            rebuilt_lines.append(translated_line_map[key])
        else:
            rebuilt_lines.append(source_line)

    repaired = "---\n" + "\n".join(rebuilt_lines) + "\n---\n"
    if body:
        repaired += body
        if translated.endswith("\n") and not repaired.endswith("\n"):
            repaired += "\n"
    return repaired


def split_markdown_chunks(text: str, max_chars: int = 8000) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    lines = text.splitlines(keepends=True)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    in_fence = False

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append("".join(current))
            current = []
            current_len = 0

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence

        is_heading = bool(re.match(r"^#{1,3}\s", stripped))
        is_blank = not stripped.strip()
        should_split = (
            current
            and current_len >= max_chars
            and not in_fence
            and (is_heading or is_blank)
        )

        if should_split:
            flush()

        current.append(line)
        current_len += len(line)

    flush()
    return chunks


def validate_markdown_translation(source: str, translated: str) -> list[str]:
    issues: list[str] = []

    source_frontmatter, _ = split_frontmatter(source)
    translated_frontmatter, _ = split_frontmatter(translated)

    if source_frontmatter and not translated_frontmatter:
        issues.append("frontmatter malformed")
    elif source_frontmatter and translated_frontmatter:
        if extract_frontmatter_keys(source_frontmatter) != extract_frontmatter_keys(translated_frontmatter):
            issues.append("frontmatter keys changed")
        source_line_map = collect_frontmatter_line_map(source_frontmatter)
        translated_line_map = collect_frontmatter_line_map(translated_frontmatter)
        for key, source_line in source_line_map.items():
            if key in TRANSLATABLE_FRONTMATTER_KEYS:
                continue
            if translated_line_map.get(key) != source_line:
                issues.append(f"frontmatter protected key changed: {key}")
                break

    if count_headings(source) != count_headings(translated):
        issues.append("heading count changed")

    if count_fences(source) != count_fences(translated):
        issues.append("code fence count changed")

    if count_admonitions(source) != count_admonitions(translated):
        issues.append("admonition count changed")

    return issues


def normalize_translated_markdown_links(text: str) -> str:
    """Rewrite source-site /docs links for the Chinese site deployed at root."""
    replacements = (
        (r"\]\(/docs/", "](/"),
        (r'href="/docs/', 'href="/'),
        (r'src="/docs/', 'src="/'),
        (r"/docs/user-guide/features/profiles(?=$|[)#])", "/user-guide/profiles"),
        (r"/user-guide/features/profiles(?=$|[)#])", "/user-guide/profiles"),
        (r"/user-guide/features/hooks#pre_api_request", "/user-guide/features/hooks#plugin-hooks"),
        (r"/user-guide/features/hooks#post_api_request", "/user-guide/features/hooks#plugin-hooks"),
    )
    normalized = text
    for pattern, replacement in replacements:
        normalized = re.sub(pattern, replacement, normalized)
    return normalized


MARKDOWN_LINK_PATTERN = re.compile(
    r"(?<!\!)\[[^\]]+\]\((?P<url>[^)\s]+(?:\s+\"[^\"]*\")?)\)"
)


def collect_markdown_link_matches(text: str) -> list[dict[str, int | str]]:
    frontmatter, body = split_frontmatter(text)
    matches: list[dict[str, int | str]] = []
    in_fence = False
    fence_char = ""
    offset = len(frontmatter)

    for line in body.splitlines(keepends=True):
        fence_match = re.match(r"^(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
            elif marker[0] == fence_char:
                in_fence = False
                fence_char = ""
            offset += len(line)
            continue

        if not in_fence:
            for match in MARKDOWN_LINK_PATTERN.finditer(line):
                matches.append(
                    {
                        "start": offset + match.start("url"),
                        "end": offset + match.end("url"),
                        "url": match.group("url"),
                    }
                )

        offset += len(line)

    return matches


def restore_source_link_destinations(source_text: str, translated_text: str) -> str:
    source_matches = collect_markdown_link_matches(source_text)
    translated_matches = collect_markdown_link_matches(translated_text)

    if not source_matches or len(source_matches) != len(translated_matches):
        return translated_text

    rebuilt: list[str] = []
    last_index = 0

    for source_match, translated_match in zip(source_matches, translated_matches, strict=True):
        start = int(translated_match["start"])
        end = int(translated_match["end"])
        rebuilt.append(translated_text[last_index:start])
        rebuilt.append(str(source_match["url"]))
        last_index = end

    rebuilt.append(translated_text[last_index:])
    return "".join(rebuilt)


def escape_angle_placeholders_in_inline_code(text: str) -> str:
    """Prevent MDX from treating CLI placeholders like <name> as JSX tags."""

    def replace_code_span(match: re.Match[str]) -> str:
        code = match.group(0)
        return re.sub(r"<([A-Za-z][^<>`\n]*)>", r"&lt;\1&gt;", code)

    return re.sub(r"`[^`\n]+`", replace_code_span, text)


def strip_markdown_inline_formatting(text: str) -> str:
    normalized = text
    normalized = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"`([^`]*)`", r"\1", normalized)
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    normalized = re.sub(r"[*_~]", "", normalized)
    normalized = normalized.replace("&lt;", " ").replace("&gt;", " ")
    return normalized.strip()


def slugify_heading_anchor(text: str) -> str:
    normalized = strip_markdown_inline_formatting(text)
    normalized = unicodedata.normalize("NFKD", normalized)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    normalized = re.sub(r"[-\s]+", "-", normalized).strip("-")
    return normalized


def extract_markdown_headings(text: str) -> list[dict[str, str | int | None]]:
    _, body = split_frontmatter(text)
    headings: list[dict[str, str | int | None]] = []
    lines = body.splitlines()
    in_fence = False
    fence_char = ""

    for index, line in enumerate(lines):
        fence_match = re.match(r"^(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
            elif marker[0] == fence_char:
                in_fence = False
                fence_char = ""
            continue

        if in_fence:
            continue

        match = re.match(r"^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$", line)
        if not match:
            continue

        raw_text = match.group(2).strip()
        explicit_id = None
        id_match = re.search(r"\s*\{#([A-Za-z0-9._:-]+)\}\s*$", raw_text)
        if id_match:
            explicit_id = id_match.group(1)
            raw_text = raw_text[: id_match.start()].rstrip()

        headings.append(
            {
                "line_index": index,
                "heading_text": raw_text,
                "explicit_id": explicit_id,
            }
        )

    return headings


def inject_source_anchor_aliases(source_text: str, translated_text: str) -> str:
    source_frontmatter, source_body = split_frontmatter(source_text)
    translated_frontmatter, translated_body = split_frontmatter(translated_text)

    source_headings = extract_markdown_headings(source_text)
    translated_headings = extract_markdown_headings(translated_text)

    if not source_headings or len(source_headings) != len(translated_headings):
        return translated_text

    translated_lines = translated_body.splitlines()
    existing_aliases = set(re.findall(r'<a id="([^"]+)"></a>', translated_body))
    insertions: list[tuple[int, str]] = []

    for source_heading, translated_heading in zip(source_headings, translated_headings, strict=True):
        source_anchor = source_heading["explicit_id"] or slugify_heading_anchor(
            str(source_heading["heading_text"])
        )
        translated_anchor = translated_heading["explicit_id"]

        if not source_anchor:
            continue
        if source_anchor == translated_anchor:
            continue
        if source_anchor in existing_aliases:
            continue

        insertions.append((int(translated_heading["line_index"]), f'<a id="{source_anchor}"></a>'))
        existing_aliases.add(source_anchor)

    if not insertions:
        return translated_text

    had_trailing_newline = translated_body.endswith("\n")
    offset = 0
    for line_index, alias in insertions:
        insert_at = line_index + offset
        if insert_at > 0 and translated_lines[insert_at - 1].strip() == alias:
            continue
        translated_lines.insert(insert_at, alias)
        offset += 1

    rebuilt_body = "\n".join(translated_lines)
    if had_trailing_newline:
        rebuilt_body += "\n"

    return translated_frontmatter + rebuilt_body if translated_frontmatter else rebuilt_body


STABLE_HEADING_IDS: dict[str, dict[str, str]] = {
    "developer-guide/creating-skills.md": {
        "### 配置设置 (config.yaml)": "config-settings-configyaml",
    },
    "developer-guide/memory-provider-plugin.md": {
        "## 添加 CLI 命令": "adding-cli-commands",
    },
    "guides/build-a-hermes-plugin.md": {
        "### `pre_llm_call` 上下文注入": "pre_llm_call-context-injection",
    },
    "guides/migrate-from-openclaw.md": {
        "## API Key 解析": "api-key-resolution",
        "## SecretRef 处理": "secretref-handling",
    },
    "integrations/providers.md": {
        "### WSL2 网络（Windows 用户）": "wsl2-networking-windows-users",
        "### 上下文长度检测": "context-length-detection",
        "## 回退模型 (Fallback Model)": "fallback-model",
    },
    "reference/faq.md": {
        "## Profile (配置文件)": "profiles",
    },
    "reference/slash-commands.md": {
        "## 注意事项": "notes",
    },
    "user-guide/cli.md": {
        "## 后台会话": "background-sessions",
    },
    "user-guide/configuration.md": {
        "## 技能设置": "skill-settings",
        "## 上下文压缩": "context-compression",
        "## 辅助模型": "auxiliary-models",
        "## 显示设置": "display-settings",
        "## 快捷命令": "quick-commands",
        "## 凭证池策略": "credential-pool-strategies",
        "## 网站黑名单": "website-blocklist",
    },
    "user-guide/docker.md": {
        "## Docker Compose 示例": "docker-compose-example",
    },
    "user-guide/features/context-files.md": {
        "## 安全：提示词注入保护": "security-prompt-injection-protection",
    },
    "user-guide/features/hooks.md": {
        "## Gateway 事件钩子": "gateway-event-hooks",
        "## Plugin 钩子": "plugin-hooks",
    },
    "user-guide/features/mcp.md": {
        "### 动态工具发现": "dynamic-tool-discovery",
        "## 将 Hermes 作为 MCP 服务器运行": "running-hermes-as-an-mcp-server",
    },
    "user-guide/features/plugins.md": {
        "## 注入消息": "injecting-messages",
    },
    "user-guide/features/skills.md": {
        "## 外部技能目录": "external-skill-directories",
    },
    "user-guide/messaging/discord.md": {
        "### Discord 中的会话模型": "session-model-in-discord",
    },
    "user-guide/messaging/feishu.md": {
        "## WebSocket 调优": "websocket-tuning",
        "## 逐群组访问控制": "per-group-access-control",
    },
    "user-guide/messaging/index.md": {
        "### 私信 (DM) 配对（白名单的替代方案）": "dm-pairing-alternative-to-allowlists",
        "## 后台会话": "background-sessions",
    },
    "user-guide/messaging/telegram.md": {
        "## 第 3 步：隐私模式（群组关键设置）": "step-3-privacy-mode-critical-for-groups",
        "## 私聊话题 (Bot API 9.4)": "private-chat-topics-bot-api-94",
    },
    "user-guide/security.md": {
        "### DM 配对系统": "dm-pairing-system",
    },
    "user-guide/sessions.md": {
        "### 恢复时的对话回顾": "conversation-recap-on-resume",
        "## 会话命名": "session-naming",
    },
}


STABLE_ALIAS_INSERTIONS: dict[str, list[tuple[str, str]]] = {
    "user-guide/features/hooks.md": [
        ("## Plugin 钩子", '<a id="pre_api_request"></a>\n<a id="post_api_request"></a>'),
    ],
}


def apply_stable_heading_ids(relative_path: Path, source_text: str, text: str) -> str:
    rel = relative_path.as_posix()
    updated = inject_source_anchor_aliases(source_text, text)

    for heading, anchor_id in STABLE_HEADING_IDS.get(rel, {}).items():
        anchored_heading = f"{heading} {{#{anchor_id}}}"
        if anchored_heading in updated:
            continue
        updated = updated.replace(heading, anchored_heading, 1)

    for marker, alias_block in STABLE_ALIAS_INSERTIONS.get(rel, []):
        if alias_block in updated:
            continue
        marker_with_id = marker
        if marker in STABLE_HEADING_IDS.get(rel, {}):
            marker_with_id = f"{marker} {{#{STABLE_HEADING_IDS[rel][marker]}}}"

        exact_line = re.compile(rf"^{re.escape(marker_with_id)}$", re.MULTILINE)
        if exact_line.search(updated):
            updated = exact_line.sub(f"{marker_with_id}\n{alias_block}", updated, count=1)
            continue

        plain_line = re.compile(rf"^{re.escape(marker)}$", re.MULTILINE)
        updated = plain_line.sub(f"{marker}\n{alias_block}", updated, count=1)

    return updated


def compare_json_shape(source, translated, path: str = "$") -> list[str]:
    issues: list[str] = []

    if type(source) is not type(translated):
        return [f"type changed at {path}"]

    if isinstance(source, dict):
        if list(source.keys()) != list(translated.keys()):
            return [f"keys changed at {path}"]
        for key in source:
            issues.extend(compare_json_shape(source[key], translated[key], f"{path}.{key}"))
        return issues

    if isinstance(source, list):
        if len(source) != len(translated):
            return [f"list length changed at {path}"]
        for index, (src_item, tgt_item) in enumerate(zip(source, translated, strict=True)):
            issues.extend(compare_json_shape(src_item, tgt_item, f"{path}[{index}]"))
        return issues

    if not isinstance(source, str) and source != translated:
        issues.append(f"non-string value changed at {path}")

    return issues


def validate_json_translation(source: str, translated: str) -> list[str]:
    issues: list[str] = []

    try:
        source_obj = json.loads(source)
    except json.JSONDecodeError as exc:  # pragma: no cover - source is versioned data
        return [f"source json invalid: {exc}"]

    try:
        translated_obj = json.loads(translated)
    except json.JSONDecodeError as exc:
        return [f"translated json invalid: {exc}"]

    issues.extend(compare_json_shape(source_obj, translated_obj))
    return issues


def call_model(client, transport: str, model: str, system_prompt: str, prompt: str) -> str:
    if transport == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )

        parts = []
        for block in response.content:
            block_text = getattr(block, "text", "")
            if block_text:
                parts.append(block_text)
        return "".join(parts).strip()

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=16000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def translate_markdown_text(
    client,
    transport: str,
    model: str,
    relative_path: Path,
    content: str,
    retries: int = 2,
    chunk_index: int | None = None,
    chunk_total: int | None = None,
    validate: bool = True,
) -> str:
    if chunk_index is not None and chunk_total is not None:
        prompt = MARKDOWN_CHUNK_TEMPLATE.format(
            path=relative_path.as_posix(),
            content=content,
            chunk_index=chunk_index,
            chunk_total=chunk_total,
        )
    else:
        prompt = MARKDOWN_USER_TEMPLATE.format(path=relative_path.as_posix(), content=content)

    extra_hint = ""
    issues: list[str] = []

    last_exception: Exception | None = None

    for _ in range(retries + 1):
        try:
            translated = call_model(
                client,
                transport,
                model,
                MARKDOWN_SYSTEM_PROMPT + extra_hint,
                prompt,
            )
        except Exception as exc:
            last_exception = exc
            extra_hint = "\n\n上一次调用失败，请重新输出完整文档，并严格保持结构不变。"
            time.sleep(1)
            continue
        issues = validate_markdown_translation(content, translated) if validate else []
        if not issues:
            if content.endswith("\n") and not translated.endswith("\n"):
                translated += "\n"
            return translated

        extra_hint = (
            "\n\n上一次输出有问题："
            + "、".join(issues)
            + "。请严格保持原文结构与标记数量不变，重新输出完整文档。"
        )

    if last_exception is not None and not issues:
        raise RuntimeError(f"Markdown translation failed for {relative_path}: {last_exception}") from last_exception

    raise RuntimeError(f"Markdown translation validation failed for {relative_path}: {issues}")


def translate_json_text(
    client,
    transport: str,
    model: str,
    relative_path: Path,
    content: str,
    retries: int = 2,
    validate: bool = True,
) -> str:
    prompt = JSON_USER_TEMPLATE.format(path=relative_path.as_posix(), content=content)
    extra_hint = ""
    issues: list[str] = []
    last_exception: Exception | None = None

    for _ in range(retries + 1):
        try:
            translated = call_model(client, transport, model, JSON_SYSTEM_PROMPT + extra_hint, prompt)
        except Exception as exc:
            last_exception = exc
            extra_hint = "\n\n上一次调用失败，请重新输出完整 JSON，并保持原有结构完全不变。"
            time.sleep(1)
            continue
        issues = validate_json_translation(content, translated) if validate else []
        if not issues:
            if content.endswith("\n") and not translated.endswith("\n"):
                translated += "\n"
            return translated

        extra_hint = (
            "\n\n上一次输出有问题："
            + "、".join(issues)
            + "。请重新输出完整 JSON，保持键名、层级和非字符串值完全不变。"
        )

    if last_exception is not None and not issues:
        raise RuntimeError(f"JSON translation failed for {relative_path}: {last_exception}") from last_exception

    raise RuntimeError(f"JSON translation validation failed for {relative_path}: {issues}")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def translate_markdown_file(
    client,
    transport: str,
    model: str,
    source_path: Path,
    target_path: Path,
    source_root: Path = SOURCE_DOCS_ROOT,
    dry_run: bool = False,
    chunk_size: int = 8000,
    validate: bool = True,
) -> None:
    original = source_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(original)
    chunks = split_markdown_chunks(body, max_chars=chunk_size)
    relative_path = source_path.relative_to(source_root)

    translated_chunks: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        payload = frontmatter + chunk if idx == 1 else chunk
        translated_chunk = translate_markdown_text(
            client,
            transport,
            model,
            relative_path,
            payload,
            chunk_index=idx if len(chunks) > 1 else None,
            chunk_total=len(chunks) if len(chunks) > 1 else None,
            validate=validate,
        )
        translated_chunk = repair_translated_frontmatter(frontmatter, translated_chunk)
        translated_chunk = restore_source_link_destinations(payload, translated_chunk)
        translated_chunk = normalize_translated_markdown_links(translated_chunk)
        translated_chunk = escape_angle_placeholders_in_inline_code(translated_chunk)
        translated_chunk = apply_stable_heading_ids(relative_path, payload, translated_chunk)
        translated_chunks.append(translated_chunk)

    translated = "".join(translated_chunks)
    issues = validate_markdown_translation(original, translated) if validate else []
    if issues:
        raise RuntimeError(f"Final markdown validation failed for {relative_path}: {issues}")

    if dry_run:
        print(f"[dry-run] translated {target_path.relative_to(REPO_ROOT)}")
        return

    ensure_parent(target_path)
    target_path.write_text(translated, encoding="utf-8")
    print(f"[ok] {target_path.relative_to(REPO_ROOT)}")


def translate_json_file(
    client,
    transport: str,
    model: str,
    source_path: Path,
    target_path: Path,
    source_root: Path = SOURCE_DOCS_ROOT,
    dry_run: bool = False,
    validate: bool = True,
) -> None:
    original = source_path.read_text(encoding="utf-8")
    translated = translate_json_text(
        client,
        transport,
        model,
        source_path.relative_to(source_root),
        original,
        validate=validate,
    )

    issues = validate_json_translation(original, translated) if validate else []
    if issues:
        raise RuntimeError(
            f"Final json validation failed for {source_path.relative_to(source_root)}: {issues}"
        )

    if dry_run:
        print(f"[dry-run] translated {target_path.relative_to(REPO_ROOT)}")
        return

    ensure_parent(target_path)
    target_path.write_text(translated, encoding="utf-8")
    print(f"[ok] {target_path.relative_to(REPO_ROOT)}")


def translate_path(
    client,
    transport: str,
    model: str,
    source_path: Path,
    target_path: Path,
    source_root: Path = SOURCE_DOCS_ROOT,
    dry_run: bool = False,
    chunk_size: int = 8000,
    validate: bool = True,
) -> None:
    if source_path.suffix == ".md":
        translate_markdown_file(
            client,
            transport,
            model,
            source_path,
            target_path,
            source_root=source_root,
            dry_run=dry_run,
            chunk_size=chunk_size,
            validate=validate,
        )
        return

    if source_path.suffix == ".json":
        translate_json_file(
            client,
            transport,
            model,
            source_path,
            target_path,
            source_root=source_root,
            dry_run=dry_run,
            validate=validate,
        )
        return

    raise ValueError(f"Unsupported file type: {source_path}")


def looks_translated(path: Path) -> bool:
    if not path.exists():
        return False

    text = path.read_text(encoding="utf-8")

    if path.suffix == ".json":
        return bool(re.search(r"[\u4e00-\u9fff]", text))

    lines = text.splitlines()[:20]
    sample = "\n".join(lines)
    return bool(re.search(r"(?m)^(title:\s*\"?.*[\u4e00-\u9fff].*\"?|#\s+.*[\u4e00-\u9fff])", sample))


def iter_doc_files(
    root: Path,
    limit: int | None = None,
    selected: Iterable[str] | None = None,
) -> list[Path]:
    if selected:
        files = [root / item for item in selected]
    else:
        files = sorted(
            path for path in root.rglob("*") if path.is_file() and path.suffix in TRANSLATABLE_SUFFIXES
        )

    if limit is not None:
        return files[:limit]
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate Hermes docs from website/docs into site/docs.")
    parser.add_argument(
        "--model",
        default=os.getenv("HERMES_DOCS_TRANSLATION_MODEL", "kimi-k2-turbo-preview"),
    )
    parser.add_argument(
        "--transport",
        choices=["anthropic", "openai"],
        default=os.getenv("HERMES_DOCS_TRANSLATION_TRANSPORT"),
    )
    parser.add_argument("--limit", type=int, default=None, help="Translate only the first N files for testing.")
    parser.add_argument("--files", nargs="*", default=None, help="Translate only these website/docs relative paths.")
    parser.add_argument("--chunk-size", type=int, default=8000, help="Maximum characters per translation chunk.")
    parser.add_argument("--no-validate", action="store_true", help="Skip structural validation for difficult pages.")
    parser.add_argument(
        "--skip-translated",
        action="store_true",
        help="Skip target files that already look translated.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Call the model but do not write files.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between files in seconds.")
    parser.add_argument("--source-root", default=str(SOURCE_DOCS_ROOT), help="Source docs root directory.")
    parser.add_argument("--target-root", default=str(TARGET_DOCS_ROOT), help="Target docs root directory.")
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    target_root = Path(args.target_root).resolve()

    api_key = find_api_key()
    base_url = find_base_url()
    transport = resolve_transport(base_url, args.transport)
    client = build_client(transport, api_key, base_url)

    files = iter_doc_files(source_root, limit=args.limit, selected=args.files)
    if args.skip_translated:
        files = [
            path
            for path in files
            if not looks_translated(target_root / path.relative_to(source_root))
        ]

    print(f"Translating {len(files)} files with model: {args.model} via {transport}")

    for index, source_path in enumerate(files, start=1):
        target_path = target_root / source_path.relative_to(source_root)
        print(f"[{index}/{len(files)}] {source_path.relative_to(REPO_ROOT)} -> {target_path.relative_to(REPO_ROOT)}")
        translate_path(
            client,
            transport=transport,
            model=args.model,
            source_path=source_path,
            target_path=target_path,
            source_root=source_root,
            dry_run=args.dry_run,
            chunk_size=args.chunk_size,
            validate=not args.no_validate,
        )
        time.sleep(args.sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
