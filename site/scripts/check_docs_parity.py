from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DOCS = REPO_ROOT / "website" / "docs"
TARGET_DOCS = REPO_ROOT / "site" / "docs"


def list_docs(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json"}
    }


def main() -> int:
    source_docs = list_docs(SOURCE_DOCS)
    target_docs = list_docs(TARGET_DOCS)

    missing = sorted(source_docs - target_docs)
    extra = sorted(target_docs - source_docs)

    print(f"source docs: {len(source_docs)}")
    print(f"target docs: {len(target_docs)}")

    if missing:
        print("\nMissing files:")
        for path in missing:
            print(f"  - {path}")

    if extra:
        print("\nExtra files:")
        for path in extra:
            print(f"  - {path}")

    if missing or extra:
        return 1

    print("\nDocs structure matches source site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
