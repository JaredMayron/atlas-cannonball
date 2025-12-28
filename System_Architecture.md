# End-to-End System Architecture

This diagram illustrates the flow of financial data from various sources into the final visualization dashboards.

## Data Flow Diagram

```mermaid
graph TD
    subgraph "External Sources"
        Banks["Individual Banks"]
        CCs["Credit Cards"]
        Portfolios["Investment Portfolios"]
        RE["Real Estate"]
        Other["Other Assets"]
    end

    subgraph "Aggregation & API Layer"
        PS[("PocketSmith")]
    end

    subgraph "Automation &<br/>Transformation"
        GAS["Google Apps Script"]
        GS[("Google Sheets")]
    end

    subgraph "Data Warehouse"
        BQ[("BigQuery")]
    end

    subgraph "Visualization <br>(Evidence.Studio)"
        E_NetWorth["Net Worth Dashboard"]
        E_CashReserves["Cash Reserves Dashboard"]
    end

    %% Data Flow Connections
    Banks & CCs & Portfolios & RE & Other -- "Plaid / Yodlee" --> PS
    PS -- "REST API" --> GAS
    GAS -- "Process / Categorize" --> GS
    GS -- "Sheet Connection / Sync" --> BQ
    BQ -- "SQL Queries" --> E_NetWorth
    BQ -- "SQL Queries" --> E_CashReserves
```

## Flow Description

1.  **Ingestion**: Financial data from banks, credit cards, investment accounts, real estate, and other assets is automatically aggregated by **PocketSmith** via **Plaid / Yodlee**.
2.  **Extraction**: **Google Apps Script** pulls raw transaction and account data from the **PocketSmith** API on a daily schedule.
3.  **Transformation**: The script categorizes accounts (e.g., "Cash", "Investment") and calculates metrics like mandatory spending and financial runway.
4.  **Staging**: The processed data is written to dedicated tabs in a **Google Sheet**.
5.  **Storage**: The Google Sheet is synchronized with **BigQuery**, acting as the central data warehouse.
6.  **Visualization**: **Evidence Studio** dashboards (`Net Worth.md` and `Cash Reserves.md`) query the BigQuery tables using SQL to generate interactive reports and visualizations.
