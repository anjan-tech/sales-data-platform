from collections import defaultdict


def _normalise(record: dict) -> dict:
    """Trim spaces and standardise formats for one record."""
    return {
        "order_id": record["order_id"].strip(),
        "customer_id": record["customer_id"].strip(),
        "region": record["region"].strip().title(),
        "status": record["status"].strip().upper(),
        "amount": round(float(record["amount"]), 2),
        "currency": record["currency"].strip().upper(),
        "order_date": record["order_date"].strip(),
    }


def clean_orders(records: list[dict]) -> list[dict]:
    """Normalise records, keep the latest version of each order, drop cancelled ones."""
    latest: dict[str, dict] = {}
    for record in records:
        cleaned = _normalise(record)
        current = latest.get(cleaned["order_id"])
        # ">=" means that for the same date, the later row in the file wins
        if current is None or cleaned["order_date"] >= current["order_date"]:
            latest[cleaned["order_id"]] = cleaned

    return [r for r in latest.values() if r["status"] != "CANCELLED"]


def convert_to_inr(records: list[dict], fx_rate: float) -> list[dict]:
    """Add an amount_inr column. Supports INR and USD."""
    if fx_rate <= 0:
        raise ValueError("fx_rate must be greater than 0")

    converted = []
    for record in records:
        if record["currency"] == "INR":
            amount_inr = record["amount"]
        elif record["currency"] == "USD":
            amount_inr = record["amount"] * fx_rate
        else:
            raise ValueError(f"Unsupported currency: {record['currency']}")
        converted.append({**record, "amount_inr": round(amount_inr, 2)})
    return converted


def summarize_by_region(records: list[dict]) -> list[dict]:
    """Order count and total INR amount per region, highest total first."""
    totals = defaultdict(lambda: {"order_count": 0, "total_amount_inr": 0.0})
    for record in records:
        region_totals = totals[record["region"]]
        region_totals["order_count"] += 1
        region_totals["total_amount_inr"] += record["amount_inr"]

    summary = [
        {
            "region": region,
            "order_count": values["order_count"],
            "total_amount_inr": round(values["total_amount_inr"], 2),
        }
        for region, values in totals.items()
    ]
    return sorted(summary, key=lambda row: row["total_amount_inr"], reverse=True)