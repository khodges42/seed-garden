"""Deterministic palette picker."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PALETTES_PATH = Path(__file__).with_name("palettes.json")
REQUIRED_FIELDS = {"id", "name", "background", "text", "accent", "muted", "description"}


def _load_palettes(path: Path = PALETTES_PATH) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            palettes = json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Palette file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Palette file is not valid JSON: {path}") from exc

    if not isinstance(palettes, list) or not palettes:
        raise RuntimeError(f"Palette file must contain a non-empty list: {path}")

    for index, palette in enumerate(palettes):
        if not isinstance(palette, dict):
            raise RuntimeError(f"Palette at index {index} must be an object.")
        missing = REQUIRED_FIELDS - set(palette)
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise RuntimeError(f"Palette {index} is missing required fields: {missing_fields}")

    return palettes


def select_palette(seed_hash: str) -> dict:
    """Select a full palette object deterministically from a seed hash."""

    palettes = _load_palettes()
    try:
        seed_value = int(seed_hash, 16)
    except ValueError as exc:
        raise ValueError("seed_hash must be a hexadecimal string") from exc

    return dict(palettes[seed_value % len(palettes)])
