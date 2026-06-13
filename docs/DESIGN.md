# Seed Garden Design Document v1

## Vision

Seed Garden is a daily-generated, single-page static website that presents a collection of deterministic artifacts derived from a shared seed.

The site should feel like a discovered object: part grimoire, part almanac, part design artifact, and part simulation.

Visitors are not interacting with an application. They are examining a document generated from today's conditions.

The site is regenerated daily through GitHub Actions and deployed as a static site.

---

# Core Principles

## Deterministic

Given the same inputs, Seed Garden must always produce the same outputs.

No module should rely on non-deterministic randomness.

All randomness should be derived from the current seed.

---

## Single Page

The entire site exists as one page.

There are no sub-pages.

There is no navigation hierarchy.

The page is a daily artifact composed of multiple sections.

---

## Explainable

Every major artifact should include hoverable explanations describing:

* What it is
* How it was generated
* What inputs were used

Visitors should be able to understand how the artifact came to exist.

---

## Extensible

Each artifact is an independent module.

Modules consume a seed and produce structured JSON.

Modules should not know about HTML rendering.

---

# Emotional Goals

The site should evoke:

* Mystery
* Curiosity
* Wonder
* Playfulness

The site should not feel:

* Corporate
* Productivity-focused
* Dashboard-like
* Overly serious

---

# Daily Seed

The daily seed is generated from multiple inputs.

Initial design:

```text
date
+
worldroot_checksum
+
natural_signal
```

The resulting string is hashed to produce the final seed.

Example:

```json
{
  "date": "2026-06-13",
  "worldroot_checksum": "c8f07d11",
  "moon_phase": "waxing_gibbous",
  "sacred_site": "Stonehenge",
  "site_pressure": 1018.6
}
```

---

# Natural Signals

Natural signals provide real-world input into the daily seed.

Initial sources:

* Moon phase
* Atmospheric pressure at a sacred site

Future possibilities:

* Sunrise / sunset
* Solstice proximity
* Tidal information
* Planetary positions

If external data cannot be fetched:

```text
external:null
```

is substituted.

Generation must never fail because of unavailable external data.

---

# Sacred Sites

A sacred site is selected based on the current moon phase.

Example mapping:

New Moon -> Göbekli Tepe

Waxing Crescent -> Newgrange

First Quarter -> Machu Picchu

Waxing Gibbous -> Stonehenge

Full Moon -> Great Pyramid of Giza

Waning Gibbous -> Delphi

Last Quarter -> Chaco Canyon

Waning Crescent -> Maeshowe

The selected site contributes weather data to the seed.

Symbolic meaning is intentionally deferred to a later version.

---

# Site Structure

The page is composed of sections.

Initial task-plan sections:

* Seed Information
* I Ching
* Worldroot

Deferred sections:

* Tarot
* Numbers Station
* Expanded Moon Information

Additional sections may be added later.

---

# Visual Design

The site is monochromatic.

A daily palette is selected deterministically from the seed.

The palette changes daily.

The page should feel:

* Editorial
* Experimental
* Monochromatic
* Printed
* Brutalist
* Minimal
* Like a found plate, specimen sheet, or almanac leaf

Design inspiration comes from contemporary design studios, net art, zines, and archival documents.

---

# Palette System

The seed determines the active palette.

Example palettes:

* Verdigris
* Blueprint
* Phosphor
* Amber
* Blood
* Violet
* Slate

Only one palette is active per day.

The selected font is also generated deterministically from the daily seed and stored in the JSON artifact.

The page background uses a subtle animated field of palette-colored dots rather than obvious stripes. Motion must remain slow, atmospheric, and disabled for visitors who prefer reduced motion.

---

# I Ching Module

The I Ching is generated from the daily seed.

Outputs:

* Hexagram
* Name
* Unicode hexagram symbol
* Upper trigram
* Lower trigram
* Changing lines
* Description

The I Ching influences Worldroot evolution.

Worldroot should be considered a reflection of the current hexagram.

The site renders I Ching as an oracle diagram: the Unicode symbol and line structure are the primary visual artifact, while raw binary strings remain data only.

---

# Tarot Module

Status: Deferred / inactive

Purpose:

Tarot exists as a future educational project.

Future implementation may contain:

* Single card draws
* Placeholder explanations

The design should make it easy to expand later.

---

# Worldroot

Worldroot is a persistent simulation.

The world advances by one cycle per day.

The current state is stored between runs.

The site renders Worldroot as a preserved map specimen with a monospaced ASCII grid, compact population bars, and concise events.

---

## Worldroot Philosophy

Worldroot is not a game.

Worldroot is not intended to be optimized.

Worldroot is a living chronicle.

Birth, growth, decay, death, and renewal are central themes.

---

## Worldroot Entities

```text
. Empty / Void
, Sprout
* Bloom
T Tree / Memory
o Wanderer
x Rot
~ Water / Potential
# Stone / Permanence
```

---

## Wanderers

A wanderer is anything that wanders and affects change.

Examples:

* Spirit
* Lost soul
* Cat
* Traveler
* Shaman

Interpretation is intentionally flexible.

---

## Entity Structure

Example:

```json
{
  "kind": "tree",
  "cycles": 14
}
```

Cycles represent persistence through the world's history.

---

## Naming

Named entities are rare.

Named entities may:

* Live
* Grow
* Die

Named entity deaths are chronicle-worthy events.

The number of named entities is intentionally limited.

---

## Eras

Worldroot organizes history into eras.

Eras are determined by major changes in world conditions.

Possible triggers:

* Mass growth
* Collapse
* Extinction
* Rot tide
* Significant population shifts

The exact rules will be refined later.

---

## Chronicle

The world remembers only important events.

The chronicle stores:

* Era transitions
* Named births
* Named deaths
* Major records

The chronicle intentionally forgets most details.

History is compressed into mythology.

---

# Numbers Station

Produces deterministic transmissions from the daily seed.

Output format is intentionally aesthetic and mysterious.

Interpretation is left to the visitor.

---

# Data Flow

```text
GitHub Action
    ↓
Generate Daily Seed
    ↓
Run Modules
    ↓
Produce JSON
    ↓
Render Site
    ↓
Deploy To Cloudflare
```

---

# Module Contract

All modules implement:

```python
generate(seed, state) -> dict
```

Modules consume structured inputs and return structured outputs.

Modules do not generate HTML.

---

# Initial Milestone

1. Seed generation
2. Palette generation
3. I Ching module
4. Worldroot simulation
5. Tarot placeholder
6. Numbers Station
7. Single-page template
8. Daily GitHub Action
9. Cloudflare deployment

The first release should be functional, deterministic, visually compelling, and small.

---

# Fine details on the sites and seed generation

Use **Open-Meteo** for this. It’s free, no API key, supports global lat/lon, and exposes `surface_pressure` in hourly/current weather data. It also advertises free forecast + historical APIs with no key required. ([Open-Meteo][1])

## Sacred site mapping

```json
{
  "new_moon": {
    "name": "Gobekli Tepe",
    "lat": 37.2231,
    "lon": 38.9226
  },
  "waxing_crescent": {
    "name": "Newgrange",
    "lat": 53.6947,
    "lon": -6.4756
  },
  "first_quarter": {
    "name": "Machu Picchu",
    "lat": -13.1631,
    "lon": -72.5450
  },
  "waxing_gibbous": {
    "name": "Stonehenge",
    "lat": 51.1789,
    "lon": -1.8262
  },
  "full_moon": {
    "name": "Great Pyramid of Giza",
    "lat": 29.9792,
    "lon": 31.1342
  },
  "waning_gibbous": {
    "name": "Delphi",
    "lat": 38.4828,
    "lon": 22.5010
  },
  "last_quarter": {
    "name": "Chaco Canyon",
    "lat": 36.0600,
    "lon": -107.9589
  },
  "waning_crescent": {
    "name": "Maeshowe",
    "lat": 58.9967,
    "lon": -3.1875
  }
}
```

## Open-Meteo request

For the selected site:

```txt
https://api.open-meteo.com/v1/forecast?latitude=51.1789&longitude=-1.8262&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code&timezone=auto
```

Example response fields to store:

```json
{
  "site": "Stonehenge",
  "lat": 51.1789,
  "lon": -1.8262,
  "temperature_2m": 17.2,
  "relative_humidity_2m": 78,
  "surface_pressure": 1018.6,
  "wind_speed_10m": 14.2,
  "weather_code": 3
}
```

## Seed input shape

```json
{
  "date": "2026-06-13",
  "moon_phase": "waxing_gibbous",
  "sacred_site": "Stonehenge",
  "site_pressure": 1018.6,
  "worldroot_checksum": "c8f07d11"
}
```

## Fallback

```json
{
  "date": "2026-06-13",
  "moon_phase": "waxing_gibbous",
  "sacred_site": "Stonehenge",
  "site_pressure": null,
  "weather_status": "unavailable",
  "worldroot_checksum": "c8f07d11"
}
```

The daily build should continue even if the API call fails.

[1]: https://open-meteo.com/?utm_source=chatgpt.com "Open-Meteo.com: 🌤️ Free Open-Source Weather API"
