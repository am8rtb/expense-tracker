import sys
import json
from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QDoubleSpinBox, QComboBox,
    QMessageBox, QInputDialog, QFileDialog, QFrame, QScrollArea,
    QDateEdit, QGridLayout,
)

DATA_FILE = Path(__file__).with_name("expenses.json")


STYLESHEET = """
QWidget#Background { background-color: #F5F5F5; }

QFrame#Card {
    background-color: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 14px;
}

QLabel#Caption {
    color: #8A8A8A;
    font-size: 12px;
}
QLabel#Title {
    color: #111111;
    font-size: 26px;
    font-weight: 700;
}
QLabel#FieldLabel {
    color: #1B1B1B;
    font-size: 13px;
    font-weight: 500;
}
QLabel#HintRight {
    color: #8A8A8A;
    font-size: 11px;
}
QLabel#SectionLabel {
    color: #1B1B1B;
    font-size: 14px;
    font-weight: 600;
}
QLabel#TotalValue {
    color: #111111;
    font-size: 14px;
    font-weight: 700;
}

QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #DCDCDC;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 13px;
    min-height: 22px;
    color: #111111;
    selection-background-color: #C7C7C7;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 1px solid #6B6B6B;
}
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #DCDCDC;
    selection-background-color: #F0F0F0;
    selection-color: #111111;
    outline: none;
}

QPushButton#Secondary {
    background-color: #FFFFFF;
    border: 1px solid #D9D9D9;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #1B1B1B;
    min-height: 20px;
}
QPushButton#Secondary:hover { background-color: #F2F2F2; }
QPushButton#Secondary:pressed { background-color: #E8E8E8; }

QPushButton#Primary {
    background-color: #B8B8B8;
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#Primary:hover { background-color: #A4A4A4; }
QPushButton#Primary:pressed { background-color: #909090; }

QFrame#ExpenseCard {
    background-color: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
}
QLabel#ExpenseDesc { font-size: 13px; font-weight: 600; color: #111111; }
QLabel#ExpenseAmount { font-size: 12px; color: #333333; }
QLabel#ExpenseMeta { font-size: 11px; color: #8A8A8A; }

QPushButton#EditLink {
    background: transparent;
    border: none;
    color: #3B6FE0;
    font-size: 12px;
    padding: 0;
}
QPushButton#EditLink:hover { color: #1F4FBF; }

QPushButton#CloseX {
    background: transparent;
    border: none;
    color: #8A8A8A;
    font-size: 16px;
    font-weight: bold;
    padding: 0;
}
QPushButton#CloseX:hover { color: #D64545; }

QLabel#Thumb {
    background-color: #D4D4D4;
    border-radius: 6px;
}

QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #CFCFCF;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class ExpenseCard(QFrame):
    removed = Signal(int)
    edit_requested = Signal(int)

    def __init__(self, index: int, expense: dict):
        super().__init__()
        self.setObjectName("ExpenseCard")
        self.index = index

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        thumb = QLabel()
        thumb.setObjectName("Thumb")
        thumb.setFixedSize(56, 56)
        layout.addWidget(thumb)

        info = QVBoxLayout()
        info.setSpacing(2)
        desc = QLabel(expense.get("description", ""))
        desc.setObjectName("ExpenseDesc")
        amount = QLabel(f"{expense.get('amount', 0):.2f} {expense.get('currency', 'USD')}")
        amount.setObjectName("ExpenseAmount")
        meta = QLabel(f"{expense.get('date', '')} \u00b7 {expense.get('category', '')}")
        meta.setObjectName("ExpenseMeta")
        info.addWidget(desc)
        info.addWidget(amount)
        info.addWidget(meta)
        info.addStretch(1)
        layout.addLayout(info, 1)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        close_btn = QPushButton("\u00d7")
        close_btn.setObjectName("CloseX")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(lambda: self.removed.emit(self.index))
        right.addWidget(close_btn, 0, Qt.AlignRight)
        right.addStretch(1)
        edit_btn = QPushButton("Edit Expense")
        edit_btn.setObjectName("EditLink")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.index))
        right.addWidget(edit_btn, 0, Qt.AlignRight)
        layout.addLayout(right)


class ExpenseTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense tracker")
        self.resize(560, 780)

        self.categories: list[str] = []
        self.expenses: list[dict] = []
        self.currency = "USD"

        bg = QWidget()
        bg.setObjectName("Background")
        self.setCentralWidget(bg)

        outer = QVBoxLayout(bg)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(14)

        caption = QLabel("Create expense report")
        caption.setObjectName("Caption")
        caption.setAlignment(Qt.AlignHCenter)
        outer.addWidget(caption)

        title = QLabel("Expense tracker")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignHCenter)
        outer.addWidget(title)
        outer.addSpacing(4)

        outer.addWidget(self._build_form_card())
        outer.addWidget(self._build_list_card(), 1)
        outer.addLayout(self._build_buttons())

        self.setStyleSheet(STYLESHEET)

        if DATA_FILE.exists():
            self.load(path=DATA_FILE, silent=True)
        self.refresh()

    def _build_form_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        cat_row = QHBoxLayout()
        cat_label = QLabel("Choose Category")
        cat_label.setObjectName("FieldLabel")
        cat_row.addWidget(cat_label)
        cat_row.addStretch(1)
        self.cat_hint = QLabel("Number of Categories: 0")
        self.cat_hint.setObjectName("HintRight")
        cat_row.addWidget(self.cat_hint)
        lay.addLayout(cat_row)

        self.category_box = QComboBox()
        lay.addWidget(self.category_box)

        desc_label = QLabel("Description")
        desc_label.setObjectName("FieldLabel")
        lay.addWidget(desc_label)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("e.g. Boots")
        lay.addWidget(self.description_edit)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(4)
        amt_label = QLabel("Amount")
        amt_label.setObjectName("FieldLabel")
        date_label = QLabel("Date")
        date_label.setObjectName("FieldLabel")
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMaximum(1_000_000_000)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$ ")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())
        grid.addWidget(amt_label, 0, 0)
        grid.addWidget(date_label, 0, 1)
        grid.addWidget(self.amount_spin, 1, 0)
        grid.addWidget(self.date_edit, 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)

        return card

    def _build_list_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(8)

        header = QHBoxLayout()
        label = QLabel("Total Amount:")
        label.setObjectName("SectionLabel")
        self.total_label = QLabel("$0.00")
        self.total_label.setObjectName("TotalValue")
        header.addWidget(label)
        header.addStretch(1)
        header.addWidget(self.total_label)
        lay.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_host = QWidget()
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch(1)
        self.scroll.setWidget(self.list_host)
        lay.addWidget(self.scroll, 1)

        return card

    def _build_buttons(self) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(8)

        self.new_cat_btn = QPushButton("ADD new category")
        self.new_cat_btn.setObjectName("Secondary")
        self.new_cat_btn.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.new_cat_btn)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.add_btn = QPushButton("Add Expense")
        self.add_btn.setObjectName("Secondary")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("Secondary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.add_btn)
        row.addWidget(self.save_btn)
        lay.addLayout(row)

        self.submit_btn = QPushButton("Submit Expense Report")
        self.submit_btn.setObjectName("Primary")
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.submit_btn)

        self.new_cat_btn.clicked.connect(self.new_category)
        self.add_btn.clicked.connect(self.add_expense)
        self.save_btn.clicked.connect(self.save)
        self.submit_btn.clicked.connect(self.submit)
        return lay

    def add_expense(self):
        cat = self.category_box.currentText().strip()
        if not cat:
            QMessageBox.warning(self, "Missing category",
                                "Create a category first.")
            return
        desc = self.description_edit.text().strip() or "(no description)"
        amount = float(self.amount_spin.value())
        if amount <= 0:
            QMessageBox.warning(self, "Invalid amount",
                                "Amount must be greater than zero.")
            return

        self.expenses.append({
            "category": cat,
            "description": desc,
            "amount": amount,
            "currency": self.currency,
            "date": self.date_edit.date().toString("dd/MM/yyyy"),
        })

        self.description_edit.clear()
        self.amount_spin.setValue(0)
        self.refresh()

    def new_category(self):
        name, ok = QInputDialog.getText(self, "New category",
                                        "Category name:")
        name = name.strip()
        if not ok or not name:
            return
        if name in self.categories:
            QMessageBox.information(self, "Exists",
                                    "Category already exists.")
            return
        self.categories.append(name)
        self.refresh()
        self.category_box.setCurrentText(name)

    def remove_expense(self, index: int):
        if 0 <= index < len(self.expenses):
            self.expenses.pop(index)
            self.refresh()

    def edit_expense(self, index: int):
        if not (0 <= index < len(self.expenses)):
            return
        exp = self.expenses[index]
        new_desc, ok = QInputDialog.getText(
            self, "Edit description", "Description:", text=exp["description"])
        if not ok:
            return
        new_amount, ok = QInputDialog.getDouble(
            self, "Edit amount", "Amount:", exp["amount"], 0, 1_000_000_000, 2)
        if not ok:
            return
        exp["description"] = new_desc.strip() or exp["description"]
        exp["amount"] = float(new_amount)
        self.refresh()

    def save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save expenses", str(DATA_FILE), "JSON (*.json)")
        if not path:
            return
        payload = {
            "categories": self.categories,
            "expenses": self.expenses,
        }
        Path(path).write_text(json.dumps(payload, indent=2))
        QMessageBox.information(self, "Saved", f"Saved to {path}")

    def submit(self):
        if not self.expenses:
            QMessageBox.information(self, "Nothing to submit",
                                    "Add at least one expense first.")
            return
        total = sum(e["amount"] for e in self.expenses)
        QMessageBox.information(
            self, "Report submitted",
            f"Submitted {len(self.expenses)} expenses totalling ${total:,.2f}.")

    def load(self, *, path: Path | None = None, silent: bool = False):
        if path is None:
            chosen, _ = QFileDialog.getOpenFileName(
                self, "Load expenses", str(DATA_FILE), "JSON (*.json)")
            if not chosen:
                return
            path = Path(chosen)
        try:
            data = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            if not silent:
                QMessageBox.critical(self, "Load failed", str(exc))
            return

        if isinstance(data, dict) and "expenses" in data:
            self.categories = list(data.get("categories", []))
            self.expenses = list(data.get("expenses", []))
        elif isinstance(data, dict):
            self.categories = sorted(data.keys())
            today = date.today().strftime("%d/%m/%Y")
            self.expenses = [
                {"category": cat, "description": desc, "amount": amt,
                 "currency": self.currency, "date": today}
                for cat, items in data.items()
                for desc, amt in items.items()
            ]
        else:
            if not silent:
                QMessageBox.critical(self, "Load failed", "Unknown format.")
            return
        self.refresh()

    def refresh(self):
        current_cat = self.category_box.currentText()
        self.category_box.blockSignals(True)
        self.category_box.clear()
        self.category_box.addItems(self.categories)
        if current_cat in self.categories:
            self.category_box.setCurrentText(current_cat)
        self.category_box.blockSignals(False)
        self.cat_hint.setText(f"Number of Categories: {len(self.categories)}")

        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        total = 0.0
        for i, exp in enumerate(self.expenses):
            total += float(exp.get("amount", 0))
            card = ExpenseCard(i, exp)
            card.removed.connect(self.remove_expense)
            card.edit_requested.connect(self.edit_expense)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

        self.total_label.setText(f"${total:,.2f}")


def main():
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
