"""Seed Garden daily artifact generator."""

from __future__ import annotations

import hashlib
import json
import secrets
import argparse
from datetime import date
from pathlib import Path
from typing import Any

from garden.natural import get_natural_signal
from garden.fonts.picker import select_font
from garden.iching import generate_iching
from garden.palettes.picker import select_palette
from garden.seed import generate_daily_seed, generate_random_seed
from garden.worldroot.chronicle import default_chronicle, update_chronicle
from garden.worldroot.rules import evolve_worldroot
from garden.worldroot.state import default_state


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "garden.json"
WORLDROOT_STATE_PATH = ROOT / "state" / "worldroot.json"
CHRONICLE_STATE_PATH = ROOT / "state" / "chronicle.json"

DEFAULT_WORLDROOT = default_state()
DEFAULT_CHRONICLE = default_chronicle()


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(path, default)
        return dict(default)

    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except json.JSONDecodeError:
        return dict(default)

    return data if isinstance(data, dict) else dict(default)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _state_checksum(state: dict[str, Any]) -> str:
    payload = json.dumps(state, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]


def _empty_random_signal() -> dict:
    return {
        "date": None,
        "moon_phase": None,
        "moon_age_fraction": None,
        "sacred_site": None,
        "site": None,
        "site_pressure": None,
        "weather_status": "not_used",
        "weather": {
            "weather_status": "not_used",
            "temperature_2m": None,
            "relative_humidity_2m": None,
            "surface_pressure": None,
            "wind_speed_10m": None,
            "weather_code": None,
        },
        "explanation": "Random preview builds do not use date, moon phase, sacred site, or weather inputs.",
    }


def generate(target_date: str | None = None, random_seed: str | None = None) -> dict:
    is_random = random_seed is not None
    target_date = target_date or date.today().isoformat()
    worldroot_state = _read_json(WORLDROOT_STATE_PATH, DEFAULT_WORLDROOT)
    chronicle_state = _read_json(CHRONICLE_STATE_PATH, DEFAULT_CHRONICLE)

    if is_random:
        artifact_date = "random"
        natural_signal = _empty_random_signal()
        seed = generate_random_seed(random_seed, previous_checksum=_state_checksum(worldroot_state))
    else:
        artifact_date = target_date
        natural_signal = get_natural_signal(target_date)
        seed = generate_daily_seed(
            target_date,
            previous_checksum=_state_checksum(worldroot_state),
            natural_signal=natural_signal,
        )

    palette = select_palette(seed["seed_hash"])
    palette["explanation"] = "Palette is selected deterministically from today's seed hash."
    font = select_font(seed["seed_hash"])
    iching = generate_iching(seed["seed_hash"])
    worldroot = evolve_worldroot(worldroot_state, seed["seed_hash"], iching)
    chronicle = update_chronicle(chronicle_state, worldroot)

    if not is_random:
        _write_json(
            WORLDROOT_STATE_PATH,
            {
                "cycle": worldroot["cycle"],
                "width": worldroot["width"],
                "height": worldroot["height"],
                "grid": worldroot["grid"],
                "named_entities": worldroot["named_entities"],
                "records": worldroot["records"],
            },
        )
        _write_json(CHRONICLE_STATE_PATH, chronicle)

    artifact = {
        "date": artifact_date,
        "mode": "random" if is_random else "daily",
        "seed": seed,
        "natural_signal": natural_signal,
        "palette": palette,
        "font": font,
        "sections": [
            {
                "id": "iching",
                "title": "I Ching",
                "status": "active",
                "data": iching,
            },
            {
                "id": "worldroot",
                "title": "Worldroot",
                "status": "active",
                "data": {
                    **worldroot,
                    "chronicle": chronicle,
                    "explanation": (
                        "Worldroot advances one deterministic cycle from the previous "
                        "state using today's seed and I Ching modifiers."
                    ),
                },
            },
        ],
    }
    _write_json(DATA_PATH, artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Seed Garden JSON artifact.")
    parser.add_argument("--date", help="Generate the daily artifact for an ISO date.")
    parser.add_argument(
        "--random",
        action="store_true",
        help="Generate a random preview artifact without advancing persistent state.",
    )
    parser.add_argument(
        "--random-seed",
        help="Use a specific seed string for a repeatable random preview artifact.",
    )
    args = parser.parse_args()

    random_seed = args.random_seed
    if args.random and random_seed is None:
        random_seed = secrets.token_hex(16)

    generate(target_date=args.date, random_seed=random_seed)


if __name__ == "__main__":
    main()
