from expensetracker.csv_export import export_csv, import_csv
from expensetracker.tracker import Expense, ExpenseTracker


def test_export_csv_creates_file(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food", "lunch", on="2025-01-05")
    tracker.add(20, "rent", on="2025-01-01")

    out = tmp_path / "out.csv"
    export_csv(tracker.expenses, out)

    assert out.exists()
    content = out.read_text()
    assert "food" in content
    assert "rent" in content
    assert "id,date,category,amount,description" in content


def test_export_csv_sorted_by_date(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(10, "food", on="2025-01-20")
    tracker.add(20, "rent", on="2025-01-01")

    out = tmp_path / "out.csv"
    export_csv(tracker.expenses, out)

    lines = out.read_text().strip().split("\n")
    # first data row (after header) should be the earlier date
    assert "2025-01-01" in lines[1]
    assert "2025-01-20" in lines[2]


def test_export_then_import_round_trip(tmp_path):
    tracker = ExpenseTracker(tmp_path / "e.json")
    tracker.add(15.5, "transport", "bus", on="2025-03-01")

    out = tmp_path / "out.csv"
    export_csv(tracker.expenses, out)
    rows = import_csv(out)

    assert len(rows) == 1
    assert rows[0]["category"] == "transport"
    assert rows[0]["amount"] == 15.5
    assert rows[0]["description"] == "bus"
