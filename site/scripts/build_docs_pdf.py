from __future__ import annotations

import argparse
import contextlib
import html
import json
import re
import socket
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "site"
DOCS_ROOT = SITE_ROOT / "docs"
BUILD_ROOT = SITE_ROOT / "build"
DEFAULT_OUTPUT = SITE_ROOT / "static" / "downloads" / "hermes-agent-zh-docs.pdf"
DEFAULT_SITE_URL = "https://hermes-doc.aigc.green"
MERMAID_WAIT_MS = 300
CHROME_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)
type SidebarNode = dict[str, object]


def list_doc_ids(docs_root: Path) -> set[str]:
    doc_ids: set[str] = set()
    for path in docs_root.rglob("*.md"):
        relative = path.relative_to(docs_root)
        if relative.name == "_category_.json":
            continue
        if relative.name.endswith(".md"):
            doc_ids.add(relative.as_posix()[:-3])
    return doc_ids


def load_sidebar_docs_config(sidebars_path: Path) -> list[object]:
    text = sidebars_path.read_text(encoding="utf-8")
    text = re.sub(r"^import[^\n]*\n", "", text, flags=re.M)
    text = text.replace(
        "const sidebars: SidebarsConfig = {",
        "const sidebars = {",
        1,
    )
    text = text.replace(
        "export default sidebars;",
        "console.log(JSON.stringify(sidebars.docs));",
        1,
    )
    result = subprocess.run(
        ["node", "-e", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def normalize_sidebar_tree(
    items: list[object],
    doc_ids: set[str],
    seen: set[str],
) -> list[SidebarNode]:
    nodes: list[SidebarNode] = []
    for item in items:
        if isinstance(item, str):
            if item in doc_ids and item not in seen:
                seen.add(item)
                nodes.append({"kind": "doc", "doc_id": item})
            continue

        if not isinstance(item, dict):
            continue

        item_type = item.get("type")
        if item_type == "doc":
            doc_id = item.get("id") or item.get("docId")
            if isinstance(doc_id, str) and doc_id in doc_ids and doc_id not in seen:
                seen.add(doc_id)
                node: SidebarNode = {"kind": "doc", "doc_id": doc_id}
                if isinstance(item.get("label"), str):
                    node["label"] = item["label"]
                nodes.append(node)
            continue

        if item_type == "category":
            raw_children = item.get("items")
            if not isinstance(raw_children, list):
                continue
            children = normalize_sidebar_tree(raw_children, doc_ids, seen)
            if children:
                nodes.append(
                    {
                        "kind": "category",
                        "label": item.get("label") or "未命名分类",
                        "children": children,
                    }
                )
    return nodes


def load_sidebar_tree(sidebars_path: Path, doc_ids: set[str]) -> list[SidebarNode]:
    raw_docs_config = load_sidebar_docs_config(sidebars_path)
    seen = {"index"}
    tree: list[SidebarNode] = [{"kind": "doc", "doc_id": "index", "label": "首页"}]
    tree.extend(normalize_sidebar_tree(raw_docs_config, doc_ids, seen))

    remaining = [
        doc_id
        for doc_id in sorted(doc_ids)
        if doc_id not in seen
    ]
    if remaining:
        tree.append(
            {
                "kind": "category",
                "label": "附录（未在网站侧边栏中显示）",
                "children": [{"kind": "doc", "doc_id": doc_id} for doc_id in remaining],
            }
        )
    return tree


def flatten_sidebar_tree(tree: list[SidebarNode]) -> list[str]:
    ordered: list[str] = []
    for node in tree:
        if node["kind"] == "doc":
            ordered.append(str(node["doc_id"]))
            continue
        ordered.extend(flatten_sidebar_tree(node["children"]))  # type: ignore[index]
    return ordered


def doc_id_to_route(doc_id: str) -> str:
    if doc_id == "index":
        return "/"
    if doc_id.endswith("/index"):
        return f"/{doc_id[:-len('/index')]}/"
    return f"/{doc_id}"


def route_to_doc_id(route_path: str, doc_ids: set[str]) -> str | None:
    clean = route_path.strip("/")
    if not clean:
        return "index"
    if clean in doc_ids:
        return clean
    with_index = f"{clean}/index"
    if with_index in doc_ids:
        return with_index
    return None


def page_anchor(doc_id: str) -> str:
    if doc_id == "index":
        return "doc--index"
    return f"doc--{doc_id.replace('/', '--')}"


def build_request_handler(directory: Path):
    return partial(SimpleHTTPRequestHandler, directory=str(directory))


def find_open_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def serve_directory(directory: Path):
    port = find_open_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), build_request_handler(directory))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def resolve_browser_executable(playwright) -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return playwright.chromium.executable_path


def collect_rendered_pages(doc_ids: list[str], base_url: str) -> tuple[dict[str, str], dict[str, str], list[str]]:
    html_by_doc: dict[str, str] = {}
    title_by_doc: dict[str, str] = {}
    stylesheet_urls: list[str] = []

    with sync_playwright() as playwright:
        chromium_executable = resolve_browser_executable(playwright)
        browser = playwright.chromium.launch(executable_path=chromium_executable)
        page = browser.new_page()
        for index, doc_id in enumerate(doc_ids):
            route = doc_id_to_route(doc_id)
            page.goto(f"{base_url}{route}", wait_until="networkidle")
            page.wait_for_timeout(MERMAID_WAIT_MS)

            if index == 0:
                stylesheet_urls = page.eval_on_selector_all(
                    "link[rel='stylesheet']",
                    "nodes => nodes.map(node => node.href)",
                )

            page.wait_for_selector("main .theme-doc-markdown.markdown")
            html_by_doc[doc_id] = page.eval_on_selector(
                "main .theme-doc-markdown.markdown",
                "node => node.innerHTML",
            )
            title_by_doc[doc_id] = (
                page.eval_on_selector(
                    "article h1",
                    "node => node.textContent.trim()",
                )
                or doc_id
            )

        browser.close()

    return html_by_doc, title_by_doc, stylesheet_urls


def rewrite_fragment(
    fragment_html: str,
    doc_id: str,
    doc_ids: set[str],
    asset_base_url: str,
    site_url: str,
) -> str:
    soup = BeautifulSoup(fragment_html, "html.parser")
    prefix = page_anchor(doc_id)

    for node in soup.select("a.hash-link"):
        node.decompose()

    for element in soup.find_all(id=True):
        element["id"] = f"{prefix}--{element['id']}"

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if href.startswith("#"):
            anchor["href"] = f"#{prefix}--{href[1:]}"
            continue

        if href.startswith(("http://", "https://", "mailto:", "tel:")):
            continue

        if href.startswith("/"):
            parsed = urlparse(href)
            target_doc = route_to_doc_id(parsed.path, doc_ids)
            if target_doc is not None:
                target_prefix = page_anchor(target_doc)
                if parsed.fragment:
                    anchor["href"] = f"#{target_prefix}--{parsed.fragment}"
                else:
                    anchor["href"] = f"#{target_prefix}"
            else:
                anchor["href"] = f"{site_url.rstrip('/')}{href}"

    for node in soup.find_all(src=True):
        src = node["src"]
        if src.startswith("/"):
            node["src"] = f"{asset_base_url}{src}"

    return str(soup)


def build_toc(tree: list[SidebarNode], title_by_doc: dict[str, str]) -> str:
    items: list[str] = []
    for node in tree:
        if node["kind"] == "doc":
            doc_id = str(node["doc_id"])
            label = str(node.get("label") or title_by_doc[doc_id])
            items.append(
                f'<li class="pdf-toc-doc"><a href="#{page_anchor(doc_id)}">{html.escape(label)}</a></li>'
            )
            continue

        label = html.escape(str(node["label"]))
        child_html = build_toc(node["children"], title_by_doc)  # type: ignore[index]
        items.append(
            (
                '<li class="pdf-toc-category">'
                f'<span class="pdf-toc-category-label">{label}</span>'
                f'<ol class="pdf-toc-children">{child_html}</ol>'
                "</li>"
            )
        )
    return "\n".join(items)


def build_pdf_html(
    tree: list[SidebarNode],
    doc_ids: list[str],
    title_by_doc: dict[str, str],
    fragment_by_doc: dict[str, str],
    stylesheet_urls: list[str],
    site_url: str,
) -> str:
    stylesheet_tags = "\n".join(
        f'<link rel="stylesheet" href="{html.escape(url)}">' for url in stylesheet_urls
    )
    toc_html = build_toc(tree, title_by_doc)
    sections = []
    for doc_id in doc_ids:
        sections.append(
            (
                f'<section class="pdf-doc-page" id="{page_anchor(doc_id)}">'
                f'{fragment_by_doc[doc_id]}'
                "</section>"
            )
        )

    return f"""<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <title>Hermes Agent 中文文档 PDF</title>
  {stylesheet_tags}
  <style>
    @page {{
      size: A4;
      margin: 16mm 12mm 18mm;
    }}

    html {{
      scroll-behavior: auto;
    }}

    body {{
      background: #ffffff !important;
      color: #111111 !important;
    }}

    .pdf-cover,
    .pdf-toc {{
      page-break-after: always;
    }}

    .pdf-cover {{
      display: flex;
      min-height: calc(297mm - 34mm);
      flex-direction: column;
      justify-content: center;
      gap: 1.2rem;
    }}

    .pdf-cover h1 {{
      margin: 0;
      font-size: 2.4rem;
    }}

    .pdf-cover p {{
      margin: 0;
      max-width: 42rem;
      line-height: 1.7;
    }}

    .pdf-meta {{
      color: #555;
      font-size: 0.95rem;
    }}

    .pdf-toc h2 {{
      margin-bottom: 1rem;
    }}

    .pdf-toc-root,
    .pdf-toc-children {{
      margin: 0;
      padding-left: 1.25rem;
    }}

    .pdf-toc-root {{
      padding-left: 1.4rem;
    }}

    .pdf-toc-root > li,
    .pdf-toc-children > li {{
      margin: 0 0 0.6rem 0;
      break-inside: avoid;
    }}

    .pdf-toc-category {{
      margin-top: 0.4rem;
    }}

    .pdf-toc-category-label {{
      display: inline-block;
      font-weight: 700;
      margin-bottom: 0.3rem;
    }}

    .pdf-toc-children {{
      margin-top: 0.2rem;
    }}

    .pdf-doc-page {{
      page-break-before: always;
    }}

    .pdf-doc-page:first-of-type {{
      page-break-before: auto;
    }}

    .hash-link,
    .theme-edit-this-page,
    .pagination-nav,
    .theme-back-to-top-button,
    .theme-doc-footer,
    .tabs,
    button {{
      display: none !important;
    }}

    a {{
      color: #0b57d0 !important;
      text-decoration: none;
    }}

    pre,
    blockquote,
    table,
    img,
    svg,
    figure,
    .theme-admonition {{
      break-inside: avoid;
    }}

    img,
    svg {{
      max-width: 100%;
      height: auto;
    }}

    .theme-doc-markdown {{
      max-width: none !important;
    }}
  </style>
</head>
<body>
  <section class="pdf-cover">
    <div class="pdf-meta">Hermes Agent 中文文档 · 单文件 PDF 导出</div>
    <h1>Hermes Agent 中文文档</h1>
    <p>本 PDF 基于当前中文文档站生成，包含整站正文内容，并保留目录跳转、页内锚点和外部链接。</p>
    <div class="pdf-meta">站点地址：{html.escape(DEFAULT_SITE_URL)}</div>
  </section>
  <section class="pdf-toc">
    <h2>目录</h2>
    <ol class="pdf-toc-root">
      {toc_html}
    </ol>
  </section>
  {''.join(sections)}
</body>
</html>
"""


def export_pdf(
    build_root: Path,
    tree: list[SidebarNode],
    doc_ids: list[str],
    output_path: Path,
    site_url: str,
) -> None:
    temp_dir = build_root / "__pdf__"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_html = temp_dir / "combined.html"

    with serve_directory(build_root) as base_url:
        html_by_doc, title_by_doc, stylesheet_urls = collect_rendered_pages(doc_ids, base_url)
        rewritten = {
            doc_id: rewrite_fragment(
                html_by_doc[doc_id],
                doc_id,
                set(doc_ids),
                base_url,
                site_url,
            )
            for doc_id in doc_ids
        }
        pdf_html = build_pdf_html(tree, doc_ids, title_by_doc, rewritten, stylesheet_urls, site_url)
        temp_html.write_text(pdf_html, encoding="utf-8")

        with sync_playwright() as playwright:
            chromium_executable = resolve_browser_executable(playwright)
            browser = playwright.chromium.launch(executable_path=chromium_executable)
            page = browser.new_page()
            page.goto(f"{base_url}/__pdf__/combined.html", wait_until="networkidle")
            page.wait_for_timeout(500)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "16mm",
                    "right": "12mm",
                    "bottom": "18mm",
                    "left": "12mm",
                },
                prefer_css_page_size=True,
            )
            browser.close()

    with contextlib.suppress(FileNotFoundError):
        temp_html.unlink()
    with contextlib.suppress(OSError):
        temp_dir.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a single PDF for the localized Hermes docs site."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output PDF path. Defaults to site/static/downloads/hermes-agent-zh-docs.pdf",
    )
    parser.add_argument(
        "--site-url",
        default=DEFAULT_SITE_URL,
        help="Public site URL used for non-doc absolute links.",
    )
    args = parser.parse_args()

    if not BUILD_ROOT.exists():
        raise SystemExit(
            f'Build output not found at "{BUILD_ROOT}". Run `npm run build` in site/ first.'
        )

    tree = load_sidebar_tree(SITE_ROOT / "sidebars.ts", list_doc_ids(DOCS_ROOT))
    doc_ids = flatten_sidebar_tree(tree)
    export_pdf(BUILD_ROOT, tree, doc_ids, Path(args.output).resolve(), args.site_url)
    print(Path(args.output).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
