import sys
from pathlib import Path
from typing import List, Optional

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from models import (
    CartItem,
    Clothing,
    Customer,
    Electronics,
    Furniture,
    Order,
    OrderStatus,
    Payment,
    PaymentStatus,
    Product,
    ShoppingCart,
    Storage,
    StoreManager,
)

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"


# ---------- Table models ----------
class ProductTableModel(QAbstractTableModel):
    HEADERS = ["Name", "Category", "Price", "Stock", "Manufacturer", "Discounted"]

    def __init__(self, products: List[Product]) -> None:
        super().__init__()
        self._products = products

    def rowCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self._products)

    def columnCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        product = self._products[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return product.name
            if col == 1:
                return product.category
            if col == 2:
                return f"{product.price:.2f}"
            if col == 3:
                return product.stock
            if col == 4:
                return product.manufacturer
            if col == 5:
                return f"{product.discount_price():.2f}"
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return section + 1

    def add_product(self, product: Product) -> None:
        self.beginInsertRows(QModelIndex(), len(self._products), len(self._products))
        self._products.append(product)
        self.endInsertRows()

    def update_product(self, row: int, product: Product) -> None:
        if 0 <= row < len(self._products):
            self._products[row] = product
            left = self.index(row, 0)
            right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(left, right, [Qt.DisplayRole])

    def remove_product(self, row: int) -> None:
        if 0 <= row < len(self._products):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._products[row]
            self.endRemoveRows()

    def product_at(self, row: int) -> Product:
        return self._products[row]

    def all_products(self) -> List[Product]:
        return list(self._products)


class CartTableModel(QAbstractTableModel):
    HEADERS = ["Name", "Qty", "Subtotal"]

    def __init__(self, cart: ShoppingCart) -> None:
        super().__init__()
        self.cart = cart

    def rowCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self.cart.all_items())

    def columnCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        items = self.cart.all_items()
        item = items[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return item.product.name
            if col == 1:
                return item.quantity
            if col == 2:
                return f"{item.subtotal():.2f}"
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return section + 1

    def refresh(self) -> None:
        left = self.index(0, 0)
        right = self.index(max(0, self.rowCount() - 1), self.columnCount() - 1)
        self.dataChanged.emit(left, right, [Qt.DisplayRole])
        self.layoutChanged.emit()


# ---------- Dialogs ----------
class ProductDialog(QDialog):
    def __init__(self, parent: QWidget = None, product: Optional[Product] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Product")
        self.selected_category = "Electronics"

        self.name_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Electronics", "Clothing", "Furniture"])
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1_000_000)
        self.price_spin.setDecimals(2)
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 10_000)
        self.mfr_edit = QLineEdit()

        # Category-specific controls
        self.warranty_spin = QSpinBox()
        self.warranty_spin.setRange(0, 10)
        self.wifi_check = QCheckBox("Wi-Fi enabled")

        self.size_combo = QComboBox()
        self.size_combo.addItems(["XS", "S", "M", "L", "XL"])
        self.material_edit = QLineEdit()

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 1000)
        self.weight_spin.setDecimals(2)
        self.assembled_check = QCheckBox("Delivered assembled")

        # Radio buttons to choose delivery option (fulfills RadioButton requirement)
        self.delivery_standard = QRadioButton("Standard delivery")
        self.delivery_express = QRadioButton("Express delivery")
        self.delivery_standard.setChecked(True)

        form = QFormLayout()
        form.addRow("Name:", self.name_edit)
        form.addRow("Category:", self.category_combo)
        form.addRow("Price:", self.price_spin)
        form.addRow("Stock:", self.stock_spin)
        form.addRow("Manufacturer:", self.mfr_edit)
        form.addRow("Warranty (years):", self.warranty_spin)
        form.addRow("", self.wifi_check)
        form.addRow("Size:", self.size_combo)
        form.addRow("Material:", self.material_edit)
        form.addRow("Weight (kg):", self.weight_spin)
        form.addRow("", self.assembled_check)
        form.addRow("Delivery:", self.delivery_standard)
        form.addRow("", self.delivery_express)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.setLayout(form)
        self.category_combo.currentTextChanged.connect(self.on_category_change)
        self.on_category_change(self.category_combo.currentText())

        if product:
            self.fill_from_product(product)

    def on_category_change(self, category: str) -> None:
        self.selected_category = category
        # Show/hide relevant controls
        is_electronics = category == "Electronics"
        is_clothing = category == "Clothing"
        is_furniture = category == "Furniture"
        self.warranty_spin.setEnabled(is_electronics)
        self.wifi_check.setEnabled(is_electronics)
        self.size_combo.setEnabled(is_clothing)
        self.material_edit.setEnabled(is_clothing)
        self.weight_spin.setEnabled(is_furniture)
        self.assembled_check.setEnabled(is_furniture)

    def fill_from_product(self, product: Product) -> None:
        self.name_edit.setText(product.name)
        self.category_combo.setCurrentText(product.category)
        self.price_spin.setValue(product.price)
        self.stock_spin.setValue(product.stock)
        self.mfr_edit.setText(product.manufacturer)
        if isinstance(product, Electronics):
            self.warranty_spin.setValue(product.warranty_years)
            self.wifi_check.setChecked(product.has_wifi)
        if isinstance(product, Clothing):
            self.size_combo.setCurrentText(product.size)
            self.material_edit.setText(product.material)
        if isinstance(product, Furniture):
            self.weight_spin.setValue(product.weight)
            self.assembled_check.setChecked(product.assembled)

    def build_product(self) -> Product:
        name = self.name_edit.text().strip()
        if not name:
            raise ValueError("Name is required")
        mfr = self.mfr_edit.text().strip() or "Unknown"
        price = self.price_spin.value()
        stock = self.stock_spin.value()
        category = self.selected_category
        if category == "Electronics":
            return Electronics(
                name=name,
                category=category,
                price=price,
                stock=stock,
                manufacturer=mfr,
                warranty_years=self.warranty_spin.value(),
                has_wifi=self.wifi_check.isChecked(),
            )
        if category == "Clothing":
            return Clothing(
                name=name,
                category=category,
                price=price,
                stock=stock,
                manufacturer=mfr,
                size=self.size_combo.currentText(),
                material=self.material_edit.text().strip() or "Cotton",
            )
        return Furniture(
            name=name,
            category=category,
            price=price,
            stock=stock,
            manufacturer=mfr,
            weight=self.weight_spin.value(),
            assembled=self.assembled_check.isChecked(),
        )


class CheckoutDialog(QDialog):
    """Dialog uses TextBox, ComboBox, CheckBox, RadioButton as required."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Checkout")
        self.name_edit = QLineEdit()
        self.contact_edit = QLineEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems([OrderStatus.NEW, OrderStatus.PAID, OrderStatus.SHIPPED])
        self.express_check = QCheckBox("Express shipping")
        self.cash_radio = QRadioButton("Cash")
        self.card_radio = QRadioButton("Card")
        self.card_radio.setChecked(True)

        form = QFormLayout()
        form.addRow("Customer name:", self.name_edit)
        form.addRow("Contact info:", self.contact_edit)
        form.addRow("Initial status:", self.status_combo)
        form.addRow("Shipping:", self.express_check)
        form.addRow("Payment:", self.card_radio)
        form.addRow("", self.cash_radio)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.setLayout(form)

    def build_customer(self) -> Customer:
        name = self.name_edit.text().strip() or "Guest"
        contact = self.contact_edit.text().strip()
        return Customer(full_name=name, contact=contact)

    def payment_method(self) -> str:
        return "Card" if self.card_radio.isChecked() else "Cash"

    def initial_status(self) -> str:
        return self.status_combo.currentText()

    def express(self) -> bool:
        return self.express_check.isChecked()


# ---------- Main window ----------
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Online Store (PyQt)")
        self.resize(1100, 700)

        self.manager = StoreManager()
        self.cart = ShoppingCart()
        self.storage = Storage(DATA_DIR)

        for sample in self._default_products():
            self.manager.add_product(sample)

        self.product_model = ProductTableModel(self.manager.products())
        self.cart_model = CartTableModel(self.cart)

        self._init_ui()
        self._refresh_totals()

    def _init_ui(self) -> None:
        central = QWidget()
        main_layout = QHBoxLayout()

        # Product table and controls
        table_group = QVBoxLayout()
        self.table = QTableView()
        self.table.setModel(self.product_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_group.addWidget(self.table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add")
        edit_btn = QPushButton("Edit")
        del_btn = QPushButton("Delete")
        add_cart_btn = QPushButton("Add to cart")
        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        btn_row.addWidget(add_cart_btn)

        add_btn.clicked.connect(self.on_add)
        edit_btn.clicked.connect(self.on_edit)
        del_btn.clicked.connect(self.on_delete)
        add_cart_btn.clicked.connect(self.on_add_to_cart)
        table_group.addLayout(btn_row)

        # Cart and checkout
        side_group = QVBoxLayout()
        cart_box = QGroupBox("Cart")
        cart_layout = QVBoxLayout()
        self.cart_table = QTableView()
        self.cart_table.setModel(self.cart_model)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cart_layout.addWidget(self.cart_table)
        self.total_label = QLabel("Total: 0.00")
        cart_layout.addWidget(self.total_label)
        cart_box.setLayout(cart_layout)
        side_group.addWidget(cart_box)

        order_btn = QPushButton("Place order")
        clear_cart_btn = QPushButton("Clear cart")
        side_group.addWidget(order_btn)
        side_group.addWidget(clear_cart_btn)
        order_btn.clicked.connect(self.on_checkout)
        clear_cart_btn.clicked.connect(self.on_clear_cart)

        # Reports / history
        report_box = QGroupBox("Reports")
        report_layout = QVBoxLayout()
        self.report_list = QListWidget()
        report_layout.addWidget(self.report_list)
        gen_report_btn = QPushButton("Generate sales report")
        report_layout.addWidget(gen_report_btn)
        gen_report_btn.clicked.connect(self.on_generate_report)
        report_box.setLayout(report_layout)
        side_group.addWidget(report_box)

        # Persistence buttons
        save_json_btn = QPushButton("Save JSON")
        load_json_btn = QPushButton("Load JSON")
        save_bin_btn = QPushButton("Save Binary")
        load_bin_btn = QPushButton("Load Binary")
        save_xml_btn = QPushButton("Save XML")
        load_xml_btn = QPushButton("Load XML")

        persist_layout = QGridLayout()
        persist_layout.addWidget(save_json_btn, 0, 0)
        persist_layout.addWidget(load_json_btn, 0, 1)
        persist_layout.addWidget(save_bin_btn, 1, 0)
        persist_layout.addWidget(load_bin_btn, 1, 1)
        persist_layout.addWidget(save_xml_btn, 2, 0)
        persist_layout.addWidget(load_xml_btn, 2, 1)
        side_group.addLayout(persist_layout)

        save_json_btn.clicked.connect(lambda: self.on_save("store.json", mode="json"))
        load_json_btn.clicked.connect(lambda: self.on_load("store.json", mode="json"))
        save_bin_btn.clicked.connect(lambda: self.on_save("store.bin", mode="bin"))
        load_bin_btn.clicked.connect(lambda: self.on_load("store.bin", mode="bin"))
        save_xml_btn.clicked.connect(lambda: self.on_save("store.xml", mode="xml"))
        load_xml_btn.clicked.connect(lambda: self.on_load("store.xml", mode="xml"))

        main_layout.addLayout(table_group, 3)
        main_layout.addLayout(side_group, 2)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def _default_products(self) -> List[Product]:
        return [
            Electronics("Laptop", "Electronics", 1200.0, 5, "TechCorp", 2, True),
            Clothing("Jacket", "Clothing", 150.0, 20, "Warm&Co", "L", "Wool"),
            Furniture("Desk", "Furniture", 300.0, 10, "Furni", 55.0, False),
        ]

    # ---- UI actions ----
    def selected_row(self) -> Optional[int]:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return rows[0].row()

    def on_add(self) -> None:
        dlg = ProductDialog(self)
        if dlg.exec_():
            try:
                product = dlg.build_product()
                self.manager.add_product(product)
                self.product_model.add_product(product)
            except Exception as ex:
                QMessageBox.warning(self, "Validation error", str(ex))

    def on_edit(self) -> None:
        row = self.selected_row()
        if row is None:
            QMessageBox.information(self, "Select product", "Select a product to edit.")
            return
        product = self.product_model.product_at(row)
        dlg = ProductDialog(self, product=product)
        if dlg.exec_():
            try:
                updated = dlg.build_product()
                self.manager.update_product(row, updated)
                self.product_model.update_product(row, updated)
            except Exception as ex:
                QMessageBox.warning(self, "Validation error", str(ex))

    def on_delete(self) -> None:
        row = self.selected_row()
        if row is None:
            QMessageBox.information(self, "Select product", "Select a product to delete.")
            return
        if QMessageBox.question(self, "Delete", "Remove selected product?") == QMessageBox.Yes:
            self.manager.delete_product(row)
            self.product_model.remove_product(row)

    def on_add_to_cart(self) -> None:
        row = self.selected_row()
        if row is None:
            QMessageBox.information(self, "Select product", "Select a product to add to cart.")
            return
        product = self.product_model.product_at(row)
        try:
            product.purchase(1)
            self.cart.add_item(product, 1)
            self.product_model.dataChanged.emit(self.product_model.index(row, 0), self.product_model.index(row, self.product_model.columnCount() - 1))
            self.cart_model.refresh()
            self._refresh_totals()
        except Exception as ex:
            QMessageBox.warning(self, "Cannot add", str(ex))

    def on_clear_cart(self) -> None:
        self.cart.clear()
        self.cart_model.refresh()
        self._refresh_totals()

    def on_checkout(self) -> None:
        if not self.cart.all_items():
            QMessageBox.information(self, "Cart empty", "Add items to cart first.")
            return
        dlg = CheckoutDialog(self)
        if not dlg.exec_():
            return
        customer = dlg.build_customer()
        order = Order(customer=customer, items=self.cart.all_items(), status=dlg.initial_status())
        payment = Payment(amount=order.total_amount(), method=dlg.payment_method(), status=PaymentStatus.COMPLETED)
        fee = payment.calculate_fee(order.total_amount())
        payment.amount += fee
        order.mark_paid(payment)
        self.manager.record_order(order)
        self.cart.clear()
        self.cart_model.refresh()
        self._refresh_totals()
        QMessageBox.information(self, "Order created", f"Total with fee: {payment.amount:.2f}")

    def on_generate_report(self) -> None:
        self.report_list.clear()
        report = self.manager.sales_report()
        self.report_list.addItem(QListWidgetItem(f"Orders: {report['orders_count']}"))
        self.report_list.addItem(QListWidgetItem(f"Revenue: {report['total_revenue']:.2f}"))
        for cat, amount in report["by_category"].items():
            self.report_list.addItem(QListWidgetItem(f"{cat}: {amount:.2f}"))

    def on_save(self, filename: str, mode: str = "json") -> None:
        try:
            if mode == "json":
                path = self.storage.save_json(self.manager, filename)
            elif mode == "bin":
                path = self.storage.save_binary(self.manager, filename)
            else:
                path = self.storage.save_xml(self.manager, filename)
            QMessageBox.information(self, "Saved", f"Data saved to {path}")
        except Exception as ex:
            QMessageBox.critical(self, "Save error", str(ex))

    def on_load(self, filename: str, mode: str = "json") -> None:
        try:
            if mode == "json":
                self.manager = self.storage.load_json(filename)
            elif mode == "bin":
                self.manager = self.storage.load_binary(filename)
            else:
                self.manager = self.storage.load_xml(filename)
            self.product_model = ProductTableModel(self.manager.products())
            self.table.setModel(self.product_model)
            self.cart.clear()
            self.cart_model.refresh()
            self._refresh_totals()
            QMessageBox.information(self, "Loaded", f"Data loaded from {filename}")
        except Exception as ex:
            QMessageBox.critical(self, "Load error", str(ex))

    def _refresh_totals(self) -> None:
        total = self.cart.total()
        self.total_label.setText(f"Total: {total:.2f}")


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
