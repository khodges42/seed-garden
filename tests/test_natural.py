from garden import natural


def test_sacred_site_selection_includes_site_details():
    site = natural.select_sacred_site("waxing_gibbous")

    assert site["name"] == "Stonehenge"
    assert site["lat"] == 51.1789
    assert site["lon"] == -1.8262


def test_weather_bad_response_falls_back(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'{"current": null}'

    monkeypatch.setattr(natural, "urlopen", lambda *args, **kwargs: Response())

    weather = natural.fetch_site_weather({"lat": 1, "lon": 2})

    assert weather["weather_status"] == "unavailable"
    assert weather["surface_pressure"] is None
