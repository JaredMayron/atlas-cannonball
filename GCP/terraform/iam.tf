resource "google_secret_manager_secret" "pocketsmith_api_key" {
  secret_id = "pocketsmith_api_key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "pocketsmith_user_id" {
  secret_id = "pocketsmith_user_id"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "config_json" {
  secret_id = "config_json"
  replication {
    auto {}
  }
}

# Service Account for the Cloud Run Job
resource "google_service_account" "job_sa" {
  account_id   = "financial-refresh-job-sa"
  display_name = "Financial Data Refresh Job Service Account"
}

# Permissions
resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "api_key_accessor" {
  secret_id = google_secret_manager_secret.pocketsmith_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "user_id_accessor" {
  secret_id = google_secret_manager_secret.pocketsmith_user_id.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "config_accessor" {
  secret_id = google_secret_manager_secret.config_json.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_sa.email}"
}

# Evidence Access Service Account Permissions
resource "google_project_iam_member" "evidence_access_bq_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:evidence-access@finance-dashboard-481505.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "evidence_access_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:evidence-access@finance-dashboard-481505.iam.gserviceaccount.com"
}
