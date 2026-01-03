resource "google_cloud_run_v2_job" "financial_refresh" {
  name     = "financial-refresh"
  location = var.region

  template {
    template {
      service_account = google_service_account.job_sa.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/financial-refresh:latest"

        env {
          name = "POCKETSMITH_API_KEY"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.pocketsmith_api_key.secret_id
              version = "latest"
            }
          }
        }

        env {
          name = "POCKETSMITH_USER_ID"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.pocketsmith_user_id.secret_id
              version = "latest"
            }
          }
        }

        env {
          name = "CONFIG_JSON"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.config_json.secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].image,
    ]
  }
}

resource "google_cloud_scheduler_job" "refresh_timer" {
  name             = "financial-refresh-scheduler"
  description      = "Trigger financial data refresh every 6 hours"
  schedule         = "0 */6 * * *"
  time_zone        = "Etc/UTC"
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.financial_refresh.name}:run"

    oauth_token {
      service_account_email = google_service_account.job_sa.email
    }
  }
}
