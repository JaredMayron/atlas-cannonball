import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()

    def write_accounts(self, categorized_accounts):
        # TODO: Get table ID from config/env
        table_id = "finance-dashboard-481505.financial_data.accounts_raw"
        
        # Deduplication: Delete existing entries for today's snapshot_date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE snapshot_date = '{today}'
        """
        try:
            query_job = self.client.query(delete_query)
            query_job.result() # Wait for job to complete
            logger.info(f"Cleared existing entries for {today} to prevent duplicates.")
        except Exception as e:
            logger.warning(f"Failed to clear existing entries (table might not exist yet): {e}")

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

    def write_spending(self, mandatory_spending):
        import json
        table_id = "finance-dashboard-481505.financial_data.mandatory_spending"
        
        # Ensure manual_estimates is serialized if it exists
        if "manual_estimates" in mandatory_spending:
            mandatory_spending["manual_estimates"] = json.dumps(mandatory_spending["manual_estimates"])
            
        # Use Load Job
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        try:
            job = self.client.load_table_from_json([mandatory_spending], table_id, job_config=job_config)
            job.result()
            logger.info("Successfully loaded spending into BigQuery.")
        except Exception as e:
            logger.error(f"Failed to load spending: {e}")

    def write_runway(self, runway_metrics):
        if not runway_metrics:
            return
        table_id = "finance-dashboard-481505.financial_data.runway_info"
        
        # Deduplication: Delete existing entries for today's snapshot_date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE snapshot_date = '{today}'
        """
        try:
            query_job = self.client.query(delete_query)
            query_job.result()
            logger.info(f"Cleared existing runway entries for {today}.")
        except Exception as e:
            logger.warning(f"Failed to clear existing runway entries: {e}")

        # Use Load Job
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        try:
            job = self.client.load_table_from_json([runway_metrics], table_id, job_config=job_config)
            job.result()
            logger.info("Successfully loaded runway metrics into BigQuery.")
        except Exception as e:
            logger.error(f"Failed to load runway metrics: {e}")
