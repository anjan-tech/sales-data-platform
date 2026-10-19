import csv
from pathlib import Path


def read_csv(path: str) -> list[dict]:
    """Read a CSV file into a list of dictionaries (one per row)."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with file_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, rows: list[dict]) -> int:
    """Write rows to a CSV file, creating folders if needed. Returns rows written."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        file_path.write_text("", encoding="utf-8")
        return 0

    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)