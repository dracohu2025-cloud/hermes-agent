from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "site" / "docs"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.anthropic_adapter import build_anthropic_client  # noqa: E402
from openai import OpenAI  # noqa: E402


SYSTEM_PROMPT = """你是一名专业的软件文档翻译编辑。

请把英文 Docusaurus Markdown/MDX 文档完整翻译成简体中文，并严格遵守下面规则：

1. 不得遗漏任何内容，段落、标题、表格、提示框、列表、引用、HTML/JSX 块都要保留。
2. 保持原始文档结构不变，标题层级、段落顺序、表格行数、链接目标、锚点、相对路径都不能改。
3. YAML frontmatter 的键名必须原样保留，只翻译用户可见的值，比如 title、description。
4. 代码块内容默认原样保留，不翻译命令、路径、环境变量、代码、JSON/YAML/TOML 配置项，也不要改代码块语言标记。
5. 行内代码、文件路径、命令名、模型名、品牌名、产品名、API 名称保持英文。
6. Mermaid、DOT、ASCII 图、HTML 标签、JSX 语法、注释标记、admonition 语法（:::tip 等）必须保留可用。
7. 中文风格要通俗易懂、自然、不端着，避免翻译腔，避免使用“落盘”“收口”等黑话，也不要频繁使用“不是……而是……”这种句式。
8. 输出只能是翻译后的文档正文，不要补充解释，不要加“以下是翻译”之类的话。
"""


USER_TEMPLATE = """请翻译下面这篇 Hermes Agent 文档。

额外要求：
- 保持所有 Markdown 结构、链接、锚点、代码块数量与原文一致。
- 如果原文包含 HTML/JSX 标签，只翻译其中对用户可见的文本，不要破坏标签或属性。
- 表格结构必须完全保留。
- 文档面向中文开发者，但要尽量好懂。

文档路径：{path}

--- BEGIN DOCUMENT ---
{content}
--- END DOCUMENT ---
"""


CHUNK_TEMPLATE = """请翻译下面这篇 Hermes Agent 文档的其中一个片段。

额外要求：
- 这是第 {chunk_index} / {chunk_total} 个片段，请只输出这个片段对应的中文内容。
- 保持所有 Markdown 结构、链接、锚点、代码块数量与原文一致。
- 如果原文包含 HTML/JSX 标签，只翻译其中对用户可见的文本，不要破坏标签或属性。
- 表格结构必须完全保留。
- 文档面向中文开发者，但要尽量好懂。

文档路径：{path}

--- BEGIN DOCUMENT CHUNK ---
{content}
--- END DOCUMENT CHUNK ---
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


def validate_translation(source: str, translated: str) -> list[str]:
    issues: list[str] = []

    if source.lstrip().startswith("---") and not translated.lstrip().startswith("---"):
        issues.append("frontmatter missing")

    if count_headings(source) != count_headings(translated):
        issues.append("heading count changed")

    if count_fences(source) != count_fences(translated):
        issues.append("code fence count changed")

    if count_admonitions(source) != count_admonitions(translated):
        issues.append("admonition count changed")

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


def translate_text(
    client,
    transport: str,
    model: str,
    path: Path,
    content: str,
    retries: int = 2,
    chunk_index: int | None = None,
    chunk_total: int | None = None,
    validate: bool = True,
) -> str:
    if chunk_index is not None and chunk_total is not None:
        prompt = CHUNK_TEMPLATE.format(
            path=path.as_posix(),
            content=content,
            chunk_index=chunk_index,
            chunk_total=chunk_total,
        )
    else:
        prompt = USER_TEMPLATE.format(path=path.as_posix(), content=content)

    extra_hint = ""
    issues: list[str] = []

    for _ in range(retries + 1):
        translated = call_model(client, transport, model, SYSTEM_PROMPT + extra_hint, prompt)
        issues = validate_translation(content, translated) if validate else []
        if not issues:
            return translated + ("\n" if content.endswith("\n") and not translated.endswith("\n") else "")

        extra_hint = (
            "\n\n上一次输出有问题："
            + "、".join(issues)
            + "。请严格保持原文结构与标记数量不变，重新输出完整文档。"
        )

    raise RuntimeError(f"Translation validation failed for {path}: {issues}")


def translate_file(
    client,
    transport: str,
    model: str,
    path: Path,
    dry_run: bool = False,
    chunk_size: int = 8000,
    validate: bool = True,
) -> None:
    original = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(original)
    chunks = split_markdown_chunks(body, max_chars=chunk_size)

    translated_chunks: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        payload = frontmatter + chunk if idx == 1 else chunk
        translated_chunk = translate_text(
            client,
            transport,
            model,
            path.relative_to(DOCS_ROOT),
            payload,
            chunk_index=idx if len(chunks) > 1 else None,
            chunk_total=len(chunks) if len(chunks) > 1 else None,
            validate=validate,
        )
        translated_chunks.append(translated_chunk)

    translated = "".join(translated_chunks)
    issues = validate_translation(original, translated) if validate else []
    if issues:
        raise RuntimeError(f"Final translation validation failed for {path}: {issues}")

    if dry_run:
        print(f"[dry-run] translated {path.relative_to(REPO_ROOT)}")
        return

    path.write_text(translated, encoding="utf-8")
    print(f"[ok] {path.relative_to(REPO_ROOT)}")


def looks_translated(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()[:20]
    sample = "\n".join(lines)
    return bool(re.search(r"(?m)^(title:\s*\"?.*[\u4e00-\u9fff].*\"?|#\s+.*[\u4e00-\u9fff])", sample))


def iter_markdown_files(limit: int | None = None, selected: Iterable[str] | None = None) -> list[Path]:
    if selected:
        files = [DOCS_ROOT / item for item in selected]
    else:
        files = sorted(DOCS_ROOT.rglob("*.md"))

    if limit is not None:
        return files[:limit]
    return files


def resolve_transport(base_url: str | None, explicit: str | None) -> str:
    if explicit:
        return explicit

    lowered = (base_url or "").lower()
    if "openrouter.ai" in lowered or "/api/v1" in lowered:
        return "openai"
    return "anthropic"


def build_client(transport: str, api_key: str, base_url: str | None):
    if transport == "anthropic":
        return build_anthropic_client(api_key, base_url)

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate Hermes docs in site/docs to Simplified Chinese.")
    parser.add_argument("--model", default=os.getenv("HERMES_DOCS_TRANSLATION_MODEL", "kimi-k2-turbo-preview"))
    parser.add_argument("--transport", choices=["anthropic", "openai"], default=os.getenv("HERMES_DOCS_TRANSLATION_TRANSPORT"))
    parser.add_argument("--limit", type=int, default=None, help="Translate only the first N files for testing.")
    parser.add_argument("--files", nargs="*", default=None, help="Translate only these site/docs relative paths.")
    parser.add_argument("--chunk-size", type=int, default=8000, help="Maximum characters per translation chunk.")
    parser.add_argument("--no-validate", action="store_true", help="Skip structural validation for difficult pages.")
    parser.add_argument("--skip-translated", action="store_true", help="Skip files that already look translated.")
    parser.add_argument("--dry-run", action="store_true", help="Call the model but do not write files.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between files in seconds.")
    args = parser.parse_args()

    api_key = find_api_key()
    base_url = find_base_url()
    transport = resolve_transport(base_url, args.transport)
    client = build_client(transport, api_key, base_url)

    files = iter_markdown_files(limit=args.limit, selected=args.files)
    if args.skip_translated:
        files = [path for path in files if not looks_translated(path)]
    print(f"Translating {len(files)} files with model: {args.model} via {transport}")

    for index, path in enumerate(files, start=1):
        print(f"[{index}/{len(files)}] {path.relative_to(REPO_ROOT)}")
        translate_file(
            client,
            transport=transport,
            model=args.model,
            path=path,
            dry_run=args.dry_run,
            chunk_size=args.chunk_size,
            validate=not args.no_validate,
        )
        time.sleep(args.sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
