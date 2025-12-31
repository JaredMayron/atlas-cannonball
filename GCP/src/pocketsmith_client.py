import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PocketSmithClient:
    def __init__(self, api_key, user_id):
        self.api_key = api_key
        self.user_id = user_id
        self.base_url = f"https://api.pocketsmith.com/v2/users/{user_id}"
        self.headers = {
            "Accept": "application/json",
            "X-Developer-Key": api_key
        }

    def get_accounts(self):
        url = f"{self.base_url}/accounts"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_transactions_past_year(self):
        # Calculate dates
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=365)
        
        url = f"{self.base_url}/transactions"
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "uncategorised": 0,
            "type": "debit"
        }
        
        all_transactions = []
        page = 1
        while True:
            params["page"] = page
            logger.info(f"Fetching transactions page {page}...")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            all_transactions.extend(data)
            page += 1
        
        return all_transactions
