"""Worldroot ASCII rendering."""

from __future__ import annotations


SYMBOLS = {
    "empty": ".",
    "sprout": ",",
    "bloom": "*",
    "tree": "T",
    "wanderer": "o",
    "rot": "x",
    "water": "~",
    "stone": "#",
}


def render_ascii(state: dict) -> str:
    """Render a Worldroot state as fixed-width ASCII."""

    lines = []
    for row in state["grid"]:
        lines.append("".join(SYMBOLS.get(cell.get("kind"), "?") for cell in row))
    return "\n".join(lines)


def count_kinds(state: dict) -> dict[str, int]:
    """Count all known entity kinds in the grid."""

    stats = {kind: 0 for kind in SYMBOLS}
    for row in state["grid"]:
        for cell in row:
            kind = cell.get("kind", "empty")
            stats[kind] = stats.get(kind, 0) + 1
    return stats
