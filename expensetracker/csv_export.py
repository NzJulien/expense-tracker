"""Export expenses to CSV."""
from __future__ import annotations

import csv
from pathlib import Path

from .tracker import Expense


def export_csv(expenses: list[Expense], path: str | Path) -> None:
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "category", "amount", "description"])
        for e in sorted(expenses, key=lambda x: x.date):
            writer.writerow([e.id, e.date, e.category, f"{e.amount:.2f}", e.description])


def import_csv(path: str | Path) -> list[dict]:
    """Read a CSV previously written by export_csv back into plain dicts."""
    path = Path(path)
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "id": row["id"],
                "date": row["date"],
                "category": row["category"],
                "amount": float(row["amount"]),
                "description": row.get("description", ""),
            })
    return rows
