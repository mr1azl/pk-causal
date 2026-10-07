-- Google Flight Search (GFS): is the PK-UK booking collapse after 2 Sep 2026 a price, visibility or
-- demand change on Google Flights, independent of paid search?
-- Run with the billing client gcp-stg-prj-data-dgm-ds01; tables live in gcp-prd-prj-data-dgm01.
-- Weighted means only. Weekly, Sunday-start weeks. Both years, so September 2025 is the control.
-- PK origins: ISB LHE KHI MUX SKT PEW LYP UET. UK+IE: LHR LGW MAN BHX EDI GLA STN LTN BRS NCL LBA DUB ORK SNN.

-- 0. Checks: date coverage, user_country format, partners present on PK-UK routes.
SELECT MIN(date) AS first_day, MAX(date) AS last_day
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR';

SELECT user_country, SUM(price_bucket_lowest_weight) AS w
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR' AND date BETWEEN '2026-08-01' AND '2026-10-05'
  AND origin_airport_code IN ('ISB','LHE','KHI','MUX','SKT','PEW','LYP','UET')
GROUP BY user_country ORDER BY w DESC LIMIT 20;

SELECT partner, COUNT(*) AS rows_, SUM(participation_rate_weight) AS w
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE date BETWEEN '2026-06-01' AND '2026-10-05'
  AND origin_airport_code IN ('ISB','LHE','KHI','MUX','SKT','PEW','LYP','UET')
  AND destination_airport_code IN ('LHR','LGW','MAN','BHX','EDI','GLA','STN','LTN','BRS','NCL','LBA','DUB','ORK','SNN')
GROUP BY partner ORDER BY w DESC;

-- 1. QR price competitiveness and visibility, PK origin, weekly, UK+IE vs other destinations.
SELECT
  DATE_TRUNC(date, WEEK(SUNDAY)) AS week,
  IF(destination_airport_code IN ('LHR','LGW','MAN','BHX','EDI','GLA','STN','LTN','BRS','NCL','LBA','DUB','ORK','SNN'),
     'UK+IE', 'other') AS dest_group,
  SAFE_DIVIDE(SUM(price_bucket_lowest * price_bucket_lowest_weight), SUM(price_bucket_lowest_weight)) AS pct_cheapest,
  SAFE_DIVIDE(SUM(price_bucket_not_lowest * price_bucket_not_lowest_weight), SUM(price_bucket_not_lowest_weight)) AS pct_not_cheapest,
  SAFE_DIVIDE(SUM(average_positive_price_diff * average_positive_price_diff_weight),
              SUM(average_positive_price_diff_weight)) AS avg_gap_when_more_expensive,
  SAFE_DIVIDE(SUM(participation_rate * participation_rate_weight), SUM(participation_rate_weight)) AS participation,
  SAFE_DIVIDE(SUM(top_impression_share * top_impression_share_weight), SUM(top_impression_share_weight)) AS top_impr_share,
  SUM(price_bucket_lowest_weight) AS demand_weight
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR'
  AND date BETWEEN '2025-06-01' AND '2026-10-05'
  AND origin_airport_code IN ('ISB','LHE','KHI','MUX','SKT','PEW','LYP','UET')
GROUP BY week, dest_group
ORDER BY dest_group, week;

-- 2. QR shopping behaviour on Google Flights, same split: rank, best flights, selection when shown.
SELECT
  DATE_TRUNC(date, WEEK(SUNDAY)) AS week,
  IF(destination IN ('LHR','LGW','MAN','BHX','EDI','GLA','STN','LTN','BRS','NCL','LBA','DUB','ORK','SNN'),
     'UK+IE', 'other') AS dest_group,
  SAFE_DIVIDE(SUM(avg_rank * avg_rank_weight), SUM(avg_rank_weight)) AS avg_rank,
  SAFE_DIVIDE(SUM(in_best_flights_when_present * in_best_flights_when_present_weight),
              SUM(in_best_flights_when_present_weight)) AS pct_best_flights,
  SAFE_DIVIDE(SUM(participation * participation_weight), SUM(participation_weight)) AS participation,
  SAFE_DIVIDE(SUM(pct_of_all_outbound_selections * pct_of_all_outbound_selections_weight),
              SUM(pct_of_all_outbound_selections_weight)) AS share_of_all_selections,
  SAFE_DIVIDE(SUM(pct_of_outbound_selections_given_partner_was_present
                  * pct_of_outbound_selections_given_partner_was_present_weight),
              SUM(pct_of_outbound_selections_given_partner_was_present_weight)) AS selection_rate_when_present,
  SUM(participation_weight) AS volume_weight
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_shopping_competitiveness`
WHERE partner = 'QR'
  AND date BETWEEN '2025-06-01' AND '2026-10-05'
  AND origin IN ('ISB','LHE','KHI','MUX','SKT','PEW','LYP','UET')
GROUP BY week, dest_group
ORDER BY dest_group, week;

-- 3. Same as 1, by route, for the PK-UK routes only, 1 Aug to 5 Oct 2026 and 2025, to see which routes moved.
SELECT
  EXTRACT(YEAR FROM date) AS yr,
  IF(EXTRACT(DAYOFYEAR FROM date) < EXTRACT(DAYOFYEAR FROM DATE '2026-09-02'), 'before 2 Sep', 'from 2 Sep') AS half,
  CONCAT(origin_airport_code, '-', destination_airport_code) AS ond,
  SAFE_DIVIDE(SUM(price_bucket_lowest * price_bucket_lowest_weight), SUM(price_bucket_lowest_weight)) AS pct_cheapest,
  SAFE_DIVIDE(SUM(average_positive_price_diff * average_positive_price_diff_weight),
              SUM(average_positive_price_diff_weight)) AS avg_gap_when_more_expensive,
  SAFE_DIVIDE(SUM(participation_rate * participation_rate_weight), SUM(participation_rate_weight)) AS participation,
  SUM(price_bucket_lowest_weight) AS demand_weight
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_competitiveness`
WHERE partner = 'QR'
  AND (date BETWEEN '2026-08-01' AND '2026-10-05' OR date BETWEEN '2025-08-01' AND '2025-10-05')
  AND origin_airport_code IN ('ISB','LHE','KHI','MUX','SKT','PEW','LYP','UET')
  AND destination_airport_code IN ('LHR','LGW','MAN','BHX','EDI','GLA','STN','LTN','BRS','NCL','LBA','DUB','ORK','SNN')
GROUP BY yr, half, ond
ORDER BY yr, ond, half;

-- 4. Competitors on PK-UK routes: participation and share of selections by partner, weekly, Jun-Oct 2026.
-- Only works if the tables hold other partners' rows (the guide says they do). A new direct carrier or a
-- big competitor fare move around 1-3 Sep would show here.
SELECT
  DATE_TRUNC(date, WEEK(SUNDAY)) AS week,
  partner,
  SAFE_DIVIDE(SUM(participation * participation_weight), SUM(participation_weight)) AS participation,
  SAFE_DIVIDE(SUM(pct_of_all_outbound_selections * pct_of_all_outbound_selections_weight),
              SUM(pct_of_all_outbound_selections_weight)) AS share_of_all_selections,
  SUM(participation_weight) AS volume_weight
FROM `gcp-prd-prj-data-dgm01.bq_lnd_google_flight_search.lnd_gfs_shopping_competitiveness`
WHERE date BETWEEN '2026-06-01' AND '2026-10-05'
  AND origin IN ('ISB','LHE','KHI','MUX','SKT','PEW','LYP','UET')
  AND destination IN ('LHR','LGW','MAN','BHX','EDI','GLA','STN','LTN','BRS','NCL','LBA','DUB','ORK','SNN')
GROUP BY week, partner
ORDER BY week, volume_weight DESC;
