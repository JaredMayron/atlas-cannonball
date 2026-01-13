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
    |  Cloud Scheduler      |---(Internal OIDC)-|-------------->|  Cloud Run Job       |
    |  (Trigger)            |                   |               |  (Python Processor)  |
    +-----------------------+                   |               +----------|-----------+
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
1.  **PocketSmith Boundary (Inbound)**: The gap between the external PocketSmith API and the GCP environment. Communication is secured via TLS and authenticated with a Developer Key.
2.  **Cloud Run Perimeter (Compute)**: The environment where financial calculations occur. Protected by IAM; secrets are never stored in the source code.
3.  **BigQuery Storage**: The central repository for processed data. Access is strictly controlled via fine-grained Service Account permissions.
4.  **Evidence Studio (Outbound)**: The visualization layer which has read-only access to specific BigQuery tables.

---

## STRIDE Analysis

| Category | Threat | Status | Mitigations |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker mimics the Cloud Run Job to inject malicious data. | **MITIGATED** | BigQuery access is restricted to a unique Service Account (`financial-refresh-job-sa`) with OIDC authentication. |
| **Tampering** | Man-in-the-middle modification of transaction data. | **MITIGATED** | All communication with PocketSmith and Google APIs uses HTTPS/TLS. |
| **Repudiation** | Lack of visibility into data refresh successes or failures. | **MITIGATED** | Cloud Logging captures stdout/stderr; Cloud Scheduler tracks execution history and deadlines. |
| **Information Disclosure** | Leakage of API Keys or User IDs. | **MITIGATED** | Secret Manager handles rotation and storage. `terraform` references secrets by version ID, not literal values. |
| **Denial of Service** | Sustained API failures cause the job to consume excessive compute resources. | **MITIGATED** | Cloud Run Jobs have a 10-minute timeout; Python code includes robust error handling to prevent infinite loops. |
| **Elevation of Privilege** | Compromised SA gains access to other GCP projects or resources. | **MITIGATED** | Service accounts follow Principle of Least Privilege (PoLP), as verified by recent manual code audit. |

---

## Security Resolutions (Feedback Incorporated)
Based on `THREAT_MODEL_FEEDBACK.md`, the following previously identified gaps have been resolved:

- **IAM Audit**: A complete review of `GCP/terraform/iam.tf` confirmed that the Service Accounts are appropriately scoped to specialized roles (`roles/bigquery.dataEditor`, `roles/secretmanager.secretAccessor`).
- **SQL Injection Check**: Manual review and SAST scanning of `GCP/src/bigquery_client.py` and `GCP/src/main.py` confirmed that data fields are not injectable. Parameterized queries/templates are used for data mutation and deletion.

---

## Remaining Gaps & Monitoring
- **API Health**: No automated alerting currently exists if the PocketSmith API key expires or if rate limits are reached.
- **Dependency Vulnerabilities**: Regular scanning of Python dependencies in `requirements.txt` is recommended to prevent upstream security risks.

---

## Changelog
- **2026-01-12**: Full refresh of the threat model.
    - Added ASCII Logical Architecture diagram.
    - Broadened analysis to include the Cloud Scheduler trigger.
    - Incorporated audit feedback regarding IAM scoping and SQL injection mitigation.
