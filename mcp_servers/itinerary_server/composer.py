"""
composer.py
-----------
Pure business logic for the itinerary server. No MCP code here at all -
just a plain Python function that assembles a day-by-day itinerary
string out of the dicts returned by the other servers' provider
functions (weather, flights, hotels, places).

Phase 5 of the build plan: test this in isolation before any MCP
wrapping happens, using fake inputs shaped like the other providers'
return values.
"""


def build_itinerary(weather: dict, flights: dict, hotels: dict, places: dict, days: int = 3) -> str:
    """Assemble a markdown day-by-day itinerary from tool result dicts.

    This is intentionally a single, long function (no helper functions)
    so the whole assembly + formatting logic is visible in one place,
    matching the style of weather_server/provider.py.

    Args:
        weather: Shape returned by weather_server.provider.get_weather().
        flights: Shape returned by flight_server.provider.search_flights().
        hotels: Shape returned by hotel_server.provider.search_hotels().
        places: Shape returned by maps_server.provider.get_places().
        days: How many days the itinerary should cover.

    Returns:
        A single markdown-formatted string with a trip summary followed
        by one section per day.
    """

    # Pull out the pieces we need, defaulting gracefully if a caller
    # passes a partial/empty dict instead of raising a KeyError - keeps
    # this usable even while some servers are still being built out.
    destination = weather.get("location") or flights.get("destination") or hotels.get("location") or places.get("location") or "Unknown Destination"

    weather_condition = weather.get("condition", "unknown")
    weather_temp_c = weather.get("temp_c", "n/a")

    flight_options = flights.get("options", [])
    best_flight = flight_options[0] if flight_options else None

    hotel_options = hotels.get("options", [])
    best_hotel = hotel_options[0] if hotel_options else None

    place_list = places.get("places", [])

    # Build the trip summary header first.
    lines = []
    lines.append(f"# Itinerary: {destination}")
    lines.append("")
    lines.append("## Trip Summary")
    lines.append(f"- Weather: {weather_condition}, {weather_temp_c}\u00b0C")

    if best_flight:
        lines.append(
            f"- Flight: {best_flight.get('airline', 'n/a')} - "
            f"${best_flight.get('price_usd', 'n/a')}, "
            f"{best_flight.get('duration_hours', 'n/a')}h, "
            f"{best_flight.get('stops', 'n/a')} stop(s)"
        )
    else:
        lines.append("- Flight: no flight options available")

    if best_hotel:
        lines.append(
            f"- Hotel: {best_hotel.get('name', 'n/a')} - "
            f"${best_hotel.get('price_per_night_usd', 'n/a')}/night, "
            f"{best_hotel.get('rating', 'n/a')}\u2605 rating"
        )
    else:
        lines.append("- Hotel: no hotel options available")

    lines.append("")
    lines.append("## Day-by-Day Plan")

    # Spread the available places evenly across the requested number of
    # days, cycling back to the start of the list if there are fewer
    # places than days.
    for day_index in range(days):
        day_number = day_index + 1
        lines.append(f"### Day {day_number}")

        if place_list:
            place_for_day = place_list[day_index % len(place_list)]
            lines.append(
                f"- Visit: {place_for_day.get('name', 'n/a')} "
                f"({place_for_day.get('rating', 'n/a')}\u2605)"
            )
        else:
            lines.append("- Visit: no places available")

        if day_number == 1:
            lines.append("- Arrival day: check in to hotel, rest and settle in.")
        elif day_number == days:
            lines.append("- Departure day: check out of hotel, head to airport.")
        else:
            lines.append("- Free time / local exploration in the evening.")

        lines.append("")

    itinerary_text = "\n".join(lines)
    return itinerary_text


if __name__ == "__main__":
    # Quick test of the function in isolation, with fake inputs shaped
    # like the real provider return values, without any MCP wrapping.
    fake_weather = {"location": "Tokyo", "condition": "Sunny", "temp_c": 28}
    fake_flights = {"destination": "Tokyo", "options": [{"airline": "SkyBridge Air", "price_usd": 950, "duration_hours": 14, "stops": 0}]}
    fake_hotels = {"location": "Tokyo", "options": [{"name": "Grand Central Hotel", "price_per_night_usd": 180, "rating": 4.2}]}
    fake_places = {"location": "Tokyo", "places": [{"name": "Senso-ji Temple", "rating": 4.5}, {"name": "Shibuya Crossing", "rating": 4.3}]}
    print(build_itinerary(fake_weather, fake_flights, fake_hotels, fake_places, days=3))
