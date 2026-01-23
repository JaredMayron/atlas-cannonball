resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "financial-refresh-repo"
  description   = "Docker repository for financial refresh job"
  format        = "DOCKER"

  labels = {
    "environment" = lower(var.environment)
    "service"     = "financial-refresh"
    "owner"       = lower(var.github_owner)
    "managed-by"  = "terraform"
  }
}
