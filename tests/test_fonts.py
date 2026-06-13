import json

import pytest

from garden.fonts import picker


def test_font_selection_is_deterministic():
    seed_hash = "2" * 64

    assert picker.select_font(seed_hash) == picker.select_font(seed_hash)


def test_font_loader_uses_default_for_missing_file(tmp_path):
    fonts = picker._load_fonts(tmp_path / "missing.json")

    assert fonts[0]["id"] == "cormorant-garamond"


def test_font_loader_reports_invalid_schema(tmp_path):
    font_path = tmp_path / "fonts.json"
    font_path.write_text(json.dumps([{"id": "missing-fields"}]), encoding="utf-8")

    with pytest.raises(RuntimeError, match="missing required fields"):
        picker._load_fonts(font_path)
