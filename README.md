# Seed Garden

Seed Garden generates one JSON artifact and renders one static page from it.

## Manual Rebuild

Install dependencies once:

```sh
pip install -r requirements.txt
```

Generate today's data and advance persistent Worldroot state:

```sh
python -m garden.generate
python site/build.py
```

The static site is written to:

```txt
output/index.html
output/styles.css
```

## Generate A Specific Date

```sh
python -m garden.generate --date 2026-06-13
python site/build.py
```

This uses the normal daily pipeline and advances persistent state.

## Generate A Random Preview

```sh
python -m garden.generate --random
python site/build.py
```

Random preview mode writes `data/garden.json` for rendering, but does not advance `state/worldroot.json` or `state/chronicle.json`.

For a repeatable preview:

```sh
python -m garden.generate --random-seed "my test seed"
python site/build.py
```

## Test

```sh
pytest
```
