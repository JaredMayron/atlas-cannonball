import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Constants for category matching
GROCERIES_CATEGORY = "GROCERIES"


class DataProcessor:
    def __init__(self, config_json: Optional[str]):
        self.config = json.loads(config_json) if config_json else {}
        
        # Pre-parse account categorization config
        self.cash_titles = [t.upper() for t in self.config.get("CASH_TITLES", [])]
        self.investment_titles = [t.upper() for t in self.config.get("INVESTMENT_TITLES", [])]
        self.car_identifier = self.config.get("CAR_IDENTIFIER", "").upper()
        self.condo_identifier = self.config.get("CONDO_IDENTIFIER", "").upper()

    def categorize_accounts(
        self, accounts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        categorized = []
        for acc in accounts:
            title = acc.get("title", "")
            balance = acc.get("current_balance", 0)
            acc_type = self._determine_account_type(title)

            categorized.append(
                {
                    "title": title,
                    "balance": round(balance, 2),
                    "type": acc_type,
                    "snapshot_date": datetime.now().strftime("%Y-%m-%d"),
                }
            )
        return categorized

    def _determine_account_type(self, title: str) -> str:
        title_upper = title.upper()

        if title_upper in self.cash_titles:
            return "Cash"
        elif title_upper in self.investment_titles:
            return "Investment"
        elif self.car_identifier and self.car_identifier in title_upper:
            return "Car"
        elif self.condo_identifier and title_upper == self.condo_identifier:
            return "Condo"
        return "Other"

    def calculate_mandatory_spending(
        self, transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        api_categories = self.config.get("API_CALCULATED_CATEGORIES", [])

        api_total = 0
        for tx in transactions:
            category_obj = tx.get("category")
            category = (
                category_obj.get("title", "Uncategorized")
                if category_obj
                else "Uncategorized"
            )
            if category in api_categories and GROCERIES_CATEGORY not in category.upper():
                api_total += tx.get("amount", 0)

        # Pocketsmith debits are negative, we want positive cost
        api_total = abs(api_total)

        manual_estimates = {
            "Groceries": self.config.get("GROCERIES_ESTIMATE", 0),
            "Restaurant": self.config.get("RESTAURANT_ESTIMATE", 0),
            "Health Insurance": self.config.get("HEALTH_INSURANCE_ESTIMATE", 0),
        }

        grand_total = round(api_total + sum(manual_estimates.values()), -2)

        return {
            "api_mandatory_spend": api_total,
            "manual_estimates": manual_estimates,
            "grand_total_annual": grand_total,
            "grand_total_daily": grand_total / 365,
            "snapshot_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def calculate_runway(
        self, categorized_accounts: List[Dict[str, Any]], spending: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        cash_on_hand = sum(
            acc["balance"] for acc in categorized_accounts if acc["type"] == "Cash"
        )
        burn_rate = spending["grand_total_annual"]

        if burn_rate <= 0:
            return None

        runway_years = cash_on_hand / burn_rate
        runway_days = round(365 * runway_years)

        return {
            "cash_on_hand": cash_on_hand,
            "annual_burn": burn_rate,
            "runway_days": runway_days,
            "runway_years": round(runway_years, 2),
            "snapshot_date": datetime.now().strftime("%Y-%m-%d"),
        }
