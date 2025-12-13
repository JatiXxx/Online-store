import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QDate
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QDateEdit,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QButtonGroup,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
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

# --- Localization ---
LANG: Dict[str, Dict[str, str]] = {
    "en": {
        "window_title": "Online Store",
        "add": "Add product",
        "edit": "Edit product",
        "delete": "Delete product",
        "add_cart": "Add to cart",
        "place_order": "Place order",
        "clear_cart": "Clear cart",
        "generate_report": "Generate sales report",
        "open_reports": "Open reports",
        "open_orders": "Orders history",
        "cart": "Cart",
        "reports": "Reports",
        "reports_window": "Sales reports",
        "saved": "Saved",
        "loaded": "Loaded",
        "save_json": "Save JSON",
        "load_json": "Load JSON",
        "save_bin": "Save Binary",
        "load_bin": "Load Binary",
        "save_xml": "Save XML",
        "load_xml": "Load XML",
        "total": "Total",
        "select_edit": "Select a product to edit.",
        "select_delete": "Select a product to delete.",
        "select_add": "Select a product to add to cart.",
        "delete_confirm": "Remove selected product?",
        "cart_empty": "Add items to cart first.",
        "order_created": "Order created",
        "save_error": "Save error",
        "load_error": "Load error",
        "data_saved": "Data saved to {path}",
        "data_loaded": "Data loaded from {path}",
        "orders_label": "Orders",
        "revenue_label": "Revenue",
        "amount": "Amount",
        "category_summary": "Category summary",
        "product_summary": "Product summary",
        "quantity_label": "Quantity",
        "start_date": "Start date",
        "end_date": "End date",
        "apply_filters": "Apply filters",
        "pcs": "pcs",
        "status_new": "New",
        "status_paid": "Paid",
        "status_shipped": "Shipped",
        "qty": "Qty",
        "subtotal": "Subtotal",
        "name_required": "Name is required",
        "unknown": "Unknown",
        "guest": "Guest",
        "default_material": "Cotton",
        "validation_error": "Validation error",
        "cannot_add": "Cannot add",
        "discounted": "Discounted",
        "manufacturer": "Manufacturer",
        "price": "Price",
        "stock": "Stock",
        "category": "Category",
        "name": "Name",
        "category_electronics": "Electronics",
        "category_clothing": "Clothing",
        "category_furniture": "Furniture",
        "status": "Initial status:",
        "shipping": "Shipping:",
        "payment": "Payment:",
        "customer_name": "Customer name:",
        "customer_id": "Customer ID",
        "contact": "Contact info:",
        "delivery": "Delivery:",
        "standard_delivery": "Standard delivery",
        "express_delivery": "Express delivery",
        "warranty": "Warranty (years):",
        "wifi": "Wi-Fi enabled",
        "size": "Size:",
        "material": "Material:",
        "weight": "Weight (kg):",
        "assembled": "Delivered assembled",
        "payment_cash": "Cash",
        "payment_card": "Card",
        "language": "Language",
        "order_date": "Date",
        "order_status": "Status",
        "order_items": "Items",
        "order_payment": "Payment",
        "filter_name": "Filter by name",
        "filter_contact": "Filter by phone",
        "filter_query": "Search (name or phone)",
        "filter_start_date": "From date",
        "filter_end_date": "To date",
        "apply_filter_orders": "Apply filters",
    },
    "uk": {
        "window_title": "Онлайн-магазин",
        "add": "Додати товар",
        "edit": "Редагувати товар",
        "delete": "Видалити товар",
        "add_cart": "До кошика",
        "place_order": "Оформити замовлення",
        "clear_cart": "Очистити кошик",
        "generate_report": "Звіт про продажі",
        "open_reports": "Відкрити звіти",
        "open_orders": "Історія замовлень",
        "cart": "Кошик",
        "reports": "Звіти",
        "reports_window": "Звіти про продажі",
        "saved": "Збережено",
        "loaded": "Завантажено",
        "save_json": "Зберегти JSON",
        "load_json": "Завантажити JSON",
        "save_bin": "Зберегти Binary",
        "load_bin": "Завантажити Binary",
        "save_xml": "Зберегти XML",
        "load_xml": "Завантажити XML",
        "total": "Разом",
        "select_edit": "Оберіть товар для редагування.",
        "select_delete": "Оберіть товар для видалення.",
        "select_add": "Оберіть товар для додавання до кошика.",
        "delete_confirm": "Видалити вибраний товар?",
        "cart_empty": "Спершу додайте товари до кошика.",
        "order_created": "Замовлення створено",
        "save_error": "Помилка збереження",
        "load_error": "Помилка завантаження",
        "data_saved": "Дані збережено у {path}",
        "data_loaded": "Дані завантажено з {path}",
        "orders_label": "Замовлення",
        "revenue_label": "Дохід",
        "amount": "Сума",
        "category_summary": "Підсумок по категоріях",
        "product_summary": "Підсумок по товарах",
        "quantity_label": "Кількість",
        "start_date": "Початкова дата",
        "end_date": "Кінцева дата",
        "apply_filters": "Застосувати фільтри",
        "pcs": "шт",
        "status_new": "Новий",
        "status_paid": "Оплачено",
        "status_shipped": "Відправлено",
        "qty": "К-сть",
        "subtotal": "Сума",
        "name_required": "Потрібна назва товару",
        "unknown": "Невідомо",
        "guest": "Гість",
        "default_material": "Бавовна",
        "validation_error": "Помилка валідації",
        "cannot_add": "Не вдалося додати",
        "discounted": "Ціна зі знижкою",
        "manufacturer": "Виробник",
        "price": "Ціна",
        "stock": "Залишок",
        "category": "Категорія",
        "name": "Назва",
        "category_electronics": "Електроніка",
        "category_clothing": "Одяг",
        "category_furniture": "Меблі",
        "status": "Статус:",
        "shipping": "Доставка:",
        "payment": "Оплата:",
        "customer_name": "ПІБ клієнта:",
        "customer_id": "ID клієнта",
        "contact": "Контакти:",
        "delivery": "Доставка:",
        "standard_delivery": "Стандартна доставка",
        "express_delivery": "Експрес-доставка",
        "warranty": "Гарантія (роки):",
        "wifi": "Є Wi‑Fi",
        "size": "Розмір:",
        "material": "Матеріал:",
        "weight": "Вага (кг):",
        "assembled": "Постачається зібраним",
        "payment_cash": "Готівка",
        "payment_card": "Картка",
        "language": "Мова",
        "order_date": "Дата",
        "order_status": "Статус",
        "order_items": "Товари",
        "order_payment": "Оплата",
        "filter_name": "Фільтр за ім'ям",
        "filter_contact": "Фільтр за телефоном",
        "filter_query": "Пошук (ім'я або телефон)",
        "filter_start_date": "Від дати",
        "filter_end_date": "До дати",
        "apply_filter_orders": "Застосувати фільтри",
    },
}


def make_translator(lang: str) -> Callable[[str], str]:
    current = LANG.get(lang, LANG["en"])
    return lambda key: current.get(key, key)


# ---------- Table models ----------
class ProductTableModel(QAbstractTableModel):
    def __init__(self, products: List[Product], translate: Callable[[str], str]) -> None:
        super().__init__()
        self._products = products
        self._translate = translate

    def headers(self) -> List[str]:
        t = self._translate
        return [
            t("name"),
            t("category"),
            t("price"),
            t("stock"),
            t("manufacturer"),
            t("discounted"),
        ]

    def rowCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self._products)

    def columnCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self.headers())

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
                manu = str(product.manufacturer)
                if manu.strip().lower() in ("unknown", "невідомо"):
                    return self._translate("unknown")
                return manu
            if col == 5:
                return f"{product.discount_price():.2f}"
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def headerData(self, section: int, orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.headers()[section]
        return section + 1

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:  # type: ignore[override]
        if not self._products:
            return
        reverse = order == Qt.DescendingOrder
        col = max(0, min(column, self.columnCount() - 1))

        def key_func(p: Product):
            if col == 0:
                return p.name
            if col == 1:
                return p.category
            if col == 2:
                return p.price
            if col == 3:
                return p.stock
            if col == 4:
                return p.manufacturer
            if col == 5:
                return p.discount_price()
            return p.name

        self.layoutAboutToBeChanged.emit()
        self._products.sort(key=key_func, reverse=reverse)
        self.layoutChanged.emit()

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
    def __init__(self, cart: ShoppingCart, translate: Callable[[str], str]) -> None:
        super().__init__()
        self.cart = cart
        self._translate = translate

    def headers(self) -> List[str]:
        t = self._translate
        return [t("name"), t("qty"), t("subtotal")]

    def rowCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self.cart.all_items())

    def columnCount(self, parent=QModelIndex()) -> int:  # type: ignore[override]
        return len(self.headers())

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
            return self.headers()[section]
        return section + 1

    def refresh(self) -> None:
        left = self.index(0, 0)
        right = self.index(max(0, self.rowCount() - 1), self.columnCount() - 1)
        self.dataChanged.emit(left, right, [Qt.DisplayRole])
        self.layoutChanged.emit()


# ---------- Reports window ----------
class ReportWindow(QDialog):
    def __init__(self, manager: StoreManager, translate: Callable[[str], str], parent: QWidget = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self._ = translate
        self.setWindowTitle(self._("reports_window"))
        self.resize(700, 500)

        # Filters
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        # Category filter
        self.category_list = QListWidget()
        self.category_list.setSelectionMode(QListWidget.MultiSelection)
        self.category_list.setMaximumHeight(90)
        for cat in sorted({p.category for p in self.manager.products()}):
            key = f"category_{cat.lower()}"
            display = self._(key) if key in LANG.get("en", {}) else cat
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, cat)
            item.setCheckState(Qt.Unchecked)
            self.category_list.addItem(item)

        filter_layout = QGridLayout()
        filter_layout.addWidget(QLabel(self._("start_date")), 0, 0)
        filter_layout.addWidget(self.start_date, 0, 1)
        filter_layout.addWidget(QLabel(self._("end_date")), 1, 0)
        filter_layout.addWidget(self.end_date, 1, 1)
        filter_layout.addWidget(QLabel(self._("category")), 2, 0)
        filter_layout.addWidget(self.category_list, 2, 1)

        apply_btn = QPushButton(self._("apply_filters"))
        apply_btn.clicked.connect(self.refresh)

        # Summary tables
        self.category_table = QTableWidget(0, 3)
        self.category_table.setHorizontalHeaderLabels([
            self._("category"),
            self._("amount"),
            self._("quantity_label"),
        ])
        self.category_table.verticalHeader().setVisible(False)
        self.category_table.horizontalHeader().setStretchLastSection(True)

        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels([
            self._("name"),
            self._("category"),
            self._("amount"),
            self._("quantity_label"),
        ])
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.category_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.total_label = QLabel()
        layout = QVBoxLayout()
        layout.addLayout(filter_layout)
        layout.addWidget(apply_btn)
        layout.addWidget(QLabel(self._("category_summary")))
        layout.addWidget(self.category_table)
        layout.addWidget(QLabel(self._("product_summary")))
        layout.addWidget(self.product_table)
        layout.addWidget(self.total_label)
        self.setLayout(layout)
        self.refresh()

    def selected_categories(self) -> List[str]:
        names: List[str] = []
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            if item.checkState() == Qt.Checked:
                names.append(item.data(Qt.UserRole) or item.text())
        return names

    def refresh(self) -> None:
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            categories = self.selected_categories()
            report = self.manager.sales_report_filtered(start=start, end=end, categories=categories)

            self.category_table.clearContents()
            self.product_table.clearContents()
            cat_qty = report["by_category_qty"]
            cat_amt = report["by_category_amount"]
            # fill category table
            self.category_table.setRowCount(len(cat_qty))
            for row, (cat, qty) in enumerate(cat_qty.items()):
                amount = cat_amt.get(cat, 0.0)
                self.category_table.setItem(row, 0, QTableWidgetItem(cat))
                self.category_table.setItem(row, 1, QTableWidgetItem(f"{amount:.2f}"))
                self.category_table.setItem(row, 2, QTableWidgetItem(str(qty)))
            # fill product table
            prod_amt = report.get("by_product_amount", {})
            prod_qty = report.get("by_product_qty", {})
            self.product_table.setRowCount(len(prod_amt))
            for row, (name, amount) in enumerate(prod_amt.items()):
                qty = prod_qty.get(name, 0)
                self.product_table.setItem(row, 0, QTableWidgetItem(name))
                # find category from manager products
                cat = next((p.category for p in self.manager.products() if p.name == name), "")
                self.product_table.setItem(row, 1, QTableWidgetItem(cat))
                self.product_table.setItem(row, 2, QTableWidgetItem(f"{amount:.2f}"))
                self.product_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.total_label.setText(f"{self._('total')}: {report.get('total_revenue', 0.0):.2f}")
        except Exception as ex:
            QMessageBox.critical(self, self._("save_error"), str(ex))


# ---------- Orders history window ----------
class OrderHistoryWindow(QDialog):
    def __init__(self, manager: StoreManager, translate: Callable[[str], str], parent: QWidget = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self._ = translate
        self.setWindowTitle(self._("open_orders") if "open_orders" in LANG.get("en", {}) else "Orders")
        self.resize(700, 500)

        self.orders_list = QListWidget()
        self.details_list = QListWidget()
        self.orders_list.currentRowChanged.connect(self.show_details)

        # Filters
        self.query_filter = QLineEdit()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_check = QCheckBox()
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_check = QCheckBox()

        filter_layout = QGridLayout()
        filter_layout.addWidget(QLabel(self._("filter_query")), 0, 0)
        filter_layout.addWidget(self.query_filter, 0, 1, 1, 2)
        filter_layout.addWidget(QLabel(self._("start_date")), 1, 0)
        filter_layout.addWidget(self.start_check, 1, 1)
        filter_layout.addWidget(self.start_date, 1, 2)
        filter_layout.addWidget(QLabel(self._("end_date")), 2, 0)
        filter_layout.addWidget(self.end_check, 2, 1)
        filter_layout.addWidget(self.end_date, 2, 2)

        left = QVBoxLayout()
        left.addLayout(filter_layout)
        left.addWidget(self.orders_list)

        layout = QHBoxLayout()
        layout.addLayout(left, 1)
        layout.addWidget(self.details_list, 2)
        self.setLayout(layout)

        # auto-refresh on filters
        self.query_filter.textChanged.connect(self.load_orders)
        self.start_date.dateChanged.connect(lambda _d: self.load_orders())
        self.end_date.dateChanged.connect(lambda _d: self.load_orders())
        self.start_check.stateChanged.connect(lambda _s: self.load_orders())
        self.end_check.stateChanged.connect(lambda _s: self.load_orders())

        self.load_orders()

    def load_orders(self) -> None:
        self.orders_list.clear()
        query = self.query_filter.text().strip().lower()
        use_start = self.start_check.isChecked()
        use_end = self.end_check.isChecked()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        for order in self.manager.orders():
            if query and (query not in order.customer.full_name.lower() and query not in order.customer.contact.lower()):
                continue
            d = order.created_at.date()
            if use_start and d < start:
                continue
            if use_end and d > end:
                continue
            label = f"{order.customer.customer_id} | {order.customer.full_name} | {order.created_at.date()} | {order.status}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, order)
            self.orders_list.addItem(item)

    def show_details(self, index: int) -> None:
        self.details_list.clear()
        if index < 0:
            return
        item = self.orders_list.item(index)
        order: Order = item.data(Qt.UserRole)
        self.details_list.addItem(f"{self._('customer_id')}: {order.customer.customer_id}")
        self.details_list.addItem(f"{self._('customer_name')}: {order.customer.full_name}")
        self.details_list.addItem(f"{self._('contact')}: {order.customer.contact}")
        self.details_list.addItem(f"{self._('order_date')}: {order.created_at}")
        self.details_list.addItem(f"{self._('order_status')}: {order.status}")
        self.details_list.addItem(f"{self._('order_items')}:")
        for ci in order.items:
            self.details_list.addItem(f"- {ci.quantity} x {ci.product.name} @ {ci.product.price:.2f} = {ci.subtotal():.2f}")
        if order.payment:
            self.details_list.addItem(f"{self._('order_payment')}: {order.payment.method} {order.payment.amount:.2f} ({order.payment.status})")
# ---------- Dialogs ----------
class ProductDialog(QDialog):
    def __init__(self, parent: QWidget = None, product: Optional[Product] = None, translate: Callable[[str], str] = lambda k: k) -> None:
        super().__init__(parent)
        self._ = translate
        self.setWindowTitle(self._("add") + " / " + self._("edit"))
        self.selected_category = "Electronics"

        self.name_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.addItem(self._("category_electronics"), "Electronics")
        self.category_combo.addItem(self._("category_clothing"), "Clothing")
        self.category_combo.addItem(self._("category_furniture"), "Furniture")
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1_000_000)
        self.price_spin.setDecimals(2)
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 10_000)
        self.mfr_edit = QLineEdit()

        # Category-specific controls
        self.warranty_spin = QSpinBox()
        self.warranty_spin.setRange(0, 10)
        self.wifi_check = QCheckBox(self._("wifi"))

        self.size_combo = QComboBox()
        self.size_combo.addItems(["XS", "S", "M", "L", "XL"])
        self.material_edit = QLineEdit()

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 1000)
        self.weight_spin.setDecimals(2)
        self.assembled_check = QCheckBox(self._("assembled"))

        # Radio buttons to choose delivery option (fulfills RadioButton requirement)
        self.delivery_standard = QRadioButton(self._("standard_delivery"))
        self.delivery_express = QRadioButton(self._("express_delivery"))
        self.delivery_standard.setChecked(True)

        form = QFormLayout()
        form.addRow(self._("name") + ":", self.name_edit)
        form.addRow(self._("category") + ":", self.category_combo)
        form.addRow(self._("price") + ":", self.price_spin)
        form.addRow(self._("stock") + ":", self.stock_spin)
        form.addRow(self._("manufacturer") + ":", self.mfr_edit)
        form.addRow(self._("warranty"), self.warranty_spin)
        form.addRow("", self.wifi_check)
        form.addRow(self._("size"), self.size_combo)
        form.addRow(self._("material"), self.material_edit)
        form.addRow(self._("weight"), self.weight_spin)
        form.addRow("", self.assembled_check)
        form.addRow(self._("delivery"), self.delivery_standard)
        form.addRow("", self.delivery_express)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.setLayout(form)
        self.category_combo.currentIndexChanged.connect(lambda _: self.on_category_change(self.category_combo.currentData()))
        self.on_category_change(self.category_combo.currentData())

        if product:
            self.fill_from_product(product)

    def on_category_change(self, category: str) -> None:
        self.selected_category = category or "Electronics"
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
        idx = self.category_combo.findData(product.category)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
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
            raise ValueError(self._("name_required"))
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
                material=self.material_edit.text().strip() or self._("default_material"),
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

    def __init__(self, parent: QWidget = None, translate: Callable[[str], str] = lambda k: k) -> None:
        super().__init__(parent)
        self._ = translate
        self.setWindowTitle(self._("place_order"))
        self.name_edit = QLineEdit()
        self.contact_edit = QLineEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItem(self._("status_new"), OrderStatus.NEW)
        self.status_combo.addItem(self._("status_paid"), OrderStatus.PAID)
        self.status_combo.addItem(self._("status_shipped"), OrderStatus.SHIPPED)
        self.express_check = QCheckBox(self._("express_delivery"))
        self.cash_radio = QRadioButton(self._("payment_cash"))
        self.card_radio = QRadioButton(self._("payment_card"))
        self.card_radio.setChecked(True)

        form = QFormLayout()
        form.addRow(self._("customer_name"), self.name_edit)
        form.addRow(self._("contact"), self.contact_edit)
        form.addRow(self._("status"), self.status_combo)
        form.addRow(self._("shipping"), self.express_check)
        form.addRow(self._("payment"), self.card_radio)
        form.addRow("", self.cash_radio)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.setLayout(form)

    def build_customer(self) -> Customer:
        name = self.name_edit.text().strip() or self._("guest")
        contact = self.contact_edit.text().strip()
        return Customer(full_name=name, contact=contact)

    def payment_method(self) -> str:
        return "Card" if self.card_radio.isChecked() else "Cash"

    def initial_status(self) -> str:
        data = self.status_combo.currentData()
        return data if data else self.status_combo.currentText()

    def express(self) -> bool:
        return self.express_check.isChecked()


# ---------- Main window ----------
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_lang = "en"
        self._ = make_translator(self.current_lang)
        self.setWindowTitle(self._("window_title"))
        self.resize(1100, 700)

        self.manager = StoreManager()
        self.cart = ShoppingCart()
        self.storage = Storage(DATA_DIR)

        for sample in self._default_products():
            self.manager.add_product(sample)

        self.product_model = ProductTableModel(self.manager.products(), self._)
        self.cart_model = CartTableModel(self.cart, self._)

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
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        table_group.addWidget(self.table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(self._("add"))
        edit_btn = QPushButton(self._("edit"))
        del_btn = QPushButton(self._("delete"))
        self.add_cart_qty = QSpinBox()
        self.add_cart_qty.setRange(1, 1000)
        self.add_cart_qty.setValue(1)
        add_cart_btn = QPushButton(self._("add_cart"))
        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        btn_row.addWidget(QLabel(self._("quantity_label")))
        btn_row.addWidget(self.add_cart_qty)
        btn_row.addWidget(add_cart_btn)

        add_btn.clicked.connect(self.on_add)
        edit_btn.clicked.connect(self.on_edit)
        del_btn.clicked.connect(self.on_delete)
        add_cart_btn.clicked.connect(self.on_add_to_cart)
        table_group.addLayout(btn_row)

        # Cart and checkout
        side_group = QVBoxLayout()
        cart_box = QGroupBox(self._("cart"))
        cart_layout = QVBoxLayout()
        self.cart_table = QTableView()
        self.cart_table.setModel(self.cart_model)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cart_layout.addWidget(self.cart_table)
        self.total_label = QLabel(f"{self._('total')}: 0.00")
        cart_layout.addWidget(self.total_label)
        cart_box.setLayout(cart_layout)
        side_group.addWidget(cart_box)

        order_btn = QPushButton(self._("place_order"))
        clear_cart_btn = QPushButton(self._("clear_cart"))
        side_group.addWidget(order_btn)
        side_group.addWidget(clear_cart_btn)
        order_btn.clicked.connect(self.on_checkout)
        clear_cart_btn.clicked.connect(self.on_clear_cart)

        # Reports / history buttons
        open_reports_btn = QPushButton(self._("open_reports"))
        open_orders_btn = QPushButton(self._("open_orders"))
        open_reports_btn.clicked.connect(self.on_open_reports)
        open_orders_btn.clicked.connect(self.on_open_orders)
        side_group.addWidget(open_reports_btn)
        side_group.addWidget(open_orders_btn)

        # Persistence buttons
        save_json_btn = QPushButton(self._("save_json"))
        load_json_btn = QPushButton(self._("load_json"))
        save_bin_btn = QPushButton(self._("save_bin"))
        load_bin_btn = QPushButton(self._("load_bin"))
        save_xml_btn = QPushButton(self._("save_xml"))
        load_xml_btn = QPushButton(self._("load_xml"))

        # Language switcher as toggle buttons
        lang_row = QHBoxLayout()
        lang_label = QLabel(self._("language"))
        lang_row.addWidget(lang_label)
        self.lang_group = QButtonGroup(self)
        for code, label in (("en", "EN"), ("uk", "UK")):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("lang", code)
            if self.current_lang == code:
                btn.setChecked(True)
            self.lang_group.addButton(btn)
            lang_row.addWidget(btn)
        self.lang_group.buttonClicked.connect(self.on_language_button)
        side_group.addLayout(lang_row)

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
        dlg = ProductDialog(self, translate=self._)
        if dlg.exec_():
            try:
                product = dlg.build_product()
                self.manager.add_product(product)
                self.product_model.add_product(product)
            except Exception as ex:
                QMessageBox.warning(self, self._("validation_error"), str(ex))

    def on_edit(self) -> None:
        row = self.selected_row()
        if row is None:
            QMessageBox.information(self, self._("edit"), self._("select_edit"))
            return
        product = self.product_model.product_at(row)
        dlg = ProductDialog(self, product=product, translate=self._)
        if dlg.exec_():
            try:
                updated = dlg.build_product()
                self.manager.update_product(row, updated)
                self.product_model.update_product(row, updated)
            except Exception as ex:
                QMessageBox.warning(self, self._("validation_error"), str(ex))

    def on_delete(self) -> None:
        row = self.selected_row()
        if row is None:
            QMessageBox.information(self, self._("delete"), self._("select_delete"))
            return
        if QMessageBox.question(self, self._("delete"), self._("delete_confirm")) == QMessageBox.Yes:
            self.manager.delete_product(row)
            self.product_model.remove_product(row)

    def on_add_to_cart(self) -> None:
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(self, self._("add_cart"), self._("select_add"))
            return
        qty = self.add_cart_qty.value()
        errors = []
        for index in sel:
            row = index.row()
            product = self.product_model.product_at(row)
            try:
                product.purchase(qty)
                self.cart.add_item(product, qty)
                self.product_model.dataChanged.emit(self.product_model.index(row, 0), self.product_model.index(row, self.product_model.columnCount() - 1))
            except Exception as ex:
                errors.append(f"{product.name}: {ex}")
        self.cart_model.refresh()
        self._refresh_totals()
        if errors:
            QMessageBox.warning(self, self._("cannot_add"), "\n".join(errors))

    def on_clear_cart(self) -> None:
        self.cart.clear()
        self.cart_model.refresh()
        self._refresh_totals()

    def on_checkout(self) -> None:
        if not self.cart.all_items():
            QMessageBox.information(self, self._("cart"), self._("cart_empty"))
            return
        dlg = CheckoutDialog(self, translate=self._)
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
        QMessageBox.information(self, self._("order_created"), f"{self._('total')}: {payment.amount:.2f}")

    def on_save(self, filename: str, mode: str = "json") -> None:
        try:
            if mode == "json":
                path = self.storage.save_json(self.manager, filename)
            elif mode == "bin":
                path = self.storage.save_binary(self.manager, filename)
            else:
                path = self.storage.save_xml(self.manager, filename)
            QMessageBox.information(self, self._("saved"), self._("data_saved").format(path=path))
        except Exception as ex:
            QMessageBox.critical(self, self._("save_error"), str(ex))

    def on_load(self, filename: str, mode: str = "json") -> None:
        try:
            if mode == "json":
                self.manager = self.storage.load_json(filename)
            elif mode == "bin":
                self.manager = self.storage.load_binary(filename)
            else:
                self.manager = self.storage.load_xml(filename)
            self.product_model = ProductTableModel(self.manager.products(), self._)
            self.table.setModel(self.product_model)
            self.cart.clear()
            self.cart_model = CartTableModel(self.cart, self._)
            self.cart_table.setModel(self.cart_model)
            self._refresh_totals()
            QMessageBox.information(self, self._("loaded"), self._("data_loaded").format(path=filename))
        except Exception as ex:
            QMessageBox.critical(self, self._("load_error"), str(ex))

    def _refresh_totals(self) -> None:
        total = self.cart.total()
        self.total_label.setText(f"{self._('total')}: {total:.2f}")

    def on_language_changed(self, lang: str) -> None:
        self.current_lang = lang
        self._ = make_translator(lang)
        self.setWindowTitle(self._("window_title"))
        # Rebuild models with translated headers
        self.product_model = ProductTableModel(self.manager.products(), self._)
        self.table.setModel(self.product_model)
        self.cart_model = CartTableModel(self.cart, self._)
        self.cart_table.setModel(self.cart_model)
        # Update static labels/buttons
        self._init_ui()
        self._refresh_totals()

    def on_language_button(self, button: QPushButton) -> None:
        lang = button.property("lang")
        if lang and lang != self.current_lang:
            self.on_language_changed(lang)

    def on_open_reports(self) -> None:
        dlg = ReportWindow(self.manager, self._, self)
        dlg.exec_()

    def on_open_orders(self) -> None:
        dlg = OrderHistoryWindow(self.manager, self._, self)
        dlg.exec_()


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
