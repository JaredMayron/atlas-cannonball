import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, config_json):
        self.config = json.loads(config_json) if config_json else {}

    def categorize_accounts(self, accounts):
        cash_titles = [t.upper() for t in self.config.get("CASH_TITLES", [])]
        inv_titles = [t.upper() for t in self.config.get("INVESTMENT_TITLES", [])]
        car_id = self.config.get("CAR_IDENTIFIER", "").upper()
        condo_id = self.config.get("CONDO_IDENTIFIER", "").upper()

        categorized = []
        for acc in accounts:
            title = acc.get("title", "")
            balance = acc.get("current_balance", 0)
            title_upper = title.upper()
            
            acc_type = "Other"
            if title_upper in cash_titles:
                acc_type = "Cash"
            elif title_upper in inv_titles:
                acc_type = "Investment"
            elif car_id and car_id in title_upper:
                acc_type = "Car"
            elif condo_id and title_upper == condo_id:
                acc_type = "Condo"
            
            categorized.append({
                "title": title,
                "balance": round(balance, 2),
                "type": acc_type,
                "snapshot_date": datetime.now().strftime("%Y-%m-%d")
            })
        return categorized

    def calculate_mandatory_spending(self, transactions):
        api_categories = self.config.get("API_CALCULATED_CATEGORIES", [])
        
        api_total = 0
        for tx in transactions:
            category_obj = tx.get("category")
            category = category_obj.get("title", "Uncategorized") if category_obj else "Uncategorized"
            if category in api_categories and "GROCERIES" not in category.upper():
                api_total += tx.get("amount", 0)
        
        # Pocketsmith debits are negative, we want positive cost
        api_total = abs(api_total)
        
        manual_estimates = {
            "Groceries": self.config.get("GROCERIES_ESTIMATE", 0),
            "Restaurant": self.config.get("RESTAURANT_ESTIMATE", 0),
            "Health Insurance": self.config.get("HEALTH_INSURANCE_ESTIMATE", 0)
        }
        
        grand_total = api_total + sum(manual_estimates.values())
        
        return {
            "api_mandatory_spend": api_total,
            "manual_estimates": manual_estimates,
            "grand_total_annual": grand_total,
            "grand_total_daily": grand_total / 365,
            "snapshot_date": datetime.now().strftime("%Y-%m-%d")
        }

    def calculate_runway(self, categorized_accounts, spending):
        cash_on_hand = sum(acc["balance"] for acc in categorized_accounts if acc["type"] == "Cash")
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
            "snapshot_date": datetime.now().strftime("%Y-%m-%d")
        }
