"""Build the single static Seed Garden page."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "garden.json"
WHY_PATH = ROOT / "docs" / "WHY.md"
TEMPLATE_PATH = ROOT / "site" / "index.html"
STYLES_PATH = ROOT / "site" / "styles.css"
OUTPUT_DIR = ROOT / "output"


def build() -> None:
    data = _read_json(DATA_PATH)
    OUTPUT_DIR.mkdir(exist_ok=True)
    page = TEMPLATE_PATH.read_text(encoding="utf-8")
    page = page.replace("{{ title }}", f"Seed Garden / {html.escape(data['date'])}")
    page = page.replace("{{ font_link }}", _font_link(data.get("font")))
    page = page.replace("{{ design_vars }}", _design_vars(data["palette"], data.get("font")))
    page = page.replace("{{ content }}", _render_content(data))
    (OUTPUT_DIR / "index.html").write_text(page, encoding="utf-8")
    shutil.copyfile(STYLES_PATH, OUTPUT_DIR / "styles.css")


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _design_vars(palette: dict, font: dict | None) -> str:
    stack = (font or {}).get("stack") or 'Georgia, "Times New Roman", serif'
    fields = {
        "--background": palette["background"],
        "--text": palette["text"],
        "--accent": palette["accent"],
        "--muted": palette["muted"],
        "--daily-font": stack,
    }
    return " ".join(f"{name}: {html.escape(value, quote=False)};" for name, value in fields.items())


def _font_link(font: dict | None) -> str:
    if not font or not font.get("name"):
        return ""
    family = str(font["name"]).replace(" ", "+")
    href = f"https://fonts.googleapis.com/css2?family={family}&display=swap"
    return f'<link rel="stylesheet" href="{html.escape(href, quote=True)}">'


def _render_content(data: dict) -> str:
    sections = _ornament("Between daily conditions and artifacts")
    sections += "\n".join(_render_section(section) for section in data["sections"])
    seed = data["seed"]
    natural = data["natural_signal"]
    palette = data["palette"]
    font = data.get("font", {})
    moon_phase = natural.get("moon_phase")
    moon_value = moon_phase.replace("_", " ") if isinstance(moon_phase, str) else "null"
    sacred_site = _nullable(natural.get("sacred_site"))
    display_date = data["date"]
    kicker = "Daily deterministic almanac"
    if data.get("mode") == "random":
        display_date = f"random / {seed['short_seed']}"
        kicker = "Random deterministic preview"

    return f"""
      <header class="artifact-header">
        <p class="kicker">{html.escape(kicker)}</p>
        <h1>Seed Garden</h1>
        <p class="date">{html.escape(display_date)}</p>
      </header>

      <section class="conditions-strip" aria-label="Daily conditions">
        {_fact("Seed", seed["short_seed"], seed.get("explanation"))}
        {_fact("Moon phase", moon_value, "Moon phase is approximated from the date and selects the sacred site. Random previews do not use it.")}
        {_fact("Sacred site", sacred_site, "The sacred site is selected from the moon phase and contributes weather to the seed. Random previews do not use it.")}
        {_fact("Site pressure", _nullable(natural.get("site_pressure")), "Surface pressure comes from Open-Meteo when available; null is used when unavailable.")}
        {_fact("Palette", palette["name"], palette.get("explanation") or palette.get("description"))}
        {_fact("Font", font.get("name", "default"), font.get("explanation", "Font selected from the generated artifact."))}
      </section>

      {sections}

      {_why_disclosure()}
    """


def _render_section(section: dict) -> str:
    data = section["data"]
    status = html.escape(section["status"])
    if section["id"] == "iching":
        upper = data.get("upper_trigram", {})
        lower = data.get("lower_trigram", {})
        return f"""
          <section class="section artifact-plate section-iching">
            <div class="metadata-rail">
              <span>{status}</span>
              <span>Oracle</span>
              <span>No. {data["hexagram"]}</span>
            </div>
            <div class="section-heading">
              <p class="kicker">I Ching</p>
              <h2><abbr title="{_attr(data.get("explanation"))}">{data["hexagram"]}: {html.escape(data["name"])}</abbr></h2>
            </div>
            <div class="iching-artifact" aria-label="I Ching hexagram diagram">
              <div class="hexagram-ghost" aria-hidden="true">{html.escape(data.get("unicode", ""))}</div>
              <div class="hexagram-symbol">{html.escape(data.get("unicode", ""))}</div>
              <div class="hexagram-title">{html.escape(data["name"]).upper()}</div>
              <div class="trigrams">
                <span>{html.escape(str(upper.get("name", "Unknown"))).upper()}</span>
                <span>{html.escape(str(lower.get("name", "Unknown"))).upper()}</span>
              </div>
              {_hexagram_lines(data["binary"], data["changing_lines"])}
            </div>
            <dl class="artifact-details">
              <div><dt>Unicode</dt><dd>{html.escape(data.get("unicode", ""))}</dd></div>
              <div><dt>Upper trigram</dt><dd>{html.escape(str(upper.get("name", "Unknown")))}</dd></div>
              <div><dt>Lower trigram</dt><dd>{html.escape(str(lower.get("name", "Unknown")))}</dd></div>
              <div><dt>Changing lines</dt><dd>{html.escape(", ".join(str(line) for line in data["changing_lines"]) or "none")}</dd></div>
            </dl>
            <p>Modifiers: growth {data["modifiers"]["growth"]}, rot {data["modifiers"]["rot"]}, movement {data["modifiers"]["movement"]}</p>
          </section>
          {_ornament("Before Worldroot")}
        """
    if section["id"] == "worldroot":
        stats = data["stats"]
        events = "".join(f"<li>{html.escape(event)}</li>" for event in data.get("events", []))
        if not events:
            events = "<li>No notable event was retained this cycle.</li>"
        return f"""
          <section class="section artifact-plate section-worldroot">
            <div class="metadata-rail">
              <span>{status}</span>
              <span>Cycle {data["cycle"]}</span>
              <span>{data["width"]} x {data["height"]}</span>
            </div>
            <div class="section-heading">
              <p class="kicker">Worldroot</p>
              <h2><abbr title="{_attr(data.get("explanation"))}">Preserved Map</abbr></h2>
            </div>
            <div class="worldroot-shell">
              <pre class="worldroot" aria-label="Worldroot ASCII map">{html.escape(data["ascii"])}</pre>
            </div>
            <p class="caption">{html.escape(data.get("caption", ""))}</p>
            {_stat_bars(stats)}
            <ul class="events">{events}</ul>
          </section>
        """
    return ""


def _fact(label: str, value: object, explanation: str | None) -> str:
    return f"""
      <div class="fact">
        <dt><abbr title="{_attr(explanation)}">{html.escape(label)}</abbr></dt>
        <dd>{html.escape(str(value))}</dd>
      </div>
    """


def _hexagram_lines(binary: str, changing_lines: list[int]) -> str:
    lines = []
    for line_number, bit in reversed(list(enumerate(binary, start=1))):
        changing = " changing" if line_number in changing_lines else ""
        if bit == "1":
            line = '<span class="hex-line solid"></span>'
        else:
            line = '<span class="hex-line broken"><i></i><i></i></span>'
        lines.append(f'<div class="hex-row{changing}" aria-label="line {line_number}">{line}</div>')
    return f'<div class="hex-lines">{"".join(lines)}</div>'


def _stat_bars(stats: dict) -> str:
    total = max(1, sum(int(value or 0) for value in stats.values()))
    order = ["bloom", "sprout", "empty", "tree", "rot", "water", "stone", "wanderer"]
    rows = []
    for kind in order:
        value = int(stats.get(kind, 0) or 0)
        filled = max(1 if value else 0, round((value / total) * 18))
        bar = "&#9608;" * filled
        rows.append(
            f'<div class="stat-row"><span>{html.escape(kind.title())}</span>'
            f'<b aria-hidden="true">{bar}</b><em>{value}</em></div>'
        )
    return f'<div class="stats-bars" aria-label="Worldroot population stats">{"".join(rows)}</div>'


def _ornament(label: str) -> str:
    return f'<div class="ornament" role="separator" aria-label="{html.escape(label)}"><span>&#10022;</span><i></i><span>&#10086;</span><i></i><span>&#10022;</span></div>'


def _why_disclosure(path: Path = WHY_PATH) -> str:
    try:
        markdown = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return ""
    return f"""
      <details class="why-panel">
        <summary>WHY?</summary>
        <div class="why-copy">
          {_simple_markdown(markdown)}
        </div>
      </details>
    """


def _simple_markdown(markdown: str) -> str:
    blocks = []
    paragraph = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if paragraph:
                blocks.append(_paragraph(paragraph))
                paragraph = []
            continue
        if line.startswith("# "):
            if paragraph:
                blocks.append(_paragraph(paragraph))
                paragraph = []
            blocks.append(f"<h2>{html.escape(line[2:].strip())}</h2>")
        else:
            paragraph.append(line)
    if paragraph:
        blocks.append(_paragraph(paragraph))
    return "\n".join(blocks)


def _paragraph(lines: list[str]) -> str:
    return f"<p>{html.escape(' '.join(lines))}</p>"


def _nullable(value: object) -> str:
    return "null" if value is None else str(value)


def _attr(value: str | None) -> str:
    return html.escape(value or "", quote=True)


if __name__ == "__main__":
    build()
