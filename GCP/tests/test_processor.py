import pytest
from src.processor import DataProcessor

def test_categorize_accounts(mock_config_json, sample_accounts):
    processor = DataProcessor(mock_config_json)
    categorized = processor.categorize_accounts(sample_accounts)
    
    assert len(categorized) == 5
    
    # Checking -> Cash
    assert categorized[0]["type"] == "Cash"
    # Savings -> Cash
    assert categorized[1]["type"] == "Cash"
    # 401k -> Investment
    assert categorized[2]["type"] == "Investment"
    # Honda -> Car
    assert categorized[3]["type"] == "Car"
    # My Condo -> Condo
    assert categorized[4]["type"] == "Condo"

def test_calculate_mandatory_spending(mock_config_json, sample_transactions):
    processor = DataProcessor(mock_config_json)
    spending = processor.calculate_mandatory_spending(sample_transactions)
    
    # API Mandatory: Rent(2000) + Utilities(100) + Internet(80) = 2180
    assert spending["api_mandatory_spend"] == 2180
    
    # Manual Estimates: Groceries(500) + Restaurant(200) + Health(300) = 1000
    assert spending["manual_estimates"]["Groceries"] == 500
    
    # Grand Total: 2180 + 1000 = 3180
    assert spending["grand_total_annual"] == 3180
    assert spending["grand_total_daily"] == pytest.approx(3180 / 365)

def test_calculate_runway(mock_config_json):
    processor = DataProcessor(mock_config_json)
    
    categorized_accounts = [
        {"type": "Cash", "balance": 10000},
        {"type": "Investment", "balance": 50000}
    ]
    spending = {
        "grand_total_annual": 5000
    }
    
    runway = processor.calculate_runway(categorized_accounts, spending)
    
    assert runway["cash_on_hand"] == 10000
    assert runway["annual_burn"] == 5000
    assert runway["runway_years"] == 2.0
    assert runway["runway_days"] == 730
