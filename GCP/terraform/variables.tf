variable "project_id" {
  description = "The GCP project ID where resources will be deployed"
  type        = string
}

variable "region" {
  description = "The GCP region for regional resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "github_owner" {
  description = "Owner of the GitHub repository for Cloud Build triggers"
  type        = string
}

variable "github_repo" {
  description = "Name of the GitHub repository"
  type        = string
}
