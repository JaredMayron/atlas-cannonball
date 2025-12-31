import pytest
import json

@pytest.fixture
def mock_config():
    return {
        "CASH_TITLES": ["CHECKING", "SAVINGS"],
        "INVESTMENT_TITLES": ["401K", "IRA"],
        "CAR_IDENTIFIER": "HONDA",
        "CONDO_IDENTIFIER": "MY CONDO",
        "API_CALCULATED_CATEGORIES": ["Rent", "Utilities", "Internet"],
        "GROCERIES_ESTIMATE": 500,
        "RESTAURANT_ESTIMATE": 200,
        "HEALTH_INSURANCE_ESTIMATE": 300
    }

@pytest.fixture
def mock_config_json(mock_config):
    return json.dumps(mock_config)

@pytest.fixture
def sample_accounts():
    return [
        {"title": "Checking", "current_balance": 1000},
        {"title": "Savings", "current_balance": 5000},
        {"title": "401k", "current_balance": 20000},
        {"title": "Honda Civic", "current_balance": -30000},
        {"title": "My Condo", "current_balance": 500000}
    ]

@pytest.fixture
def sample_transactions():
    return [
        {"amount": -2000, "category": {"title": "Rent"}},
        {"amount": -100, "category": {"title": "Utilities"}},
        {"amount": -80, "category": {"title": "Internet"}},
        {"amount": -150, "category": {"title": "Groceries"}},  # Should be ignored by API total
        {"amount": -50, "category": {"title": "Misc"}}        # Should be ignored (not in mandatory list)
    ]
