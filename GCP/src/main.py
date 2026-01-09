import os
import logging
import requests
from google.api_core import exceptions
from pocketsmith_client import PocketSmithClient
from processor import DataProcessor
from bigquery_client import BigQueryClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("--- Starting Daily Data Refresh (Cloud Run Job) ---")

    # 1. Load Configuration (from Secret Manager or Env)
    # TODO: Implement Secret Manager loading
    api_key = os.getenv("POCKETSMITH_API_KEY")
    user_id = os.getenv("POCKETSMITH_USER_ID")
    config_json = os.getenv("CONFIG_JSON")  # Contains CATEGORIES, TITLES, etc.

    if not api_key or not user_id:
        logger.error("Missing required environment variables.")
        return

    powerquery_client = PocketSmithClient(api_key, user_id)
    bq_client = BigQueryClient()
    processor = DataProcessor(config_json)

    try:
        # 2. Fetch Accounts
        logger.info("Fetching accounts from PocketSmith...")
        accounts = powerquery_client.get_accounts()
        categorized_accounts = processor.categorize_accounts(accounts)

        # 3. Fetch Transactions (Mandatory Spending)
        logger.info("Fetching transactions for mandatory spending...")
        transactions = powerquery_client.get_transactions_past_year()
        mandatory_spending = processor.calculate_mandatory_spending(transactions)

        # 4. Calculate Runway
        logger.info("Calculating financial runway...")
        runway_metrics = processor.calculate_runway(
            categorized_accounts, mandatory_spending
        )

        # 5. Push to BigQuery
        logger.info("Pushing results to BigQuery...")
        bq_client.write_accounts(categorized_accounts)
        bq_client.write_spending(mandatory_spending)
        bq_client.write_runway(runway_metrics)

        logger.info("--- Refresh Complete ---")

    except requests.exceptions.RequestException as e:
        logger.error(f"PocketSmith API Error: {e}")
    except exceptions.GoogleAPICallError as e:
        logger.error(f"BigQuery API Error: {e}")
    except Exception as e:
        logger.exception(f"An error occurred during the data refresh: {e}")


if __name__ == "__main__":
    main()
