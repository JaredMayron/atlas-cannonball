import pytest
from src.processor import DataProcessor


def test_categorize_accounts(mock_config_json, sample_accounts):
    """Test that accounts are correctly categorized based on configuration."""
    # Arrange
    processor = DataProcessor(mock_config_json)

    # Act
    categorized = processor.categorize_accounts(sample_accounts)

    # Assert
    assert len(categorized) == 5
    assert categorized[0]["type"] == "Cash"  # Checking -> Cash
    assert categorized[1]["type"] == "Cash"  # Savings -> Cash
    assert categorized[2]["type"] == "Investment"  # 401k -> Investment
    assert categorized[3]["type"] == "Car"  # Honda -> Car
    assert categorized[4]["type"] == "Condo"  # My Condo -> Condo


def test_calculate_mandatory_spending(mock_config_json, sample_transactions):
    """Test calculation of mandatory spending including manual estimates."""
    # Arrange
    processor = DataProcessor(mock_config_json)

    # Act
    spending = processor.calculate_mandatory_spending(sample_transactions)

    # Assert
    # API Mandatory: Rent(2000) + Utilities(100) + Internet(80) = 2180
    assert spending["api_mandatory_spend"] == 2180

    # Manual Estimates: Groceries(500) + Restaurant(200) + Health(300) = 1000
    assert spending["manual_estimates"]["Groceries"] == 500

    # Grand Total: 2180 + 1000 = 3180 -> rounded to 3200
    assert spending["grand_total_annual"] == 3200
    assert spending["grand_total_daily"] == pytest.approx(3200 / 365)


def test_calculate_runway(mock_config_json):
    """Test financial runway calculation."""
    # Arrange
    processor = DataProcessor(mock_config_json)

    categorized_accounts = [
        {"type": "Cash", "balance": 10000},
        {"type": "Investment", "balance": 50000},
    ]
    spending = {"grand_total_annual": 5000}

    # Act
    runway = processor.calculate_runway(categorized_accounts, spending)

    # Assert
    assert runway["cash_on_hand"] == 10000
    assert runway["annual_burn"] == 5000
    assert runway["runway_years"] == 2.0
    assert runway["runway_days"] == 730


def test_calculate_runway_zero_burn(mock_config_json):
    """Test that zero or negative burn rate doesn't crash calculations."""
    # Arrange
    processor = DataProcessor(mock_config_json)
    accounts = [{"type": "Cash", "balance": 1000}]

    # Act
    runway_zero = processor.calculate_runway(accounts, {"grand_total_annual": 0})
    runway_negative = processor.calculate_runway(accounts, {"grand_total_annual": -100})

    # Assert
    assert runway_zero is None
    assert runway_negative is None


def test_validate_config_missing_keys():
    """Test that DataProcessor raises ValueError on missing required config keys."""
    # Arrange
    invalid_config = '{"CASH_TITLES": ["CHECKING"]}'  # Missing others

    # Act & Assert
    import pytest
    with pytest.raises(ValueError) as excinfo:
        DataProcessor(invalid_config)
    
    assert "Missing required configuration keys" in str(excinfo.value)
    assert "INVESTMENT_TITLES" in str(excinfo.value)
    assert "API_CALCULATED_CATEGORIES" in str(excinfo.value)


def test_categorize_accounts_schema_error_logging(mock_config_json, caplog):
    """Test that malformed accounts are skipped and logged."""
    # Arrange
    processor = DataProcessor(mock_config_json)
    dirty_accounts = [
        {"title": "Valid", "current_balance": 100},
        {"current_balance": 100},  # Missing title
    ]

    # Act
    with caplog.at_level("WARNING"):
        categorized = processor.categorize_accounts(dirty_accounts)

    # Assert
    assert len(categorized) == 1
    assert "Skipping malformed account" in caplog.text
    assert "title" in caplog.text


def test_calculate_spending_schema_error_logging(mock_config_json, caplog):
    """Test that malformed transactions are skipped and logged."""
    # Arrange
    processor = DataProcessor(mock_config_json)
    dirty_transactions = [
        {"amount": -100, "category": {"title": "Rent"}},
        {"category": {"title": "Rent"}},  # Missing amount
    ]

    # Act
    with caplog.at_level("WARNING"):
        spending = processor.calculate_mandatory_spending(dirty_transactions)

    # Assert
    assert spending["api_mandatory_spend"] == 100
    assert "Skipping malformed transaction" in caplog.text
    assert "amount" in caplog.text
