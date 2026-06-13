"""Daily seed generation."""

from __future__ import annotations

import hashlib
from typing import Any


SEED_EXPLANATION = (
    "Generated from the date, previous Worldroot checksum, moon phase, "
    "sacred site, and site pressure."
)
RANDOM_SEED_EXPLANATION = (
    "Generated from a manual random seed and the previous Worldroot checksum. "
    "Random preview builds do not use date, moon, sacred site, or weather inputs."
)


def _normalize_seed_value(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)


def generate_daily_seed(
    date: str, previous_checksum: str | None, natural_signal: dict | None
) -> dict:
    """Generate the deterministic daily seed artifact."""

    natural_signal = natural_signal or {}
    inputs = {
        "date": date,
        "worldroot_checksum": previous_checksum,
        "moon_phase": natural_signal.get("moon_phase"),
        "sacred_site": natural_signal.get("sacred_site"),
        "site_pressure": natural_signal.get("site_pressure"),
    }

    seed_material = "|".join(
        f"{key}={_normalize_seed_value(inputs[key])}" for key in sorted(inputs)
    )
    seed_hash = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()

    return {
        "seed_material": seed_material,
        "seed_hash": seed_hash,
        "short_seed": seed_hash[:12],
        "inputs": inputs,
        "explanation": SEED_EXPLANATION,
    }


def generate_random_seed(random_seed: str, previous_checksum: str | None) -> dict:
    """Generate a manual preview seed from arbitrary seed text."""

    inputs = {
        "random_seed": random_seed,
        "worldroot_checksum": previous_checksum,
    }
    seed_material = "|".join(
        f"{key}={_normalize_seed_value(inputs[key])}" for key in sorted(inputs)
    )
    seed_hash = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()

    return {
        "seed_material": seed_material,
        "seed_hash": seed_hash,
        "short_seed": seed_hash[:12],
        "inputs": inputs,
        "explanation": RANDOM_SEED_EXPLANATION,
    }
