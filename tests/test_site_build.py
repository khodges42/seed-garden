import importlib.util
from pathlib import Path


def _load_build_module():
    path = Path(__file__).resolve().parents[1] / "site" / "build.py"
    spec = importlib.util.spec_from_file_location("site_build", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_simple_markdown_renders_heading_and_paragraph():
    build = _load_build_module()

    html = build._simple_markdown("# Why?\n\nA small reason.")

    assert "<h2>Why?</h2>" in html
    assert "<p>A small reason.</p>" in html


def test_why_disclosure_reads_markdown_file(tmp_path):
    build = _load_build_module()
    why_path = tmp_path / "WHY.md"
    why_path.write_text("# Why?\n\nBecause it is strange.", encoding="utf-8")

    html = build._why_disclosure(why_path)

    assert "<summary>WHY?</summary>" in html
    assert "Because it is strange." in html
