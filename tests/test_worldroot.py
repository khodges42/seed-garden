from garden.worldroot.chronicle import update_chronicle
from garden.worldroot.rules import _events_from_stats, evolve_worldroot
from garden.worldroot.state import default_state


ICHING = {"modifiers": {"growth": 0.05, "rot": -0.02, "movement": 0.01}}


def test_worldroot_same_input_produces_same_next_state():
    state = default_state()
    seed_hash = "d" * 64

    first = evolve_worldroot(state, seed_hash, ICHING)
    second = evolve_worldroot(state, seed_hash, ICHING)

    assert first == second


def test_worldroot_missing_previous_state_creates_valid_ascii():
    result = evolve_worldroot(None, "e" * 64, ICHING)
    lines = result["ascii"].splitlines()

    assert result["cycle"] == 1
    assert len(lines) == 20
    assert all(len(line) == 20 for line in lines)


def test_chronicle_does_not_store_grid_snapshots():
    worldroot = evolve_worldroot(None, "f" * 64, ICHING)
    chronicle = update_chronicle(None, worldroot)

    assert "grid" not in chronicle
    assert len(chronicle["eras"]) <= 12
    assert len(chronicle["notable_events"]) <= 25


def test_heavy_bloom_event_uses_plain_language():
    events = _events_from_stats({"bloom": 90, "sprout": 0, "tree": 0, "rot": 0}, 400)

    assert events == ["The garden is in heavy bloom."]
