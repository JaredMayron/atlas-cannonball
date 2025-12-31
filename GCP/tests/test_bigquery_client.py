import pytest
from unittest.mock import MagicMock, patch
from src.bigquery_client import BigQueryClient

@patch("google.cloud.bigquery.Client")
def test_write_accounts(mock_bq_client):
    client = BigQueryClient()
    mock_instance = mock_bq_client.return_value
    mock_instance.insert_rows_json.return_value = [] # No errors
    
    data = [{"title": "Checking", "balance": 1000}]
    client.write_accounts(data)
    
    mock_instance.insert_rows_json.assert_called_once_with(
        "your_project.your_dataset.accounts_raw", data
    )

@patch("google.cloud.bigquery.Client")
def test_write_spending(mock_bq_client):
    client = BigQueryClient()
    mock_instance = mock_bq_client.return_value
    mock_instance.insert_rows_json.return_value = []
    
    data = {"api_mandatory_spend": 2180}
    client.write_spending(data)
    
    mock_instance.insert_rows_json.assert_called_once_with(
        "your_project.your_dataset.mandatory_spending", [data]
    )

@patch("google.cloud.bigquery.Client")
def test_write_runway(mock_bq_client):
    client = BigQueryClient()
    mock_instance = mock_bq_client.return_value
    mock_instance.insert_rows_json.return_value = []
    
    data = {"runway_days": 730}
    client.write_runway(data)
    
    mock_instance.insert_rows_json.assert_called_once_with(
        "your_project.your_dataset.runway_info", [data]
    )

@patch("google.cloud.bigquery.Client")
def test_write_accounts_with_errors(mock_bq_client, caplog):
    client = BigQueryClient()
    mock_instance = mock_bq_client.return_value
    mock_instance.insert_rows_json.return_value = [{"error": "something went wrong"}]
    
    client.write_accounts([])
    
    assert "Encountered errors while inserting accounts" in caplog.text
