# Round 3 log

One entry per check: script, date range actually returned, row count, key number, errors and fixes.

---

## Setup

Script `scripts/s01_setup_accounts_campaigns.py`.

704 accounts under MCC 1144701035. Four contain "PK":

| id | name | currency | time zone |
|---|---|---|---|
| **4851538229** | **Google-GCCLI-PK-EN** | **USD** | **Asia/Qatar** |
| 1423602235 | Google-GCCLI-PK-EN-Brand | USD | Asia/Qatar |
| 3135137611 | Bing-SEA_SASC-PK-EN | USD | Europe/Moscow |
| 1249009829 | Bing-SEA_SASC-PK-EN-Brand | USD | Europe/Moscow |

PK account used: **4851538229**, USD, Asia/Qatar.

### The non-brand filter excludes nothing, and that is correct

15,868 campaigns in the account, all `SEARCH`, split 544 ENABLED, 3,132 PAUSED, 12,192 REMOVED.
Applying the brief's rule (no `|Brand|`, no `Perf_Max`, no `pmax`) excludes **zero** campaigns.
Checked the looser test too: **no campaign name in this account contains the string "brand" at all**,
in either year window. Brand sits in the separate account 1423602235, so the whole of 4851538229 is
non-brand by construction. Logged rather than silently passed over, since a filter that removes
nothing usually means it is wrong.

### Two naming conventions, not one

The pattern in the brief, `Google|PK|Dest|Country|XXX|GB|EN|MOD`, covers only **589 of 15,868**
campaigns. The other 15,279 carry legacy names with no pipes.

| window | campaigns with spend | total spend | share of spend on pipe names |
|---|---|---|---|
| 2025-06-01 to 2025-10-31 | 2,965 | 59,142 USD | **28.6%** |
| 2026-06-01 to 2026-10-05 | 471 | 99,317 USD | **96.1%** |

So 2025 is mostly legacy naming and a destination parser built only for the pipe form would have
silently dropped 71% of 2025 spend. The legacy form is
`_PK-Country-XXX-AU-EN_phrase`, `_PK-D-XXX-DOH-EN_phrase`, `_PK-O&D-LHE-LHR-EN_exact`:
underscore delimited match type suffix, then hyphen delimited tokens with the destination
immediately before the language code, and the destination is the second airport in O&D names.

`dest_code()` in `lib_sa360.py` handles both. Coverage check across both windows: **289 distinct
destination codes**, and exactly one campaign with no parseable destination,
`_PK-Generic-RMKT_Exact` (6,764 USD), which genuinely has none. No unclassified residual.

Top 20 campaigns by cost, 2025 window: `_PK-Country-XXX-AU-EN_phrase` 4,239 USD,
`_PK-Country-XXX-QA-EN_phrase` 3,001, `_PK-Generic-RMKT_Exact` 2,856, `_PK-D-XXX-DOH-EN_phrase`
2,665, `_PK-Country-XXX-US-EN_phrase` 2,010, then `_PK-O&D-LHE-DOH-EN_exact` 1,236 and a long tail.
Only three pipe-named campaigns reach the 2025 top 20, consistent with the pipe campaigns starting
2025-08-22.

### Destination grouping

UK+IE uses exactly the brief's list: GB, IE, LHR, LGW, MAN, BHX, EDI, DUB. Six further UK and
Ireland codes appear in the data and are reported separately rather than folded in, so the boundary
stays auditable: LON, GLA, BHD, NCL, ABZ, ORK, together 214 USD in 2025 and 0 in 2026.
Long-haul is North America, Europe excluding UK and IE, and Oceania, with the member codes written
out explicitly in `lib_sa360.py`. Regional is everything else.

| window | UK+IE | long-haul | regional | no destination |
|---|---|---|---|---|
| 2025 Jun-Oct | 13.5% | 45.3% | 36.1% | 4.8% |
| 2026 Jun-Oct | **39.5%** | 30.5% | 26.1% | 3.9% |

UK+IE went from an eighth of PK non-brand spend to nearly two fifths year on year.

---

## A. Seasonality, 2025 against 2026

Scripts `s02_a_seasonality_pull.py` (pull, monthly chunks), `s03_a_build_clean.py` (clean tables),
`s04_a_seasonality_compare.py` (comparison).

Date ranges actually returned: **2025-06-01 to 2025-10-31** and **2026-06-01 to 2026-10-05**, both
complete, no gaps.

| file | rows |
|---|---|
| `data/raw/a_traffic_2025.jsonl` | 131,496 |
| `data/raw/a_conv_2025.jsonl` | 200,846 |
| `data/raw/a_traffic_2026.jsonl` | 40,675 |
| `data/raw/a_conv_2026.jsonl` | 151,655 |
| `data/clean/pk_nb_traffic_2025.csv` | 131,496 |
| `data/clean/pk_nb_daily_2025.csv` | 199,782 |
| `data/clean/pk_nb_traffic_2026.csv` | 40,675 |
| `data/clean/pk_nb_daily_2026.csv` | 151,501 |

Two queries per chunk as required, since `segments.conversion_action_name` forbids
`metrics.cost_micros` and `metrics.clicks` in the same SELECT. Joined on date and campaign id.

### A4, custom columns

`Bookings (FL)` and `Revenue (FL)` are **not reachable through the API**. The account's
`customColumns` endpoint lists only two columns, `Bookings` (id 2948730) and `Flight Searches`
(id 2949198), both of which reference `metrics.all_conversions` segmented by
`segments.conversion_action`, so both are counts and neither carries revenue. There is no revenue
custom column at all. The `Bookings (FL)` and `Revenue (FL)` columns seen in UI exports are
report level constructs that the Reporting API does not expose. Logged as unavailable.

### Conversion actions differ between the two years

28 actions carry volume in 2025, 33 in 2026. `QR_Booking` exists in both, so bookings are
comparable year on year. Present in 2026 only: `QR_FlightSearch_VBB`, `QR_FlightSearch_VBB_ML`,
`Flight Search (TEST Sept2026)`, `Ancillary Purchase`, `Retrieve Booking`, `Stopover Search`,
the two app purchase actions, `Privilege Club Step 1` and `Step 2`, `Qverse (web) searchForFlights`.
Present in 2025 only: `Android App Booking`, `iOS App Booking`, `Privilege Club - Student`,
`QR_PrivilegeClub_Studentclub_signup`, `QR_BeyondBusiness_EnrollNow_success`,
`Subscribe - Email Enrol`.

### Key numbers: UK+IE bookings by month (QR_Booking plus Booking)

| month | 2025 bookings | 2026 bookings | 2025 clicks | 2026 clicks |
|---|---|---|---|---|
| June | 21.3 | 152.5 | 5,097 | 13,335 |
| July | 42.6 | 94.1 | 12,284 | 13,817 |
| August | 33.3 | 110.6 | 11,096 | 10,310 |
| **September** | **39.3** | **5.9** | 7,841 | 1,987 |
| October (partial 2026) | 42.9 | 2.0 | 10,080 | 965 |

**In 2025 UK+IE bookings did not drop in September.** 39.3 in September sits above August's 33.3
and just under July's 42.6, and October 2025 is the strongest month of the five at 42.9. The
calendar period is not a weak one for this market.

September 2026 is 5.9 against 110.6 in August, a **95 percent fall**.

Comparison by group, August to September 2026: UK+IE **-95%**, long-haul -65%, regional -71%.
UK+IE fell roughly thirty points harder than either of the others.

Weekly, aligned on ISO week, UK+IE bookings:
2025 weeks 36 to 44 run 8.6, 5.0, 10.0, 13.7, 8.0, 14.0, 11.0, 6.0, 5.9, flat throughout.
2026 weeks 36 to 41 run 5.0, 0.9, 0.0, 1.0, 1.3, 0.7.

---

## B. What Floodlight counts as a PK booking

Scripts `s05_b1_conversion_actions.py`, `s06_b2_conversion_rows.py`,
`s07_b3_b4_booking_analysis.py`. Date range actually returned: **2026-08-01 to 2026-10-05**.

Row counts: 102,773 conversion rows scanned across the window, **89 booking rows** kept.
141 conversion actions in the account, 11 matching "Booking" or `QR_FlightSearch_VBB`.

Order IDs and advertiser conversion IDs are SHA-256 hashed inside `s06` **before any write**,
including into `data/raw/`, and the plaintext fields are removed from the record. No file in this
round contains an order ID or a GA client ID.

### B1. Configuration of the booking actions

| id | name | type | category | incl. in Conversions | primary | attribution | lookback | floodlight activity | default value |
|---|---|---|---|---|---|---|---|---|---|
| 415339895 | `QR_Booking` | **FLOODLIGHT_TRANSACTION** | PURCHASE | no | no | UNKNOWN | **90** | 2648297, tag `maste0`, group `sales0` | 0, always=false |
| 207919651 | `Booking` | **WEBPAGE** | PURCHASE | no | yes | GOOGLE_SEARCH_ATTRIBUTION | **30** | none | 1, always=false |
| 2353383 | `Booking` | WEBPAGE | PURCHASE | no | yes | GOOGLE_ADS_LAST_CLICK | 30 | none | 1, always=false |
| 5431929 | `Booking` | WEBPAGE | DEFAULT | no | yes | GOOGLE_ADS_LAST_CLICK | 30 | none | 1, always=false |
| 7518149465 | `QR_FlightSearch_VBB` | FLOODLIGHT_TRANSACTION | PURCHASE | no | no | UNKNOWN | 90 | 376254416, tag `qr_fl0`, group `sales0` | 0, always=false |
| 817202046 | `DONOTUSE_BOOKINGS` | FLOODLIGHT_ACTION | DEFAULT | no | no | UNKNOWN | 90 | 11994056 | 0, always=**true** |
| 939039830 | `QR_DiscoverQatar_Booking` | FLOODLIGHT_TRANSACTION | PURCHASE | no | no | UNKNOWN | 90 | 12751631 | 0 |
| 347667299 / 347667311 | Android / iOS App Booking | FIREBASE custom | PURCHASE | no | yes | mixed | 30 | none | 1 |
| 7497705793 | `Retrieve Booking` | WEBPAGE | DEFAULT | no | yes | GOOGLE_ADS_LAST_CLICK | 30 | none | 0, always=true |

Only `QR_Booking` (415339895) and `Booking` (207919651) carry volume in the window. The other two
actions named `Booking` are dormant but still exist, and because reports segment on
`conversion_action_name` they would silently merge into a single line if they ever fired.

### B2 and B3. What one row is

All 89 rows belong to `QR_Booking`. The three `Booking` actions produce **zero** conversion rows,
because they are WEBPAGE conversions and `FROM conversion` only returns Floodlight conversions.

- `conversion_quantity` is **1000 on every one of the 89 rows**, with no variation. The field is
  scaled by 1000, so quantity is 1 throughout. **One row is one transaction with quantity one**,
  not a basket of tickets and not a passenger count. Quantity carries no information here.
- Status `ENABLED` on all 89, attribution type `VISIT` on all 89. No adjustments or restatements.
- Revenue zero on **2 rows of 89**, 2.2 percent.
- **Duplicates: 1 of 88 distinct hashed order IDs appears twice**, and both of its rows carry
  revenue. So duplication is 1.1 percent of orders and it is not a zero revenue mechanism.

**Error and fix.** The first pass reported 87 of 89 rows where reported revenue disagreed with
`floodlight_original_revenue`. That was a unit mistake in the analysis script, not a data problem:
`conversion_revenue_micros` was divided by 1e6 while `floodlight_original_revenue` was not.
`floodlight_original_revenue` is also in micros. The ratio is exactly 1,000,000 on every row with
revenue, minimum, median and maximum identical. **The two revenue fields agree on all 89 rows.**

### B4. Destination split, Floodlight transaction rows

| group | rows pre 2 Sep | rows from 2 Sep | revenue pre | revenue from |
|---|---|---|---|---|
| UK+IE | 14 | **1** | 13,736 | 852 |
| long-haul | 24 | 21 | 28,233 | 27,339 |
| regional | 13 | 8 | 10,775 | 7,371 |
| no destination | 2 | 6 | 902 | 3,920 |

### B5. Conversion rows against aggregate all_conversions, same action, same dates

| action | id | conversion rows | row revenue | all_conversions | aggregate value |
|---|---|---|---|---|---|
| `QR_Booking` | 415339895 | **89** | 93,129 | **309.0** | 396,593 |
| `Booking` | 207919651 | **0** | 0 | **279.0** | 288,826 |
| total reported as "bookings" | | 89 | 93,129 | **588.0** | **685,419** |

Two separate gaps, and they compound.

First, `Booking` is not a Floodlight tag at all. It is a Google Ads website conversion with
`GOOGLE_SEARCH_ATTRIBUTION` and a 30 day window, and it contributes 279 conversions and 288,826 USD
with no underlying Floodlight transaction. Any report that adds `QR_Booking` and `Booking` is
summing two different measurement systems.

Second, `QR_Booking` itself reports 309 attributed conversions against 89 actual transaction rows,
a factor of **3.47**. `all_conversions` is a modelled, attributed, cross device number; the
conversion resource is the transaction ledger. They are not the same quantity.

Attributed against actual, by destination group, 1 Aug to 1 Sep:

| group | all_conversions (QR_Booking) | conversion rows | inflation |
|---|---|---|---|
| UK+IE | 57.0 | 14 | 4.1x |
| long-haul | 74.0 | 24 | 3.1x |
| **regional** | **127.0** | **13** | **9.8x** |

Regional is inflated roughly three times more than long-haul. That is the answer to why regional
shows far more Floodlight bookings than Adobe.

### The UK number, split by action

| group | period | `QR_Booking` | `Booking` | total |
|---|---|---|---|---|
| UK+IE | pre 2 Sep | 57.0 | 55.6 | 112.6 |
| UK+IE | **from 2 Sep** | **0.0** | 5.9 | **5.9** |
| long-haul | pre 2 Sep | 74.0 | 79.8 | 153.8 |
| long-haul | from 2 Sep | 24.0 | 42.3 | 66.3 |
| regional | pre 2 Sep | 127.0 | 58.3 | 185.3 |
| regional | from 2 Sep | 17.0 | 17.7 | 34.7 |

UK+IE Floodlight bookings go to **exactly zero** after 2 September, and the 5.9 that remain are
entirely the WEBPAGE action. One single UK+IE Floodlight transaction row exists in the whole
period from 2 September to 5 October. Long-haul over the same split went 74.0 to 24.0 and regional
127.0 to 17.0, so both fell hard but neither reached zero.
