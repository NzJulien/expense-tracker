"""Per-category monthly budget tracking and alerts."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .tracker import ExpenseTracker


@dataclass
class BudgetStatus:
    category: str
    limit: float
    spent: float

    @property
    def remaining(self) -> float:
        return round(self.limit - self.spent, 2)

    @property
    def percent_used(self) -> float:
        if self.limit == 0:
            return 0.0
        return round((self.spent / self.limit) * 100, 1)

    @property
    def is_over(self) -> bool:
        return self.spent > self.limit

    @property
    def is_near_limit(self) -> bool:
        return 80.0 <= self.percent_used < 100.0


class BudgetManager:
    """Stores per-category monthly budget limits as a small JSON sidecar file."""

    def __init__(self, storage_path: str | Path = "budgets.json"):
        self.storage_path = Path(storage_path)
        self.limits: dict[str, float] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            self.limits = json.loads(self.storage_path.read_text(encoding="utf-8"))
        else:
            self.limits = {}

    def save(self) -> None:
        self.storage_path.write_text(json.dumps(self.limits, indent=2) + "\n", encoding="utf-8")

    def set_limit(self, category: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("budget limit cannot be negative")
        self.limits[category.strip().lower()] = round(float(amount), 2)
        self.save()

    def remove_limit(self, category: str) -> bool:
        category = category.strip().lower()
        if category in self.limits:
            del self.limits[category]
            self.save()
            return True
        return False

    def get_limit(self, category: str) -> Optional[float]:
        return self.limits.get(category.strip().lower())

    def status_for_month(self, tracker: ExpenseTracker, month: str) -> list[BudgetStatus]:
        """Compute spend-vs-limit for every budgeted category in a given month."""
        month_expenses = tracker.by_month(month)
        spent_by_category = tracker.total_by_category(month_expenses)

        statuses = []
        for category, limit in self.limits.items():
            spent = spent_by_category.get(category, 0.0)
            statuses.append(BudgetStatus(category=category, limit=limit, spent=spent))
        return sorted(statuses, key=lambda s: -s.percent_used)
