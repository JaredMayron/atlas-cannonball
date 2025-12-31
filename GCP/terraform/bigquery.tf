resource "google_bigquery_dataset" "financial_data" {
  dataset_id = local.dataset_id
  location   = var.region
}

resource "google_bigquery_table" "accounts_raw" {
  dataset_id = google_bigquery_dataset.financial_data.dataset_id
  table_id   = "accounts_raw"

  schema = <<EOF
[
  {"name": "title", "type": "STRING", "mode": "REQUIRED"},
  {"name": "balance", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "type", "type": "STRING", "mode": "REQUIRED"},
  {"name": "snapshot_date", "type": "DATE", "mode": "REQUIRED"}
]
EOF
}

resource "google_bigquery_table" "mandatory_spending" {
  dataset_id = google_bigquery_dataset.financial_data.dataset_id
  table_id   = "mandatory_spending"

  schema = <<EOF
[
  {"name": "api_mandatory_spend", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "grand_total_annual", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "grand_total_daily", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "snapshot_date", "type": "DATE", "mode": "REQUIRED"}
]
EOF
}

resource "google_bigquery_table" "runway_info" {
  dataset_id = google_bigquery_dataset.financial_data.dataset_id
  table_id   = "runway_info"

  schema = <<EOF
[
  {"name": "cash_on_hand", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "annual_burn", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "runway_days", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "runway_years", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "snapshot_date", "type": "DATE", "mode": "REQUIRED"}
]
EOF
}
