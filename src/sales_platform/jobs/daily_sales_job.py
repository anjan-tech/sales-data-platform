import logging
from pathlib import Path

from sales_platform.transformations.orders import (
    clean_orders,
    convert_to_inr,
    summarize_by_region,
)
from sales_platform.utils.config import Config, load_config
from sales_platform.utils.file_io import read_csv, write_csv
from sales_platform.utils.fx_client import fetch_fx_rate
from sales_platform.utils.validators import split_valid_invalid

logger = logging.getLogger(__name__)


def resolve_fx_rate(config: Config) -> float:
    """Use the live API if a URL is configured, otherwise the fixed rate."""
    if config.fx_api_url:
        return fetch_fx_rate(config.fx_api_url)
    return config.fx_rate


def run(config: Config) -> dict:
    """Run the daily sales pipeline and return row counts for each stage."""
    records = read_csv(config.input_path)
    valid, invalid = split_valid_invalid(records)
    cleaned = clean_orders(valid)
    converted = convert_to_inr(cleaned, resolve_fx_rate(config))
    summary = summarize_by_region(converted)

    output_dir = Path(config.output_dir)
    write_csv(str(output_dir / "clean_orders.csv"), converted)
    write_csv(str(output_dir / "rejected_orders.csv"), invalid)
    write_csv(str(output_dir / "region_summary.csv"), summary)

    stats = {
        "read": len(records),
        "valid": len(valid),
        "rejected": len(invalid),
        "loaded": len(converted),
    }
    logger.info("Daily sales job finished: %s", stats)
    return stats


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config())


if __name__ == "__main__":
    main()