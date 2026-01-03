# Configuration Reference

The `config_json` secret in Google Cloud Secret Manager controls how your financial data is categorized and calculated.

## JSON Structure

```json
{
  "CASH_TITLES": ["Primary Checking", "Emergency Fund", "Savings"],
  "INVESTMENT_TITLES": ["Vanguard Brokerage", "401k", "Roth IRA"],
  "CAR_IDENTIFIER": "Tesla",
  "CONDO_IDENTIFIER": "Primary Residence",
  "API_CALCULATED_CATEGORIES": [
    "Utilities",
    "Mortgage & Rent",
    "Insurance",
    "Subscriptions"
  ],
  "GROCERIES_ESTIMATE": 7200,
  "RESTAURANT_ESTIMATE": 2400,
  "HEALTH_INSURANCE_ESTIMATE": 4800
}
```

## Field Descriptions

| Key | Type | Description |
| :--- | :--- | :--- |
| `CASH_TITLES` | `Array<string>` | Exact names of accounts to be treated as liquid cash for runway calculations. |
| `INVESTMENT_TITLES` | `Array<string>` | Exact names of accounts to be categorized as investments. |
| `CAR_IDENTIFIER` | `string` | A substring used to identify vehicle-related asset accounts (case-insensitive). |
| `CONDO_IDENTIFIER` | `string` | The exact name of your real estate asset account (case-insensitive). |
| `API_CALCULATED_CATEGORIES` | `Array<string>` | PocketSmith category names to sum up for mandatory spending (e.g., bills). |
| `GROCERIES_ESTIMATE` | `number` | **Annual** estimate for groceries (since volatility makes historical data hard to track). |
| `RESTAURANT_ESTIMATE` | `number` | **Annual** estimate for dining out. |
| `HEALTH_INSURANCE_ESTIMATE`| `number` | **Annual** estimate for health-related costs. |

> [!NOTE]
> All currency values should be **annual** totals. The system automatically calculates daily burn rates by dividing by 365.
