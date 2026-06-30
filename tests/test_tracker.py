import pytest
from expensetracker.tracker import Expense, ExpenseTracker


def test_create_expense_normalizes_category():
    e = Expense.create(12.5, "  Food ", "Lunch")
    assert e.category == "food"
    assert e.amount == 12.5


def test_create_expense_rejects_non_positive_amount():
    with pytest.raises(ValueError):
        Expense.create(0, "food")
    with pytest.raises(ValueError):
        Expense.create(-5, "food")


def test_expense_round_trip_dict():
    e = Expense.create(9.99, "transport", "bus pass")
    restored = Expense.from_dict(e.to_dict())
    assert restored == e


def test_tracker_add_and_persist(tmp_path):
    path = tmp_path / "expenses.json"
    tracker = ExpenseTracker(path)
    tracker.add(20, "food", "groceries")
    tracker.add(50, "rent")

    reloaded = ExpenseTracker(path)
    assert len(reloaded.expenses) == 2
    assert reloaded.total() == 70.0


def test_tracker_remove(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    e = tracker.add(10, "food")
    assert tracker.remove(e.id) is True
    assert tracker.remove(e.id) is False
    assert len(tracker.expenses) == 0


def test_by_category_is_case_insensitive(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "Food")
    tracker.add(5, "food")
    tracker.add(8, "rent")
    assert len(tracker.by_category("FOOD")) == 2


def test_by_month(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food", on="2025-01-15")
    tracker.add(20, "food", on="2025-02-01")
    assert tracker.total(tracker.by_month("2025-01")) == 10
    assert tracker.total(tracker.by_month("2025-02")) == 20


def test_total_by_category_sorted_descending(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food")
    tracker.add(50, "rent")
    tracker.add(5, "transport")
    totals = tracker.total_by_category()
    assert list(totals.keys()) == ["rent", "food", "transport"]


def test_monthly_summary(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food", on="2025-01-05")
    tracker.add(15, "food", on="2025-01-20")
    tracker.add(30, "rent", on="2025-02-01")
    summary = tracker.monthly_summary()
    assert summary == {"2025-01": 25.0, "2025-02": 30.0}


def test_average_daily_spend(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food", on="2025-01-01")
    tracker.add(10, "food", on="2025-01-01")  # same day
    tracker.add(20, "food", on="2025-01-02")
    # 2 unique days, total 40 -> avg 20
    assert tracker.average_daily_spend("2025-01") == 20.0


def test_largest_expense(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(5, "food")
    big = tracker.add(500, "rent")
    assert tracker.largest_expense() == big


def test_largest_expense_empty(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    assert tracker.largest_expense() is None


def test_categories_and_months(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food", on="2025-01-01")
    tracker.add(10, "rent", on="2025-02-01")
    assert tracker.categories() == ["food", "rent"]
    assert tracker.months() == ["2025-01", "2025-02"]
