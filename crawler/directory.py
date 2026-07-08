from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "data" / "catalog"
LEGACY_FILES = [
    ROOT / "data" / "beijing_soe_directory.yaml",
    ROOT / "data" / "institutions_extra.yaml",
]


def load_soe_directory(path: Path | None = None) -> list[dict[str, Any]]:
    """加载全部招聘单位名录（catalog + 旧版 yaml）。"""
    if path is not None:
        return _load_file(path)

    entries: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for fp in sorted(CATALOG_DIR.glob("*.yaml")):
        entries.extend(_dedupe_by_name(_load_file(fp), seen_names))

    for fp in LEGACY_FILES:
        if fp.exists():
            entries.extend(_dedupe_by_name(_load_file(fp), seen_names))

    return entries


def _load_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("enterprises", [])


def _dedupe_by_name(
    items: list[dict[str, Any]], seen: set[str]
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ent in items:
        name = ent.get("name", "")
        if not name or name in seen:
            continue
        seen.add(name)
        out.append(ent)
    return out


def directory_whitelist(directory: list[dict[str, Any]] | None = None) -> list[str]:
    entries = directory if directory is not None else load_soe_directory()
    names: list[str] = []
    for ent in entries:
        names.append(ent.get("name", ""))
        names.extend(ent.get("search_keywords", []))
    return [n for n in names if n]
