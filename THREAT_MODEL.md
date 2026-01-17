# Threat Model: Atlas Cannonball

This document provides a STRIDE-based threat model for the Atlas Cannonball financial tracking system. It reflects the current logical architecture and security posture as of the latest repository state.

## Logical Architecture
The following ASCII diagram illustrates the system's data flow and trust boundaries.

```text
                                  [ TRUST BOUNDARY: Public Internet ]
                                                |
    +-----------------------+                   |               +----------------------+
    |  Financial Sources    |                   |               |  PocketSmith API     |
    | (Banks/Plaid/Yodlee)  |---[Aggregation]-->|---(HTTPS)---->|  (External Provider) |
    +-----------------------+                   |               +----------|-----------+
                                                |                          | (HTTPS + API Key)
    --------------------------------------------|--------------------------|-----------
                                                |                          |
                                  [ TRUST BOUNDARY: Google Cloud Platform ]|
                                                |                          v
    +-----------------------+                   |               +----------------------+
    |  GitHub Repository    |---(Webhook)-------|-------------->|  Cloud Build         |
    |  (Source Code)        |                   |               |  (CI/CD Pipeline)    |
    +-----------------------+                   |               +----------|-----------+
                                                |                          | (Docker Push)
    +-----------------------+                   |                          v
    |  Cloud Scheduler      |---(Internal OIDC)-|-------------->+----------------------+
    |  (Trigger)            |                   |               |  Artifact Registry   |
    +-----------------------+                   |               |  (Image Storage)     |
                                                |               +----------|-----------+
                                                |                          | (Docker Pull)
    +-----------------------+                   |                          v
    |  Secret Manager       |<--(IAM Auth)------|--------------->+----------------------+
    |  (API Keys / Config)  |                   |               |  Cloud Run Job       |
    +-----------------------+                   |               |  (Python Processor)  |
                                                |               +----------|-----------+
                                                |                          |
                                                |               +----------|-----------+
                                                |               |   BigQuery           |
                                                |               |   (Data Warehouse)   |
                                                |               +----------|-----------+
                                                |                          | (IAM Auth)
    --------------------------------------------|--------------------------|-----------
                                                |                          |
                                  [ TRUST BOUNDARY: Visualization ]        v
                                                |               +----------------------+
                                                |               |   Evidence Studio    |
                                                |               |   (Dashboards)       |
                                                |               +----------------------+
```

## Trust Boundaries
1.  **Supply Chain Boundary**: The connection between GitHub, Cloud Build, and Artifact Registry. Secured via validated GitHub webhooks and specialized build service accounts.
2.  **PocketSmith Boundary (Inbound)**: The gap between the external PocketSmith API and the GCP environment. Communication is secured via TLS and authenticated with a Developer Key (stored in Secret Manager).
3.  **Cloud Run Perimeter (Compute)**: The internal environment where financial calculations occur. Protected by IAM; secrets are injected at runtime and never stored in the source code.
4.  **BigQuery Storage (Persistence)**: The central repository for processed data. Access is strictly controlled via fine-grained Service Account permissions.
5.  **Evidence Studio (Outbound)**: External visualization layer with read-only access to specific BigQuery tables.

---

## STRIDE Analysis

| Category | Threat | Status | Mitigations |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker mimics the Cloud Run Job to inject malicious data into BigQuery. | **MITIGATED** | BigQuery access is restricted to a unique Service Account (`financial-refresh-job-sa`) with OIDC authentication. |
| **Tampering** | Modification of transaction data in transit or build artifacts in registry. | **MITIGATED** | All communication uses HTTPS/TLS. Cloud Build uses unique image tags; Artifact Registry restricts write access to the build SA. |
| **Repudiation** | Actions performed by service accounts are not auditable. | **MITIGATED** | GCP Cloud Logging captures all service account interactions and job execution history. |
| **Information Disclosure** | Leakage of API Keys or User IDs during build or runtime. | **MITIGATED** | Secret Manager handles storage; secrets are injected as environment variables. Code reviews ensure `logging` calls do not leak secret values. |
| **Denial of Service** | Sustained API failures or job timeouts leading to data staleness. | **MITIGATED** | Cloud Run Jobs have a 10-minute timeout; Cloud Scheduler retries on failures (configured in `cloud_run.tf`). |
| **Elevation of Privilege** | Compromised Job SA gains access to non-financial secrets or other project resources. | **MITIGATED** | Service accounts follow Principle of Least Privilege (PoLP). IAM Audit confirmed appropriate scoping. |

---

## Security Resolutions (Feedback Incorporated)
Based on `THREAT_MODEL_FEEDBACK.md`, the following previously identified gaps have been resolved:

- **IAM Audit**: A complete review of `GCP/terraform/iam.tf` confirmed that the Service Accounts are appropriately scoped to specialized roles (e.g., `roles/bigquery.dataEditor`, `roles/secretmanager.secretAccessor`).
- **SQL Injection Check**: Manual review and SAST scanning of `GCP/src/bigquery_client.py` confirmed that data fields are not injectable. Parameterized queries/templates are used for data mutation and deletion (using `bigquery.ScalarQueryParameter`).

---

## Remaining Gaps & Monitoring
- **API Health**: No automated alerting currently exists if the PocketSmith API key expires or if rate limits are reached.
- **Dependency Vulnerabilities**: Regular scanning of Python dependencies in `pyproject.toml` and `uv.lock` is recommended (e.g., via `pip-audit` or Dependabot).
- **Deletion Protection**: BigQuery tables currently have `deletion_protection = false` in Terraform, which increases the risk of accidental data loss during infrastructure updates.
- **Log Masking**: While secrets themselves aren't logged, large JSON configurations (`CONFIG_JSON`) could potentially be logged in debugging scenarios; consider explicit masking.

---

## Changelog
- **2026-01-13**: Refreshed to include Artifact Registry and supply chain components in the architecture and analysis.
- **2026-01-13 (Earlier)**: Refreshed to include Cloud Build CI/CD pipeline in the logical architecture and trust boundaries.
- **2026-01-12**: Full refresh of the threat model.
    - Added ASCII Logical Architecture diagram.
    - Broadened analysis to include the Cloud Scheduler trigger.
    - Incorporated audit feedback regarding IAM scoping and SQL injection mitigation.
