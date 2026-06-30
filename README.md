# expense-tracker

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-24%20passing-brightgreen)

**A personal expense tracker for the command line — categories, monthly budgets, spending summaries, and CSV export. Zero runtime dependencies.**

## Why

Spreadsheets are clunky for quick "what did I spend on food this month?"
questions, and most expense-tracking apps want an account, a subscription,
or your data in their cloud. `expensetracker` is a single JSON file on your
own disk and a CLI that's fast to use after the first coffee shop purchase
of the day.

## Install

```bash
git clone https://github.com/NzJulien/expense-tracker.git
cd expense-tracker
pip install -e .
```

## Quick start

```bash
# Log some expenses
expensetracker add 12.50 food "Lunch at cafe"
expensetracker add 45 transport "Monthly metro pass"
expensetracker add 800 rent

# See everything
expensetracker list

# This month's summary, broken down by category
expensetracker summary --month 2025-01
```

```
Summary — 2025-01
========================================
Total spent:      $887.50
Number of items:  4
Largest expense:  $800.00 (rent — no description)
Avg per active day: $221.88

By category:
  rent           $   800.00  ██████████████░░ 90.1%
  transport      $    45.00  █░░░░░░░░░░░░░░░  5.1%
  food           $    42.50  █░░░░░░░░░░░░░░░  4.8%
```

## Budgets

Set a monthly limit per category, then check your status any time:

```bash
expensetracker budget set food 50
expensetracker budget set rent 700
expensetracker budget status --month 2025-01
```

```
Budget status — 2025-01
==================================================
  rent           $  800.00 / $700.00   ████████████████ 114.3% OVER
  food           $   42.50 / $50.00    ██████████████░░  85.0% NEAR LIMIT
```

The command exits with status `1` if any category is over budget — handy
for a daily cron job or a pre-checkout shell hook.

## CSV export

```bash
expensetracker export january.csv --month 2025-01
```

## All commands

| Command | Description |
|---|---|
| `add <amount> <category> [description] [--date YYYY-MM-DD]` | Log a new expense |
| `remove <id>` | Delete an expense by its id |
| `list [--category X] [--month YYYY-MM]` | List expenses, optionally filtered |
| `summary [--month YYYY-MM]` | Totals, largest expense, per-category breakdown |
| `budget set <category> <amount>` | Set a monthly budget limit |
| `budget remove <category>` | Remove a budget limit |
| `budget status [--month YYYY-MM]` | Compare spend vs. budget per category |
| `export <file.csv> [--month YYYY-MM]` | Export expenses to CSV |

Every command accepts `--storage path.json` and `--budget-storage path.json`
to point at a different data file (e.g. separate ledgers per project).

## Library usage

```python
from expensetracker import ExpenseTracker, BudgetManager

tracker = ExpenseTracker("expenses.json")
tracker.add(12.50, "food", "Lunch")

print(tracker.total())                 # 12.5
print(tracker.total_by_category())     # {'food': 12.5}
print(tracker.monthly_summary())       # {'2025-01': 12.5}

budgets = BudgetManager("budgets.json")
budgets.set_limit("food", 200)
for status in budgets.status_for_month(tracker, "2025-01"):
    print(status.category, status.percent_used, status.is_over)
```

## Project layout

```
expense-tracker/
├── expensetracker/
│   ├── tracker.py       # Expense dataclass + ExpenseTracker (storage & queries)
│   ├── budget.py        # BudgetManager + BudgetStatus
│   ├── csv_export.py    # CSV export / import
│   └── cli.py           # argparse CLI: add, remove, list, summary, budget, export
├── tests/                # pytest suite (24 tests)
├── setup.py
└── LICENSE
```

## Running the tests

```bash
pip install -e ".[dev]"
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).

---

Made by [NzJulien](https://github.com/NzJulien)
