"""
provider.py
-----------
Pure business logic for the weather server. No MCP code here at all -
just a plain Python function that returns fake (mocked) weather data.

Phase 1, Step 1.1 of the build plan: test this in isolation before any
MCP wrapping happens:

    python -c "from provider import get_weather; print(get_weather('Tokyo', '2026-08-01'))"
"""


def get_weather(location: str, date: str) -> dict:
    """Return mocked weather data for a given location and date.

    This is intentionally a single, long function (no helper functions)
    so the whole lookup + fallback + formatting logic is visible in one
    place while the MCP protocol is being proven out.
    """

    # Normalize the incoming location so "tokyo", "Tokyo", " TOKYO "
    # all hit the same mock entry.
    normalized_location = location.strip().title()

    # Hardcoded mock "database" of known locations. Each entry has a
    # small set of possible conditions and a base temperature range -
    # we don't need a real weather API yet, just believable fake data.
    mock_weather_data = {
        "Tokyo": {
            "conditions": ["Sunny", "Cloudy", "Light Rain"],
            "base_temp_c": 28,
            "humidity_percent": 65,
        },
        "Paris": {
            "conditions": ["Cloudy", "Rainy", "Clear"],
            "base_temp_c": 18,
            "humidity_percent": 70,
        },
        "New York": {
            "conditions": ["Sunny", "Windy", "Snow"],
            "base_temp_c": 12,
            "humidity_percent": 55,
        },
        "London": {
            "conditions": ["Rainy", "Overcast", "Foggy"],
            "base_temp_c": 15,
            "humidity_percent": 80,
        },
        "Dubai": {
            "conditions": ["Sunny", "Clear", "Hazy"],
            "base_temp_c": 38,
            "humidity_percent": 40,
        },
        "Sydney": {
            "conditions": ["Sunny", "Partly Cloudy", "Windy"],
            "base_temp_c": 22,
            "humidity_percent": 60,
        },
    }

    # Use the date string itself as a cheap, deterministic "seed" so the
    # same (location, date) pair always returns the same fake reading,
    # without needing the `random` module or any external service.
    seed_value = sum(ord(character) for character in date) if date else 0

    if normalized_location in mock_weather_data:
        location_data = mock_weather_data[normalized_location]
        condition_options = location_data["conditions"]
        condition = condition_options[seed_value % len(condition_options)]
        temp_c = location_data["base_temp_c"] + (seed_value % 7) - 3
        humidity_percent = location_data["humidity_percent"] + (seed_value % 10) - 5
        location_known = True
    else:
        # Unknown location: fall back to generic mild-weather defaults
        # instead of raising an error, so the agent always gets a usable
        # tool result to reason about.
        generic_conditions = ["Clear", "Cloudy", "Mild Rain"]
        condition = generic_conditions[seed_value % len(generic_conditions)]
        temp_c = 20 + (seed_value % 10) - 5
        humidity_percent = 50 + (seed_value % 10)
        location_known = False

    result = {
        "location": normalized_location,
        "date": date,
        "condition": condition,
        "temp_c": temp_c,
        "humidity_percent": humidity_percent,
        "source": "mock",
        "location_known": location_known,
    }

    return result


if __name__ == "__main__":
    # Quick manual sanity check when running this file directly:
    #   python provider.py
    print(get_weather("Tokyo", "2026-08-01"))
    print(get_weather("Atlantis", "2026-08-01"))
