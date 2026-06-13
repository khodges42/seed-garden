"""Worldroot evolution rules."""

from __future__ import annotations

import copy

from garden.worldroot.render import count_kinds, render_ascii
from garden.worldroot.state import hash_choice, hash_float, make_cell, normalize_state


LIFE_KINDS = {"sprout", "bloom", "tree"}
STABLE_KINDS = {"water", "stone"}
NEIGHBORS = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]


def evolve_worldroot(previous_state: dict | None, seed_hash: str, iching: dict) -> dict:
    """Advance Worldroot by exactly one cycle."""

    state = normalize_state(previous_state, seed_hash)
    next_cycle = state["cycle"] + 1
    width = state["width"]
    height = state["height"]
    modifiers = iching.get("modifiers", {}) if isinstance(iching, dict) else {}

    moved_grid = _move_wanderers(state, seed_hash, next_cycle)
    next_grid = copy.deepcopy(moved_grid)
    events = []

    for y in range(height):
        for x in range(width):
            cell = moved_grid[y][x]
            if cell["kind"] == "wanderer":
                next_grid[y][x] = _age(cell)
                _perturb_from_wanderer(next_grid, x, y, seed_hash, next_cycle, modifiers)
            else:
                next_grid[y][x] = _evolve_cell(moved_grid, x, y, seed_hash, next_cycle, modifiers)

    next_state = {
        "cycle": next_cycle,
        "width": width,
        "height": height,
        "grid": next_grid,
        "named_entities": _collect_notables(next_grid, width),
        "records": _update_records(state.get("records", {}), next_grid),
    }
    stats = count_kinds(next_state)
    events.extend(_events_from_stats(stats, width * height))

    return {
        **next_state,
        "ascii": render_ascii(next_state),
        "stats": stats,
        "events": events,
        "caption": _caption(stats),
    }


def _move_wanderers(state: dict, seed_hash: str, cycle: int) -> list[list[dict]]:
    width = state["width"]
    height = state["height"]
    source = state["grid"]
    target = [[make_cell("empty") for _x in range(width)] for _y in range(height)]

    for y in range(height):
        for x in range(width):
            cell = source[y][x]
            if cell["kind"] != "wanderer":
                target[y][x] = copy.deepcopy(cell)

    for y in range(height):
        for x in range(width):
            cell = source[y][x]
            if cell["kind"] != "wanderer":
                continue
            candidates = _neighbors(width, height, x, y) + [(x, y)]
            offset = int(hash_float(seed_hash, cycle, x, y, "wanderer-offset") * len(candidates))
            ordered = candidates[offset:] + candidates[:offset]
            for nx, ny in ordered:
                if target[ny][nx]["kind"] == "empty":
                    target[ny][nx] = copy.deepcopy(cell)
                    break
            else:
                target[y][x] = copy.deepcopy(cell)

    return target


def _evolve_cell(grid: list[list[dict]], x: int, y: int, seed_hash: str, cycle: int, modifiers: dict) -> dict:
    cell = grid[y][x]
    kind = cell["kind"]
    aged = _age(cell)
    growth_mod = float(modifiers.get("growth", 0))
    rot_mod = float(modifiers.get("rot", 0))

    if kind in STABLE_KINDS:
        return aged

    if kind == "empty":
        chance = 0.015 + _nearby_count(grid, x, y, LIFE_KINDS | {"water"}) * 0.025 + growth_mod
        if _roll(seed_hash, cycle, x, y, "empty-sprout", chance):
            return make_cell("sprout")
        return aged

    if kind == "sprout":
        if _roll(seed_hash, cycle, x, y, "sprout-bloom", 0.24 + growth_mod):
            return make_cell("bloom")
        if _roll(seed_hash, cycle, x, y, "sprout-empty", 0.045 + rot_mod):
            return make_cell("empty")
        return aged

    if kind == "bloom":
        crowding = max(0, _nearby_count(grid, x, y, LIFE_KINDS) - 3) * 0.04
        if _roll(seed_hash, cycle, x, y, "bloom-tree", 0.075 + growth_mod / 2):
            return make_cell("tree")
        if _roll(seed_hash, cycle, x, y, "bloom-rot", 0.035 + crowding + rot_mod):
            return make_cell("rot")
        return aged

    if kind == "tree":
        age_pressure = max(0, cell.get("cycles", 0) - 18) * 0.002
        if _roll(seed_hash, cycle, x, y, "tree-rot", 0.018 + age_pressure + rot_mod):
            return make_cell("rot")
        if _roll(seed_hash, cycle, x, y, "tree-spread", 0.025 + growth_mod / 3):
            return aged
        return aged

    if kind == "rot":
        if _roll(seed_hash, cycle, x, y, "rot-empty", 0.2 - rot_mod / 2):
            return make_cell("empty")
        return aged

    return aged


def _perturb_from_wanderer(grid: list[list[dict]], x: int, y: int, seed_hash: str, cycle: int, modifiers: dict) -> None:
    neighbors = _neighbors(len(grid[0]), len(grid), x, y)
    if not neighbors:
        return
    label = "wanderer-target"
    target_key = hash_choice([f"{nx},{ny}" for nx, ny in neighbors], seed_hash, cycle, x, y, label)
    tx, ty = [int(part) for part in target_key.split(",")]
    target = grid[ty][tx]
    movement_mod = float(modifiers.get("movement", 0))
    if target["kind"] == "empty" and _roll(seed_hash, cycle, x, y, "wanderer-sprout", 0.08 + movement_mod):
        grid[ty][tx] = make_cell("sprout")
    elif target["kind"] in LIFE_KINDS and _roll(seed_hash, cycle, x, y, "wanderer-rot", 0.03):
        grid[ty][tx] = make_cell("rot")


def _age(cell: dict) -> dict:
    aged = dict(cell)
    aged["cycles"] = int(aged.get("cycles") or 0) + 1
    aged.setdefault("name", None)
    return aged


def _roll(seed_hash: str, cycle: int, x: int, y: int, label: str, chance: float) -> bool:
    chance = max(0.0, min(0.95, chance))
    return hash_float(seed_hash, cycle, x, y, label) < chance


def _neighbors(width: int, height: int, x: int, y: int) -> list[tuple[int, int]]:
    points = []
    for dx, dy in NEIGHBORS:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < width and 0 <= ny < height:
            points.append((nx, ny))
    return points


def _nearby_count(grid: list[list[dict]], x: int, y: int, kinds: set[str]) -> int:
    return sum(1 for nx, ny in _neighbors(len(grid[0]), len(grid), x, y) if grid[ny][nx]["kind"] in kinds)


def _collect_notables(grid: list[list[dict]], width: int) -> list[dict]:
    candidates = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell["kind"] == "tree" and cell.get("cycles", 0) >= 30:
                candidates.append({"kind": "tree", "cycles": cell["cycles"], "name": f"Tree of {cell['cycles']} Cycles", "x": x, "y": y})
            if cell["kind"] == "wanderer" and cell.get("cycles", 0) >= 12:
                candidates.append({"kind": "wanderer", "cycles": cell["cycles"], "name": "The Oldest Wanderer", "x": x, "y": y})
    cap = max(3, width // 4)
    return sorted(candidates, key=lambda item: (-item["cycles"], item["name"]))[:cap]


def _update_records(records: dict, grid: list[list[dict]]) -> dict:
    updated = dict(records or {})
    stats = {kind: 0 for kind in ["sprout", "bloom", "tree", "wanderer", "rot"]}
    oldest_tree = int(updated.get("oldest_tree_cycles", 0) or 0)
    for row in grid:
        for cell in row:
            kind = cell["kind"]
            if kind in stats:
                stats[kind] += 1
            if kind == "tree":
                oldest_tree = max(oldest_tree, int(cell.get("cycles") or 0))
    for kind, count in stats.items():
        updated[f"max_{kind}"] = max(int(updated.get(f"max_{kind}", 0) or 0), count)
    updated["oldest_tree_cycles"] = oldest_tree
    return updated


def _events_from_stats(stats: dict, total_cells: int) -> list[str]:
    events = []
    life_count = sum(stats.get(kind, 0) for kind in LIFE_KINDS)
    if life_count == 0:
        events.append("No living green thing remains in the root.")
    if stats.get("rot", 0) > total_cells * 0.3:
        events.append("A rot tide moves through the garden.")
    if stats.get("bloom", 0) > total_cells * 0.2:
        events.append("The garden is in heavy bloom.")
    return events


def _caption(stats: dict) -> str:
    if stats.get("rot", 0) > stats.get("bloom", 0) + stats.get("tree", 0):
        return "Rot gathers beneath the visible garden."
    if stats.get("water", 0) >= stats.get("stone", 0):
        return "Water holds the pattern open."
    if stats.get("tree", 0):
        return "Trees keep their small account of time."
    return "The root waits under a quiet surface."
