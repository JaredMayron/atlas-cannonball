from typing import List, Dict, Any

def validate_account_schema(account: Dict[str, Any]):
    """Validates that an account object has the minimum required fields."""
    required = ["title", "current_balance"]
    missing = [field for field in required if field not in account]
    if missing:
        raise ValueError(f"Account data missing required fields: {', '.join(missing)}")

def validate_transaction_schema(transaction: Dict[str, Any]):
    """Validates that a transaction object has the minimum required fields."""
    # Note: category can be None in some APIs, but we expect the key to exist
    required = ["amount"]
    missing = [field for field in required if field not in transaction]
    if missing:
        raise ValueError(f"Transaction data missing required fields: {', '.join(missing)}")
