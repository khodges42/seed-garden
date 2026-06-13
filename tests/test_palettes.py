import json

import pytest

from garden.palettes import picker


def test_palette_selection_is_deterministic():
    seed_hash = "a" * 64

    assert picker.select_palette(seed_hash) == picker.select_palette(seed_hash)


def test_palette_loader_reports_missing_file(tmp_path):
    with pytest.raises(RuntimeError, match="Palette file is missing"):
        picker._load_palettes(tmp_path / "missing.json")


def test_palette_loader_reports_invalid_schema(tmp_path):
    palette_path = tmp_path / "palettes.json"
    palette_path.write_text(json.dumps([{"id": "missing-fields"}]), encoding="utf-8")

    with pytest.raises(RuntimeError, match="missing required fields"):
        picker._load_palettes(palette_path)
