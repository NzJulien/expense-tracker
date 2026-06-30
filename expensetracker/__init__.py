"""expensetracker — a small, dependency-free personal expense tracker.

Stores expenses as JSON, supports categories, budgets, monthly summaries,
and CSV export, all through a clean argparse-based CLI.
"""
from .tracker import ExpenseTracker, Expense
from .budget import BudgetManager

__version__ = "1.0.0"
__all__ = ["ExpenseTracker", "Expense", "BudgetManager"]
