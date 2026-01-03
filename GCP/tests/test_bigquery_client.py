import pytest
from unittest.mock import MagicMock, patch, call
from src.bigquery_client import BigQueryClient
from google.cloud import bigquery

@pytest.fixture
def mock_bq_client():
    with patch("google.cloud.bigquery.Client") as mock:
        yield mock

@pytest.fixture
def client(mock_bq_client):
    return BigQueryClient()

def test_write_accounts_success(client, mock_bq_client):
    """
    Test that write_accounts:
    1. Deduplicates input data.
    2. Deletes existing data for the snapshot date.
    3. Loads the clean data using a LoadJob.
    """
    mock_instance = mock_bq_client.return_value
    mock_query_job = MagicMock()
    mock_load_job = MagicMock()
    mock_instance.query.return_value = mock_query_job
    mock_instance.load_table_from_json.return_value = mock_load_job

    # Input data with duplicates and missing date
    data = [
        {"title": "Checking", "balance": 1000},
        {"title": "Checking", "balance": 1000}, # Duplicate
        {"title": "Savings", "balance": 5000}
    ]
    
    # Expected execution
    client.write_accounts(data)

    # 1. Check Deduplication (implicitly checked by what's passed to load_table_from_json)
    # 2. Check Delete Query
    # We expect the DELETE query to use the current date since snapshot_date is missing
    assert mock_instance.query.called
    delete_query = mock_instance.query.call_args[0][0]
    assert "DELETE FROM `finance-dashboard-481505.financial_data.accounts_raw`" in delete_query
    
    # 3. Check Load Job
    assert mock_instance.load_table_from_json.called
    args, kwargs = mock_instance.load_table_from_json.call_args
    uploaded_data = args[0]
    
    # Verify duplicates are removed
    assert len(uploaded_data) == 2
    assert {"title": "Checking", "balance": 1000} in uploaded_data
    assert {"title": "Savings", "balance": 5000} in uploaded_data
    
    # Verify Job Config
    job_config = kwargs['job_config']
    assert job_config.write_disposition == "WRITE_APPEND"

def test_write_accounts_empty(client, mock_bq_client):
    """Test that empty input returns early."""
    client.write_accounts([])
    mock_instance = mock_bq_client.return_value
    assert not mock_instance.query.called
    assert not mock_instance.load_table_from_json.called

def test_write_accounts_delete_error(client, mock_bq_client):
    """Test handling of errors during the DELETE phase."""
    mock_instance = mock_bq_client.return_value
    mock_div = MagicMock()
    mock_instance.query.side_effect = Exception("BigQuery Error")
    
    data = [{"title": "Checking", "snapshot_date": "2023-01-01"}]
    
    with pytest.raises(Exception, match="BigQuery Error"):
        client.write_accounts(data)

def test_write_spending_success(client, mock_bq_client):
    """Test write_spending logic including JSON serialization of manual_estimates."""
    mock_instance = mock_bq_client.return_value
    
    data = {
        "snapshot_date": "2023-10-27",
        "api_mandatory_spend": 2000,
        "manual_estimates": {"Rent": 1500}
    }
    
    client.write_spending(data)
    
    # Verify DELETE
    assert mock_instance.query.called
    delete_query = mock_instance.query.call_args[0][0]
    assert "DELETE FROM `finance-dashboard-481505.financial_data.mandatory_spending`" in delete_query
    assert "2023-10-27" in delete_query

    # Verify Load
    assert mock_instance.load_table_from_json.called
    args, _ = mock_instance.load_table_from_json.call_args
    uploaded_row = args[0][0] # It's a list containing one dict
    
    # Check JSON serialization
    assert isinstance(uploaded_row["manual_estimates"], str)
    assert '"Rent": 1500' in uploaded_row["manual_estimates"]

def test_write_runway_success(client, mock_bq_client):
    """Test write_runway basic success path."""
    mock_instance = mock_bq_client.return_value
    
    data = {"snapshot_date": "2023-10-27", "runway_days": 365}
    
    client.write_runway(data)
    
    # Verify DELETE
    delete_query = mock_instance.query.call_args[0][0]
    assert "DELETE FROM `finance-dashboard-481505.financial_data.runway_info`" in delete_query
    
    # Verify Load
    mock_instance.load_table_from_json.assert_called()
