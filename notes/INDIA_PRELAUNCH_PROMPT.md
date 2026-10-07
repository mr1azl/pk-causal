# Prompt for the SA360 agent: India pre-launch checks for value-based bidding

*Built from what went wrong or was confounded in PK (`notes/PK_DECISION.md`). Paste the block below.*

```
India pre-launch checks for value-based bidding (VBB). Work in ~/vbb_india_prelaunch/, same rules as
before: every script saved before it runs, LOG.md with date range returned and row counts, raw output in
data/raw/, clean tables in data/clean/, no credentials, no order IDs, no GA client IDs, no gclids,
no em dashes. Reuse lib_sa360.py from the PK rounds (chunking, two naming conventions, dest_code()).

Context. PK moved to Maximise Conversion Value on QR_FlightSearch_VBB on 2 Sep 2026 with no target ROAS.
What we learned:
- with no ROAS target, cost per click jumped 2 to 7 times and campaigns went budget-limited in all four
  markets that switched (PK, SA, CA, MY);
- PK UK campaigns lost about half their bookings per click, because the UK search value was the most
  inflated relative to booking value (search value per click / booking value per click 5.7 against 3.0
  for regional), and the bidder bought reverse-direction and generic queries on UK campaigns;
- "Bookings (FL)" adds a Floodlight action (QR_Booking) and a Google Ads webpage action (Booking), and
  Google cross-device modelling was 83% of PK regional conversions; the QR_Booking transaction rows
  from FROM conversion are the reliable count;
- a budget cut 13 days before the switch confounded every PK read.
These checks are meant to catch the same problems in India before launch.

I0. Setup
- From MCC 1144701035, list every India account (name contains "IN"; Google and Bing; brand and non-brand)
  with id, currency, time zone, status. Pick the main Google non-brand account(s); log the choice.
- Campaign inventory: count by status, naming convention (pipe form vs legacy), spend share on each
  form over the last 12 weeks, destination parse coverage (share of spend with no destination code).
- Define destination groups for an India origin and write the member codes out in lib_sa360.py:
  UK+IE; North America; Europe excl. UK/IE; Oceania; GCC and Middle East; South and South-East Asia;
  Africa; other. Log spend share per group.

I1. Baseline, 12 weeks to yesterday, daily, every India non-brand campaign
- Traffic: cost, clicks, impressions, average CPC, search_impression_share, search_top_impression_share,
  search_budget_lost_impression_share, search_rank_lost_impression_share (keep impressions; flag 10/90 clamps).
- Conversions by conversion_action_name (separate query, join on date and campaign): all_conversions,
  all_conversions_value, cross_device_conversions, for QR_Booking, every action named Booking (by id),
  Flight Search, and QR_FlightSearch_VBB / QR_FlightSearch_VBB_ML if they already fire for India.
- Summary by destination group and week: clicks, CPC, QR_Booking per 1k clicks, Booking (webpage) per 1k
  clicks, flight searches per click, cross-device share of QR_Booking.
- Same weeks of 2025 for the same campaigns or destinations, so the launch weeks have a seasonal baseline.

I2. Transaction ledger and inflation
- FROM conversion, last 8 weeks, QR_Booking: date, visit date, revenue, quantity, status, campaign, order ID
  hashed in the script before any write. Rows, revenue, zero-revenue rows, duplicate hashed order IDs, by
  destination group.
- Ratio all_conversions / ledger rows and cross-device share by destination group. Flag any group above 3x.

I3. Value calibration by destination (the PK UK failure)
- If VBB search conversions already fire for India: by destination group and for the top 30 destinations
  by spend, search value per click (QR_FlightSearch_VBB value / clicks) against booking value per click
  (QR_Booking ledger revenue / clicks, and the attributed value as a second view). Ratio per group.
  Flag every group or destination whose ratio is above 1.3 times the median ratio, and say by how much its
  values would have to be scaled to match the median.
- From FROM conversion rows of QR_FlightSearch_VBB (last 4 weeks): share of searches at exactly 0.50
  (fallback) and at 0, by destination group and top destinations. Parse only the type and OND parts of the
  order ID (type - ond - ...), hash or drop the rest before writing.
- If VBB does not fire for India yet, say so, and list what is needed to run this before launch.

I4. Bid headroom (how far CPC can jump)
- Per campaign and per group, last 4 weeks: rank-lost and budget-lost impression share, CPC, budget
  utilisation (cost / budget). Campaigns with low rank-lost and low budget-lost have the most room to bid up
  (PK started at 22% rank-lost and its CPC rose 6.6 times; SA started at 53% and rose 2.1 times). Rank them.
- Shared budgets: which campaigns share which budget, amount, and what share of it each used.

I5. Query hygiene from the API
- Keyword inventory for India non-brand: text, match type, status, negative flag, by campaign. Broad-match
  share of clicks by destination group.
- Negative keywords at campaign, ad group and shared-set level. For every destination campaign, does a
  reverse-direction negative exist ("to delhi", "to mumbai", "to india", "london to", and so on)? List the
  campaigns without one, by spend.
- The API has no search-term report. Ask me for the UI export of the last 8 weeks; do not substitute.

I6. Portfolio and settings
- The portfolio(s) India will join: owner, type, target ROAS, CPC ceiling and floor (query from the MCC).
- campaign.geo_target_type_setting and targeted locations for every active campaign (current values).
- last_modified_time on campaigns, ad groups, keywords and budgets over the last 30 days, to show nothing
  else is moving. Note that attributes are current values only.

I7. Holdout and guardrail design
- Propose a holdout: about 20% of spend per destination group kept on the current strategy for 4 weeks,
  chosen so each group's holdout matches the treated campaigns on the last 8 weeks of CPC, booking rate
  and spend. List the campaigns and the match quality.
- Guardrail table: for each destination group, the weekly QR_Booking ledger bookings per 1k clicks over the
  last 8 weeks, with its mean and a lower bound (Poisson, 90%). A group below that bound for 2 weeks after
  launch is flagged.

Hand back data/clean/ CSVs, LOG.md and FINDINGS_india.md with a go / fix-first table:
1. Target ROAS: is one set on the portfolio? If not, proposed starting value from the last 8 weeks.
2. Value calibration: which destination groups are out of line, and the scaling needed.
3. Fallback and zero-value share of search values, by group.
4. Bid headroom: which campaigns are most at risk of a CPC spike.
5. Reverse-direction negatives: which campaigns lack them.
6. Measurement: ledger vs attributed inflation and cross-device share by group.
7. Budget or other changes scheduled within two weeks of launch.
8. The holdout list and the guardrail thresholds.
Post a progress note after I1, I3 and I5.
```
