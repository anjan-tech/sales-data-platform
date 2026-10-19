import requests


class FxRateError(Exception):
    """Raised when the exchange rate cannot be fetched."""


def fetch_fx_rate(api_url: str, currency: str = "USD", timeout: int = 10) -> float:
    """Fetch the exchange rate from `currency` to INR."""
    try:
        response = requests.get(
            api_url, params={"base": currency, "symbols": "INR"}, timeout=timeout
        )
    except requests.RequestException as exc:
        raise FxRateError(f"Could not reach FX API: {exc}") from exc

    if response.status_code != 200:
        raise FxRateError(f"FX API returned status {response.status_code}")

    rate = response.json().get("rates", {}).get("INR")
    if rate is None:
        raise FxRateError("INR rate missing in FX API response")
    return float(rate)