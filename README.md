# End-to-End System Architecture

> [!NOTE]
> This repository is for personal use and is maintained for historical tracking and display purposes. **Pull requests are not being accepted at this time.**

This diagram illustrates the flow of financial data from various sources into the final visualization dashboards.

## Data Flow Diagram

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./Assets/architecture_dark.svg">
  <img alt="System Architecture" src="./Assets/architecture.svg">
</picture>

## Flow Description

1.  **Ingestion**: Financial data from banks, credit cards, investment accounts, real estate, and other assets is automatically aggregated by **PocketSmith** via **Plaid / Yodlee**.
2.  **Extraction**: **Google Apps Script** pulls raw transaction and account data from the **PocketSmith** API on a daily schedule.
3.  **Transformation**: The script categorizes accounts (e.g., "Cash", "Investment") and calculates metrics like mandatory spending and financial runway.
4.  **Staging**: The processed data is written to dedicated tabs in a **Google Sheet**.
5.  **Storage**: The Google Sheet is synchronized with **BigQuery**, acting as the central data warehouse.
6.  **Visualization**: **Evidence Studio** dashboards (`Net Worth.md` and `Cash Reserves.md`) query the BigQuery tables using SQL to generate interactive reports and visualizations.

## Live Dashboards

- **Cash Reserves**: [https://www.evidence.studio/org_01KCNDDX3PYPNT5HNPSZQXZPKV/net-worth-appscript/cash-reserves](https://www.evidence.studio/org_01KCNDDX3PYPNT5HNPSZQXZPKV/net-worth-appscript/cash-reserves)
- **Net Worth**: [https://www.evidence.studio/org_01KCNDDX3PYPNT5HNPSZQXZPKV/net-worth-appscript/net-worth](https://www.evidence.studio/org_01KCNDDX3PYPNT5HNPSZQXZPKV/net-worth-appscript/net-worth)

## Configuration

To use this system, you must configure the following **Script Properties** in your Google Apps Script project:

| Property | Description | Example |
| :--- | :--- | :--- |
| `POCKETSMITH_API_KEY` | Your PocketSmith Developer Key | `your_api_key` |
| `POCKETSMITH_USER_ID` | Your PocketSmith User ID | `12345` |
| `GROCERIES_ESTIMATE` | Annual groceries spend estimate | `4000.00` |
| `RESTAURANT_ESTIMATE` | Annual restaurant spend estimate | `8000.00` |
| `HEALTH_INSURANCE_ESTIMATE` | Annual health insurance estimate | `6000.00` |
| `CASH_TITLES` | Comma-separated list of cash account titles | `Chase Checking, Ally Savings, Wells Fargo` |
| `INVESTMENT_TITLES` | Comma-separated list of investment account titles | `IRA, 401(K)` |
| `API_CALCULATED_CATEGORIES` | Categories to include in mandatory spend | `Mortgages, Utilities` |
| `CAR_IDENTIFIER` | Partial match for car assets | `Honda, Toyota` |
| `CONDO_IDENTIFIER` | Exact match for condo asset | `Condo` |

## Contributing

This project is a personal financial tracking system tailored to a specific workflow and set of tools. As such, it is not currently open for external contributions or pull requests. You are welcome to fork the repository for your own personal use, but please be aware that the code is provided "as-is" without support or maintenance guarantees.
