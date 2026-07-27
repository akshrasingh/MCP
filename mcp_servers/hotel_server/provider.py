"""
provider.py
-----------
Pure business logic for the hotel server. No MCP code here at all -
just a plain Python function that returns fake (mocked) hotel search
results.

Phase 4 of the build plan: test this in isolation before any MCP
wrapping happens:

    python -c "from provider import search_hotels; print(search_hotels('Tokyo', '2026-08-01', '2026-08-04'))"
"""


def search_hotels(location: str, checkin: str, checkout: str, guests: int = 1) -> dict:
    """Return mocked hotel search results for a location and date range.

    This is intentionally a single, long function (no helper functions)
    so the whole lookup + generation + formatting logic is visible in
    one place, matching the style of weather_server/provider.py.
    """

    # Normalize location so "tokyo", "Tokyo", " TOKYO " all hit the
    # same mock entry.
    normalized_location = location.strip().title()

    # Hardcoded mock nightly-price tiers per location. Not real hotels -
    # just believable fake data.
    mock_location_data = {
        "Tokyo": {"base_price_usd": 180, "base_rating": 4.2},
        "Paris": {"base_price_usd": 220, "base_rating": 4.4},
        "New York": {"base_price_usd": 260, "base_rating": 4.1},
        "London": {"base_price_usd": 210, "base_rating": 4.3},
        "Dubai": {"base_price_usd": 300, "base_rating": 4.6},
        "Sydney": {"base_price_usd": 190, "base_rating": 4.0},
    }

    mock_hotel_names = [
        "Grand Central Hotel",
        "Harbor View Inn",
        "The Lantern Suites",
        "Riverside Boutique Hotel",
    ]

    # Use the checkin string itself as a cheap, deterministic "seed" so
    # the same (location, checkin) pair always returns the same fake
    # options, without needing the `random` module.
    seed_value = sum(ord(character) for character in checkin) if checkin else 0

    # Very rough night count: parse YYYY-MM-DD and subtract day numbers
    # within the same month. Good enough for mocked data - a real
    # implementation would use `datetime.date` subtraction.
    try:
        checkin_day = int(checkin.split("-")[2])
        checkout_day = int(checkout.split("-")[2])
        nights = max(checkout_day - checkin_day, 1)
    except (IndexError, ValueError):
        nights = 1

    if normalized_location in mock_location_data:
        location_data = mock_location_data[normalized_location]
        base_price = location_data["base_price_usd"]
        base_rating = location_data["base_rating"]
        location_known = True
    else:
        # Unknown location: fall back to generic mid-range defaults
        # instead of raising an error, so the agent always gets a usable
        # tool result to reason about.
        base_price = 150
        base_rating = 3.8
        location_known = False

    # Build 3 hotel options with slight, deterministic variation in
    # price and rating - just enough to look like real search results
    # without hitting a real hotel API.
    hotel_options = []
    for option_index in range(3):
        hotel_name = mock_hotel_names[(seed_value + option_index) % len(mock_hotel_names)]
        price_per_night_usd = base_price + ((seed_value + option_index * 23) % 80) - 20
        rating = round(base_rating + ((seed_value + option_index) % 5) * 0.1 - 0.2, 1)
        stars = 3 + option_index if option_index < 2 else 5
        total_price_usd = round(price_per_night_usd * nights, 2)

        hotel_options.append(
            {
                "name": hotel_name,
                "price_per_night_usd": round(price_per_night_usd, 2),
                "rating": rating,
                "stars": stars,
                "total_price_usd": total_price_usd,
            }
        )

    result = {
        "location": normalized_location,
        "checkin": checkin,
        "checkout": checkout,
        "nights": nights,
        "guests": guests,
        "options": hotel_options,
        "source": "mock",
        "location_known": location_known,
    }

    return result


if __name__ == "__main__":
    # Quick test of the function in isolation, without any MCP wrapping.
    test_location = "Tokyo"
    test_checkin = "2026-08-01"
    test_checkout = "2026-08-04"
    hotels = search_hotels(test_location, test_checkin, test_checkout)
    print(hotels)
