terraform {
  required_version = ">= 1.5.0"

  # Recommended: Store state in GCS for environment isolation
  # backend "gcs" {
  #   bucket = "YOUR_TERRAFORM_STATE_BUCKET"
  #   prefix = "terraform/state"
  # }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.0.0" 
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  dataset_id = "financial_data"
}
