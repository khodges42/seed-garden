"""Deterministic I Ching generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HEXAGRAMS_PATH = Path(__file__).with_name("iching") / "hexagrams.json"


def _load_hexagrams(path: Path = HEXAGRAMS_PATH) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            hexagrams = json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"I Ching hexagram file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"I Ching hexagram file is not valid JSON: {path}") from exc

    if not isinstance(hexagrams, list) or len(hexagrams) != 64:
        raise RuntimeError("I Ching hexagram file must contain exactly 64 entries.")

    return hexagrams


def _slice_int(seed_hash: str, label: str) -> int:
    material = f"{seed_hash}:{label}".encode("utf-8")
    return int(hashlib.sha256(material).hexdigest(), 16)


def _changing_lines(seed_hash: str) -> list[int]:
    lines = []
    value = _slice_int(seed_hash, "changing-lines")
    for line in range(1, 7):
        if ((value >> (line - 1)) & 0b11) == 0:
            lines.append(line)
    return lines


def _modifiers(binary: str, changing_lines: list[int]) -> dict[str, float]:
    solid_lines = binary.count("1")
    broken_lines = 6 - solid_lines
    changing_weight = len(changing_lines) * 0.03

    growth = (solid_lines - 3) * 0.04 + changing_weight
    rot = (broken_lines - 3) * 0.04 - (changing_weight / 2)
    movement = (len(changing_lines) - 2) * 0.04

    return {
        "growth": round(max(-0.2, min(0.2, growth)), 3),
        "rot": round(max(-0.2, min(0.2, rot)), 3),
        "movement": round(max(-0.2, min(0.2, movement)), 3),
    }


def generate_iching(seed_hash: str) -> dict:
    """Generate today's I Ching result from the seed hash."""

    try:
        seed_value = int(seed_hash, 16)
    except ValueError as exc:
        raise ValueError("seed_hash must be a hexadecimal string") from exc

    hexagram = _load_hexagrams()[seed_value % 64]
    changing_lines = _changing_lines(seed_hash)
    binary = hexagram["binary"]
    hexagram_number = int(hexagram["number"])

    return {
        "hexagram": hexagram_number,
        "name": hexagram["name"],
        "unicode": chr(0x4DC0 + hexagram_number - 1),
        "changing_lines": changing_lines,
        "binary": binary,
        "upper_trigram": hexagram.get("upper_trigram", {}),
        "lower_trigram": hexagram.get("lower_trigram", {}),
        "modifiers": _modifiers(binary, changing_lines),
        "keywords": hexagram.get("keywords", []),
        "explanation": (
            "The hexagram is generated from today's seed and influences "
            "Worldroot's growth, decay, and movement."
        ),
    }
