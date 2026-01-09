## Net Worth by Type (Mock)
```sql accounts_gcp
SELECT * FROM accounts_raw_gcp_mock WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM accounts_raw_gcp_mock)
```

This is a breakdown in my current net worth of {% value
  data="accounts_gcp"
  value="sum(balance)"
  fmt="usd"
/%}, which are my assets minus liabilities. [Find a more detailed breakdown of net worth here](https://my.pocketsmith.com/net_worth)

{% pie_chart
  data="accounts_gcp"
  category="type"
  value="sum(balance)"
  where="type != '' AND balance > 0"
/%}

{% table
    data="accounts_gcp"
    order="title asc"
    row_shading=true
    where="type != '' AND balance > 0"
%}
{% dimension
  value="title"
/%}
{% measure
  title="Balance"
  value="sum(balance)"
  fmt="usd"
/%}
{% pivot
  value="type"
/%}
{% /table %}

{% line_break /%}

{% partial file="system-architecture" /%}
