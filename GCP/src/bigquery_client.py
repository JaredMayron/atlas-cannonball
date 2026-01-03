import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()

    def write_accounts(self, categorized_accounts):
        if not categorized_accounts:
            logger.warning("No accounts to write.")
            return

        # Deduplicate payload: Remove exact duplicate dictionaries from the list
        # This protects against upstream API issues returning duplicate accounts
        unique_accounts = []
        seen_accounts = set()
        for acc in categorized_accounts:
            # Create a tuple of items to allow hashing
            acc_tuple = tuple(sorted(acc.items()))
            if acc_tuple not in seen_accounts:
                seen_accounts.add(acc_tuple)
                unique_accounts.append(acc)
        
        if len(unique_accounts) < len(categorized_accounts):
            logger.info(f"Removed {len(categorized_accounts) - len(unique_accounts)} duplicate accounts from payload.")
        
        categorized_accounts = unique_accounts

        # TODO: Get table ID from config/env
        table_id = "finance-dashboard-481505.financial_data.accounts_raw"
        
        # Deduplication: Use date from the data itself
        snapshot_date = categorized_accounts[0].get("snapshot_date")
        if not snapshot_date:
            from datetime import datetime
            snapshot_date = datetime.now().strftime("%Y-%m-%d")
            logger.warning(f"Snapshot date missing in data, using current date: {snapshot_date}")

        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE snapshot_date = '{snapshot_date}'
        """
        try:
            query_job = self.client.query(delete_query)
            query_job.result() # Wait for job to complete
            logger.info(f"Cleared existing entries for {snapshot_date} to prevent duplicates.")
        except Exception as e:
            if "Not found" in str(e):
                logger.info(f"Table {table_id} not found, proceeding to create it.")
            else:
                logger.error(f"Failed to clear existing entries: {e}")
                raise e

        # Use Load Job instead of Streaming Insert
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND", # We already handled dedup via DELETE
        )
        try:
            job = self.client.load_table_from_json(categorized_accounts, table_id, job_config=job_config)
            job.result() # Wait for loading to complete
            logger.info("Successfully loaded accounts into BigQuery.")
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
            raise e

    def write_spending(self, mandatory_spending):
        if not mandatory_spending:
            return

        import json
        table_id = "finance-dashboard-481505.financial_data.mandatory_spending"
        
        # Ensure manual_estimates is serialized if it exists
        if "manual_estimates" in mandatory_spending:
            mandatory_spending["manual_estimates"] = json.dumps(mandatory_spending["manual_estimates"])
            
        # Deduplication: Use date from data
        snapshot_date = mandatory_spending.get("snapshot_date")
        if not snapshot_date:
            from datetime import datetime
            snapshot_date = datetime.now().strftime("%Y-%m-%d")

        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE snapshot_date = '{snapshot_date}'
        """
        try:
            query_job = self.client.query(delete_query)
            query_job.result()
            logger.info(f"Cleared existing spending entries for {snapshot_date}.")
        except Exception as e:
            if "Not found" in str(e):
                 logger.info(f"Table {table_id} not found, proceeding.")
            else:
                logger.error(f"Failed to clear existing spending entries: {e}")
                raise e

        # Use Load Job
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        try:
            job = self.client.load_table_from_json([mandatory_spending], table_id, job_config=job_config)
            job.result()
            logger.info("Successfully loaded spending into BigQuery.")
        except Exception as e:
            logger.error(f"Failed to load spending: {e}")
            raise e

    def write_runway(self, runway_metrics):
        if not runway_metrics:
            return
        table_id = "finance-dashboard-481505.financial_data.runway_info"
        
        # Deduplication: Use date from data
        snapshot_date = runway_metrics.get("snapshot_date")
        if not snapshot_date:
            from datetime import datetime
            snapshot_date = datetime.now().strftime("%Y-%m-%d")

        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE snapshot_date = '{snapshot_date}'
        """
        try:
            query_job = self.client.query(delete_query)
            query_job.result()
            logger.info(f"Cleared existing runway entries for {snapshot_date}.")
        except Exception as e:
            if "Not found" in str(e):
                logger.info(f"Table {table_id} not found, proceeding.")
            else:
                logger.error(f"Failed to clear existing runway entries: {e}")
                raise e

        # Use Load Job
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        try:
            job = self.client.load_table_from_json([runway_metrics], table_id, job_config=job_config)
            job.result()
            logger.info("Successfully loaded runway metrics into BigQuery.")
        except Exception as e:
            logger.error(f"Failed to load runway metrics: {e}")
            raise e
