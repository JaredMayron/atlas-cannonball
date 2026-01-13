from src.pocketsmith_client import PocketSmithClient
from freezegun import freeze_time


def test_get_accounts(requests_mock):
    """Test retrieving accounts successfully."""
    # Arrange
    client = PocketSmithClient(api_key="test_key", user_id="123")
    mock_response = [{"id": 1, "title": "Test Account"}]
    requests_mock.get(
        "https://api.pocketsmith.com/v2/users/123/accounts", json=mock_response
    )

    # Act
    accounts = client.get_accounts()

    # Assert
    assert accounts == mock_response
    assert requests_mock.called


def test_get_transactions_past_year_paginated(requests_mock):
    """Test retrieving transactions with pagination support."""
    # Arrange
    client = PocketSmithClient(api_key="test_key", user_id="123")
    page1 = [{"id": 101, "amount": -10}]
    page2 = [{"id": 102, "amount": -20}]
    empty_page = []

    url = "https://api.pocketsmith.com/v2/users/123/transactions"
    requests_mock.get(url, [{"json": page1}, {"json": page2}, {"json": empty_page}])

    # Act
    transactions = client.get_transactions_past_year()

    # Assert
    assert len(transactions) == 2
    assert transactions[0]["id"] == 101
    assert transactions[1]["id"] == 102
    assert requests_mock.call_count == 3


def test_get_transactions_past_year_out_of_bounds(requests_mock):
    """Test handling of 'out of bounds' error from PocketSmith API."""
    # Arrange
    client = PocketSmithClient(api_key="test_key", user_id="123")
    url = "https://api.pocketsmith.com/v2/users/123/transactions"
    # Mocking first page success, second page 'out of bounds'
    requests_mock.get(
        url,
        [
            {"json": [{"id": 1, "amount": -10}]},
            {"status_code": 400, "text": "page is out of bounds"},
        ],
    )

    # Act
    transactions = client.get_transactions_past_year()

    # Assert
    assert len(transactions) == 1
    assert requests_mock.call_count == 2


def test_get_transactions_api_failure(requests_mock):
    """Test that API failures raise an exception."""
    import requests

    # Arrange
    client = PocketSmithClient(api_key="test_key", user_id="123")
    url = "https://api.pocketsmith.com/v2/users/123/transactions"
    requests_mock.get(url, status_code=500)

    # Act & Assert
    import pytest

    with pytest.raises(requests.exceptions.HTTPError):
        client.get_transactions_past_year()


@freeze_time("2026-01-13")
def test_get_transactions_date_calculation(requests_mock):
    """Test that start_date and end_date are calculated correctly using fixed time."""
    # Arrange
    client = PocketSmithClient(api_key="test_key", user_id="123")
    url = "https://api.pocketsmith.com/v2/users/123/transactions"
    requests_mock.get(url, json=[])

    # Act
    client.get_transactions_past_year()

    # Assert
    # Today is 2026-01-13
    # end_date = 2026-01-13 - 1 day = 2026-01-12
    # start_date = 2026-01-12 - 365 days = 2025-01-12
    last_request = requests_mock.request_history[0]
    assert last_request.qs["start_date"] == ["2025-01-12"]
    assert last_request.qs["end_date"] == ["2026-01-12"]


def test_request_headers(requests_mock):
    """Test that the correct headers are sent to the API."""
    # Arrange
    client = PocketSmithClient(api_key="secret_key", user_id="123")
    url = "https://api.pocketsmith.com/v2/users/123/accounts"
    requests_mock.get(url, json=[])

    # Act
    client.get_accounts()

    # Assert
    last_request = requests_mock.request_history[0]
    assert last_request.headers["X-Developer-Key"] == "secret_key"
    assert last_request.headers["Accept"] == "application/json"
