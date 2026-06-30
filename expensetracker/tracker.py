"""Core expense data model and storage/query logic."""
from __future__ import annotations

import json
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional


@dataclass
class Expense:
    id: str
    amount: float
    category: str
    description: str
    date: str  # ISO format YYYY-MM-DD

    @classmethod
    def create(cls, amount: float, category: str, description: str = "", on: Optional[str] = None) -> "Expense":
        if amount <= 0:
            raise ValueError("amount must be positive")
        return cls(
            id=uuid.uuid4().hex[:8],
            amount=round(float(amount), 2),
            category=category.strip().lower(),
            description=description.strip(),
            date=on or date.today().isoformat(),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(**data)

    @property
    def month_key(self) -> str:
        """Return YYYY-MM for grouping by month."""
        return self.date[:7]


class ExpenseTracker:
    """Loads, stores, and queries expenses persisted as a JSON file."""

    def __init__(self, storage_path: str | Path = "expenses.json"):
        self.storage_path = Path(storage_path)
        self.expenses: list[Expense] = []
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.expenses = [Expense.from_dict(e) for e in raw]
        else:
            self.expenses = []

    def save(self) -> None:
        data = [e.to_dict() for e in self.expenses]
        self.storage_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def add(self, amount: float, category: str, description: str = "", on: Optional[str] = None) -> Expense:
        expense = Expense.create(amount, category, description, on)
        self.expenses.append(expense)
        self.save()
        return expense

    def remove(self, expense_id: str) -> bool:
        before = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.id != expense_id]
        removed = len(self.expenses) != before
        if removed:
            self.save()
        return removed

    def find(self, expense_id: str) -> Optional[Expense]:
        for e in self.expenses:
            if e.id == expense_id:
                return e
        return None

    # ---- Queries -----------------------------------------------------

    def by_category(self, category: str) -> list[Expense]:
        category = category.strip().lower()
        return [e for e in self.expenses if e.category == category]

    def by_month(self, month: str) -> list[Expense]:
        """month is 'YYYY-MM'."""
        return [e for e in self.expenses if e.month_key == month]

    def by_date_range(self, start: str, end: str) -> list[Expense]:
        return [e for e in self.expenses if start <= e.date <= end]

    def total(self, expenses: Optional[list[Expense]] = None) -> float:
        target = expenses if expenses is not None else self.expenses
        return round(sum(e.amount for e in target), 2)

    def total_by_category(self, expenses: Optional[list[Expense]] = None) -> dict[str, float]:
        target = expenses if expenses is not None else self.expenses
        totals: dict[str, float] = defaultdict(float)
        for e in target:
            totals[e.category] += e.amount
        return {k: round(v, 2) for k, v in sorted(totals.items(), key=lambda kv: -kv[1])}

    def categories(self) -> list[str]:
        return sorted({e.category for e in self.expenses})

    def months(self) -> list[str]:
        return sorted({e.month_key for e in self.expenses})

    def monthly_summary(self) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for e in self.expenses:
            totals[e.month_key] += e.amount
        return {k: round(v, 2) for k, v in sorted(totals.items())}

    def average_daily_spend(self, month: str) -> float:
        month_expenses = self.by_month(month)
        if not month_expenses:
            return 0.0
        days = {e.date for e in month_expenses}
        return round(self.total(month_expenses) / len(days), 2)

    def largest_expense(self, expenses: Optional[list[Expense]] = None) -> Optional[Expense]:
        target = expenses if expenses is not None else self.expenses
        if not target:
            return None
        return max(target, key=lambda e: e.amount)
