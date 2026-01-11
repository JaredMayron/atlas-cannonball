import pytest
from unittest.mock import MagicMock, patch
import datetime
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
    Test that write_accounts deduplicates input, cleans old data, and loads new data.
    """
    # Arrange
    mock_instance = mock_bq_client.return_value
    mock_query_job = MagicMock()
    mock_load_job = MagicMock()
    mock_instance.query.return_value = mock_query_job
    mock_instance.load_table_from_json.return_value = mock_load_job

    data = [
        {"title": "Checking", "balance": 1000},
        {"title": "Checking", "balance": 1000},  # Duplicate
        {"title": "Savings", "balance": 5000},
    ]

    # Act
    client.write_accounts(data)

    # Assert
    # 1. Check Delete Query
    assert mock_instance.query.called
    delete_query = mock_instance.query.call_args[0][0]
    assert (
        "DELETE FROM `finance-dashboard-481505.financial_data.accounts_raw`"
        in delete_query
    )
    assert "WHERE snapshot_date = @snapshot_date" in delete_query

    # 2. Verify Query Parameters
    _, kwargs = mock_instance.query.call_args
    job_config = kwargs["job_config"]
    assert isinstance(job_config, bigquery.QueryJobConfig)
    assert job_config.query_parameters[0].name == "snapshot_date"

    # 3. Check Load Job and Deduplication
    assert mock_instance.load_table_from_json.called
    args, kwargs = mock_instance.load_table_from_json.call_args
    uploaded_data = args[0]

    assert len(uploaded_data) == 2
    assert {"title": "Checking", "balance": 1000} in uploaded_data
    assert {"title": "Savings", "balance": 5000} in uploaded_data

    assert kwargs["job_config"].write_disposition == "WRITE_APPEND"


def test_write_accounts_empty(client, mock_bq_client):
    """Test that empty input returns early."""
    # Arrange
    mock_instance = mock_bq_client.return_value

    # Act
    client.write_accounts([])

    # Assert
    assert not mock_instance.query.called
    assert not mock_instance.load_table_from_json.called


def test_write_accounts_delete_error(client, mock_bq_client):
    """Test handling of errors during the DELETE phase."""
    # Arrange
    mock_instance = mock_bq_client.return_value
    mock_instance.query.side_effect = Exception("BigQuery Error")
    data = [{"title": "Checking", "snapshot_date": "2023-01-01"}]

    # Act & Assert
    with pytest.raises(Exception, match="BigQuery Error"):
        client.write_accounts(data)


def test_write_spending_success(client, mock_bq_client):
    """Test write_spending logic including JSON serialization of manual_estimates."""
    # Arrange
    mock_instance = mock_bq_client.return_value
    data = {
        "snapshot_date": "2023-10-27",
        "api_mandatory_spend": 2000,
        "manual_estimates": {"Rent": 1500},
    }

    # Act
    client.write_spending(data)

    # Assert
    # 1. Verify DELETE
    assert mock_instance.query.called
    delete_query = mock_instance.query.call_args[0][0]
    assert (
        "DELETE FROM `finance-dashboard-481505.financial_data.mandatory_spending`"
        in delete_query
    )
    assert "WHERE snapshot_date = @snapshot_date" in delete_query

    _, kwargs = mock_instance.query.call_args
    job_config = kwargs["job_config"]
    assert job_config.query_parameters[0].name == "snapshot_date"

    if isinstance(job_config.query_parameters[0].value, str):
        assert job_config.query_parameters[0].value == "2023-10-27"
    else:
        assert job_config.query_parameters[0].value == datetime.date(2023, 10, 27)

    # 2. Verify Load
    assert mock_instance.load_table_from_json.called
    args, _ = mock_instance.load_table_from_json.call_args
    uploaded_row = args[0][0]

    assert isinstance(uploaded_row["manual_estimates"], str)
    assert '"Rent": 1500' in uploaded_row["manual_estimates"]


def test_write_runway_success(client, mock_bq_client):
    """Test write_runway basic success path."""
    # Arrange
    mock_instance = mock_bq_client.return_value
    data = {"snapshot_date": "2023-10-27", "runway_days": 365}

    # Act
    client.write_runway(data)

    # Assert
    # 1. Verify DELETE
    delete_query = mock_instance.query.call_args[0][0]
    assert (
        "DELETE FROM `finance-dashboard-481505.financial_data.runway_info`"
        in delete_query
    )
    assert "WHERE snapshot_date = @snapshot_date" in delete_query

    _, kwargs = mock_instance.query.call_args
    job_config = kwargs["job_config"]
    if isinstance(job_config.query_parameters[0].value, str):
        assert job_config.query_parameters[0].value == "2023-10-27"
    else:
        assert job_config.query_parameters[0].value == datetime.date(2023, 10, 27)

    # 2. Verify Load
    mock_instance.load_table_from_json.assert_called()
