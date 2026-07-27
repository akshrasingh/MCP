"""
provider.py
-----------
Pure business logic for the currency server. No MCP code here at all -
just a plain Python function that returns fake (mocked) exchange-rate
data.

Phase 4 of the build plan: test this in isolation before any MCP
wrapping happens:

    python -c "from provider import convert_currency; print(convert_currency(500, 'USD', 'JPY'))"
"""


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Return a mocked currency conversion result.

    This is intentionally a single, long function (no helper functions)
    so the whole lookup + fallback + formatting logic is visible in one
    place, matching the style of weather_server/provider.py.
    """

    # Normalize currency codes so "usd", "Usd", " USD " all hit the
    # same mock entry.
    normalized_from = from_currency.strip().upper()
    normalized_to = to_currency.strip().upper()

    # Hardcoded mock exchange rates, all relative to 1 USD. Not real
    # rates - just believable fake numbers so the agent has something
    # concrete to reason about.
    mock_rates_to_usd = {
        "USD": 1.0,
        "JPY": 155.0,
        "EUR": 0.92,
        "GBP": 0.78,
        "AUD": 1.5,
        "INR": 83.0,
        "AED": 3.67,
        "CAD": 1.36,
    }

    if normalized_from in mock_rates_to_usd:
        from_rate = mock_rates_to_usd[normalized_from]
        from_known = True
    else:
        # Unknown currency: assume parity with USD instead of raising,
        # so the agent always gets a usable tool result to reason about.
        from_rate = 1.0
        from_known = False

    if normalized_to in mock_rates_to_usd:
        to_rate = mock_rates_to_usd[normalized_to]
        to_known = True
    else:
        to_rate = 1.0
        to_known = False

    # Convert amount -> USD -> target currency.
    amount_in_usd = amount / from_rate
    converted_amount = amount_in_usd * to_rate

    # Effective rate used, useful for the agent to show its work.
    effective_rate = to_rate / from_rate

    result = {
        "amount": amount,
        "from_currency": normalized_from,
        "to_currency": normalized_to,
        "converted_amount": round(converted_amount, 2),
        "rate_used": round(effective_rate, 6),
        "source": "mock",
        "from_currency_known": from_known,
        "to_currency_known": to_known,
    }

    return result


if __name__ == "__main__":
    # Quick test of the function in isolation, without any MCP wrapping.
    test_amount = 500
    test_from = "USD"
    test_to = "JPY"
    conversion = convert_currency(test_amount, test_from, test_to)
    print(conversion)
