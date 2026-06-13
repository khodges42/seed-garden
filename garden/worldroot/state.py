"""Worldroot state helpers."""

from __future__ import annotations

import copy
import hashlib


DEFAULT_WIDTH = 20
DEFAULT_HEIGHT = 20


def make_cell(kind: str = "empty", cycles: int = 0, name: str | None = None) -> dict:
    return {"kind": kind, "cycles": cycles, "name": name}


def default_state() -> dict:
    return {
        "cycle": 0,
        "width": DEFAULT_WIDTH,
        "height": DEFAULT_HEIGHT,
        "grid": [],
        "named_entities": [],
        "records": {},
    }


def hash_float(seed_hash: str, cycle: int, x: int, y: int, label: str) -> float:
    material = f"{seed_hash}:{cycle}:{x}:{y}:{label}".encode("utf-8")
    value = int(hashlib.sha256(material).hexdigest()[:12], 16)
    return value / float(0xFFFFFFFFFFFF)


def hash_choice(items: list[str], seed_hash: str, cycle: int, x: int, y: int, label: str) -> str:
    value = hash_float(seed_hash, cycle, x, y, label)
    index = min(len(items) - 1, int(value * len(items)))
    return items[index]


def normalize_state(previous_state: dict | None, seed_hash: str) -> dict:
    """Return a complete Worldroot state, creating the first grid if needed."""

    state = copy.deepcopy(previous_state) if isinstance(previous_state, dict) else default_state()
    width = int(state.get("width") or DEFAULT_WIDTH)
    height = int(state.get("height") or DEFAULT_HEIGHT)
    grid = state.get("grid")

    if not _valid_grid(grid, width, height):
        grid = _initial_grid(width, height, seed_hash)

    return {
        "cycle": int(state.get("cycle") or 0),
        "width": width,
        "height": height,
        "grid": grid,
        "named_entities": state.get("named_entities", []),
        "records": state.get("records", {}),
    }


def _valid_grid(grid: object, width: int, height: int) -> bool:
    if not isinstance(grid, list) or len(grid) != height:
        return False
    for row in grid:
        if not isinstance(row, list) or len(row) != width:
            return False
        if not all(isinstance(cell, dict) and "kind" in cell for cell in row):
            return False
    return True


def _initial_grid(width: int, height: int, seed_hash: str) -> list[list[dict]]:
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            roll = hash_float(seed_hash, 0, x, y, "initial-kind")
            if roll < 0.055:
                kind = "water"
            elif roll < 0.105:
                kind = "stone"
            elif roll < 0.225:
                kind = "sprout"
            elif roll < 0.29:
                kind = "bloom"
            elif roll < 0.315:
                kind = "rot"
            elif roll < 0.327:
                kind = "wanderer"
            else:
                kind = "empty"
            row.append(make_cell(kind))
        grid.append(row)
    return grid
