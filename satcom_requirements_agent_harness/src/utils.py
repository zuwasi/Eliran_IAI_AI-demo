"""Utility functions."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def read_text_files(directory: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not directory.exists():
        return result

    for path in sorted(directory.glob("*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            result[path.name] = path.read_text(encoding="utf-8")
    return result


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_requirement_blocks(document_name: str, text: str) -> list[dict[str, Any]]:
    """
    Simple deterministic extractor for demo data.

    Looks for lines like A-REQ-001 followed by requirement text.
    This is intentionally simple and should be replaced or extended
    for production Word/PDF parsing.
    """
    pattern = re.compile(r"(?m)^([A-Z]-REQ-\d{3})\s*\n(.+?)(?=\n\n[A-Z]-REQ-\d{3}|\Z)", re.DOTALL)
    results = []

    for match in pattern.finditer(text):
        req_id = match.group(1).strip()
        req_text = " ".join(match.group(2).strip().split())
        results.append({
            "id": req_id,
            "text": req_text,
            "source_document": document_name,
            "keywords": [],
            "domain": "satcom"
        })

    return results
