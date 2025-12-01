from __future__ import annotations

import datetime
import json
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatchmethod, total_ordering
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class Comparable(ABC):
    """Custom comparable interface similar to IComparable."""

    @abstractmethod
    def compare_to(self, other: "Comparable") -> int:
        """Return -1, 0, or 1 depending on ordering."""
        raise NotImplementedError


@total_ordering
class Product(Comparable, ABC):
    """Abstract base product with encapsulated fields and validation."""

    def __init__(
        self,
        name: str = "",
        category: str = "General",
        price: float = 0.0,
        stock: int = 0,
        manufacturer: str = "",
    ) -> None:
        self._name = name
        self._category = category
        self._price = float(price)
        self._stock = int(stock)
        self._manufacturer = manufacturer
        self._base_discount = 0.02  # protected value shared by descendants

    # --- constructor delegation helpers ---
    @classmethod
    def from_basic(cls, name: str, price: float) -> "Product":
        """Delegating constructor that calls the main initializer."""
        return cls(name=name, price=price, stock=1, manufacturer="Unknown")

    # --- properties (encapsulation) ---
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value:
            raise ValueError("Name is required")
        self._name = value

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        self._category = value or "General"

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = float(value)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, value: int) -> None:
        if value < 0:
            raise ValueError("Stock cannot be negative")
        self._stock = int(value)

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value: str) -> None:
        self._manufacturer = value

    # --- behavior methods ---
    def restock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Restock amount must be positive")
        self._stock += amount

    def purchase(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Purchase amount must be positive")
        if amount > self._stock:
            raise ValueError("Not enough stock")
        self._stock -= amount

    def base_price_with_tax(self, tax_rate: float = 0.2) -> float:
        return self.price * (1 + tax_rate)

    def discount_price(self) -> float:
        """Dynamic polymorphism: descendants override discount calculation."""
        return self.price * (1 - (self._base_discount + self.specific_discount_rate()))

    def compare_to(self, other: "Product") -> int:
        """Comparable implementation: compare by price then name."""
        if not isinstance(other, Product):
            return 1
        if self.price == other.price:
            return (self.name > other.name) - (self.name < other.name)
        return (self.price > other.price) - (self.price < other.price)

    def __lt__(self, other: Any) -> bool:
        return self.compare_to(other) < 0

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Product) and self.compare_to(other) == 0

    @abstractmethod
    def specific_discount_rate(self) -> float:
        """Each product type has its own discount policy."""
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "manufacturer": self.manufacturer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        mapping = {
            "Electronics": Electronics,
            "Clothing": Clothing,
            "Furniture": Furniture,
        }
        product_cls = mapping.get(data.get("type"), Product)
        if product_cls is Product:
            raise ValueError(f"Unknown product type: {data.get('type')}")
        return product_cls._from_dict_payload(data)  # type: ignore[attr-defined]


class Electronics(Product):
    def __init__(
        self,
        name: str = "",
        category: str = "Electronics",
        price: float = 0.0,
        stock: int = 0,
        manufacturer: str = "",
        warranty_years: int = 1,
        has_wifi: bool = False,
    ) -> None:
        super().__init__(name, category, price, stock, manufacturer)
        self.warranty_years = int(warranty_years)
        self.has_wifi = has_wifi

    def specific_discount_rate(self) -> float:
        return 0.05 if self.warranty_years >= 2 else 0.03

    def discount_price(self) -> float:
        # Call base method then add Wi-Fi loyalty bonus
        base_price = super().discount_price()
        return base_price * (0.97 if self.has_wifi else 1.0)

    def extra_support_message(self) -> str:
        return "Premium support included" if self.has_wifi else "Standard support"

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "Electronics":
        return cls(
            name=data.get("name", ""),
            category=data.get("category", "Electronics"),
            price=data.get("price", 0.0),
            stock=data.get("stock", 0),
            manufacturer=data.get("manufacturer", ""),
            warranty_years=data.get("warranty_years", 1),
            has_wifi=data.get("has_wifi", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = super().to_dict()
        payload.update({"warranty_years": self.warranty_years, "has_wifi": self.has_wifi})
        return payload


class Clothing(Product):
    def __init__(
        self,
        name: str = "",
        category: str = "Clothing",
        price: float = 0.0,
        stock: int = 0,
        manufacturer: str = "",
        size: str = "M",
        material: str = "Cotton",
    ) -> None:
        super().__init__(name, category, price, stock, manufacturer)
        self.size = size
        self.material = material

    def specific_discount_rate(self) -> float:
        m = str(self.material).strip().lower()
        if m in ("wool", "вовна"):
            return 0.04
        return 0.02

    def to_dict(self) -> Dict[str, Any]:
        payload = super().to_dict()
        payload.update({"size": self.size, "material": self.material})
        return payload

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "Clothing":
        return cls(
            name=data.get("name", ""),
            category=data.get("category", "Clothing"),
            price=data.get("price", 0.0),
            stock=data.get("stock", 0),
            manufacturer=data.get("manufacturer", ""),
            size=data.get("size", "M"),
            material=data.get("material", "Cotton"),
        )


class Furniture(Product):
    def __init__(
        self,
        name: str = "",
        category: str = "Furniture",
        price: float = 0.0,
        stock: int = 0,
        manufacturer: str = "",
        weight: float = 0.0,
        assembled: bool = False,
    ) -> None:
        super().__init__(name, category, price, stock, manufacturer)
        self.weight = float(weight)
        self.assembled = assembled

    def specific_discount_rate(self) -> float:
        weight_fee = 0.06 if self.weight > 50 else 0.03
        return weight_fee

    def shipping_cost(self) -> float:
        return 15.0 if self.assembled else 5.0

    def to_dict(self) -> Dict[str, Any]:
        payload = super().to_dict()
        payload.update({"weight": self.weight, "assembled": self.assembled})
        return payload

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "Furniture":
        return cls(
            name=data.get("name", ""),
            category=data.get("category", "Furniture"),
            price=data.get("price", 0.0),
            stock=data.get("stock", 0),
            manufacturer=data.get("manufacturer", ""),
            weight=data.get("weight", 0.0),
            assembled=data.get("assembled", False),
        )


@dataclass
class CartItem:
    product: Product
    quantity: int

    def subtotal(self) -> float:
        return self.product.discount_price() * self.quantity


class ShoppingCart:
    """Parameterized collection of products in the cart."""

    def __init__(self) -> None:
        self._items: List[CartItem] = []

    def add_item(self, product: Product, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        existing = next((i for i in self._items if i.product == product), None)
        if existing:
            existing.quantity += quantity
        else:
            self._items.append(CartItem(product, quantity))

    def remove_item(self, product: Product) -> None:
        self._items = [i for i in self._items if i.product != product]

    def clear(self) -> None:
        self._items.clear()

    def total(self) -> float:
        return sum(item.subtotal() for item in self._items)

    def all_items(self) -> List[CartItem]:
        return list(self._items)


class PaymentStatus:
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Payment:
    """Represents payment with static polymorphism through method overloading."""

    def __init__(
        self,
        amount: float = 0.0,
        method: str = "Card",
        status: str = PaymentStatus.PENDING,
        date: Optional[datetime.datetime] = None,
    ) -> None:
        self.amount = amount
        self.method = method
        self.status = status
        self.date = date or datetime.datetime.now()

    @singledispatchmethod
    def calculate_fee(self, base: Any) -> float:
        """Static polymorphism: overload by argument type."""
        return float(base) * 0.02

    @calculate_fee.register
    def _(self, product: Product) -> float:
        return product.price * 0.02

    def process(self) -> None:
        self.status = PaymentStatus.COMPLETED

    def refund(self) -> None:
        self.status = PaymentStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "method": self.method,
            "status": self.status,
            "date": self.date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payment":
        return cls(
            amount=data.get("amount", 0.0),
            method=data.get("method", "Card"),
            status=data.get("status", PaymentStatus.PENDING),
            date=datetime.datetime.fromisoformat(data["date"]) if "date" in data else None,
        )


class OrderStatus:
    NEW = "New"
    PAID = "Paid"
    SHIPPED = "Shipped"
    CANCELLED = "Cancelled"


class Order:
    def __init__(
        self,
        customer: "Customer",
        items: Iterable[CartItem],
        status: str = OrderStatus.NEW,
        created_at: Optional[datetime.datetime] = None,
        payment: Optional[Payment] = None,
    ) -> None:
        self.customer = customer
        self.items: List[CartItem] = list(items)
        self.status = status
        self.created_at = created_at or datetime.datetime.now()
        self.payment = payment

    def total_amount(self) -> float:
        return sum(item.subtotal() for item in self.items)

    def mark_paid(self, payment: Payment) -> None:
        payment.process()
        self.payment = payment
        self.status = OrderStatus.PAID

    def to_dict(self, include_customer: bool = True) -> Dict[str, Any]:
        return {
            "customer": self.customer.to_dict(include_history=False) if include_customer else {"full_name": self.customer.full_name, "contact": self.customer.contact},
            "items": [
                {"product": item.product.to_dict(), "quantity": item.quantity} for item in self.items
            ],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "payment": self.payment.to_dict() if self.payment else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        customer = Customer.from_dict(data["customer"])
        items = [
            CartItem(Product.from_dict(it["product"]), it["quantity"])
            for it in data.get("items", [])
        ]
        payment = Payment.from_dict(data["payment"]) if data.get("payment") else None
        return cls(
            customer=customer,
            items=items,
            status=data.get("status", OrderStatus.NEW),
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            payment=payment,
        )


class Customer:
    def __init__(self, full_name: str = "", contact: str = "") -> None:
        self._full_name = full_name
        self._contact = contact
        self._history: List[Order] = []

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        self._full_name = value

    @property
    def contact(self) -> str:
        return self._contact

    @contact.setter
    def contact(self, value: str) -> None:
        self._contact = value

    def add_order(self, order: Order) -> None:
        self._history.append(order)

    def history(self) -> List[Order]:
        return list(self._history)

    def total_spent(self) -> float:
        return sum(order.total_amount() for order in self._history)

    def to_dict(self, include_history: bool = False) -> Dict[str, Any]:
        data = {
            "full_name": self.full_name,
            "contact": self.contact,
        }
        if include_history:
            data["history"] = [order.to_dict(include_customer=False) for order in self._history]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Customer":
        c = cls(full_name=data.get("full_name", ""), contact=data.get("contact", ""))
        for order_data in data.get("history", []):
            c.add_order(Order.from_dict(order_data))
        return c


class StoreManager:
    """Admin managing product catalog and simple reports."""

    def __init__(self) -> None:
        self._products: List[Product] = []
        self._orders: List[Order] = []

    def add_product(self, product: Product) -> None:
        self._products.append(product)

    def update_product(self, index: int, product: Product) -> None:
        if index < 0 or index >= len(self._products):
            raise IndexError("Invalid product index")
        self._products[index] = product

    def delete_product(self, index: int) -> None:
        if index < 0 or index >= len(self._products):
            raise IndexError("Invalid product index")
        del self._products[index]

    def record_order(self, order: Order) -> None:
        self._orders.append(order)
        order.customer.add_order(order)

    def sales_report(self) -> Dict[str, Any]:
        by_category: Dict[str, float] = {}
        for order in self._orders:
            for item in order.items:
                by_category[item.product.category] = by_category.get(item.product.category, 0.0) + item.subtotal()
        return {
            "orders_count": len(self._orders),
            "total_revenue": sum(o.total_amount() for o in self._orders),
            "by_category": by_category,
        }

    def products(self) -> List[Product]:
        return list(self._products)

    def orders(self) -> List[Order]:
        return list(self._orders)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "products": [p.to_dict() for p in self._products],
            "orders": [o.to_dict(include_customer=True) for o in self._orders],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoreManager":
        mgr = cls()
        for p in data.get("products", []):
            mgr.add_product(Product.from_dict(p))
        for o in data.get("orders", []):
            mgr.record_order(Order.from_dict(o))
        return mgr


class Storage:
    """Persists data to text (JSON), binary (pickle) and XML."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_json(self, manager: StoreManager, filename: str) -> Path:
        target = self.base_path / filename
        with open(target, "w", encoding="utf-8") as f:
            json.dump(manager.to_dict(), f, ensure_ascii=False, indent=2)
        return target

    def load_json(self, filename: str) -> StoreManager:
        target = self.base_path / filename
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        return StoreManager.from_dict(data)

    def save_binary(self, manager: StoreManager, filename: str) -> Path:
        target = self.base_path / filename
        with open(target, "wb") as f:
            pickle.dump(manager.to_dict(), f)
        return target

    def load_binary(self, filename: str) -> StoreManager:
        target = self.base_path / filename
        with open(target, "rb") as f:
            data = pickle.load(f)
        return StoreManager.from_dict(data)

    def save_xml(self, manager: StoreManager, filename: str) -> Path:
        import xml.etree.ElementTree as ET

        root = ET.Element("store")
        products_el = ET.SubElement(root, "products")
        for p in manager.products():
            p_el = ET.SubElement(products_el, "product", attrib={"type": p.__class__.__name__})
            for k, v in p.to_dict().items():
                if k == "type":
                    continue
                child = ET.SubElement(p_el, k)
                child.text = str(v)

        orders_el = ET.SubElement(root, "orders")
        for o in manager.orders():
            o_el = ET.SubElement(orders_el, "order", attrib={"status": o.status})
            ET.SubElement(o_el, "customer").text = o.customer.full_name
            items_el = ET.SubElement(o_el, "items")
            for item in o.items:
                i_el = ET.SubElement(items_el, "item")
                ET.SubElement(i_el, "name").text = item.product.name
                ET.SubElement(i_el, "quantity").text = str(item.quantity)
                ET.SubElement(i_el, "subtotal").text = f"{item.subtotal():.2f}"

        target = self.base_path / filename
        ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
        return target

    def load_xml(self, filename: str) -> StoreManager:
        import xml.etree.ElementTree as ET

        target = self.base_path / filename
        tree = ET.parse(target)
        root = tree.getroot()
        data: Dict[str, Any] = {"products": [], "orders": []}

        for p_el in root.findall("./products/product"):
            payload: Dict[str, Any] = {"type": p_el.attrib.get("type", "Product")}
            for child in p_el:
                text = child.text or ""
                if child.tag in {"price", "weight"}:
                    payload[child.tag] = float(text)
                elif child.tag in {"stock", "warranty_years"}:
                    payload[child.tag] = int(text)
                elif child.tag in {"assembled", "has_wifi"}:
                    payload[child.tag] = text.lower() == "true"
                else:
                    payload[child.tag] = text
            data["products"].append(payload)

        # Orders in XML are shallow; only summarizing items
        for o_el in root.findall("./orders/order"):
            customer = Customer(full_name=o_el.findtext("customer", ""), contact="")
            items: List[CartItem] = []
            for i_el in o_el.findall("./items/item"):
                name = i_el.findtext("name", "")
                quantity = int(i_el.findtext("quantity", "1"))
                product = next((p for p in data["products"] if p.get("name") == name), None)
                if product:
                    items.append(CartItem(Product.from_dict(product), quantity))
            order = Order(customer=customer, items=items, status=o_el.attrib.get("status", OrderStatus.NEW))
            data["orders"].append(order.to_dict())

        return StoreManager.from_dict(data)
