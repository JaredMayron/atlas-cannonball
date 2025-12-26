## Net Worth by Type
This is a breakdown in my current net worth of ${% value
  data="account_categorization"
  value="sum(balance)"
  fmt="usd"
/%}, which are my assets minus liabilities. [Find a more detailed breakdown of net worth here](https://my.pocketsmith.com/net_worth)

{% pie_chart
  data="account_categorization"
  category="type"
  value="sum(balance)"
/%}

{% table
    data="account_categorization"
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