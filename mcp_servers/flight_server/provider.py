"""
provider.py
-----------
Pure business logic for the flight server. No MCP code here at all -
just a plain Python function that returns fake (mocked) flight search
results.

Phase 4 of the build plan: test this in isolation before any MCP
wrapping happens:

    python -c "from provider import search_flights; print(search_flights('NYC', 'Tokyo', '2026-08-01'))"
"""


def search_flights(origin: str, destination: str, date: str) -> dict:
    """Return mocked flight search results for an origin/destination/date.

    This is intentionally a single, long function (no helper functions)
    so the whole lookup + generation + formatting logic is visible in
    one place, matching the style of weather_server/provider.py.
    """

    # Normalize origin/destination so "nyc", "NYC", " Nyc " all hit the
    # same mock entry.
    normalized_origin = origin.strip().title()
    normalized_destination = destination.strip().title()

    # Hardcoded mock airline roster and base price/duration per
    # destination. Not real routes - just believable fake data.
    mock_destination_data = {
        "Tokyo": {"base_price_usd": 950, "base_duration_hours": 14},
        "Paris": {"base_price_usd": 650, "base_duration_hours": 8},
        "New York": {"base_price_usd": 400, "base_duration_hours": 6},
        "London": {"base_price_usd": 600, "base_duration_hours": 7},
        "Dubai": {"base_price_usd": 750, "base_duration_hours": 9},
        "Sydney": {"base_price_usd": 1100, "base_duration_hours": 16},
    }

    mock_airlines = [
        "SkyBridge Air",
        "Pacific Wings",
        "Meridian Airlines",
        "Northern Star Air",
    ]

    # Use the date string itself as a cheap, deterministic "seed" so the
    # same (origin, destination, date) triple always returns the same
    # fake options, without needing the `random` module.
    seed_value = sum(ord(character) for character in date) if date else 0

    if normalized_destination in mock_destination_data:
        destination_data = mock_destination_data[normalized_destination]
        base_price = destination_data["base_price_usd"]
        base_duration = destination_data["base_duration_hours"]
        destination_known = True
    else:
        # Unknown destination: fall back to generic mid-range defaults
        # instead of raising an error, so the agent always gets a usable
        # tool result to reason about.
        base_price = 700
        base_duration = 10
        destination_known = False

    # Build 3 flight options with slight, deterministic variation in
    # price, duration, and stops - just enough to look like real search
    # results without hitting a real flight API.
    flight_options = []
    for option_index in range(3):
        airline = mock_airlines[(seed_value + option_index) % len(mock_airlines)]
        price_usd = base_price + ((seed_value + option_index * 37) % 150) - 50
        duration_hours = base_duration + ((seed_value + option_index * 5) % 3)
        stops = option_index  # first option nonstop, then 1 stop, then 2

        flight_options.append(
            {
                "airline": airline,
                "price_usd": round(price_usd, 2),
                "duration_hours": duration_hours,
                "stops": stops,
            }
        )

    result = {
        "origin": normalized_origin,
        "destination": normalized_destination,
        "date": date,
        "options": flight_options,
        "source": "mock",
        "destination_known": destination_known,
    }

    return result


if __name__ == "__main__":
    # Quick test of the function in isolation, without any MCP wrapping.
    test_origin = "NYC"
    test_destination = "Tokyo"
    test_date = "2026-08-01"
    flights = search_flights(test_origin, test_destination, test_date)
    print(flights)
