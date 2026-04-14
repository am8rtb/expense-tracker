import sys
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QDoubleSpinBox, QComboBox,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QInputDialog, QFileDialog,
)

DATA_FILE = Path(__file__).with_name("expenses.json")


class ExpenseTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.resize(640, 480)
        self.expenses: dict[str, dict[str, float]] = {}

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        form = QHBoxLayout()
        self.category_box = QComboBox()
        self.category_box.setEditable(False)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Description")
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMaximum(1_000_000_000)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$ ")

        form.addWidget(QLabel("Category:"))
        form.addWidget(self.category_box, 1)
        form.addWidget(QLabel("Description:"))
        form.addWidget(self.description_edit, 2)
        form.addWidget(QLabel("Amount:"))
        form.addWidget(self.amount_spin, 1)
        root.addLayout(form)

        buttons = QHBoxLayout()
        self.add_btn = QPushButton("Add Expense")
        self.new_cat_btn = QPushButton("New Category")
        self.delete_btn = QPushButton("Delete Selected")
        self.save_btn = QPushButton("Save")
        self.load_btn = QPushButton("Load")
        for b in (self.add_btn, self.new_cat_btn, self.delete_btn,
                  self.save_btn, self.load_btn):
            buttons.addWidget(b)
        root.addLayout(buttons)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Category / Description", "Amount"])
        self.tree.setColumnWidth(0, 380)
        root.addWidget(self.tree, 1)

        self.total_label = QLabel("Total: $0.00")
        font = self.total_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.total_label.setFont(font)
        self.total_label.setAlignment(Qt.AlignRight)
        root.addWidget(self.total_label)

        self.add_btn.clicked.connect(self.add_expense)
        self.new_cat_btn.clicked.connect(self.new_category)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.save_btn.clicked.connect(self.save)
        self.load_btn.clicked.connect(self.load)

        if DATA_FILE.exists():
            self.load(path=DATA_FILE, silent=True)
        self.refresh()

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

        bucket = self.expenses.setdefault(cat, {})
        bucket[desc] = bucket.get(desc, 0.0) + amount

        self.description_edit.clear()
        self.amount_spin.setValue(0)
        self.refresh()

    def new_category(self):
        name, ok = QInputDialog.getText(self, "New category",
                                        "Category name:")
        name = name.strip()
        if not ok or not name:
            return
        if name in self.expenses:
            QMessageBox.information(self, "Exists",
                                    "Category already exists.")
            return
        self.expenses[name] = {}
        self.refresh()
        self.category_box.setCurrentText(name)

    def delete_selected(self):
        item = self.tree.currentItem()
        if item is None:
            return
        parent = item.parent()
        if parent is None:
            cat = item.text(0)
            if QMessageBox.question(self, "Delete category",
                                    f"Delete category '{cat}' and all its expenses?"
                                    ) == QMessageBox.Yes:
                self.expenses.pop(cat, None)
        else:
            cat = parent.text(0)
            desc = item.text(0)
            self.expenses.get(cat, {}).pop(desc, None)
        self.refresh()

    def save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save expenses", str(DATA_FILE), "JSON (*.json)")
        if not path:
            return
        Path(path).write_text(json.dumps(self.expenses, indent=2))
        QMessageBox.information(self, "Saved", f"Saved to {path}")

    def load(self, *, path: Path | None = None, silent: bool = False):
        if path is None:
            chosen, _ = QFileDialog.getOpenFileName(
                self, "Load expenses", str(DATA_FILE), "JSON (*.json)")
            if not chosen:
                return
            path = Path(chosen)
        try:
            self.expenses = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            if not silent:
                QMessageBox.critical(self, "Load failed", str(exc))
            return
        self.refresh()

    def refresh(self):
        current_cat = self.category_box.currentText()
        self.category_box.blockSignals(True)
        self.category_box.clear()
        self.category_box.addItems(sorted(self.expenses.keys()))
        if current_cat in self.expenses:
            self.category_box.setCurrentText(current_cat)
        self.category_box.blockSignals(False)

        self.tree.clear()
        total = 0.0
        for cat in sorted(self.expenses):
            subtotal = sum(self.expenses[cat].values())
            total += subtotal
            cat_item = QTreeWidgetItem([cat, f"${subtotal:.2f}"])
            for desc, amt in self.expenses[cat].items():
                cat_item.addChild(QTreeWidgetItem([desc, f"${amt:.2f}"]))
            self.tree.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)
        self.total_label.setText(f"Total: ${total:.2f}")


def main():
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
