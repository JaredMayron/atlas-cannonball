## Cash Reserves & Mandatory Expenses
I hook into PocketSmith and try to determine how long my cash reserves will last given no income and my mandatory expenses {% info
  text="Mandatory expenses are defined as Auto Insurance, Car, Dues and Subscriptions, Education, Fees & Charges, Gas & Fuel, Groceries, Hair, Healthcare & Medical, Homeowners Association, Mortgages, Restaurants & Dining, State Tax, Tax Preparation, Utilities, and Yearly Subscriptions."
/%} [Click here for more information directly in PocketSmith](https://my.pocketsmith.com/dashboard/75855-emergency).

I have a total of {% value
  data="account_categorization"
  value="sum(balance)"
  fmt="usd"
  where="type = 'Cash'"
/%} on hand in cash, which is projected to last until {% value
  data="runway_history_2"
  value="max(last_until)"
  limit=1
  order="date desc"
  fmt="fulldate"
/%}. On average I have {% value
  data="mandatory_spending"
  value="max(estimated_annual_spend)"
  limit=1
  where="expense_category='Total Mandatory Spend (Daily)'"
  fmt="usd"
/%} in mandatory expenses {% info
  text="Mandatory expenses are defined as Auto Insurance, Car, Dues and Subscriptions, Education, Fees & Charges, Gas & Fuel, Groceries, Hair, Healthcare & Medical, Homeowners Association, Mortgages, Restaurants & Dining, State Tax, Tax Preparation, Utilities, and Yearly Subscriptions."
/%} per day. 


{% callout type="info" title="Cash Reserve History"%}
An interactive graph which shows how my cash reserves change over time based on my cash on hand and my mandatory expenses {% info
  text="Mandatory expenses are defined as Auto Insurance, Car, Dues and Subscriptions, Education, Fees & Charges, Gas & Fuel, Groceries, Hair, Healthcare & Medical, Homeowners Association, Mortgages, Restaurants & Dining, State Tax, Tax Preparation, Utilities, and Yearly Subscriptions."
/%}. A darker square represents a more recent measurement. 
{% range_calendar
  id="cal_dates_range"
  default_range="last 30 days"
  preset_ranges=["last 7 days","last 30 days","last 12 months","previous week","previous month","previous year"
  ]
/%}
```sql cal_heatmap
SELECT 
    date,
    last_until,
    -1*dateDiff('day', date, UTCTimestamp()) AS days_from_today
FROM runway_history_2;
```
{% calendar_heatmap
  data="cal_heatmap"
  date="last_until"
  value="days_from_today"
  where="date {{cal_dates_range.between}}"
/%}
Within the period, I had on average {% value
  data="runway_history_2"
  value="avg(runway)"
  where="date {{cal_dates_range.between}}"
/%} days [{% delta
  data="runway_history_2"
  value="avg(runway)"
  text="days"
  date_range={
    date="date"
    range="{{cal_dates_range.range}}"
  }
  comparison={
    compare_vs="prior period"
    display_type="abs"
  }
/%}] of mandatory spending {% info
  text="Mandatory expenses are defined as Auto Insurance, Car, Dues and Subscriptions, Education, Fees & Charges, Gas & Fuel, Groceries, Hair, Healthcare & Medical, Homeowners Association, Mortgages, Restaurants & Dining, State Tax, Tax Preparation, Utilities, and Yearly Subscriptions." 
/%}. 

Sparkline of mandatory spending {% sparkline
  data="runway_history_2"
  x="date"
  y="runway"
  fit_to_data=true
  date_range={
    date="date"
    range="{{cal_dates_range.range}}"
  }
/%}
{% accordion %}
  {% accordion_item
    title="Underlying Data"
    icon="calendar"
  %}
    {% table
      data="runway_history_2"
      dimensions=["date","last_until","runway"]
      order="date desc"
    %}
    {% /table %}
  {% /accordion_item %}
{% /accordion %}

{% /callout %}

## Checking Account Rebalancing
```sql cash_difference
SELECT 
    (SELECT MAX(balance) FROM account_categorization WHERE title = 'BOA') - 
    (SELECT MAX(estimated_annual_spend) FROM mandatory_spending WHERE expense_category = 'Total Mandatory Spend (2 Months)') AS difference;
```
Reddit /r/personal_finance best practices is to have 2 months of mandatory spending {% info
  text="Mandatory expenses are defined as Auto Insurance, Car, Dues and Subscriptions, Education, Fees & Charges, Gas & Fuel, Groceries, Hair, Healthcare & Medical, Homeowners Association, Mortgages, Restaurants & Dining, State Tax, Tax Preparation, Utilities, and Yearly Subscriptions."
/%} in your checking account. 

I have {% value
  data="account_categorization"
  value="max(balance)"
  where="title = 'BOA'"
  limit=1
  fmt="usd"
/%} in my checking account and two months of mandatory expenses {% info
  text="Mandatory expenses are defined as Auto Insurance, Car, Dues and Subscriptions, Education, Fees & Charges, Gas & Fuel, Groceries, Hair, Healthcare & Medical, Homeowners Association, Mortgages, Restaurants & Dining, State Tax, Tax Preparation, Utilities, and Yearly Subscriptions."
/%} is {% value
  data="mandatory_spending"
  value="max(estimated_annual_spend)"
  where="expense_category = 'Total Mandatory Spend (2 Months)'"
  limit=1
  fmt="usd"
/%}. 

{% if
  data="cash_difference"
  where="difference>=0"
%}
A total of {% value
  data="cash_difference"
  value="max(difference)"
  limit=1
  fmt="usd"
  color="green"
/%} can be moved out of my checking account to savings.
{% /if %}
{% else %}
A total of {% value
  data="cash_difference"
  value="max(abs(difference))"
  limit=1
  fmt="usd"
  color="red"
/%} should be moved to the checking account from savings.
{% /else%}