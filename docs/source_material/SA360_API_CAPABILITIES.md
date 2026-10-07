# SA360 Reporting API: what an agent can actually get

Verified by probing, not read from docs. Every claim below was tested against a live account
(Qatar Airways MCC 1144701035, account 4851538229) on 5 to 7 October 2026.

**Shape of the API**: 56 queryable resources, 792 fields (563 attributes, 98 metrics, 75 segments).
All 56 resources answered a query. **26 of them accept metrics**, the other 30 are configuration
or lookup only. One endpoint does everything:
`POST /v0/customers/{id}/searchAds360:searchStream` with a SQL-like query.

---

## Getting in

```
POST https://oauth2.googleapis.com/token          grant_type=refresh_token
GET  /v0/customers:listAccessibleCustomers        no ID needed, discovers the MCC
POST /v0/customers/{id}/searchAds360:searchStream the only query endpoint
POST /v0/searchAds360Fields:search                the schema, query it like any resource
```

Three headers: `Authorization: Bearer`, `Content-Type: application/json`, and
`login-customer-id: {MCC}` whenever you query a client account under a manager.
Scope: `https://www.googleapis.com/auth/doubleclicksearch`.

`listAccessibleCustomers` is the right first call for an agent: it needs no account ID and
bootstraps everything else. From the MCC, `FROM customer_client` enumerates the whole tree.

---

## What an agent can answer

**Account structure.** `customer_client` (the whole MCC tree, currency, timezone, manager flag),
`customer`, `customer_manager_link`, `label`, `campaign_label`, `ad_group_label`.
Our MCC returned 704 accounts in one call.

**Every campaign setting.** `campaign` carries **67 attributes**: status and serving status,
network settings (Google search, search partners, display, each a separate boolean), geo target
type (presence against presence or interest), `selective_optimization.conversion_actions` which is
the campaign level conversion goal, `optimization_goal_setting`, every bid strategy variant with
its ceilings and floors, tracking templates, URL custom parameters, dynamic search ads settings,
frequency caps, start and end dates. One query returns the full configuration of every campaign,
which makes "is anything configured differently" a one-shot question.

**Bid strategies.** `bidding_strategy` (28 fields) and `accessible_bidding_strategy`. Type, status,
campaign count, target ROAS, target CPA, CPC ceiling and floor per strategy type.

**Budgets.** `campaign_budget` is thin, only 4 fields: amount, delivery method, period,
resource name. No name, no ID, no shared flag. Join through `campaign.campaign_budget` instead.

**Conversion configuration.** `conversion_action` (21 fields): whether each action is included in
the Conversions metric, whether it is primary for goal, its floodlight activity ID and tag, its
attribution model, its lookback window, and its value settings including the default value and the
always use default value flag. `conversion_custom_variable` for custom variables.

**Individual conversions.** `conversion` (24 fields) returns conversion rows, not aggregates:
conversion datetime and visit datetime (so you can measure click to conversion lag directly),
revenue micros, floodlight original revenue (so you can separate a tagging failure from a
currency or cap problem), floodlight order ID, quantity, status, attribution type, and the
criterion and ad that earned it. This is the resource that settles "is the revenue really missing".
Treat order IDs as personal data.

**Individual visits.** `visit` (14 fields): visit datetime, click ID, criterion, ad, asset.

**Performance, at every level.** `campaign`, `ad_group`, `ad_group_ad`, `keyword_view`,
`ad_group_criterion`, `ad_group_bid_modifier`, plus the views: `location_view`,
`user_location_view`, `age_range_view`, `gender_view`, `webpage_view`,
`campaign_audience_view`, `ad_group_audience_view`.
Shopping has `shopping_performance_view`, `product_group_view`, `cart_data_sales_view`.
`dynamic_search_ads_search_term_view` exists but is effectively empty, see the search terms
entry under what it cannot do.

**Creative and assets.** `asset` (57 fields), `asset_group`, `asset_set`, `campaign_asset`,
`ad_group_asset`, `asset_group_top_combination_view`, `asset_group_signal`.

**Audiences.** `audience`, `user_list`, and the two audience views with metrics.

**Lookups.** `geo_target_constant`, `language_constant`, `product_bidding_category_constant`.

---

## Metrics, 98 of them

The useful clusters:

- **spend and traffic**: `cost_micros`, `clicks`, `impressions`, `ctr`, `average_cpc`,
  `average_cpm`, `average_cost`, `interactions`, `interaction_rate`, `visits`
- **conversions**, 35 variants. The ones that matter are the four way split between
  `conversions` (only actions included in the Conversions column) and `all_conversions`
  (everything), each available by click date or by conversion date
  (`*_by_conversion_date`). Comparing those two date bases is how you detect reporting lag.
  Plus `conversions_value`, `value_per_conversion`, `conversions_value_per_cost`,
  `cost_per_conversion`, `cross_device_conversions`.
- **auction share**, 13 metrics, and all of them verified to return values at
  **campaign, ad group and keyword level** on the same account: `search_impression_share`,
  `search_click_share`, `search_top_impression_share`,
  `search_absolute_top_impression_share`, `search_exact_match_impression_share`,
  `search_budget_lost_impression_share`, `search_rank_lost_impression_share`, each lost and top
  metric also in an absolute top variant, plus the three `content_*` equivalents for display.
  Splitting lost share into **budget against rank** is the single most diagnostic pair in the
  whole API: it separates "we cannot afford to show" from "we cannot win the auction".
  Weight by impressions when aggregating, since each row is a ratio.

  **`search_click_share` is worth calling out separately.** It is clicks received over clicks
  available, so reading it against `search_impression_share` tells you whether you are converting
  the visibility you hold into clicks at the market rate. On our account the two diverged sharply
  after an intervention: impression share returned to its baseline (55.8 to 56.6 percent) while
  click share did not (21.7 down to 16.2 percent), at identical top and absolute top share and
  with own CTR actually rising. That combination says the auction set itself changed, which no
  cost or click metric would have revealed.
- **quality**: `average_quality_score`, `historical_quality_score`,
  `historical_creative_quality_score`, `historical_landing_page_quality_score`,
  `historical_search_predicted_ctr`
- **invalid traffic**: `invalid_clicks`, `invalid_click_rate`, `general_invalid_clicks`
- **commerce**: `orders`, `revenue_micros`, `units_sold`, `average_order_value_micros`,
  `gross_profit_micros`, `gross_profit_margin`, `cost_of_goods_sold_micros`, and cross sell
  and lead variants
- **reach**: `unique_users`, `average_impression_frequency_per_user`

## Segments, 75 of them

Time: `date`, `week`, `month`, `quarter`, `year`, `day_of_week`, `hour`.
Context: `device`, `ad_network_type` (separates Google search from search partners),
`ad_format_type`.
Geography: `geo_target_country`, `geo_target_region`, `geo_target_city`, `geo_target_metro`,
`geo_target_postal_code`.
Conversions: `conversion_action`, `conversion_action_name`, `conversion_action_category`.
Keywords: `keyword.info.text`, `keyword.info.match_type`, `keyword.ad_group_criterion`.
The remaining 40 or so are product and vertical ads dimensions.

---

## What it cannot do

- **No change history.** `change_event` does not exist. Work around it with
  `last_modified_time`, which exists on campaign, ad group, ad group criterion and campaign
  criterion. That dates bulk changes precisely, which is usually what you need.
- **No portfolio conversion goal.** `bidding_strategy` exposes no goal field. If a portfolio
  carries its own conversion goal, the API will not tell you. UI only.
- **No SA360 native bid strategy settings.** A max CPC bid limit set in SA360's own layer does not
  surface anywhere, not on the portfolio, not on the campaign. We confirmed this against a cap
  that demonstrably changed behaviour but appears in no field.
- **No search term report.** There is no `search_term_view` resource; querying it returns
  `UNRECOGNIZED_FIELD`. The only search term resource is
  `dynamic_search_ads_search_term_view`, and it carries exactly two fields, a landing page and a
  resource name, with **no search term text at all**, and it returns nothing unless the account
  runs dynamic search ads. So questions about how broad match is actually matching, or which
  queries are being bought, cannot be answered from this API. UI only. This is probably the
  single biggest gap for an agent doing search account work, and it is easy to miss because the
  resource list contains something that looks like a search term view.
- **It is read only.** No writes, no mutations.
- **Attributes are current, not historical.** Selecting `effective_cpc_bid_micros` with an August
  date range returns today's value, not August's. Only metrics are time sliced. This is the
  easiest way to draw a wrong conclusion.
- **Impression share clamps.** Below 10 percent reports as exactly 10.0, above 90 percent as
  exactly 90.0. A flat line at those values means out of range, not a stable measurement.

---

## The gotchas that will cost an agent time

1. **searchStream returns errors in a JSON array, not an object.** Parse `d[0]["error"]`, not
   `d["error"]`, or every error message you log will be unreadable.
2. **`PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE`.** Segmenting by
   `conversion_action_name` forbids `cost_micros` and `clicks` in the same SELECT. Campaign
   attributes are fine. Split into two queries and join on date.
3. **`FROM bidding_strategy` only returns portfolios owned by the account you query.** A portfolio
   owned by the MCC is invisible from the client account even though its campaigns use it. Query
   the MCC. This cost us an hour.
4. **Keywords query `FROM keyword_view` but select `ad_group_criterion.*` fields.**
   `keyword_view` itself has exactly one field, its resource name.
5. **Fields service rejects unknown selects.** `SELECT ... segmenting` fails. Stick to
   `name, category, selectable, filterable, sortable, data_type`.
6. **Budget history needs `campaign.campaign_budget`**, since `campaign_budget` has no ID field.
7. **No LIMIT means everything.** A keyword query over a 543 campaign portfolio returned 9,810
   rows. Fine, but size your timeouts: about 50 to 60 queries per two minutes in practice.
8. **`metrics.conversions` is often zero** when `all_conversions` is not. That is not a bug, it
   means the action is excluded from the Conversions column. Checking both is a free diagnostic.

---

## Minimal recipe

```python
tok   = refresh()                                    # 1 call, cache for 3600s
mcc   = GET /v0/customers:listAccessibleCustomers    # discovers the tree root
accts = stream(mcc, "SELECT customer_client.id, customer_client.descriptive_name, "
                    "customer_client.currency_code, customer_client.time_zone "
                    "FROM customer_client WHERE customer_client.manager = false")
cfg   = stream(acct, "SELECT <all 67 campaign fields> FROM campaign")   # full config snapshot
perf  = stream(acct, "SELECT segments.date, metrics.cost_micros, metrics.clicks, "
                     "metrics.impressions, metrics.search_impression_share, "
                     "metrics.search_click_share, "
                     "metrics.search_budget_lost_impression_share, "
                     "metrics.search_rank_lost_impression_share "
                     "FROM campaign WHERE segments.date BETWEEN ... ")
                     # keep impressions: the share metrics are ratios and need weighting
conv  = stream(acct, "SELECT segments.date, segments.conversion_action_name, "
                     "metrics.all_conversions, metrics.all_conversions_value "
                     "FROM campaign WHERE segments.date BETWEEN ...")   # separate, see gotcha 2
```

Four calls give an agent the account tree, the complete configuration, the auction diagnostics and
the conversion picture. Everything else is a refinement of those.
