# Campus Café Ordering & Loyalty System

A lightweight Python backend for managing university campus café orders, menu categories, promotional discounts, tax rules, payment processing, and customer loyalty points.

## Project Structure

```text
campus-cafe-ordering/
├── models.py             # Domain entities (customers, addresses, menu items, payment gateways)
├── order_processor.py    # Checkout workflow, tax rules, discounts, and receipt formatting
├── legacy_helpers.py     # Legacy audit logging, tax utilities, and loyalty point helpers
└── test_cafe_system.py   # Unit test suite
