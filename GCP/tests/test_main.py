import os
import pytest
from unittest.mock import patch, MagicMock
from src.main import main

@patch("src.main.PocketSmithClient")
@patch("src.main.BigQueryClient")
@patch("src.main.DataProcessor")
def test_main_flow(mock_processor_cls, mock_bq_client_cls, mock_ps_client_cls, mock_config_json):
    # Setup environment variables
    os.environ["POCKETSMITH_API_KEY"] = "test_key"
    os.environ["POCKETSMITH_USER_ID"] = "123"
    os.environ["CONFIG_JSON"] = mock_config_json
    
    # Mock instances
    mock_ps_client = mock_ps_client_cls.return_value
    mock_bq_client = mock_bq_client_cls.return_value
    mock_processor = mock_processor_cls.return_value
    
    # Mock behaviors
    mock_ps_client.get_accounts.return_value = [{"title": "test"}]
    mock_ps_client.get_transactions_past_year.return_value = [{"amount": -10}]
    
    mock_processor.categorize_accounts.return_value = [{"type": "Cash", "balance": 100}]
    mock_processor.calculate_mandatory_spending.return_value = {"grand_total_annual": 100}
    mock_processor.calculate_runway.return_value = {"runway_days": 365}
    
    # Run main
    main()
    
    # Verify calls
    mock_ps_client.get_accounts.assert_called_once()
    mock_ps_client.get_transactions_past_year.assert_called_once()
    mock_processor.categorize_accounts.assert_called_once()
    mock_processor.calculate_mandatory_spending.assert_called_once()
    mock_processor.calculate_runway.assert_called_once()
    
    assert mock_bq_client.write_accounts.called
    assert mock_bq_client.write_spending.called
    assert mock_bq_client.write_runway.called

def test_main_missing_env(caplog):
    # Ensure env vars are missing
    if "POCKETSMITH_API_KEY" in os.environ:
        del os.environ["POCKETSMITH_API_KEY"]
        
    main()
    
    assert "Missing required environment variables" in caplog.text
