import json

from garden import generate as generator
from garden.worldroot.state import default_state


def test_random_generation_does_not_advance_persistent_state(tmp_path, monkeypatch):
    data_path = tmp_path / "data" / "garden.json"
    worldroot_path = tmp_path / "state" / "worldroot.json"
    chronicle_path = tmp_path / "state" / "chronicle.json"
    worldroot_path.parent.mkdir(parents=True)

    starting_state = default_state()
    starting_state["cycle"] = 7
    worldroot_path.write_text(json.dumps(starting_state), encoding="utf-8")

    monkeypatch.setattr(generator, "DATA_PATH", data_path)
    monkeypatch.setattr(generator, "WORLDROOT_STATE_PATH", worldroot_path)
    monkeypatch.setattr(generator, "CHRONICLE_STATE_PATH", chronicle_path)

    artifact = generator.generate(random_seed="preview")
    saved_state = json.loads(worldroot_path.read_text(encoding="utf-8"))

    assert artifact["mode"] == "random"
    assert artifact["date"] == "random"
    assert artifact["font"]["name"]
    assert artifact["natural_signal"]["weather_status"] == "not_used"
    assert "tarot" not in [section["id"] for section in artifact["sections"]]
    assert saved_state["cycle"] == 7
