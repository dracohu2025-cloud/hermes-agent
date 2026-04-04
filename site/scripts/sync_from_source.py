from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DOCS_ROOT = REPO_ROOT / "website" / "docs"
TARGET_DOCS_ROOT = REPO_ROOT / "site" / "docs"
SOURCE_STATIC_ROOT = REPO_ROOT / "website" / "static"
TARGET_STATIC_ROOT = REPO_ROOT / "site" / "static"
STATE_FILE = REPO_ROOT / "site" / ".source-sync-state.json"
DOC_SUFFIXES = {".md", ".json"}
WATCHED_SOURCE_FILES = {
    "website/sidebars.ts": REPO_ROOT / "website" / "sidebars.ts",
    "website/docusaurus.config.ts": REPO_ROOT / "website" / "docusaurus.config.ts",
}

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from translate_docs import (  # noqa: E402
    build_client,
    find_api_key,
    find_base_url,
    resolve_transport,
    translate_path,
)


def sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_tree(root: Path, suffixes: set[str] | None = None) -> dict[str, str]:
    if not root.exists():
        return {}

    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if suffixes is not None and path.suffix not in suffixes:
            continue
        snapshot[path.relative_to(root).as_posix()] = sha256_for_file(path)
    return snapshot


def snapshot_watched_files() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for name, path in WATCHED_SOURCE_FILES.items():
        if path.exists():
            snapshot[name] = sha256_for_file(path)
    return snapshot


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {
            "version": 1,
            "source_docs": {},
            "source_static": {},
            "watched_files": snapshot_watched_files(),
        }

    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(
    state: dict,
    source_docs: dict[str, str],
    source_static: dict[str, str],
    record_watch_state: bool,
) -> None:
    watched_files = state.get("watched_files", {})
    if not watched_files or record_watch_state:
        watched_files = snapshot_watched_files()

    payload = {
        "version": 1,
        "source_docs": source_docs,
        "source_static": source_static,
        "watched_files": watched_files,
    }
    STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_report(state: dict) -> dict:
    current_docs = snapshot_tree(SOURCE_DOCS_ROOT, DOC_SUFFIXES)
    current_static = snapshot_tree(SOURCE_STATIC_ROOT)
    target_docs = snapshot_tree(TARGET_DOCS_ROOT, DOC_SUFFIXES)
    target_static = snapshot_tree(TARGET_STATIC_ROOT)

    previous_docs = state.get("source_docs", {})
    previous_static = state.get("source_static", {})
    previous_watched = state.get("watched_files", {})
    current_watched = snapshot_watched_files()

    doc_paths = set(current_docs)
    static_paths = set(current_static)

    docs_added = sorted(doc_paths - set(previous_docs))
    docs_removed = sorted(set(previous_docs) - doc_paths)
    docs_changed = sorted(
        path
        for path in doc_paths & set(previous_docs)
        if current_docs[path] != previous_docs[path]
        or not (TARGET_DOCS_ROOT / path).exists()
    )

    static_added = sorted(static_paths - set(previous_static))
    static_removed = sorted(set(previous_static) - static_paths)
    static_changed = sorted(
        path
        for path in static_paths & set(previous_static)
        if current_static[path] != previous_static[path]
        or not (TARGET_STATIC_ROOT / path).exists()
    )

    watched_changed = sorted(
        name for name, digest in current_watched.items() if previous_watched.get(name) != digest
    )

    extra_target_docs = sorted(set(target_docs) - doc_paths)
    extra_target_static = sorted(set(target_static) - static_paths)

    return {
        "current_docs": current_docs,
        "current_static": current_static,
        "docs_added": docs_added,
        "docs_changed": docs_changed,
        "docs_removed": docs_removed,
        "static_added": static_added,
        "static_changed": static_changed,
        "static_removed": static_removed,
        "watched_changed": watched_changed,
        "extra_target_docs": extra_target_docs,
        "extra_target_static": extra_target_static,
    }


def print_section(title: str, items: list[str]) -> None:
    if not items:
        return
    print(f"\n{title} ({len(items)}):")
    for item in items:
        print(f"  - {item}")


def print_report(report: dict) -> None:
    print_section("新增文档", report["docs_added"])
    print_section("变更文档", report["docs_changed"])
    print_section("已从源站移除的文档", report["docs_removed"])
    print_section("新增静态资源", report["static_added"])
    print_section("变更静态资源", report["static_changed"])
    print_section("已从源站移除的静态资源", report["static_removed"])
    print_section("需要人工复核的源站配置文件", report["watched_changed"])
    print_section("中文站里多出来的文档", report["extra_target_docs"])
    print_section("中文站里多出来的静态资源", report["extra_target_static"])

    pending_docs = len(report["docs_added"]) + len(report["docs_changed"])
    pending_static = len(report["static_added"]) + len(report["static_changed"])
    pending_manual = (
        len(report["docs_removed"])
        + len(report["static_removed"])
        + len(report["watched_changed"])
        + len(report["extra_target_docs"])
        + len(report["extra_target_static"])
    )
    print(
        "\n待处理汇总："
        f" 文档翻译 {pending_docs}，静态资源同步 {pending_static}，人工复核 {pending_manual}"
    )


def remove_if_exists(path: Path) -> None:
    if not path.exists():
        return
    if path.is_file():
        path.unlink()

    current = path.parent
    while current != path.anchor and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def sync_static_files(report: dict) -> None:
    for relative_path in report["static_added"] + report["static_changed"]:
        source_path = SOURCE_STATIC_ROOT / relative_path
        target_path = TARGET_STATIC_ROOT / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        print(f"[static] {target_path.relative_to(REPO_ROOT)}")


def prune_removed(report: dict) -> None:
    for relative_path in report["docs_removed"]:
        remove_if_exists(TARGET_DOCS_ROOT / relative_path)
        print(f"[prune-doc] site/docs/{relative_path}")

    for relative_path in report["static_removed"]:
        remove_if_exists(TARGET_STATIC_ROOT / relative_path)
        print(f"[prune-static] site/static/{relative_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync changed source docs from website/ into site/.")
    parser.add_argument("--check", action="store_true", help="Only report pending changes and exit.")
    parser.add_argument("--prune", action="store_true", help="Delete target files removed from the source site.")
    parser.add_argument(
        "--record-watch-state",
        action="store_true",
        help="Record website/sidebars.ts and website/docusaurus.config.ts as already reviewed.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the translation model. Falls back to HERMES_DOCS_TRANSLATION_MODEL or script default.",
    )
    parser.add_argument(
        "--transport",
        choices=["anthropic", "openai"],
        default=None,
        help="Override the transport used by the translation client.",
    )
    parser.add_argument("--chunk-size", type=int, default=8000, help="Maximum characters per markdown chunk.")
    parser.add_argument("--no-validate", action="store_true", help="Skip structural validation while translating.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between translated files in seconds.")
    args = parser.parse_args()

    state = load_state()
    report = build_report(state)
    print_report(report)

    has_pending = any(
        report[key]
        for key in (
            "docs_added",
            "docs_changed",
            "docs_removed",
            "static_added",
            "static_changed",
            "static_removed",
            "watched_changed",
            "extra_target_docs",
            "extra_target_static",
        )
    )

    if args.check:
        if not has_pending:
            print("\n中文站已经跟上当前 source site。")
            return 0
        return 1

    files_to_translate = report["docs_added"] + report["docs_changed"]

    if files_to_translate:
        api_key = find_api_key()
        base_url = find_base_url()
        transport = resolve_transport(
            base_url,
            args.transport or os.getenv("HERMES_DOCS_TRANSLATION_TRANSPORT"),
        )
        model_name = args.model or os.getenv("HERMES_DOCS_TRANSLATION_MODEL", "kimi-k2-turbo-preview")
        client = build_client(transport, api_key, base_url)
        print(f"\n开始翻译 {len(files_to_translate)} 个文档，模型：{model_name}，通道：{transport}")
        for index, relative_path in enumerate(files_to_translate, start=1):
            source_path = SOURCE_DOCS_ROOT / relative_path
            target_path = TARGET_DOCS_ROOT / relative_path
            print(f"[{index}/{len(files_to_translate)}] {relative_path}")
            translate_path(
                client,
                transport=transport,
                model=model_name,
                source_path=source_path,
                target_path=target_path,
                chunk_size=args.chunk_size,
                validate=not args.no_validate,
            )
            if args.sleep:
                time.sleep(args.sleep)

    if report["static_added"] or report["static_changed"]:
        print(f"\n开始同步 {len(report['static_added']) + len(report['static_changed'])} 个静态资源")
        sync_static_files(report)

    if args.prune and (report["docs_removed"] or report["static_removed"]):
        print("\n开始清理已从源站移除的目标文件")
        prune_removed(report)

    save_state(
        state=state,
        source_docs=report["current_docs"],
        source_static=report["current_static"],
        record_watch_state=args.record_watch_state,
    )

    print("\n同步完成。建议下一步运行：")
    print("  npm run check:docs-parity")
    print("  npm run build")

    if report["watched_changed"] and not args.record_watch_state:
        print("\n提醒：source site 的导航或站点配置有变更，还需要人工检查：")
        for name in report["watched_changed"]:
            print(f"  - {name}")
        print("确认中文站已经跟着改好后，再执行一次：")
        print("  npm run sync:docs -- --record-watch-state")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
