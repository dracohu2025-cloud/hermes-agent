from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_ROOT = REPO_ROOT / "website"
DEFAULT_TARGET_ROOT = REPO_ROOT / "site"


SIDEBAR_REPLACEMENTS = (
    ("label: 'Getting Started'", "label: '开始使用'"),
    ("label: 'Using Hermes'", "label: '使用 Hermes'"),
    ("label: 'Features'", "label: '功能特性'"),
    ("label: 'Core'", "label: '核心能力'"),
    ("label: 'Automation'", "label: '自动化'"),
    ("label: 'Media & Web'", "label: '媒体与 Web'"),
    ("label: 'Advanced'", "label: '高级能力'"),
    ("label: 'Messaging Platforms'", "label: '消息平台'"),
    ("label: 'Integrations'", "label: '集成'"),
    ("label: 'Guides & Tutorials'", "label: '指南与教程'"),
    ("label: 'Developer Guide'", "label: '开发者指南'"),
    ("label: 'Architecture'", "label: '架构'"),
    ("label: 'Extending'", "label: '扩展'"),
    ("label: 'Internals'", "label: '内部机制'"),
    ("label: 'Reference'", "label: '参考资料'"),
)


CONFIG_REPLACEMENTS = (
    (
        "  title: 'Hermes Agent',\n  tagline: 'The self-improving AI agent',",
        "  title: 'Hermes Agent 中文文档',\n  tagline: '会在使用中持续成长的 AI Agent',",
    ),
    ("  url: 'https://hermes-agent.nousresearch.com',", "  url: deploymentUrl,"),
    ("  baseUrl: '/docs/',", "  baseUrl: '/',"),
    ("    defaultLocale: 'en',", "    defaultLocale: 'zh-Hans',"),
    ("    locales: ['en'],", "    locales: ['zh-Hans'],"),
    ("        language: ['en'],", "        language: ['zh'],"),
    (
        "          editUrl: 'https://github.com/NousResearch/hermes-agent/edit/main/website/',",
        "          editUrl: 'https://github.com/dracohu2025-cloud/hermes-agent/edit/main/site/',",
    ),
    ("          label: 'Docs',", "          label: '文档',"),
    ("          label: 'Home',", "          label: '官网',"),
    ("          title: 'Docs',", "          title: '文档',"),
    ("            { label: 'Getting Started', to: '/getting-started/quickstart' },", "            { label: '快速开始', to: '/getting-started/quickstart' },"),
    ("            { label: 'User Guide', to: '/user-guide/cli' },", "            { label: '使用指南', to: '/user-guide/cli' },"),
    ("            { label: 'Developer Guide', to: '/developer-guide/architecture' },", "            { label: '开发者指南', to: '/developer-guide/architecture' },"),
    ("            { label: 'Reference', to: '/reference/cli-commands' },", "            { label: '参考资料', to: '/reference/cli-commands' },"),
    ("          title: 'Community',", "          title: '社区',"),
    ("            { label: 'GitHub Discussions', href: 'https://github.com/NousResearch/hermes-agent/discussions' },", "            { label: 'GitHub 讨论区', href: 'https://github.com/NousResearch/hermes-agent/discussions' },"),
    ("          title: 'More',", "          title: '更多',"),
    (
        "      copyright: `Built by <a href=\"https://nousresearch.com\">Nous Research</a> · MIT License · ${new Date().getFullYear()}`,",
        "      copyright: `由 <a href=\"https://nousresearch.com\">Nous Research</a> 打造 · MIT 许可 · ${new Date().getFullYear()}`,",
    ),
)


DEPLOYMENT_BLOCK = """const deploymentUrl =
  process.env.DOCS_SITE_URL
  ?? (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : undefined)
  ?? (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : undefined)
  ?? 'https://hermes-doc.aigc.green';

const pdfDownloadUrl = `${deploymentUrl}/downloads/hermes-agent-zh-docs.pdf`;

"""

CUSTOM_CSS_IMPORT_TARGET = (
    "@import url('https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@latest/style.css');"
)
CUSTOM_CSS_OVERRIDE_BLOCK = """

/* Chinese site font override: use LXGW WenKai everywhere */
:root {
  --ifm-font-family-base: 'LXGW WenKai', 'STKaiti', 'KaiTi', serif;
  --ifm-font-family-monospace: 'LXGW WenKai Mono', 'LXGW WenKai', 'SFMono-Regular', monospace;
}

body,
.navbar,
.footer,
.menu,
.table-of-contents,
.pagination-nav,
.theme-doc-markdown {
  font-family: var(--ifm-font-family-base);
}

code,
kbd,
samp,
pre,
pre.prism-code,
pre.prism-code.language-text,
pre.prism-code.language-plaintext,
pre.prism-code.language-txt,
pre.prism-code.language-ascii,
pre.prism-code code {
  font-family: var(--ifm-font-family-monospace);
}
"""


def replace_all(text: str, replacements: tuple[tuple[str, str], ...]) -> str:
    for source, target in replacements:
        text = text.replace(source, target)
    return text


def sync_sidebars(source_root: Path, target_root: Path) -> Path:
    source_path = source_root / "sidebars.ts"
    target_path = target_root / "sidebars.ts"
    text = source_path.read_text(encoding="utf-8")
    text = replace_all(text, SIDEBAR_REPLACEMENTS)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(text, encoding="utf-8")
    return target_path


def sync_docusaurus_config(source_root: Path, target_root: Path) -> Path:
    source_path = source_root / "docusaurus.config.ts"
    target_path = target_root / "docusaurus.config.ts"
    text = source_path.read_text(encoding="utf-8")

    text = re.sub(
        r"const config: Config = \{",
        DEPLOYMENT_BLOCK + "const config: Config = {",
        text,
        count=1,
    )
    text = replace_all(text, CONFIG_REPLACEMENTS)
    text = re.sub(
        r"\{\s*to:\s*'/skills',\s*label:\s*'Skills',\s*position:\s*'left',\s*\},\s*",
        "",
        text,
        count=1,
        flags=re.S,
    )
    if "href: pdfDownloadUrl" not in text:
        text = text.replace(
            "        {\n          type: 'docSidebar',\n          sidebarId: 'docs',\n          position: 'left',\n          label: '文档',\n        },",
            "        {\n          type: 'docSidebar',\n          sidebarId: 'docs',\n          position: 'left',\n          label: '文档',\n        },\n        {\n          href: pdfDownloadUrl,\n          label: 'PDF',\n          position: 'left',\n        },",
            1,
        )
        text = text.replace(
            "            { label: '参考资料', to: '/reference/cli-commands' },",
            "            { label: '参考资料', to: '/reference/cli-commands' },\n            { label: 'PDF 下载', href: pdfDownloadUrl },",
            1,
        )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(text, encoding="utf-8")
    return target_path


def sync_custom_css(source_root: Path, target_root: Path) -> Path:
    source_path = source_root / "src" / "css" / "custom.css"
    target_path = target_root / "src" / "css" / "custom.css"
    text = source_path.read_text(encoding="utf-8")

    text, replaced = re.subn(
        r"@import url\('https://fonts\.googleapis\.com/css2\?[^']+'\);",
        CUSTOM_CSS_IMPORT_TARGET,
        text,
        count=1,
    )
    if not replaced and CUSTOM_CSS_IMPORT_TARGET not in text:
        text = CUSTOM_CSS_IMPORT_TARGET + "\n\n" + text

    if CUSTOM_CSS_OVERRIDE_BLOCK.strip() not in text:
        text = text.rstrip() + CUSTOM_CSS_OVERRIDE_BLOCK + "\n"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(text, encoding="utf-8")
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync localized Docusaurus config files from website/ into site/."
    )
    parser.add_argument(
        "--source-root",
        default=str(DEFAULT_SOURCE_ROOT),
        help="Source website root. Defaults to repo_root/website.",
    )
    parser.add_argument(
        "--target-root",
        default=str(DEFAULT_TARGET_ROOT),
        help="Target localized site root. Defaults to repo_root/site.",
    )
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    target_root = Path(args.target_root).resolve()

    updated = [
        sync_sidebars(source_root, target_root),
        sync_docusaurus_config(source_root, target_root),
        sync_custom_css(source_root, target_root),
    ]

    for path in updated:
        try:
            print(path.relative_to(REPO_ROOT))
        except ValueError:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
