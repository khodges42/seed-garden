from garden.iching import generate_iching


def test_iching_is_deterministic():
    seed_hash = "b" * 64

    assert generate_iching(seed_hash) == generate_iching(seed_hash)


def test_iching_output_includes_worldroot_modifiers():
    result = generate_iching("c" * 64)

    assert 1 <= result["hexagram"] <= 64
    assert set(result["modifiers"]) == {"growth", "rot", "movement"}
    assert isinstance(result["changing_lines"], list)


def test_iching_output_includes_artifact_rendering_fields():
    result = generate_iching("d" * 64)

    assert result["unicode"]
    assert result["upper_trigram"]["name"]
    assert result["lower_trigram"]["name"]
