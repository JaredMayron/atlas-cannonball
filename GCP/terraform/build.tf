resource "google_cloudbuild_trigger" "financial_refresh" {
  name        = "financial-refresh-trigger"
  description = "Trigger for financial-refresh on push to main"

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }

  filename = "GCP/cloudbuild.yaml"

  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
}
