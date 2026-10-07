# Google Flight Search (GFS) data in BigQuery: what is there and how to query it

*Written 7 Oct 2026 from the queries the project already runs (`OND_Ranking.ipynb` cells 4, 8, 17;
`gcp1/bigquery/ond_ranking_feed/ond_ranking_feed.sql`; `ond_unified_ranking_v4.3_yoy.ipynb`). Column lists
below are the columns we use, not necessarily every column in the tables: run the schema query in section 3
to see the full list.*

---

## 1. Two projects: one for the data, one for the bill

We never run queries in the project that holds the data. Two projects, two roles:

| Role | Project | Used for | Access you need |
|---|---|---|---|
| **Data** (read from) | `gcp-prd-prj-data-dgm01` | inside every table name: `` `gcp-prd-prj-data-dgm01.<dataset>.<table>` `` | BigQuery Data Viewer on the datasets |
| **Billing / compute** (runs the job) | `gcp-stg-prj-data-dgm-ds01` | the project of the BigQuery **client**: it runs the query job and pays for it | BigQuery Job User (`bigquery.jobs.create`) |

In Python:

```python
from google.cloud import bigquery

GCP_PROJECT     = "gcp-prd-prj-data-dgm01"     # data project: goes in the table names
GCP_PROJECT_CLI = "gcp-stg-prj-data-dgm-ds01"  # billing project: goes in the client

client = bigquery.Client(project=GCP_PROJECT_CLI)

def bq(sql: str):
    return client.query(sql).to_dataframe(create_bqstorage_client=True)
```

Rules:

- **Never collapse the two into one variable.** We read prod data from a staging compute environment; the
  client must be the billing project and the table names must carry the data project.
- **Always write fully qualified table names** (`project.dataset.table`). A bare `dataset.table` resolves
  against the billing project, where the table does not exist.
- From the command line, the same split is `bq --project_id=gcp-stg-prj-data-dgm-ds01 query --use_legacy_sql=false '...'`
  with the data project in the table names.
- In the Composer DAG (production feed) it is different: the job runs in the per-environment
  `data_project` (`shared/config/feed_config.py`: dev `gcp-dev-prj-data-dgm01`, npd `gcp-npd-prj-data-dgm01`,
  pstg `gcp-pstg-prj-data-dgm02`, prd `gcp-prd-prj-data-dgm01`), location **`me-central1`**.
- Common errors: *"Access Denied: ... bigquery.jobs.create"* means the client project is wrong (you are
  billing to the data project). *"Not found: Dataset ..."* usually means a table name without the data
  project in front of it.

---

## 2. What GFS data exists

Dataset: **`gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search`** (landing layer, `lnd_`). GFS is the Google
Flights partner reporting: how Qatar Airways (`partner = 'QR'`) appears, prices and gets selected on Google
Flights, per route and day. It covers **more routes than Adobe** (16,726 routes with GFS demand against
7,057 with Adobe demand in the 23 Aug run), so it is the reach signal in the ranking.

| Table | What it tells you | Route key | Used in |
|---|---|---|---|
| `lnd_gfs_competitiveness` | **Price competitiveness and visibility**: how often QR is the cheapest, the price gap to competitors, impression share, participation, plus a demand weight | `origin_airport_code`, `destination_airport_code` | ranking (signal S5a, price gate, `gfs_demand_index`), production feed |
| `lnd_gfs_shopping_competitiveness` | **Shopping behaviour**: average rank of QR in the results, presence in "Best flights", share of outbound selections | `origin`, `destination` | ranking (signal S5b, enrichment columns) |
| `lnd_gfs_quality` | Quality metrics (declared in the legacy classifier) | to check | **not queried** by any current notebook |

Related, not GFS but often used next to it:
`gcp-prd-prj-data-dgm01.bq_slv_dgt_marketing.slv_instant_search_google_feed` is the **Instant Search Google
feed** (QR's own fares and URLs per route: lowest economy/premium one-way and return fares, city and country
names, `transfer_time` snapshot). Take the latest row per route.

### 2.1 `lnd_gfs_competitiveness`, columns we use

| Column | Meaning |
|---|---|
| `date` | day of the observation (filter on it, it is the partition you want to prune) |
| `partner` | airline; always filter `partner = 'QR'` |
| `origin_airport_code`, `destination_airport_code` | directional airport pair (`DOH`, `LHR`, ...) |
| `user_country` | country of the Google Flights user (point of sale view) |
| `price_bucket_lowest` (+ `_weight`) | share of searches where QR is the cheapest |
| `price_bucket_unique_lowest` (+ `_weight`) | share where QR is the only cheapest |
| `price_bucket_not_lowest` (+ `_weight`) | share where QR is not the cheapest |
| `average_positive_price_diff` (+ `_weight`) | average gap when QR is **more** expensive (fraction, 0.10 = 10%) |
| `average_negative_price_diff` (+ `_weight`) | average gap when QR is **cheaper** |
| `top_impression_share` (+ `_weight`) | share of top impressions |
| `absolute_top_impression_share` (+ `_weight`) | share of absolute-top impressions |
| `participation_rate` (+ `_weight`) | share of searches where QR is shown at all |

### 2.2 `lnd_gfs_shopping_competitiveness`, columns we use

| Column | Meaning |
|---|---|
| `date`, `partner` | as above |
| `origin`, `destination` | route (note: different column names from the competitiveness table) |
| `avg_rank` (+ `_weight`) | average position of QR in results (lower is better) |
| `in_best_flights_when_present` (+ `_weight`) | share of appearances inside "Best flights" |
| `participation` (+ `_weight`) | share of searches where QR participates |
| `pct_of_all_outbound_selections` (+ `_weight`) | QR's share of all outbound selections |
| `pct_of_outbound_selections_given_partner_was_present` (+ `_weight`) | selection rate when QR was shown |

### 2.3 How to read the `_weight` columns

Every metric comes with its own `_weight`. The metric is a rate for that row, the weight is how much that row
counts. **Always aggregate with a weighted mean**, never a plain `AVG`:

```sql
SAFE_DIVIDE(SUM(metric * metric_weight), SUM(metric_weight))
```

The sum of a weight is also a volume proxy. The ranking's **GFS demand** is exactly that:
`gfs_demand_share = SUM(price_bucket_lowest_weight)` over 90 days, and
`gfs_demand_index = gfs_demand_share / max(gfs_demand_share) * 100`. It is relative: compare routes, do not
read it as a number of searches.

---

## 3. Discover the full schema first

```sql
-- every column of every GFS table
SELECT table_name, column_name, data_type
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.INFORMATION_SCHEMA.COLUMNS`
ORDER BY table_name, ordinal_position;

-- date coverage and size of each table
SELECT 'competitiveness' AS t, MIN(date) AS first_day, MAX(date) AS last_day, COUNT(*) AS rows_
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness` WHERE partner = 'QR'
UNION ALL
SELECT 'shopping', MIN(date), MAX(date), COUNT(*)
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_shopping_competitiveness` WHERE partner = 'QR';
```

Run with the billing client (section 1). Log the last available day before any analysis: the ranking uses the
90 days before `RUN_DATE`, so a late load shortens the window silently.

---

## 4. Ready-to-run queries

All use a run anchor and the 90-day lookback of the ranking. Replace `2026-10-04` with your anchor.

### 4.1 Price and demand per route (what the ranking uses)

```sql
SELECT
  CONCAT(origin_airport_code, '-', destination_airport_code) AS ond,
  ROUND(SAFE_DIVIDE(SUM(price_bucket_lowest * price_bucket_lowest_weight),
                    SUM(price_bucket_lowest_weight)), 4)                          AS pct_cheapest,
  ROUND(SAFE_DIVIDE(SUM(average_positive_price_diff * average_positive_price_diff_weight),
                    SUM(average_positive_price_diff_weight)), 4)                  AS avg_price_gap_above,
  ROUND(SAFE_DIVIDE(SUM(top_impression_share * top_impression_share_weight),
                    SUM(top_impression_share_weight)), 4)                         AS avg_impression_share,
  ROUND(SAFE_DIVIDE(SUM(participation_rate * participation_rate_weight),
                    SUM(participation_rate_weight)), 4)                           AS avg_participation_rate,
  SUM(price_bucket_lowest_weight)                                                 AS gfs_demand_share,
  COUNT(DISTINCT user_country)                                                    AS gfs_country_count
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR'
  AND date >= DATE_SUB(DATE '2026-10-04', INTERVAL 90 DAY)
  AND date <  DATE '2026-10-04'
GROUP BY ond
```

Signal S5a (price) passes when `pct_cheapest >= 0.15 OR avg_price_gap_above < 0.10`; the price gate passes
when `pct_cheapest` is missing or `>= 0.15`.

### 4.2 Shopping visibility per route

```sql
SELECT
  CONCAT(origin, '-', destination) AS ond,
  ROUND(SAFE_DIVIDE(SUM(avg_rank * avg_rank_weight), SUM(avg_rank_weight)), 1)    AS avg_rank,
  ROUND(SAFE_DIVIDE(SUM(in_best_flights_when_present * in_best_flights_when_present_weight),
                    SUM(in_best_flights_when_present_weight)), 4)                 AS pct_best_flights,
  ROUND(SAFE_DIVIDE(SUM(pct_of_outbound_selections_given_partner_was_present
                        * pct_of_outbound_selections_given_partner_was_present_weight),
                    SUM(pct_of_outbound_selections_given_partner_was_present_weight)), 4) AS selection_rate_when_present
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_shopping_competitiveness`
WHERE partner = 'QR'
  AND date >= DATE_SUB(DATE '2026-10-04', INTERVAL 90 DAY)
  AND date <  DATE '2026-10-04'
GROUP BY ond
```

Signal S5b passes when `avg_rank <= 10 AND pct_best_flights > 0.10`.

### 4.3 One market's view (for example Pakistan users)

```sql
SELECT
  date,
  CONCAT(origin_airport_code, '-', destination_airport_code) AS ond,
  SAFE_DIVIDE(SUM(price_bucket_lowest * price_bucket_lowest_weight), SUM(price_bucket_lowest_weight)) AS pct_cheapest,
  SUM(price_bucket_lowest_weight) AS demand_weight
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR'
  AND user_country = 'PK'          -- check the code format with SELECT DISTINCT user_country first
  AND date BETWEEN '2026-08-01' AND '2026-10-04'
GROUP BY date, ond
```

Useful to tell a demand change in a market (Google Flights interest fell) from a paid-media change.

### 4.4 Weekly trend for one route

```sql
SELECT
  DATE_TRUNC(date, WEEK(SUNDAY)) AS wsd,
  SAFE_DIVIDE(SUM(price_bucket_lowest * price_bucket_lowest_weight), SUM(price_bucket_lowest_weight)) AS pct_cheapest,
  SAFE_DIVIDE(SUM(average_positive_price_diff * average_positive_price_diff_weight),
              SUM(average_positive_price_diff_weight))                                                AS avg_price_gap_above,
  SUM(price_bucket_lowest_weight)                                                                     AS demand_weight
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR'
  AND origin_airport_code = 'KHI' AND destination_airport_code = 'DOH'
  AND date >= '2026-05-01'
GROUP BY wsd
ORDER BY wsd
```

---

## 5. Joining GFS to the rest

- **Direction**: GFS routes are **directional** (`KHI-DOH` is not `DOH-KHI`), like the ranking. SA360/UC7
  and CM360 use the **sorted pair**. To join to those, build the sorted key:
  `(SELECT STRING_AGG(x, '-' ORDER BY x) FROM UNNEST([origin_airport_code, destination_airport_code]) x)`,
  then decide how to combine the two directions (sum the weights, weighted mean of the rates).
- **Case**: the ranking keys are UPPER case (`UPPER(ond)` on Adobe). Upper-case both sides before joining.
- **Airport vs city codes**: GFS uses airport codes. Some other sources use city codes (for example `LON`
  vs `LHR`); those rows will not match.
- **Missing GFS is not zero demand**: in the ranking a route with no GFS row gets `gfs_demand_index = 0` and
  passes the price gate by default. Do not read a missing row as "QR is not competitive".

---

## 6. Gotchas

1. Always filter **`partner = 'QR'`**; the tables also hold other partners.
2. Always filter on **`date`** (both ends) to limit the scan; anchor on a fixed run date, not
   `CURRENT_DATE()`, so a run can be reproduced.
3. **Weighted means only**: a plain `AVG(price_bucket_lowest)` gives each row the same weight and is wrong.
4. Rates are **fractions** (0.15 = 15%); several notebook columns multiply by 100 (`*_pct`). Check which one
   you have before comparing to a threshold.
5. The two tables name the route columns differently (`origin_airport_code` vs `origin`).
6. GFS shows Google Flights behaviour only: it is a demand and price signal, not bookings. Bookings come from
   Adobe (`slv_adobe_analytics_events`, categories `flight`) or CM360.
