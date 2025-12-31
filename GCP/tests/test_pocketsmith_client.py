import pytest
import requests
from src.pocketsmith_client import PocketSmithClient

def test_get_accounts(requests_mock):
    client = PocketSmithClient(api_key="test_key", user_id="123")
    mock_response = [{"id": 1, "title": "Test Account"}]
    
    requests_mock.get("https://api.pocketsmith.com/v2/users/123/accounts", json=mock_response)
    
    accounts = client.get_accounts()
    assert accounts == mock_response
    assert requests_mock.called

def test_get_transactions_past_year_paginated(requests_mock):
    client = PocketSmithClient(api_key="test_key", user_id="123")
    
    # Mocking two pages of results
    page1 = [{"id": 101, "amount": -10}]
    page2 = [{"id": 102, "amount": -20}]
    empty_page = []
    
    url = "https://api.pocketsmith.com/v2/users/123/transactions"
    
    # We use a side effect to return different values for each call
    requests_mock.get(url, [
        {"json": page1},
        {"json": page2},
        {"json": empty_page}
    ])
    
    transactions = client.get_transactions_past_year()
    
    assert len(transactions) == 2
    assert transactions[0]["id"] == 101
    assert transactions[1]["id"] == 102
    assert requests_mock.call_count == 3
