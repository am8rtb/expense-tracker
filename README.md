# Expense Tracker

Cross-platform expense tracker in Python with both a CLI and a PySide6 (Qt) desktop GUI.

## Features

- Organize expenses by category and description
- Running subtotals per category and a grand total
- GUI: add, edit, and delete entries; save/load to JSON
- CLI: quick terminal-based entry

## Requirements

- Python 3.10+
- PySide6 (for the GUI)

## Installation

```bash
git clone https://github.com/<your-username>/expense-tracker.git
cd expense-tracker
pip install -r requirements.txt
```

## Usage

GUI:
```bash
python3 main_qt.py
```

CLI:
```bash
python3 main.py
```

## Project structure

```
.
├── main.py           # CLI version
├── main_qt.py        # Qt GUI (PySide6)
├── requirements.txt
└── .gitignore
```

## Data

The GUI auto-loads `expenses.json` from the project folder on startup if it exists, and lets you save/load elsewhere via the file dialog. The file is gitignored so your spending data stays local.
