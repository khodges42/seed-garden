"""Compact Worldroot chronicle retention."""

from __future__ import annotations


MAX_ERAS = 12
MAX_NOTABLE_EVENTS = 25


def default_chronicle() -> dict:
    return {
        "current_era": {
            "name": "The First Bloom",
            "start_cycle": 1,
            "summary": "The garden began to spread from water and stone.",
        },
        "eras": [],
        "notable_events": [],
        "records": {},
    }


def update_chronicle(previous: dict | None, worldroot: dict) -> dict:
    """Update compact chronicle state from the latest Worldroot output."""

    chronicle = previous if isinstance(previous, dict) else default_chronicle()
    current_era = chronicle.get("current_era") or default_chronicle()["current_era"]
    eras = list(chronicle.get("eras", []))
    notable_events = list(chronicle.get("notable_events", []))
    records = dict(chronicle.get("records", {}))

    cycle = int(worldroot.get("cycle") or 0)
    stats = worldroot.get("stats", {})
    era_name, era_summary = _era_for_stats(stats)

    if current_era.get("name") != era_name:
        eras.append(current_era)
        current_era = {"name": era_name, "start_cycle": cycle, "summary": era_summary}
        notable_events.append({"cycle": cycle, "event": f"The era turned toward {era_name}."})

    for event in worldroot.get("events", []):
        notable_events.append({"cycle": cycle, "event": event})

    for key, value in worldroot.get("records", {}).items():
        if isinstance(value, int) and value > int(records.get(key, 0) or 0):
            records[key] = value
            notable_events.append({"cycle": cycle, "event": f"A record was marked: {key} reached {value}."})

    return {
        "current_era": current_era,
        "eras": eras[-MAX_ERAS:],
        "notable_events": notable_events[-MAX_NOTABLE_EVENTS:],
        "records": records,
    }


def _era_for_stats(stats: dict) -> tuple[str, str]:
    total = sum(int(value or 0) for value in stats.values()) or 1
    life = sum(int(stats.get(kind, 0) or 0) for kind in ["sprout", "bloom", "tree"])
    rot = int(stats.get("rot", 0) or 0)

    if life == 0:
        return "The Quiet Root", "Life withdrew and the garden held its breath."
    if rot / total > 0.3:
        return "The Rot Tide", "Decay became the dominant weather of the root."
    if life / total > 0.35:
        return "The Green Surge", "Living matter spread beyond its old bounds."
    return "The First Bloom", "The garden began to spread from water and stone."
