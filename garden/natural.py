"""Natural signal collection for the daily seed."""

from __future__ import annotations

import json
import math
from datetime import date as date_type
from urllib.parse import urlencode
from urllib.request import urlopen


MOON_PHASES = (
    "new_moon",
    "waxing_crescent",
    "first_quarter",
    "waxing_gibbous",
    "full_moon",
    "waning_gibbous",
    "last_quarter",
    "waning_crescent",
)

SACRED_SITES = {
    "new_moon": {"name": "Gobekli Tepe", "lat": 37.2231, "lon": 38.9226},
    "waxing_crescent": {"name": "Newgrange", "lat": 53.6947, "lon": -6.4756},
    "first_quarter": {"name": "Machu Picchu", "lat": -13.1631, "lon": -72.5450},
    "waxing_gibbous": {"name": "Stonehenge", "lat": 51.1789, "lon": -1.8262},
    "full_moon": {"name": "Great Pyramid of Giza", "lat": 29.9792, "lon": 31.1342},
    "waning_gibbous": {"name": "Delphi", "lat": 38.4828, "lon": 22.5010},
    "last_quarter": {"name": "Chaco Canyon", "lat": 36.0600, "lon": -107.9589},
    "waning_crescent": {"name": "Maeshowe", "lat": 58.9967, "lon": -3.1875},
}

WEATHER_FIELDS = (
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
    "weather_code",
)


def _empty_weather() -> dict:
    weather = {"weather_status": "unavailable"}
    weather.update({field: None for field in WEATHER_FIELDS})
    return weather


def get_moon_phase(date: str) -> dict:
    """Return a deterministic moon phase approximation for an ISO date."""

    day = date_type.fromisoformat(date)
    known_new_moon = date_type(2000, 1, 6)
    lunation_days = 29.53058867
    age = ((day - known_new_moon).days % lunation_days) / lunation_days
    phase_index = math.floor((age * 8) + 0.5) % 8
    phase = MOON_PHASES[phase_index]

    return {
        "moon_phase": phase,
        "moon_age_fraction": round(age, 4),
        "explanation": "Moon phase is approximated from the date using a fixed reference new moon.",
    }


def select_sacred_site(moon_phase: str) -> dict:
    """Select the sacred site associated with the moon phase."""

    site = SACRED_SITES.get(moon_phase, SACRED_SITES["new_moon"])
    return dict(site)


def fetch_site_weather(site: dict) -> dict:
    """Fetch current weather from Open-Meteo, falling back cleanly on errors."""

    query = urlencode(
        {
            "latitude": site["lat"],
            "longitude": site["lon"],
            "current": ",".join(WEATHER_FIELDS),
            "timezone": "auto",
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{query}"

    try:
        with urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        current = payload.get("current")
        if not isinstance(current, dict):
            return _empty_weather()
        weather = {"weather_status": "available"}
        weather.update({field: current.get(field) for field in WEATHER_FIELDS})
        return weather
    except Exception:
        return _empty_weather()


def get_natural_signal(date: str) -> dict:
    """Build the natural signal used by the daily seed."""

    moon = get_moon_phase(date)
    site = select_sacred_site(moon["moon_phase"])
    weather = fetch_site_weather(site)

    return {
        "date": date,
        "moon_phase": moon["moon_phase"],
        "moon_age_fraction": moon["moon_age_fraction"],
        "sacred_site": site["name"],
        "site": site,
        "site_pressure": weather.get("surface_pressure"),
        "weather_status": weather["weather_status"],
        "weather": weather,
        "explanation": "Natural signal combines moon phase, its associated sacred site, and optional Open-Meteo weather.",
    }
