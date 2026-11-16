"""
models.py
Domain models for the Campus Café Ordering & Loyalty System.
"""

from typing import List, Dict, Any, Optional


class CustomerProfileData:
    """Stores basic customer profile information."""
    def __init__(self, name: str, email: str, member_id: int):
        self.name = name
        self.email = email
        self.member_id = member_id

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def get_email(self) -> str:
        return self.email

    def set_email(self, email: str) -> None:
        self.email = email


class DeliveryAddress:
    """Represents a campus or local delivery address."""
    def __init__(self, street: str, city: str, state: str, zip_code: str):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code


class CustomerAccount:
    """Represents a registered café customer account with contact, address, and tier details."""
    def __init__(self, name: str, phone_str: str, street: str, city: str, state: str, zip_code: str, tier_tuple: tuple):
        self.name = name
        self.phone_str = phone_str
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.address_info = DeliveryAddress(street, city, state, zip_code)
        self.tier_tuple = tier_tuple
        self._loyalty_score = tier_tuple[2] if len(tier_tuple) > 2 else 0
        self._internal_notes = []

    def get_area_code(self) -> str:
        if self.phone_str.startswith("(") and ")" in self.phone_str:
            return self.phone_str.split(")")[0].replace("(", "")
        return self.phone_str.split("-")[0]


class OrderItem:
    """Represents a single line item in a customer's café order."""
    def __init__(self, name: str, price: float, category: str, quantity: int = 1):
        self.name = name
        self.price = price
        self.category = category
        self.quantity = quantity
        self.temp_discount_code: Optional[str] = None
        self.temp_scratchpad: Optional[Dict[str, Any]] = None

    def calculate_temp_promo(self, code: str) -> float:
        self.temp_discount_code = code
        self.temp_scratchpad = {"applied_at": "checkout", "factor": 0.9}
        discounted_price = self.price * self.temp_scratchpad["factor"]
        return discounted_price


class MenuCategory:
    """Base class for café menu categories."""
    def __init__(self, category_name: str):
        self.category_name = category_name
        self.items: List[OrderItem] = []

    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)


class ReadOnlyMenuCategory(MenuCategory):
    """Menu category for fixed daily specials that cannot be modified at runtime."""
    def __init__(self, category_name: str, fixed_items: List[OrderItem]):
        super().__init__(category_name)
        self.items = fixed_items

    def add_item(self, item: OrderItem) -> None:
        raise NotImplementedError("ReadOnlyMenuCategory does not support adding items dynamically.")


class StripeGateway:
    """Payment integration wrapper for Stripe."""
    def charge(self, amount: float) -> bool:
        return amount > 0


class PayPalGateway:
    """Payment integration wrapper for PayPal."""
    def send_payment(self, total_val: float) -> bool:
        return total_val > 0


class BaseItem:
    """Base class for menu items."""
    def __init__(self, name: str, base_price: float):
        self.name = name
        self.base_price = base_price


class DrinkItem(BaseItem):
    """Beverage menu item with size specification."""
    def __init__(self, name: str, base_price: float, size_oz: int):
        super().__init__(name, base_price)
        self.size_oz = size_oz


class FoodItem(BaseItem):
    """Food menu item with warming option."""
    def __init__(self, name: str, base_price: float, is_warmed: bool):
        super().__init__(name, base_price)
        self.is_warmed = is_warmed


class BaseItemFormatter:
    """Base class for menu item display formatting."""
    def format_item(self, item: BaseItem) -> str:
        return f"Item: {item.name}, Price: ${item.base_price:.2f}"


class DrinkItemFormatter(BaseItemFormatter):
    """Formatter for beverage menu items."""
    def format_item(self, item: DrinkItem) -> str:
        return f"Drink: {item.name} ({item.size_oz} oz), Price: ${item.base_price:.2f}"


class FoodItemFormatter(BaseItemFormatter):
    """Formatter for food menu items."""
    def format_item(self, item: FoodItem) -> str:
        status = "Warm" if item.is_warmed else "Cold"
        return f"Food: {item.name} [{status}], Price: ${item.base_price:.2f}"
