import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()

    def write_accounts(self, categorized_accounts):
        # TODO: Get table ID from config/env
        table_id = "finance-dashboard-481505.financial_data.accounts_raw"
        errors = self.client.insert_rows_json(table_id, categorized_accounts)
        if errors:
            logger.error(f"Encountered errors while inserting accounts: {errors}")
        else:
            logger.info("Successfully inserted accounts into BigQuery.")

    def write_spending(self, mandatory_spending):
        import json
        table_id = "finance-dashboard-481505.financial_data.mandatory_spending"
        
        # Ensure manual_estimates is serialized if it exists
        if "manual_estimates" in mandatory_spending:
            mandatory_spending["manual_estimates"] = json.dumps(mandatory_spending["manual_estimates"])
            
        errors = self.client.insert_rows_json(table_id, [mandatory_spending])
        if errors:
            logger.error(f"Encountered errors while inserting spending: {errors}")
        else:
            logger.info("Successfully inserted spending into BigQuery.")

    def write_runway(self, runway_metrics):
        if not runway_metrics:
            return
        table_id = "finance-dashboard-481505.financial_data.runway_info"
        errors = self.client.insert_rows_json(table_id, [runway_metrics])
        if errors:
            logger.error(f"Encountered errors while inserting runway: {errors}")
        else:
            logger.info("Successfully inserted runway metrics into BigQuery.")
