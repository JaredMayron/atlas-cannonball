import logging
from datetime import datetime
from google.cloud import bigquery
from google.api_core import exceptions
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()

    def write_accounts(self, categorized_accounts: List[Dict[str, Any]]) -> None:
        if not categorized_accounts:
            logger.warning("No accounts to write.")
            return

        unique_accounts = self._deduplicate_accounts(categorized_accounts)

        # TODO: Get table ID from config/env
        table_id = "finance-dashboard-481505.financial_data.accounts_raw"

        # Deduplication: Use date from the data itself
        snapshot_date = unique_accounts[0].get("snapshot_date")
        if not snapshot_date:
            snapshot_date = datetime.now().strftime("%Y-%m-%d")
            logger.warning(
                f"Snapshot date missing in data, using current date: {snapshot_date}"
            )

        self._delete_data_for_date(table_id, snapshot_date)

        # Use Load Job instead of Streaming Insert
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  # We already handled dedup via DELETE
        )
        self._load_data_to_bigquery(table_id, unique_accounts, job_config)

    def write_spending(self, mandatory_spending: Dict[str, Any]) -> None:
        if not mandatory_spending:
            return

        import json

        table_id = "finance-dashboard-481505.financial_data.mandatory_spending"

        # Ensure manual_estimates is serialized if it exists
        if "manual_estimates" in mandatory_spending:
            mandatory_spending["manual_estimates"] = json.dumps(
                mandatory_spending["manual_estimates"]
            )

        # Deduplication: Use date from data
        snapshot_date = mandatory_spending.get("snapshot_date")
        if not snapshot_date:
            snapshot_date = datetime.now().strftime("%Y-%m-%d")

        self._delete_data_for_date(table_id, snapshot_date)

        # Use Load Job
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        self._load_data_to_bigquery(table_id, [mandatory_spending], job_config)

    def write_runway(self, runway_metrics: Optional[Dict[str, Any]]) -> None:
        if not runway_metrics:
            return
        table_id = "finance-dashboard-481505.financial_data.runway_info"

        # Deduplication: Use date from data
        snapshot_date = runway_metrics.get("snapshot_date")
        if not snapshot_date:
            snapshot_date = datetime.now().strftime("%Y-%m-%d")

        self._delete_data_for_date(table_id, snapshot_date)

        # Use Load Job
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        self._load_data_to_bigquery(table_id, [runway_metrics], job_config)

    def _deduplicate_accounts(
        self, accounts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        unique_accounts = []
        seen_accounts = set()
        for acc in accounts:
            # Create a tuple of items to allow hashing
            acc_tuple = tuple(sorted(acc.items()))
            if acc_tuple not in seen_accounts:
                seen_accounts.add(acc_tuple)
                unique_accounts.append(acc)

        if len(unique_accounts) < len(accounts):
            logger.info(
                f"Removed {len(accounts) - len(unique_accounts)} duplicate accounts from payload."
            )
        return unique_accounts

    def _delete_data_for_date(self, table_id: str, snapshot_date: str) -> None:
        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE snapshot_date = @snapshot_date
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("snapshot_date", "DATE", snapshot_date)
            ]
        )
        try:
            query_job = self.client.query(delete_query, job_config=job_config)
            query_job.result()  # Wait for job to complete
            logger.info(f"Cleared existing entries for {snapshot_date} in {table_id}.")
        except exceptions.NotFound:
            logger.info(f"Table {table_id} not found, proceeding.")
        except exceptions.GoogleAPICallError as e:
            logger.error(f"Failed to clear existing entries: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error clearing existing entries: {e}")
            raise e

    def _load_data_to_bigquery(
        self,
        table_id: str,
        data: List[Dict[str, Any]],
        job_config: bigquery.LoadJobConfig,
    ) -> None:
        try:
            job = self.client.load_table_from_json(
                data, table_id, job_config=job_config
            )
            job.result()  # Wait for loading to complete
            logger.info(f"Successfully loaded data into {table_id}.")
        except exceptions.GoogleAPICallError as e:
            logger.error(f"Failed to load data: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            raise e
