import pytest
from expensetracker.budget import BudgetManager
from expensetracker.tracker import ExpenseTracker


def test_set_and_get_limit(tmp_path):
    budgets = BudgetManager(tmp_path / "b.json")
    budgets.set_limit("Food", 300)
    assert budgets.get_limit("food") == 300.0


def test_set_limit_rejects_negative(tmp_path):
    budgets = BudgetManager(tmp_path / "b.json")
    with pytest.raises(ValueError):
        budgets.set_limit("food", -10)


def test_remove_limit(tmp_path):
    budgets = BudgetManager(tmp_path / "b.json")
    budgets.set_limit("food", 100)
    assert budgets.remove_limit("food") is True
    assert budgets.remove_limit("food") is False
    assert budgets.get_limit("food") is None


def test_persists_across_instances(tmp_path):
    path = tmp_path / "b.json"
    BudgetManager(path).set_limit("rent", 800)
    reloaded = BudgetManager(path)
    assert reloaded.get_limit("rent") == 800.0


def test_status_for_month_under_budget(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(50, "food", on="2025-01-10")

    budgets = BudgetManager(tmp_path / "b.json")
    budgets.set_limit("food", 200)

    statuses = budgets.status_for_month(tracker, "2025-01")
    assert len(statuses) == 1
    s = statuses[0]
    assert s.spent == 50
    assert s.remaining == 150
    assert s.is_over is False
    assert s.is_near_limit is False


def test_status_for_month_over_budget(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(250, "food", on="2025-01-10")

    budgets = BudgetManager(tmp_path / "b.json")
    budgets.set_limit("food", 200)

    s = budgets.status_for_month(tracker, "2025-01")[0]
    assert s.is_over is True
    assert s.remaining == -50
    assert s.percent_used == 125.0


def test_status_near_limit(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(85, "food", on="2025-01-10")

    budgets = BudgetManager(tmp_path / "b.json")
    budgets.set_limit("food", 100)

    s = budgets.status_for_month(tracker, "2025-01")[0]
    assert s.is_near_limit is True
    assert s.is_over is False


def test_status_excludes_unbudgeted_categories(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "transport", on="2025-01-01")

    budgets = BudgetManager(tmp_path / "b.json")
    budgets.set_limit("food", 100)

    statuses = budgets.status_for_month(tracker, "2025-01")
    assert len(statuses) == 1
    assert statuses[0].category == "food"
    assert statuses[0].spent == 0
