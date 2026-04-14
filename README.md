# Expense Tracker

A lightweight, cross-platform expense tracker written in Python. Ships with two interfaces:

- **Qt GUI** — a clean, card-based desktop app built with PySide6, designed to match a Figma mock
- **CLI** — a minimal terminal version for quick entry

The GUI can also be bundled into a native macOS `.app` so you can launch it by double-clicking.

---

## Screenshots

The GUI features a light theme, rounded cards, and stacked expense entries with date, category, and inline edit/delete actions. See `main_qt.py` for the layout.

---

## Requirements

- **Python** 3.10 or newer
- **PySide6** (installed via `requirements.txt`) — only needed for the GUI
- macOS, Windows, or Linux (the GUI is cross-platform; the `.app` bundle step is macOS-only)

---

## Installation

```bash
git clone git@github.com:am8rtb/expense-tracker.git
cd expense-tracker
pip install -r requirements.txt
```

If you prefer a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running the app

### GUI (recommended)

```bash
python3 main_qt.py
```

### CLI

```bash
python3 main.py
```

---

## Using the GUI

The window is laid out top-to-bottom:

1. **Title header** — "Expense tracker" with a small "Create expense report" caption.
2. **Form card** — where you enter a new expense:
   - **Choose Category** — dropdown of existing categories (shows `Number of Categories: N` on the right)
   - **Description** — free text (e.g. *Boots*)
   - **Amount** — a currency spin box
   - **Date** — a date picker (defaults to today, `dd/MM/yyyy` format)
3. **Total Amount card** — shows the running grand total at the top, followed by a scrollable list of expense cards. Each card displays the description, amount, date, and category, with:
   - `×` button in the top-right to delete
   - **Edit Expense** link in the bottom-right to rename / change amount
4. **Action buttons**:
   - **ADD new category** — prompts for a new category name
   - **Add Expense** — commits the form contents to the list
   - **Save** — writes the current state to a JSON file of your choice
   - **Submit Expense Report** — shows a summary (count + total) of everything in the list

### Typical flow

1. Click **ADD new category** and name one (e.g. *Travel*).
2. Select it in the **Choose Category** dropdown.
3. Fill in **Description**, **Amount**, and **Date**.
4. Click **Add Expense** — it appears as a card in the list.
5. Repeat for more entries. Use the `×` and **Edit Expense** controls on each card as needed.
6. Click **Save** to write to `expenses.json`. The app auto-loads this file on next launch if it sits next to `main_qt.py`.

### Data format

Saved files are plain JSON:

```json
{
  "categories": ["Travel", "Food"],
  "expenses": [
    {
      "category": "Travel",
      "description": "Boots",
      "amount": 200.0,
      "currency": "USD",
      "date": "12/12/2022"
    }
  ]
}
```

Older save files that used the flat `{ "category": { "description": amount } }` shape from the CLI are still loaded and migrated automatically.

---

## Using the CLI

Run `python3 main.py` and follow the prompts. You can create categories, add expenses, display totals, and save/load JSON — all from the terminal. It's designed for quick one-off entries when the GUI is overkill.

---

## Bundling a macOS `.app` (optional)

If you want to double-click to launch the GUI:

```bash
pip install pyinstaller
pyinstaller --windowed --noconfirm \
  --name "Expense Tracker" \
  --osx-bundle-identifier com.amir.expensetracker \
  main_qt.py
```

The bundle will appear at `dist/Expense Tracker.app`. Drag it into `/Applications` or keep it on your Desktop.

- First launch may show a Gatekeeper warning (the app is unsigned). Right-click → **Open** once to bypass.
- The `build/`, `dist/`, and `*.spec` artifacts are git-ignored.

---

## Project structure

```
.
├── main.py              # CLI version
├── main_qt.py           # Qt GUI (PySide6)
├── requirements.txt     # Python dependencies
├── README.md
└── .gitignore
```

---

## Privacy

Your expense data (`expenses.json`) is git-ignored so it never leaves your machine.
