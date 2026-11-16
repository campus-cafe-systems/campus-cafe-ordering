"""
test_cafe_system.py
Unit test suite for the Campus Café Ordering & Loyalty System.
"""

import unittest
from models import (
    CustomerProfileData, DeliveryAddress, CustomerAccount, OrderItem,
    MenuCategory, ReadOnlyMenuCategory, StripeGateway, PayPalGateway,
    DrinkItem, DrinkItemFormatter, FoodItem, FoodItemFormatter
)
from order_processor import OrderProcessor, Order, OrderProcessorMiddleMan
from legacy_helpers import (
    LegacyAuditManager, LegacyTaxCalculator, SimpleTaxNotifier,
    AbstractQuantumDiscountStrategy, obsolete_apply_v1_discount, calculate_complex_points
)


class TestCampusCafeSystem(unittest.TestCase):

    def setUp(self):
        self.customer = CustomerAccount(
            name="Alex Student",
            phone_str="(555) 019-2831",
            street="123 Campus Way",
            city="University Town",
            state="CA",
            zip_code="90210",
            tier_tuple=("GOLD", 0.10, 150)
        )
        self.item1 = OrderItem("Espresso", 3.50, "beverage", 2)
        self.item2 = OrderItem("Panini", 8.00, "prepared_food", 1)
        self.order = Order(self.customer, [self.item1, self.item2])
        self.processor = OrderProcessor()

    def test_end_to_end_order_processing(self):
        result = self.processor.process_customer_order(
            order=self.order,
            payment_method="stripe",
            is_student=True,
            is_faculty=False,
            promo_code="CAMPUS5"
        )
        self.assertTrue(result["payment_success"])
        self.assertEqual(result["subtotal"], 15.0)
        self.assertAlmostEqual(result["tax"], 1.20)
        self.assertEqual(result["discount"], 6.50)
        self.assertAlmostEqual(result["final_total"], 9.70)

    def test_area_code_and_address(self):
        self.assertEqual(self.customer.get_area_code(), "555")
        address = DeliveryAddress("123 Campus Way", "University Town", "CA", "90210")
        self.assertEqual(address.zip_code, self.customer.zip_code)

    def test_custom_discount_calculation(self):
        discount = self.processor.calculate_custom_discount(
            100.0, True, False, False, False, True, "Tuesday", 10
        )
        self.assertAlmostEqual(discount, 22.0)

    def test_category_tax_rates(self):
        tax_bev = self.processor.apply_tax_by_type(self.item1)
        self.assertAlmostEqual(tax_bev, 0.56)

    def test_temporary_promo_calculation(self):
        discounted = self.item1.calculate_temp_promo("FALL2024")
        self.assertEqual(discounted, 3.15)
        self.assertEqual(self.item1.temp_discount_code, "FALL2024")

    def test_read_only_menu_category(self):
        read_only_cat = ReadOnlyMenuCategory("Daily Specials", [self.item1])
        with self.assertRaises(NotImplementedError):
            read_only_cat.add_item(self.item2)

    def test_payment_gateways(self):
        stripe = StripeGateway()
        paypal = PayPalGateway()
        self.assertTrue(stripe.charge(50.0))
        self.assertTrue(paypal.send_payment(50.0))

    def test_item_formatters(self):
        drink = DrinkItem("Latte", 4.50, 16)
        food = FoodItem("Croissant", 3.00, True)
        drink_formatter = DrinkItemFormatter()
        food_formatter = FoodItemFormatter()
        self.assertIn("16 oz", drink_formatter.format_item(drink))
        self.assertIn("Warm", food_formatter.format_item(food))

    def test_audit_and_legacy_tax(self):
        audit_mgr = LegacyAuditManager("db://localhost:5432/cafe")
        self.assertTrue(audit_mgr.log_to_database({"test": 1}))
        self.assertEqual(audit_mgr.export_to_csv({"customer_name": "Alex", "final_total": 10.0}), "Alex,10.0")
        legacy_calc = LegacyTaxCalculator()
        self.assertAlmostEqual(legacy_calc.calculate_legacy_tax(100.0), 8.0)

    def test_points_and_v1_discount(self):
        points = calculate_complex_points(10.0, 2)
        self.assertEqual(points, 100)
        self.assertAlmostEqual(obsolete_apply_v1_discount(100.0), 70.0)

    def test_receipt_formatting(self):
        std_receipt = self.processor.format_receipt_standard(self.order)
        exp_receipt = self.processor.format_receipt_express(self.order)
        self.assertIn("Subtotal: $15.00", std_receipt)
        self.assertIn("Subtotal: $15.00", exp_receipt)

    def test_tax_notifier_and_profile_data(self):
        notifier = SimpleTaxNotifier()
        notifier.notify_tax(1.20)
        profile = CustomerProfileData("Sam", "sam@univ.edu", 101)
        self.assertEqual(profile.get_email(), "sam@univ.edu")

    def test_quantum_discount_interface(self):
        strategy = AbstractQuantumDiscountStrategy()
        with self.assertRaises(NotImplementedError):
            strategy.calculate_quantum_discount(1.0, 2.0)

    def test_item_savings(self):
        savings = self.processor.compute_item_savings(self.item1, 4.00)
        self.assertAlmostEqual(savings, 1.00)

    def test_loyalty_score_updates(self):
        initial_score = self.customer._loyalty_score
        self.processor.adjust_customer_internals(self.customer, 50)
        self.assertEqual(self.customer._loyalty_score, initial_score + 50)
        self.assertEqual(len(self.customer._internal_notes), 1)

    def test_customer_zip_lookup(self):
        zip_code = self.processor.get_customer_zip_code(self.order)
        self.assertEqual(zip_code, "90210")

    def test_processor_wrapper(self):
        middle_man = OrderProcessorMiddleMan(self.processor)
        res = middle_man.process_customer_order(self.order, "stripe", True, False, "")
        self.assertTrue(res["payment_success"])


if __name__ == "__main__":
    unittest.main()
