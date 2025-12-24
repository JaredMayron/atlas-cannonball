## Net Worth by Type
This is a breakdown in my current net worth, assets minus liabilities. [Find a more detailed breakdown of net worth here](https://my.pocketsmith.com/net_worth)

{% big_value
  data="account_categorization"
  title="Current Net Worth"
  value="sum(balance)"
  fmt="usd"
/%}
{% pie_chart
  data="account_categorization"
  category="type"
  value="sum(balance)"
/%}

{% table
    data="account_categorization"
    order="title asc"
    where="type != ''"
%}
{% /table %}