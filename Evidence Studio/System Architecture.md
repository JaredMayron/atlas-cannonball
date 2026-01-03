# End-to-End System Architecture

This diagram illustrates the flow of financial data from various sources into the final visualization dashboards.

## Data Flow Diagram

{% image 
    url="https://raw.githubusercontent.com/JaredMayron/atlas-cannonball/refs/heads/main/Assets/architecture.svg"
    dark_url="https://raw.githubusercontent.com/JaredMayron/atlas-cannonball/refs/heads/main/Assets/architecture_dark.svg"
    description="System Architecture Diagram"
/%}

## Flow Description

1.  **Ingestion**: Financial data from banks, credit cards, investment accounts, real estate, and other assets is automatically aggregated by **PocketSmith** via **Plaid / Yodlee**.
2.  **Extraction & Transformation**: **GCP Cloud Run** (Python) pulls raw transaction and account data from the **PocketSmith** API, categorizes accounts, and calculates metrics.
3.  **Storage**: The processed data is pushed directly to **BigQuery**, acting as the central data warehouse.
4.  **Visualization**: This dashboard queries the BigQuery tables using SQL to generate interactive reports and visualizations.
