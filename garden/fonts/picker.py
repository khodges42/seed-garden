"""Deterministic font picker."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FONTS_PATH = Path(__file__).with_name("fonts.json")
DEFAULT_FONT = {
    "id": "cormorant-garamond",
    "name": "Cormorant Garamond",
    "category": "serif",
    "mood": ["scholarly", "occult", "editorial"],
}
REQUIRED_FIELDS = {"id", "name", "category", "mood"}


def _load_fonts(path: Path = FONTS_PATH) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            fonts = json.load(handle)
    except FileNotFoundError:
        return [dict(DEFAULT_FONT)]
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Font file is not valid JSON: {path}") from exc

    if not isinstance(fonts, list) or not fonts:
        return [dict(DEFAULT_FONT)]

    for index, font in enumerate(fonts):
        if not isinstance(font, dict):
            raise RuntimeError(f"Font at index {index} must be an object.")
        missing = REQUIRED_FIELDS - set(font)
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise RuntimeError(f"Font {index} is missing required fields: {missing_fields}")

    return fonts


def _font_stack(font: dict[str, Any]) -> str:
    name = font["name"]
    category = font.get("category")
    if category == "mono":
        fallback = '"Courier New", monospace'
    elif category == "sans":
        fallback = 'Arial, sans-serif'
    else:
        fallback = 'Georgia, "Times New Roman", serif'
    return f'"{name}", {fallback}'


def select_font(seed_hash: str) -> dict:
    """Select a full font object deterministically from a seed hash."""

    try:
        seed_value = int(seed_hash, 16)
    except ValueError as exc:
        raise ValueError("seed_hash must be a hexadecimal string") from exc

    fonts = _load_fonts()
    font = dict(fonts[seed_value % len(fonts)])
    font["stack"] = _font_stack(font)
    font["explanation"] = "Font is selected deterministically from today's seed hash."
    return font
