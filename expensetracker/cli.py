"""Command-line interface for expensetracker.

Usage:
    expensetracker add 12.50 food "Lunch at cafe"
    expensetracker add 800 rent --date 2025-01-01
    expensetracker list
    expensetracker list --category food
    expensetracker list --month 2025-01
    expensetracker remove a1b2c3d4
    expensetracker summary
    expensetracker summary --month 2025-01
    expensetracker budget set food 300
    expensetracker budget status
    expensetracker export expenses.csv
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

from .budget import BudgetManager
from .csv_export import export_csv
from .tracker import Expense, ExpenseTracker


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{Color.RESET}"


def bar(percent: float, width: int = 20) -> str:
    filled = min(width, round(width * percent / 100))
    return "█" * filled + "░" * (width - filled)


def cmd_add(args: argparse.Namespace) -> int:
    tracker = ExpenseTracker(args.storage)
    try:
        expense = tracker.add(args.amount, args.category, args.description or "", args.date)
    except ValueError as exc:
        print(c(f"Error: {exc}", Color.RED))
        return 1
    print(c(f"Added [{expense.id}] {expense.category}: ${expense.amount:.2f} on {expense.date}", Color.GREEN))
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    tracker = ExpenseTracker(args.storage)
    if tracker.remove(args.id):
        print(c(f"Removed expense {args.id}", Color.GREEN))
        return 0
    print(c(f"No expense found with id {args.id}", Color.RED))
    return 1


def cmd_list(args: argparse.Namespace) -> int:
    tracker = ExpenseTracker(args.storage)
    expenses = tracker.expenses

    if args.category:
        expenses = [e for e in expenses if e.category == args.category.lower()]
    if args.month:
        expenses = [e for e in expenses if e.month_key == args.month]

    if not expenses:
        print(c("No expenses found.", Color.YELLOW))
        return 0

    expenses = sorted(expenses, key=lambda e: e.date)
    print(f"{'ID':<10}{'Date':<12}{'Category':<14}{'Amount':>10}  Description")
    print("-" * 70)
    for e in expenses:
        print(f"{e.id:<10}{e.date:<12}{e.category:<14}{'$'+format(e.amount, '.2f'):>10}  {e.description}")
    print("-" * 70)
    print(c(f"Total: ${tracker.total(expenses):.2f} ({len(expenses)} expenses)", Color.BOLD))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    tracker = ExpenseTracker(args.storage)

    if args.month:
        expenses = tracker.by_month(args.month)
        label = args.month
    else:
        expenses = tracker.expenses
        label = "all time"

    if not expenses:
        print(c(f"No expenses found for {label}.", Color.YELLOW))
        return 0

    print(c(f"\nSummary — {label}", Color.BOLD))
    print("=" * 40)
    print(f"Total spent:      ${tracker.total(expenses):.2f}")
    print(f"Number of items:  {len(expenses)}")

    largest = tracker.largest_expense(expenses)
    if largest:
        print(f"Largest expense:  ${largest.amount:.2f} ({largest.category} — {largest.description or 'no description'})")

    if args.month:
        avg = tracker.average_daily_spend(args.month)
        print(f"Avg per active day: ${avg:.2f}")

    print(c("\nBy category:", Color.BLUE))
    totals = tracker.total_by_category(expenses)
    grand_total = tracker.total(expenses)
    for category, amount in totals.items():
        pct = (amount / grand_total * 100) if grand_total else 0
        print(f"  {category:<14} ${amount:>9.2f}  {bar(pct, 16)} {pct:4.1f}%")

    return 0


def cmd_budget_set(args: argparse.Namespace) -> int:
    budgets = BudgetManager(args.budget_storage)
    try:
        budgets.set_limit(args.category, args.amount)
    except ValueError as exc:
        print(c(f"Error: {exc}", Color.RED))
        return 1
    print(c(f"Set budget for '{args.category}': ${args.amount:.2f}/month", Color.GREEN))
    return 0


def cmd_budget_remove(args: argparse.Namespace) -> int:
    budgets = BudgetManager(args.budget_storage)
    if budgets.remove_limit(args.category):
        print(c(f"Removed budget for '{args.category}'", Color.GREEN))
        return 0
    print(c(f"No budget set for '{args.category}'", Color.RED))
    return 1


def cmd_budget_status(args: argparse.Namespace) -> int:
    tracker = ExpenseTracker(args.storage)
    budgets = BudgetManager(args.budget_storage)
    month = args.month or date.today().isoformat()[:7]

    statuses = budgets.status_for_month(tracker, month)
    if not statuses:
        print(c("No budgets set. Use 'expensetracker budget set <category> <amount>'.", Color.YELLOW))
        return 0

    print(c(f"\nBudget status — {month}", Color.BOLD))
    print("=" * 50)
    exit_code = 0
    for s in statuses:
        color = Color.RED if s.is_over else (Color.YELLOW if s.is_near_limit else Color.GREEN)
        status_label = "OVER" if s.is_over else ("NEAR LIMIT" if s.is_near_limit else "OK")
        print(f"  {s.category:<14} ${s.spent:>8.2f} / ${s.limit:<8.2f} {bar(min(s.percent_used,100), 16)} "
              + c(f"{s.percent_used:5.1f}% {status_label}", color))
        if s.is_over:
            exit_code = 1
    return exit_code


def cmd_export(args: argparse.Namespace) -> int:
    tracker = ExpenseTracker(args.storage)
    expenses = tracker.expenses
    if args.month:
        expenses = tracker.by_month(args.month)
    if not expenses:
        print(c("Nothing to export.", Color.YELLOW))
        return 0
    export_csv(expenses, args.output)
    print(c(f"Exported {len(expenses)} expenses to {args.output}", Color.GREEN))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expensetracker", description="Track expenses, budgets, and spending summaries.")
    parser.add_argument("--storage", default="expenses.json", help="Path to expenses JSON file")
    parser.add_argument("--budget-storage", default="budgets.json", help="Path to budgets JSON file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new expense")
    p_add.add_argument("amount", type=float, help="Expense amount")
    p_add.add_argument("category", help="Category, e.g. food, rent, transport")
    p_add.add_argument("description", nargs="?", default="", help="Optional description")
    p_add.add_argument("--date", help="Date in YYYY-MM-DD (default: today)")
    p_add.set_defaults(func=cmd_add)

    p_remove = sub.add_parser("remove", help="Remove an expense by id")
    p_remove.add_argument("id", help="Expense id")
    p_remove.set_defaults(func=cmd_remove)

    p_list = sub.add_parser("list", help="List expenses")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--month", help="Filter by month, YYYY-MM")
    p_list.set_defaults(func=cmd_list)

    p_summary = sub.add_parser("summary", help="Show a spending summary")
    p_summary.add_argument("--month", help="Limit summary to a single month, YYYY-MM")
    p_summary.set_defaults(func=cmd_summary)

    p_budget = sub.add_parser("budget", help="Manage category budgets")
    budget_sub = p_budget.add_subparsers(dest="budget_command", required=True)

    p_bset = budget_sub.add_parser("set", help="Set a monthly budget for a category")
    p_bset.add_argument("category")
    p_bset.add_argument("amount", type=float)
    p_bset.set_defaults(func=cmd_budget_set)

    p_bremove = budget_sub.add_parser("remove", help="Remove a category's budget")
    p_bremove.add_argument("category")
    p_bremove.set_defaults(func=cmd_budget_remove)

    p_bstatus = budget_sub.add_parser("status", help="Show budget vs. spend for the current or given month")
    p_bstatus.add_argument("--month", help="Month to check, YYYY-MM (default: current month)")
    p_bstatus.set_defaults(func=cmd_budget_status)

    p_export = sub.add_parser("export", help="Export expenses to CSV")
    p_export.add_argument("output", help="Output CSV file path")
    p_export.add_argument("--month", help="Limit export to a single month, YYYY-MM")
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
