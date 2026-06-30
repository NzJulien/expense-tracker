from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="expensetracker",
    version="1.0.0",
    description="A dependency-free personal expense tracker with budgets, CLI, and CSV export.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NzJulien",
    url="https://github.com/NzJulien/expense-tracker",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.9",
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "expensetracker=expensetracker.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Office/Business :: Financial",
    ],
)
