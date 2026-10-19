import os
from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def get_env(name: str, default: str | None = None) -> str:
    """Return an environment variable, or the default. Raise if neither exists."""
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise ConfigError(f"Missing required environment variable: {name}")
    return value.strip()


@dataclass(frozen=True)
class Config:
    input_path: str
    output_dir: str
    fx_rate: float
    fx_api_url: str | None = None


def load_config() -> Config:
    """Build the job configuration from environment variables."""
    fx_rate_raw = get_env("FX_RATE", "83.0")
    try:
        fx_rate = float(fx_rate_raw)
    except ValueError as exc:
        raise ConfigError(f"FX_RATE must be a number, got: {fx_rate_raw}") from exc
    if fx_rate <= 0:
        raise ConfigError("FX_RATE must be greater than 0")

    return Config(
        input_path=get_env("INPUT_PATH", "data/input/orders.csv"),
        output_dir=get_env("OUTPUT_DIR", "data/output"),
        fx_rate=fx_rate,
        fx_api_url=os.getenv("FX_API_URL") or None,
    )