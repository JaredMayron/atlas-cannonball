# Atlas Cannonball Infrastructure

This directory contains the Terraform configuration for managing the GCP infrastructure of the Atlas Cannonball project.

## Architecture

The infrastructure consists of:
- **Cloud Run Job**: Executes the financial data refresh process.
- **BigQuery**: Stores processed financial data.
- **Artifact Registry**: Hosts the Docker images for the Cloud Run jobs.
- **Secret Manager**: Securely stores API keys and sensitive configuration.
- **IAM**: Manages granular permissions for service accounts.

## Best Practices

This configuration follows industry best practices:
- **Environment Isolation**: Uses `.tfvars` files (e.g., `dev.tfvars`) and environment-specific labels.
- **State Management**: Prepared for GCS backend integration.
- **Resource Governance**: Consistent labeling for `Environment`, `Service`, `Owner`, and `ManagedBy`.
- **Modularity**: Resources reference each other dynamically instead of using hardcoded IDs.
- **Version Pinning**: Providers and required Terraform version are pinned.

## Setup & Deployment

1.  **Initialize Terraform**:
    ```bash
    terraform init
    ```

2.  **Select Environment**:
    Provide the appropriate `.tfvars` file during plan/apply.
    ```bash
    terraform plan -var-file=prod.tfvars
    ```

3.  **Apply Changes**:
    ```bash
    terraform apply -var-file=prod.tfvars
    ```

## Labels

All resources are tagged with the following labels for tracking and billing:
- `environment`: The deployment target (e.g., `dev`, `prod`).
- `service`: The logical service name (`financial-refresh`).
- `owner`: The repository owner.
- `managed-by`: Always set to `terraform`.
