from garden.seed import generate_daily_seed, generate_random_seed


def test_seed_is_stable_for_same_input():
    signal = {
        "moon_phase": "waxing_gibbous",
        "sacred_site": "Stonehenge",
        "site_pressure": 1018.6,
    }

    first = generate_daily_seed("2026-06-13", "c8f07d11", signal)
    second = generate_daily_seed("2026-06-13", "c8f07d11", dict(reversed(signal.items())))

    assert first["seed_hash"] == second["seed_hash"]
    assert first["seed_material"] == second["seed_material"]


def test_seed_handles_missing_natural_signal():
    seed = generate_daily_seed("2026-06-13", None, {})

    assert "worldroot_checksum=null" in seed["seed_material"]
    assert "site_pressure=null" in seed["seed_material"]
    assert len(seed["seed_hash"]) == 64


def test_random_seed_uses_manual_seed_text_instead_of_date():
    seed = generate_random_seed("manual-preview", "abc123")

    assert "random_seed=manual-preview" in seed["seed_material"]
    assert "date=" not in seed["seed_material"]
    assert len(seed["seed_hash"]) == 64
