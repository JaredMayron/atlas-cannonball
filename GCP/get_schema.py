from google.cloud import bigquery
import json

project_id = "finance-dashboard-481505"
dataset_id = "financial_data"
tables = ["accounts_raw", "mandatory_spending", "runway_info"]

client = bigquery.Client(project=project_id)

for table_name in tables:
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    try:
        table = client.get_table(table_ref)
        schema_list = []
        for field in table.schema:
            schema_list.append({
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode
            })
        print(f"--- {table_name} ---")
        print(json.dumps(schema_list, indent=2))
    except Exception as e:
        print(f"Error getting {table_name}: {e}")
