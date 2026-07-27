"""
provider.py
-----------
Pure business logic for the maps server. No MCP code here at all -
just a plain Python function that returns fake (mocked) points of
interest for a location.

Phase 4 of the build plan: test this in isolation before any MCP
wrapping happens:

    python -c "from provider import get_places; print(get_places('Tokyo'))"
"""


def get_places(location: str, category: str = "attractions") -> dict:
    """Return mocked points of interest for a location and category.

    This is intentionally a single, long function (no helper functions)
    so the whole lookup + generation + formatting logic is visible in
    one place, matching the style of weather_server/provider.py.
    """

    # Normalize location/category so "tokyo", "Tokyo", " TOKYO " and
    # "Attractions", "attractions" all hit the same mock entry.
    normalized_location = location.strip().title()
    normalized_category = category.strip().lower()

    # Hardcoded mock points of interest, grouped by location and
    # category. Not real listings - just believable fake data.
    mock_places_data = {
        "Tokyo": {
            "attractions": ["Senso-ji Temple", "Shibuya Crossing", "Tokyo Tower"],
            "restaurants": ["Ichiran Ramen", "Sukiyabashi Jiro", "Gonpachi"],
        },
        "Paris": {
            "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame"],
            "restaurants": ["Le Jules Verne", "Bistrot Paul Bert", "L'Ami Jean"],
        },
        "New York": {
            "attractions": ["Central Park", "Statue of Liberty", "Times Square"],
            "restaurants": ["Katz's Delicatessen", "Peter Luger", "Joe's Pizza"],
        },
        "London": {
            "attractions": ["Big Ben", "Tower of London", "British Museum"],
            "restaurants": ["Dishoom", "The Ledbury", "Borough Market"],
        },
        "Dubai": {
            "attractions": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah"],
            "restaurants": ["Al Mahara", "Pierchic", "Ravi Restaurant"],
        },
        "Sydney": {
            "attractions": ["Sydney Opera House", "Bondi Beach", "Harbour Bridge"],
            "restaurants": ["Quay", "Chiswick", "Mr. Wong"],
        },
    }

    # Use the location + category strings as a cheap, deterministic
    # "seed" so ratings vary a little but stay stable across repeated
    # calls, without needing the `random` module.
    seed_value = sum(ord(character) for character in normalized_location + normalized_category)

    if normalized_location in mock_places_data:
        location_data = mock_places_data[normalized_location]
        location_known = True
    else:
        # Unknown location: fall back to a small set of generic place
        # names instead of raising an error, so the agent always gets a
        # usable tool result to reason about.
        location_data = {
            "attractions": ["City Museum", "Old Town Square", "Riverside Park"],
            "restaurants": ["Local Bistro", "The Corner Cafe", "Downtown Grill"],
        }
        location_known = False

    if normalized_category in location_data:
        place_names = location_data[normalized_category]
        category_known = True
    else:
        # Unknown category: default to attractions instead of raising.
        place_names = location_data.get("attractions", [])
        category_known = False

    # Attach a small deterministic rating to each place name so the
    # results look like real search results.
    places = []
    for place_index, place_name in enumerate(place_names):
        rating = round(3.5 + ((seed_value + place_index) % 15) * 0.1, 1)
        places.append({"name": place_name, "rating": rating})

    result = {
        "location": normalized_location,
        "category": normalized_category,
        "places": places,
        "source": "mock",
        "location_known": location_known,
        "category_known": category_known,
    }

    return result


if __name__ == "__main__":
    # Quick test of the function in isolation, without any MCP wrapping.
    test_location = "Tokyo"
    test_category = "attractions"
    places_data = get_places(test_location, test_category)
    print(places_data)
