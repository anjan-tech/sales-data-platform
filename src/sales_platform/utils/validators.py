from datetime import datetime

REQUIRED_FIELDS = (
    "order_id", "customer_id", "region", "status", "amount", "currency", "order_date",
)
VALID_STATUSES = {"PLACED", "SHIPPED", "DELIVERED", "CANCELLED"}


def validate_order(record: dict) -> list[str]:
    """Return a list of problems with the record. Empty list means valid."""
    errors = []

    for field in REQUIRED_FIELDS:
        value = record.get(field)
        if value is None or str(value).strip() == "":
            errors.append(f"missing {field}")

    if errors:
        return errors  # no point checking values if fields are missing

    try:
        if float(record["amount"]) < 0:
            errors.append("amount must not be negative")
    except ValueError:
        errors.append(f"amount is not a number: {record['amount']}")

    if str(record["status"]).strip().upper() not in VALID_STATUSES:
        errors.append(f"invalid status: {record['status']}")

    try:
        datetime.strptime(str(record["order_date"]).strip(), "%Y-%m-%d")
    except ValueError:
        errors.append(f"invalid order_date: {record['order_date']}")

    return errors


def split_valid_invalid(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separate records into valid ones and rejected ones (with error reasons)."""
    valid, invalid = [], []
    for record in records:
        errors = validate_order(record)
        if errors:
            invalid.append({**record, "errors": "; ".join(errors)})
        else:
            valid.append(record)
    return valid, invalid