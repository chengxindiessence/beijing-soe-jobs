from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIRECTORY = ROOT / "data" / "beijing_soe_directory.yaml"
EXTRA_DIRECTORY = ROOT / "data" / "institutions_extra.yaml"


def load_soe_directory(path: Path | None = None) -> list[dict[str, Any]]:
    file_path = path or DEFAULT_DIRECTORY
    entries: list[dict[str, Any]] = []
    for fp in (file_path, EXTRA_DIRECTORY):
        if not fp.exists():
            continue
        with fp.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        entries.extend(data.get("enterprises", []))
    return entries


def directory_whitelist(directory: list[dict[str, Any]] | None = None) -> list[str]:
    entries = directory if directory is not None else load_soe_directory()
    names: list[str] = []
    for ent in entries:
        names.append(ent.get("name", ""))
        names.extend(ent.get("search_keywords", []))
    return [n for n in names if n]
