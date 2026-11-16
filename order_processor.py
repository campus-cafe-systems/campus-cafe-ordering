"""
order_processor.py
Main order processing, tax calculation, discounting, and receipt formatting module.
"""

from typing import List, Dict, Any
from models import (
    OrderItem, CustomerAccount, StripeGateway, PayPalGateway
)


class Order:
    """Container linking a customer account with ordered items."""
    def __init__(self, customer: CustomerAccount, items: List[OrderItem]):
        self.customer = customer
        self.items = items


class OrderProcessor:
    """Handles checkout processing, discounts, tax rules, receipts, and loyalty updates."""
    def __init__(self, gateway_type: str = "stripe"):
        self.gateway_type = gateway_type
        self.stripe = StripeGateway()
        self.paypal = PayPalGateway()
        self.order_history: List[Dict[str, Any]] = []

    def process_customer_order(self, order: Order, payment_method: str, is_student: bool,
                               is_faculty: bool, promo_code: str, custom_tax_override: float = -1.0) -> Dict[str, Any]:
        # 1. Calculate subtotal
        subtotal = 0.0
        for item in order.items:
            subtotal += item.price * item.quantity

        # 2. Calculate applicable taxes
        tax = 0.0
        if custom_tax_override >= 0.0:
            tax = subtotal * custom_tax_override
        else:
            for item in order.items:
                tax += self.apply_tax_by_type(item)

        # 3. Apply eligibility and promo discounts
        discount = 0.0
        if is_student:
            discount += subtotal * 0.10
        elif is_faculty:
            discount += subtotal * 0.05

        if promo_code == "CAMPUS5":
            discount += 5.0
        elif promo_code == "CAMPUS10":
            discount += 10.0

        if discount > subtotal:
            discount = subtotal

        final_total = subtotal + tax - discount

        # 4. Process payment through selected gateway
        payment_success = False
        if payment_method.lower() == "stripe":
            payment_success = self.stripe.charge(final_total)
        elif payment_method.lower() == "paypal":
            payment_success = self.paypal.send_payment(final_total)

        # 5. Update customer loyalty score
        self.adjust_customer_internals(order.customer, int(final_total))

        # 6. Record and return transaction summary
        result = {
            "customer_name": order.customer.name,
            "subtotal": subtotal,
            "tax": tax,
            "discount": discount,
            "final_total": final_total,
            "payment_success": payment_success
        }
        self.order_history.append(result)
        return result

    def calculate_custom_discount(self, base_price: float, is_student: bool, is_faculty: bool,
                                  is_senior: bool, is_military: bool, has_coupon: bool,
                                  day_of_week: str, time_of_day: int) -> float:
        rate = 0.0
        if is_student:
            rate += 0.10
        if is_faculty:
            rate += 0.05
        if is_senior:
            rate += 0.15
        if is_military:
            rate += 0.10
        if has_coupon:
            rate += 0.05
        if day_of_week == "Tuesday":
            rate += 0.05
        if time_of_day < 11:
            rate += 0.02
        return base_price * min(rate, 0.50)

    def apply_tax_by_type(self, item: OrderItem) -> float:
        category = item.category.lower()
        if category == "prepared_food":
            return item.price * item.quantity * 0.08
        elif category == "beverage":
            return item.price * item.quantity * 0.08
        elif category == "packaged_goods":
            return item.price * item.quantity * 0.02
        elif category == "merchandise":
            return item.price * item.quantity * 0.06
        else:
            return item.price * item.quantity * 0.05

    def format_receipt_standard(self, order: Order) -> str:
        subtotal = 0.0
        for item in order.items:
            subtotal += item.price * item.quantity
        tax = subtotal * 0.08
        total = subtotal + tax

        lines = [f"--- STANDARD RECEIPT ---", f"Customer: {order.customer.name}"]
        for item in order.items:
            lines.append(f"{item.name} x{item.quantity}: ${item.price * item.quantity:.2f}")
        lines.append(f"Subtotal: ${subtotal:.2f}")
        lines.append(f"Tax: ${tax:.2f}")
        lines.append(f"Total: ${total:.2f}")
        return "\n".join(lines)

    def format_receipt_express(self, order: Order) -> str:
        subtotal = 0.0
        for item in order.items:
            subtotal += item.price * item.quantity
        tax = subtotal * 0.08
        total = subtotal + tax

        lines = [f"--- EXPRESS RECEIPT ---", f"Customer: {order.customer.name}"]
        for item in order.items:
            lines.append(f"{item.name} x{item.quantity}: ${item.price * item.quantity:.2f}")
        lines.append(f"Subtotal: ${subtotal:.2f}")
        lines.append(f"Tax: ${tax:.2f}")
        lines.append(f"Total: ${total:.2f}")
        return "\n".join(lines)

    def compute_item_savings(self, item: OrderItem, MSRP: float) -> float:
        item_total_cost = item.price * item.quantity
        msrp_total_cost = MSRP * item.quantity
        return msrp_total_cost - item_total_cost

    def adjust_customer_internals(self, customer: CustomerAccount, added_points: int) -> None:
        customer._loyalty_score += added_points
        customer._internal_notes.append(f"Added {added_points} points via OrderProcessor.")

    def get_customer_zip_code(self, order: Order) -> str:
        return order.customer.address_info.zip_code


class OrderProcessorMiddleMan:
    """Service wrapper exposing OrderProcessor operations to external controllers."""
    def __init__(self, processor: OrderProcessor):
        self.processor = processor

    def process_customer_order(self, order: Order, payment_method: str, is_student: bool,
                               is_faculty: bool, promo_code: str, custom_tax_override: float = -1.0) -> Dict[str, Any]:
        return self.processor.process_customer_order(order, payment_method, is_student, is_faculty, promo_code, custom_tax_override)

    def apply_tax_by_type(self, item: OrderItem) -> float:
        return self.processor.apply_tax_by_type(item)
