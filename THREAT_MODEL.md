# Threat Model: Atlas Cannonball

This document provides a STRIDE-based threat model for the Atlas Cannonball financial tracking system. It reflects the current logical architecture and security posture of the repository.

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
                                                |                          |
    +-----------------------+                   |                          v
    |  Cloud Scheduler      |---(Internal OIDC)-|-------------->+----------------------+
    |  (Trigger)            |                   |               |  Cloud Run Job       |
    +-----------------------+                   |               |  (Python Processor)  |
                                                |               +----------|-----------+
                                                |                          |
    +-----------------------+                   |               +----------|-----------+
    |  Secret Manager       |<--(IAM Auth)------|---------------|   BigQuery           |
    |  (API Keys / Config)  |                   |               |   (Data Warehouse)   |
    +-----------------------+                   |               +----------|-----------+
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
1.  **Supply Chain Boundary**: The connection between GitHub and Cloud Build. Secured via validated GitHub webhooks and specialized build service accounts.
2.  **PocketSmith Boundary (Inbound)**: The gap between the external PocketSmith API and the GCP environment. Communication is secured via TLS and authenticated with a Developer Key.
3.  **Cloud Run Perimeter (Compute)**: The environment where financial calculations occur. Protected by IAM; secrets are never stored in the source code.
4.  **BigQuery Storage**: The central repository for processed data. Access is strictly controlled via fine-grained Service Account permissions.
5.  **Evidence Studio (Outbound)**: The visualization layer which has read-only access to specific BigQuery tables.

---

## STRIDE Analysis

| Category | Threat | Status | Mitigations |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker mimics the Cloud Run Job to inject malicious data. | **MITIGATED** | BigQuery access is restricted to a unique Service Account (`financial-refresh-job-sa`) with OIDC authentication. |
| **Tampering** | Man-in-the-middle modification of transaction data or build artifacts. | **MITIGATED** | All communication uses HTTPS/TLS. Cloud Build uses checksums for container images. |
| **Repudiation** | Lack of visibility into data refresh or build successes/failures. | **MITIGATED** | Cloud Logging captures logs; Cloud Scheduler and Cloud Build track execution history. |
| **Information Disclosure** | Leakage of API Keys or User IDs during build or runtime. | **MITIGATED** | Secret Manager handles storage. Build logs are configured to exclude sensitive output. |
| **Denial of Service** | Sustained API failures or build queue flooding. | **MITIGATED** | Cloud Run Jobs have timeouts; Cloud Build has concurrent build limits. |
| **Elevation of Privilege** | Compromised SA gains access to other GCP resources. | **MITIGATED** | Service accounts follow Principle of Least Privilege (PoLP). |

---

## Security Resolutions (Feedback Incorporated)
Based on `THREAT_MODEL_FEEDBACK.md`, the following previously identified gaps have been resolved:

- **IAM Audit**: A complete review of `GCP/terraform/iam.tf` confirmed that the Service Accounts are appropriately scoped to specialized roles (`roles/bigquery.dataEditor`, `roles/secretmanager.secretAccessor`).
- **SQL Injection Check**: Manual review and SAST scanning of `GCP/src/bigquery_client.py` and `GCP/src/main.py` confirmed that data fields are not injectable. Parameterized queries/templates are used for data mutation and deletion.

---

## Remaining Gaps & Monitoring
- **API Health**: No automated alerting currently exists if the PocketSmith API key expires or if rate limits are reached.
- **Dependency Vulnerabilities**: Regular scanning of Python dependencies in `requirements.txt` is recommended.

---

## Changelog
- **2026-01-13**: Refreshed to include Cloud Build CI/CD pipeline in the logical architecture and trust boundaries.
- **2026-01-12**: Full refresh of the threat model.
    - Added ASCII Logical Architecture diagram.
    - Broadened analysis to include the Cloud Scheduler trigger.
    - Incorporated audit feedback regarding IAM scoping and SQL injection mitigation.

