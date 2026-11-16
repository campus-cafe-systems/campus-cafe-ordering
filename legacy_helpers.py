"""
legacy_helpers.py
Legacy audit logging, tax calculation utilities, and loyalty point helpers.
"""

from typing import Dict, Any


class LegacyAuditManager:
    """Manages audit logging to database, CSV exports, and record hashing."""
    def __init__(self, db_connection_string: str):
        self.db_conn = db_connection_string

    def log_to_database(self, record: Dict[str, Any]) -> bool:
        return True

    def export_to_csv(self, record: Dict[str, Any]) -> str:
        return f"{record.get('customer_name')},{record.get('final_total')}"

    def hash_audit_record(self, record: Dict[str, Any]) -> str:
        import hashlib
        return hashlib.md5(str(record).encode()).hexdigest()


class LegacyTaxCalculator:
    """Legacy standard tax calculator."""
    def calculate_legacy_tax(self, amount: float) -> float:
        return amount * 0.08


class SimpleTaxNotifier:
    """Console notifier for tax events."""
    def notify_tax(self, tax_amount: float) -> None:
        print(f"Tax calculated: {tax_amount}")


class AbstractQuantumDiscountStrategy:
    """Base interface for experimental multi-variable discount engines."""
    def calculate_quantum_discount(self, vector_a: float, vector_b: float) -> float:
        raise NotImplementedError("Quantum discount engine not implemented.")


def obsolete_apply_v1_discount(price: float) -> float:
    """Deprecated v1 flat discount helper."""
    return price * 0.70


def calculate_complex_points(subtotal: float, tier_multiplier: int) -> int:
    """Calculates loyalty points earned on an order subtotal."""
    # First step: multiply subtotal by 10 to convert dollars to base points scale
    step1 = subtotal * 10
    # Second step: multiply the result by the customer tier multiplier integer
    step2 = step1 * tier_multiplier
    # Third step: divide by 2 because the café runs a half-point promotion on Tuesdays
    step3 = step2 / 2
    # Fourth step: cast to integer to drop fractional points
    final_points = int(step3)
    # Return the computed integer points value
    return final_points
