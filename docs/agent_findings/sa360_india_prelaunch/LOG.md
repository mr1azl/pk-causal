# India pre-launch, run log

Rules: every script saved in `scripts/` before it runs, raw API output in `data/raw/`,
derived tables in `data/clean/`. No credentials, no order IDs, no GA client IDs, no gclids
in any script, log or output. Order IDs are hashed inside the script before any write.

Dates below are the ranges the API actually returned, not the ranges requested.

---

## I0 Setup

### i00_accounts.py
First attempt failed: `UNRECOGNIZED_FIELD: customer_client.account_type`. The SA360 API exposes
only 12 `customer_client` fields and engine type is not one of them. Fixed by reading
`customer.account_type` and `customer.engine_id` from each candidate account instead.

704 accounts under MCC 1144701035. 6 match an India market token.

| id | name | engine | currency | status |
|---|---|---|---|---|
| 4881339235 | Google-GCCLI-IN-EN | GOOGLE_ADS | USD | ENABLED |
| 4034062923 | Google-GCCLI-IN-EN-2 | GOOGLE_ADS | USD | ENABLED |
| 1580300080 | Google-GCCLI-IN-EN-Brand | GOOGLE_ADS | USD | ENABLED |
| 2073557592 | Bing-SEA_SASC-IN-EN | MICROSOFT | USD | ENABLED |
| 7590642880 | Bing-SEA_SASC-IN-EN-2 | MICROSOFT | USD | ENABLED |
| 9168480809 | Bing-SEA_SASC-IN-EN-Brand | MICROSOFT | USD | ENABLED |

### i01_pick_account.py
Range returned 2026-07-16 to 2026-10-07, 84 days, 12 weeks to yesterday. Google accounts only.

| id | cost | clicks | campaigns with spend | name |
|---|---|---|---|---|
| 4034062923 | 277,390 | 957,508 | 930 | Google-GCCLI-IN-EN-2 |
| 1580300080 | 47,984 | 503,891 | 3 | Google-GCCLI-IN-EN-Brand |
| 4881339235 | 5,279 | 8,747 | 1 | Google-GCCLI-IN-EN |

**Choice logged: `4034062923` Google-GCCLI-IN-EN-2 is the main non-brand account.** It carries
98 percent of Google non-brand India spend. `4881339235` holds a single spending campaign and is
excluded; it should be checked before launch in case it is scheduled to be switched too.
Bing is out of scope, the same decision taken for PK.

### i02_inventory.py
15,081 campaigns in 4034062923, 15,080 non-brand (1 excluded as brand or pmax), all channel SEARCH.
Status: 12,808 REMOVED, 1,251 PAUSED, **1,021 ENABLED**.

Naming: **100 percent of spend on the pipe form**, 0 percent legacy. The legacy underscore form
exists only on REMOVED campaigns with zero spend. **Destination code parses on 100 percent of
non-brand spend.** This is cleaner than PK, where both conventions were live at once.

Taxonomy read from the data: `Google|IN|<Dest or O&D>|<Country, City or Routes>|<origin>|<dest>|<lang>|<match>`.
Live campaigns: 92 Country, 210 City, 986 Routes. Origins are XXX (generic), IN, or an Indian city.

479 distinct destination codes, 251,592 USD over the window.

### Ambiguous codes resolved from keyword text, not assumed
| code | resolved as | evidence |
|---|---|---|
| AUS | Austin, Texas (North America) | "bengaluru to austin business class flights"; AUS never appears in a Country slot and no AU country code exists in the account |
| RSI | the Red Sea, Saudi Arabia (GCC and ME) | "first class flights to the red sea" |
| HAS | Ha'il, Saudi Arabia (GCC and ME) | "thiruvananthapuram to ha'il business class flights" |
| GE | Georgia the country (Caucasus) | "business class flights to georgia" |
| AZ | Azerbaijan (Caucasus) | "business class flights to azerbaijan" |

**Flag raised at I0 for I5:** the GE campaigns bid on the bare word "georgia", which in English
also names a US state. An India origin generic campaign on that term will collect both intents.
Carried forward to query hygiene.

### i03_groups.py, destination groups for an India origin
Written out explicitly in `lib_sa360.py` as `IN_UK_IE`, `IN_NORTH_AMERICA`, `IN_EUROPE`,
`IN_OCEANIA`, `IN_GCC_ME`, `IN_SOUTH_SE_ASIA`, `IN_INDIA`, `IN_AFRICA`, plus `IN_LATAM` and
`IN_EAST_CENTRAL_ASIA` used only for the finer region label.

Decisions, each reversible and each flipped by editing one set:
- Turkey and the Caucasus counted as Europe. Caucasus is 3.03 percent of spend, so this is
  material; it is reported separately as a region so it can be moved.
- Egypt and the Maghreb counted as Africa, not Middle East.
- India coded campaigns kept as their own group rather than folded into South and South-East
  Asia, because from an India origin they are the reverse direction, a named PK failure mode.

| group | cost 12w | share | campaigns | enabled |
|---|---|---|---|---|
| North America | 106,530 | 42.34% | 4,003 | 288 |
| Europe excl UK+IE | 59,330 | 23.58% | 4,412 | 376 |
| GCC and Middle East | 46,805 | 18.60% | 1,689 | 121 |
| UK+IE | 23,795 | 9.46% | 825 | 128 |
| Africa | 8,899 | 3.54% | 2,260 | 76 |
| Oceania | 4,718 | 1.88% | 320 | 8 |
| other (Latin America and Caribbean) | 1,515 | 0.60% | 706 | 24 |
| South and South-East Asia | 0 | 0.00% | 527 | 0 |
| India (reverse direction) | 0 | 0.00% | 199 | 0 |

Unclassified: 2 codes (ZWS, QPP), zero spend, 0.000 percent. Coverage is complete.

**Structural note carried into I1.** India is a long-haul outbound market: North America alone is
42 percent of spend and the four long-haul groups are 94 percent. South and South-East Asia and
India-coded campaigns exist in the account but every one of them is paused or removed and none
has spent in the window. PK was the opposite shape, regional-heavy. The PK read does not
transfer group by group, only mechanism by mechanism.

---

## I1 Baseline

### i10_conv_actions.py
36 conversion actions fire for India in the window. The seven that matter:

| action | id | type | primary for goal | all_conv | value | cross-device |
|---|---|---|---|---|---|---|
| QR_Booking | 415339895 | FLOODLIGHT_TRANSACTION | **False** | 2,043 | 2,826,849 | **79.0%** |
| Booking | 207919651 | WEBPAGE | True | 1,678 | 1,633,941 | 35.8% |
| QR_FlightSearch_VBB | 7518149465 | FLOODLIGHT_TRANSACTION | **False** | 289,498 | 10,579,583 | 10.3% |
| QR_FlightSearch_VBB_ML | 7634214862 | FLOODLIGHT_TRANSACTION | **False** | 289,485 | 6,957,252 | 10.3% |
| QR_FlightSearch | 415339889 | FLOODLIGHT_ACTION | True | 251,366 | 0 | 10.6% |
| Flight Search | 302811599 | WEBPAGE | True | 275,213 | 0 | 3.3% |
| Flight Search (TEST Sept2026) | 7743822940 | WEBPAGE | True | 177,876 | 50 | 4.0% |

**VBB search values already fire for India**, so I3 can be run on real data rather than deferred.
Both VBB variants fire on effectively the same events (289,498 against 289,485) but carry
different values, 10.58M against 6.96M, a ratio of 1.52. Which of the two a launched portfolio
would read is a question for the UI; the API does not say.

**Checked and set aside.** `primary_for_goal` is false on QR_Booking and on both VBB actions, and
the primary list is byte-identical in SA (47 actions) and India (47 actions), while PK has 55.
Since PK plainly did bid on the VBB value signal, `primary_for_goal` is not the switch that
selects it. The selection happens in the portfolio's own conversion settings, which this API does
not expose. Recorded as a UI check in I6, not as a finding.

### i11_pull_traffic.py and i12_pull_conv.py
Ranges returned exactly as requested. Conversions are a separate query from traffic because
segmenting on `conversion_action_name` forbids cost and clicks in the same SELECT, the
`PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE` error learned in PK. Joined on date
plus campaign id downstream.

| file | range returned | rows |
|---|---|---|
| i1_traffic 2026 | 2026-07-16 to 2026-10-07 | 61,264 |
| i1_conv 2026 | 2026-07-16 to 2026-10-07 | 123,887 |
| i1_traffic 2025 | 2025-07-16 to 2025-10-07 | 68,169 |
| i1_conv 2025 | 2025-07-16 to 2025-10-07 | 50,056 |

### i13_summary.py, 2026 by destination group

| group | cost | clicks | CPC | QR_Booking | per 1k clicks | cross-device | Booking webpage | per 1k | FS per click | VBB value per click |
|---|---|---|---|---|---|---|---|---|---|---|
| North America | 106,530 | 176,172 | 0.605 | 451 | 2.56 | **77.8%** | 172 | 0.97 | 0.362 | **18.43** |
| Europe excl UK+IE | 59,330 | 219,036 | 0.271 | 463 | 2.11 | **82.7%** | 129 | 0.59 | 0.348 | 12.40 |
| GCC and Middle East | 46,805 | 201,073 | 0.233 | 322 | 1.60 | **98.1%** | 36 | 0.18 | 0.307 | 8.13 |
| UK+IE | 23,795 | 80,502 | 0.296 | 197 | 2.45 | **78.7%** | 68 | 0.85 | 0.364 | 15.53 |
| Africa | 8,899 | 33,680 | 0.264 | 69 | 2.05 | **94.2%** | 9 | 0.28 | 0.333 | 12.58 |
| Oceania | 4,718 | 17,682 | 0.267 | 57 | 3.22 | **98.2%** | 4 | 0.23 | 0.308 | 8.56 |
| other | 1,515 | 5,999 | 0.253 | 17 | 2.83 | 88.2% | 6 | 1.04 | 0.302 | 8.41 |

Two things stand out before any calibration is done.

**Cross-device is worse in India than it was in PK.** PK regional, the worst group in that market,
ran at 82.7 percent. India runs at 94 to 98 percent in GCC and Middle East, Oceania and Africa.
At 98 percent, essentially every booking credited to those groups is a modelled device-switching
journey rather than an observed one.

**The two booking actions disagree by group, badly.** QR_Booking against Booking the webpage
action is 2.6 to 1 in North America and 8.9 to 1 in GCC and Middle East. Any report that adds
them, as the PK "Bookings (FL)" column did, is adding two populations whose ratio moves by a
factor of three across groups.

### i14_seasonality.py, same weeks 2025 against 2026

| group | clicks 25 | clicks 26 | CPC 25 | CPC 26 | QR_Bk per 1k 25 | 26 | change |
|---|---|---|---|---|---|---|---|
| North America | 463,773 | 176,172 | 0.045 | 0.605 | 1.76 | 2.56 | +46% |
| Europe excl UK+IE | 410,762 | 219,036 | 0.044 | 0.271 | 1.66 | 2.11 | +28% |
| GCC and Middle East | 107,866 | 201,073 | 0.051 | 0.233 | 1.52 | 1.60 | +5% |
| UK+IE | 59,907 | 80,502 | 0.064 | 0.296 | 1.42 | 2.45 | +72% |
| Africa | 46,773 | 33,680 | 0.050 | 0.264 | 1.58 | 2.05 | +29% |

**Checked: the year on year CPC jump is not a naming or structure artefact.** Both years are 100
percent pipe form, 1,101 campaigns in 2025 against 947 in 2026, clicks 1.09M against 0.96M.
Account cost went 51,149 to 277,390 and CPC 0.047 to 0.290, a **6.2 times rise year on year with
no VBB involved**. India is today 100 percent MAXIMIZE_CONVERSIONS on 6 portfolios, so this rise
came from an earlier move to conversion bidding.

**Consequence for the launch read:** 2025 is a usable seasonal shape for booking rate but is
useless as a CPC baseline, and any "CPC rose after VBB" claim must be measured against the 2026
level, not the 2025 one. The guardrails in I7 are therefore built on 2026 weeks only.

### Auction share, 2026, impression weighted

| group | impression share | top share | budget lost | rank lost | clamped |
|---|---|---|---|---|---|
| GCC and Middle East | 41.2% | 28.9% | 23.5% | 35.4% | 0.0% |
| Europe excl UK+IE | 57.0% | 46.6% | 15.6% | 27.4% | 0.0% |
| **North America** | 63.2% | 53.6% | 15.3% | **21.6%** | 0.0% |
| UK+IE | 58.5% | 47.5% | 17.7% | 23.8% | 0.1% |
| Africa | 60.6% | 49.3% | 13.4% | 26.0% | 0.1% |
| Oceania | 60.2% | 49.2% | 16.5% | 23.3% | 0.0% |

Clamping is negligible, so these averages are real and not reporting bounds, unlike PK in September.

**This is the PK profile.** PK entered the switch at 21.7 percent rank lost and 10.5 percent
budget lost and its CPC rose 6.6 times. SA entered at 53 percent rank lost and rose only 2.1
times. North America, 42 percent of India spend, sits at **21.6 percent rank lost**, almost
exactly PK's starting point, and already carries 15.3 percent budget lost. Carried into I4.

---

## I2 Transaction ledger and inflation

### i20_ledger.py
First attempt failed: `UNRECOGNIZED_FIELD` on `conversion.floodlight_original_revenue_micros`,
`conversion.conversion_action_name` and `conversion.visit_date_time`. The resource exposes 24
fields; the correct names are `conversion.floodlight_original_revenue` (still in micros, the PK
unit trap), `conversion.conversion_visit_date_time`, and the action name comes from
`segments.conversion_action_name`.

Second issue caught on inspection, not by an error: the conversion `resourceName` embeds the raw
conversion and visit ids. It is now hashed like the other identifiers. Verified afterwards that
no raw conversion resource name remains in `data/raw/`.

Range returned 2026-08-13 to 2026-10-07. **243 rows.**

### Scope correction
The ledger query carries no non-brand filter, so it included
`Google|IN|Perf_Max|Generic|XXX|XXX|EN`, while the campaign inventory excludes Performance Max by
construction. The first run therefore put 103 ledger rows in "other" and their attributed twins in
"none". Performance Max is now excluded from the group table and reported on its own line.

**Performance Max holds 103 of 243 India bookings, 42 percent.** It is not a search portfolio and
would not move in a VBB search launch, but any before and after comparison that reads account
level bookings will be dominated by it.

### i21_inflation.py, search non-brand only

Ledger structure matches every other market examined: `conversion_quantity` is 1000 on all 243
rows, status ENABLED on all, attribution VISIT on all, `floodlight_original_revenue` agrees with
`conversion_revenue_micros` on **all 243** rows, 1 duplicate hashed order ID.

| group | ledger rows | all_conversions | ratio | cross-device | same-device over ledger | zero revenue | flag |
|---|---|---|---|---|---|---|---|
| Europe excl UK+IE | 49 | 310 | 6.33 | 82.6% | 1.10 | 2 | FLAG |
| North America | 58 | 264 | 4.55 | 75.8% | 1.10 | 2 | FLAG |
| GCC and Middle East | 5 | 226 | **45.20** | 97.8% | 1.00 | 0 | FLAG |
| UK+IE | 24 | 130 | 5.42 | 79.2% | 1.12 | 0 | FLAG |
| Africa | 2 | 48 | 24.00 | 95.8% | 1.00 | 0 | FLAG |
| Oceania | 1 | 31 | 31.00 | 96.8% | 1.00 | 0 | FLAG |
| other | 1 | 13 | 13.00 | 92.3% | 1.00 | 0 | FLAG |
| Performance Max (separate) | 103 | 239 | 2.32 | 38.5% | 1.43 | | |

**Every search group flags above 3x.** Search non-brand overall: 140 ledger rows against 1,022
all_conversions, **ratio 7.30**. Revenue: 141,468 USD in the ledger against 1,431,513 attributed,
**ratio 10.12**.

**Same-device over ledger is 1.00 to 1.12 in every group.** Strip cross-device and the attributed
count collapses onto the ledger almost exactly. Cross-device modelling is not part of the
inflation, it is essentially all of it. That is the PK conclusion reproduced, and more sharply:
PK's same-device ratios landed at 1.43 to 1.69, India's at 1.00 to 1.12.

Small-count caveat: GCC and Middle East, Africa, Oceania and other rest on 5, 2, 1 and 1 ledger
rows. Direction is reliable, magnitude is not.

---

## I3 Value calibration by destination

### i30_calibration.py
Window 2026-08-13 to 2026-10-07, the 8 weeks the ledger covers, so both sides use the same days.
Measured twice: against ledger revenue, which is what actually happened, and against attributed
booking value, which is what the bidder reads.

| group | clicks | search value per click | booking value per click (ledger) | ratio | x median | scale needed | flag |
|---|---|---|---|---|---|---|---|
| Africa | 24,711 | 11.94 | 0.03 | 389.77 | **8.00** | 0.12 | **yes** |
| GCC and Middle East | 169,236 | 7.74 | 0.07 | 116.38 | **2.39** | 0.42 | **yes** |
| UK+IE | 58,391 | 15.46 | 0.22 | 70.40 | **1.44** | 0.69 | **yes** |
| Europe excl UK+IE | 151,647 | 12.22 | 0.25 | 48.74 | 1.00 | 1.00 | no |
| North America | 112,065 | 18.15 | 0.64 | 28.50 | 0.58 | 1.71 | no |
| Oceania | 11,805 | 7.80 | 0.39 | 20.17 | 0.41 | 2.42 | no |
| other | 3,899 | 9.00 | 0.69 | 13.02 | 0.27 | 3.74 | no |

On the attributed view, which is less noisy because it does not depend on 140 ledger rows:

| group | ratio | x median | scale needed | flag |
|---|---|---|---|---|
| North America | 5.46 | **1.40** | 0.71 | **yes** |
| UK+IE | 5.26 | **1.35** | 0.74 | **yes** |
| Europe excl UK+IE | 4.64 | 1.19 | 0.84 | no |
| Africa | 3.89 | 1.00 | 1.00 | no |
| GCC and Middle East | 3.75 | 0.96 | 1.04 | no |
| Oceania | 2.58 | 0.66 | 1.51 | no |
| other | 1.28 | 0.33 | 3.03 | no |

**UK+IE is flagged on both views.** It is the only group that is. PK's failure was UK campaigns
whose search value ran 5.7 against 3.0 for regional; India's UK+IE runs 1.35 to 1.44 times the
median on the same construction. Smaller than PK but in the same direction, in the same group,
before launch.

The two views disagree about Africa and GCC and Middle East, which look extreme on the ledger and
ordinary on the attributed view. That disagreement is itself the I2 finding: those groups have
almost no ledger bookings and almost pure cross-device attribution, so their ledger ratio is
measuring the absence of transactions rather than a value error.

### Destinations with no transactions at all
Of the top 30 destinations by clicks, **11 have zero ledger bookings in 8 weeks**, together
108,734 clicks and **27,519 USD**. Largest: AE 48,195 clicks and 11,976 USD, AUS 9,968 and 2,699,
GE 8,047 and 2,228, RUH 8,590 and 1,945. All of them carry a positive search value per click
between 6.61 and 15.39, so a value bidder has a signal to chase and no transaction evidence
behind it.

### i31_fallback.py and i32_fallback_summary.py
Window 2026-09-10 to 2026-10-07, 4 weeks. 83,761 rows pulled, 80,927 non-brand.

The order ID has the shape `search - origin - destination - tail`, and **when the OND is missing
the tail shifts left, so position 2 can hold a GA client ID beginning "GA1."**. The parser accepts
positions 1 and 2 only when they match three lowercase letters and discards anything else, and the
tail is never read. Verified: zero occurrences of "GA1." in `data/raw/`. The files written are
already sanitised and hold no identifier of any kind.

`floodlight_original_revenue` agrees with `conversion_revenue_micros` on all 80,927 rows.
5.5 percent of rows have no parsable OND.

| group | rows | value per row | at exactly 0.50 | at 0 | fallback share of value |
|---|---|---|---|---|---|
| Europe excl UK+IE | 25,291 | 24.50 | 36.6% | 0.0% | 0.75% |
| GCC and Middle East | 24,457 | 12.84 | 29.1% | 0.0% | 1.13% |
| North America | 16,140 | 38.46 | 26.5% | 0.0% | 0.34% |
| UK+IE | 8,611 | 32.45 | 18.4% | 0.0% | 0.28% |
| Africa | 4,048 | 25.95 | 28.2% | 0.0% | 0.54% |
| Oceania | 1,744 | 11.63 | 46.5% | 0.0% | 2.00% |
| other | 636 | 12.37 | 78.9% | 0.0% | 3.19% |

**Nothing is valued at zero anywhere.** Between 18 and 79 percent of searches fall back to 0.50,
but because 0.50 is tiny next to a 12 to 38 average, the fallback rows carry under 1.2 percent of
value in every group that matters. The fallback is a volume artefact, not a value distortion.
Worst single destination: **AZ at 93.9 percent fallback**, which carries 20 percent of that
destination's value.

### i33 and i34_route_match_v2.py: does the value belong to the campaign it is credited to
The order ID carries the route the user actually searched, so this answers directly the question
that was only inferred in PK.

First pass said 35.9 percent of rows matched. **That was wrong**, because it counted a country
code and a city inside that country as a mismatch: AE against DXB, CDG against PAR, LHR against
LON. The second pass resolves every code to a country or metro first, then compares.

| group | rows | same place | different place | share of value off route | searched India |
|---|---|---|---|---|---|
| GCC and Middle East | 23,514 | 80.2% | 19.8% | 33.1% | 10.6% |
| Africa | 3,742 | 82.6% | 17.4% | 12.3% | 4.9% |
| Oceania | 1,614 | 83.0% | 17.0% | 27.9% | 6.3% |
| Europe excl UK+IE | 23,825 | 74.3% | 25.7% | 22.7% | 9.0% |
| UK+IE | 8,118 | 73.8% | 26.2% | **28.6%** | **14.9%** |
| North America | 15,064 | 64.1% | 35.9% | 26.9% | **17.7%** |

Two mechanisms, both of them the PK failure seen directly for the first time.

**Reverse direction.** 17.7 percent of the search value credited to North America campaigns, and
14.9 percent of UK+IE, comes from a search for a flight **to India**. Top pairs: CA to DEL 404
rows, YYZ to DEL 228, DXB to DEL 183, LGW to DEL 129, YYZ to ATQ 110, AE to DEL 95, YYZ to AMD 92.
This is what PK's "the bidder bought reverse-direction queries on UK campaigns" looks like when
you can see the searched route.

**One campaign is simply mis-targeted.** The AUS campaign, Austin Texas, collects Melbourne 453,
Sydney 373, Adelaide 176 and Brisbane 103, which is **1,105 of its 1,595 search rows, 69 percent,
going to Australia**. "AUS" reads as Australia to searchers. The campaign spent 2,699 USD in 8
weeks and produced zero ledger bookings. Carried into I5.

---

## I4 Bid headroom

### i40_budgets.py
`campaign_budget` exposes only 4 fields in this API: `amount_micros`, `delivery_method`, `period`
and `resource_name`. There is no id, no name and no status, so budgets are keyed by the id at the
end of the resource name and carry no human readable label. First attempt failed on
`campaign_budget.id`, `.name` and `.status`.

85,269 budgets are defined in the account, almost all orphaned from removed campaigns.
**Ten of them carry all 1,021 enabled non-brand campaigns.**

| budget | daily amount | enabled campaigns | spend per day | utilisation | groups |
|---|---|---|---|---|---|
| 15551442161 | 1,240 | 144 | 1,295 | **104%** | Europe 62, North America 26 |
| 15561308605 | 752 | 102 | 758 | **101%** | Europe 25, North America 24 |
| 15556065045 | 185 | 161 | 385 | **208%** | Europe 83, North America 33 |
| 15590721288 | 446 | 453 | 337 | 76% | Europe 166, North America 140 |
| 15839797560 | 111 | 4 | 113 | **102%** | Europe 4 |
| 15551453642 | 118 | 81 | 95 | 80% | North America 46, Europe 19 |
| 15556041258 | 70 | 24 | 62 | 89% | North America 14, Europe 6 |
| 15748426307 | 37 | 8 | 45 | **122%** | UK+IE 8 |
| 15736487415 | 7 | 28 | 6 | 84% | Europe 11, GCC and ME |
| 15649869771 | 5 | 16 | 4 | 93% | other 16 |

**Total daily budget 2,972 USD against 3,102 USD actually spent per day, 104.4 percent.**
Every enabled campaign is on a shared budget and the account as a whole is already running at
capacity. Five of the ten budgets are over 100 percent, one at 208 percent.

This is the PK precondition, present before the switch rather than after it. PK's collapse was not
caused by bidding too high in the abstract, it was caused by bidding higher against a fixed shared
budget that had no slack. India has less slack than PK had.

### i41_headroom.py, then i42_risk_split.py
The single combined risk score in i41 was wrong to publish: budget utilisation is a property of
the shared budget, not of the campaign, so all 161 campaigns on the 208 percent budget sorted to
the top and rank lost stopped discriminating. Replaced with two separate rankings in i42, because
they are two different failure modes. The i41 score is kept in the CSV but should not be read.

**Escalation risk, lowest rank lost, campaigns over 100 USD in 4 weeks**

| campaign | cost 4w | CPC | rank lost | impression share |
|---|---|---|---|---|
| Google\|IN\|O&D\|Routes\|BLR\|BER\|EN\|PHR | 109 | 0.61 | 4.2% | 94.3% |
| **Google\|IN\|O&D\|Country\|IN\|US\|EN\|MOD** | **4,968** | 0.90 | **4.8%** | 84.0% |
| Google\|IN\|O&D\|Country\|IN\|GE\|EN\|MOD | 745 | 0.27 | 7.3% | 75.4% |
| Google\|IN\|O&D\|Routes\|BOM\|EDI\|EN\|PHR | 100 | 0.31 | 9.2% | 86.7% |
| Google\|IN\|O&D\|Country\|IN\|AZ\|EN\|MOD | 358 | 0.31 | 9.3% | 77.5% |
| Google\|IN\|O&D\|Country\|IN\|FI\|EN\|MOD | 848 | 0.26 | 9.6% | 74.6% |
| Google\|IN\|O&D\|Routes\|DEL\|DXB\|EN\|PHR | 1,706 | 0.24 | 10.2% | 68.0% |

**64 campaigns sit below PK's 21.7 percent starting point, 32,158 USD over 4 weeks, 46 percent of
the spend measured here.**

Share of each group's spend sitting below that line: Oceania 86 percent, Africa 62, North America
58, Europe excl UK+IE 48, UK+IE 43, GCC and Middle East 34.

The standout object in the account is `Google|IN|O&D|Country|IN|US|EN|MOD`: 4,968 USD in 4 weeks,
**4.8 percent rank lost at 84 percent impression share**, on the budget running at 208 percent.
There is almost nothing left for it to win by bidding higher and no budget to pay for it.

**Budget wall risk** is effectively a list of the 161 campaigns on budget 15556065045, led by
`Google|IN|Dest|Country|XXX|QA|EN|MOD` at 25.7 percent budget lost. The campaign level detail
matters less than the budget level fact above.

---

## I5 Query hygiene

### Capability gap found
`shared_set`, `shared_criterion` and `campaign_shared_set` **do not exist in this API**: the field
service returns zero fields for all three. Shared negative keyword lists therefore cannot be read
from here at all. Everything below is campaign and ad group level only. A shared list could in
principle cover some of the gaps found, and that has to be checked in the UI before any of this is
acted on. Added to `SA360_API_CAPABILITIES.md`.

### i50_keywords.py and i52_hygiene.py
11,844 enabled keywords in enabled non-brand campaigns. **BROAD 7,140 (60 percent), PHRASE 4,704.
No exact match anywhere in the account.**

| group | keywords | mix |
|---|---|---|
| Europe excl UK+IE | 4,158 | BROAD 62%, PHRASE 38% |
| North America | 3,324 | BROAD 60%, PHRASE 40% |
| GCC and Middle East | 1,620 | BROAD 56%, PHRASE 44% |
| UK+IE | 1,410 | BROAD 60%, PHRASE 40% |
| Africa | 840 | BROAD 62%, PHRASE 38% |
| Oceania | 114 | BROAD 68%, PHRASE 32% |

By campaign name token: MOD 557 campaigns carrying 220,083 USD over 12 weeks, PHR 464 campaigns
carrying 31,510. **Broad campaigns carry 87 percent of spend.**

### Negatives
- Campaign level: **239** on enabled non-brand campaigns, sitting on **35 campaigns**.
- Ad group level: **0**. Confirmed twice, through `keyword_view` and through `ad_group_criterion`.
- Shared lists: not readable, see above.

What the 239 are: **232 flight number exclusions** ("flight qr 570", "qr501", "qr4773 flight"),
6 directional phrases, 1 other.

### Reverse direction negatives
Checked every enabled campaign that names a destination outside India for a negative matching
"to india" or "to" plus any of 25 Indian cities.

**1,021 of 1,021 have none. 100 percent. 986 of them have no campaign level negative of any kind.**
That covers all 251,592 USD of non-brand spend in the window.

| campaign | group | cost 12w | negatives |
|---|---|---|---|
| Google\|IN\|O&D\|Country\|IN\|US\|EN\|MOD | North America | 73,542 | 0 |
| Google\|IN\|Dest\|City\|XXX\|DXB\|EN\|MOD | GCC and Middle East | 7,304 | 0 |
| Google\|IN\|O&D\|Country\|IN\|AE\|EN\|MOD | GCC and Middle East | 7,282 | 0 |
| Google\|IN\|Dest\|Country\|XXX\|AE\|EN\|MOD | GCC and Middle East | 7,049 | 0 |
| Google\|IN\|Dest\|City\|XXX\|LGW\|EN\|MOD | UK+IE | 4,960 | 0 |
| Google\|IN\|Dest\|Country\|XXX\|CA\|EN\|MOD | North America | 4,816 | 0 |
| Google\|IN\|Dest\|City\|XXX\|AUS\|EN\|PHR | North America | 3,226 | 0 |

**This closes the loop with I3.** 60 percent broad match, no directional negatives anywhere, and
17.7 percent of the search value credited to North America campaigns coming from searches for
flights to India. The mechanism is not inferred, both ends of it are measured.

### Search terms
Not available in this API. `search_term_view` does not exist, and
`dynamic_search_ads_search_term_view` carries only a landing page and a resource name with no term
text. The UI export of the last 8 weeks is needed and has not been substituted with anything.

---

## I6 Portfolio and settings

### i60_portfolios.py
Portfolios read from the MCC, because portfolios owned by the manager account are invisible from
the client account. That was the PK lesson and it holds here: all 10 are MCC owned.

| portfolio | campaigns | cost 12w | type | target CPA | target ROAS | CPC ceiling |
|---|---|---|---|---|---|---|
| OnD Tier 2 Mid Routes - Conversions Δ | 161 | 99,028 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD Tier 1 Routes - Conversions Δ | 144 | 60,293 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD Tier 2 Low Routes - Conversions Δ | 102 | 53,260 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD T3 Routes V2 - Conversions Δ | 453 | 20,033 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD Tier 2 High Routes - Conversions Δ | 81 | 5,678 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| Push group - Conversions Δ | 8 | 4,529 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| DE Push IB - 1.09 - Conversions Δ | 4 | 4,160 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD Elite Routes - Conversions Δ | 24 | 3,741 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD New Dest - Conversions Δ | 16 | 491 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |
| OnD Tier 3 High Routes - Conversions Δ | 28 | 380 | MAXIMIZE_CONVERSIONS | **NOT SET** | NOT SET | NOT SET |

India is today **100 percent Maximize Conversions with no target CPA on any portfolio**, so the
only thing constraining spend is the budget. That matters for how the switch will behave: moving
to Maximize Conversion Value with no target ROAS does not add a constraint, it only changes what
is being maximised while leaving the same uncapped structure against the same fixed budgets.

The portfolios are tiered by route value, Elite through Tier 3 plus Push and New Dest, which is a
better structure than PK had and makes a staged launch possible.

### Geo
- 909 enabled campaigns on **PRESENCE / PRESENCE**, the tight setting.
- 113 on **PRESENCE_OR_INTEREST**, carrying 5,621 USD over 12 weeks, 2.2 percent of spend, and
  concentrated in **UK+IE (2,026 USD)** and Europe (1,748). Largest is
  `Google|IN|O&D|Routes|GOX|LHR|EN|MOD` at 1,294 USD.
- Targeted location is `geoTargetConstants/2356`, India, on all 1,021. One campaign adds 9222938.

PK was entirely PRESENCE_OR_INTEREST, so India is in better shape, but the exceptions sit in the
group already flagged on value calibration.

### Changes in the last 30 days
**646 of 1,022 enabled campaigns were modified in the last 30 days**, clustered on 14 September
(223), 13 September (154), 22 September (102), 23 September (102) and 15 September (57).
**Zero ad groups were modified.** What those edits were is not recoverable; `change_event` does not
exist in this API and `last_modified_time` keeps only the most recent edit per object. This needs
an answer before a launch date is set, because it is item 7 of the go table.

---

## I7 Holdout and guardrails

### i70, then i71_holdout_v2.py
Two errors in i70, both corrected.

**Structural fact that changes the design: budget maps one to one onto portfolio.** Each of the 10
budgets carries exactly one portfolio. But **7 of the 10 budgets carry campaigns from more than one
destination group**. So a holdout drawn at portfolio level is automatically budget separated, and a
holdout drawn inside a portfolio is not: the treated campaigns bidding higher would starve the
holdout campaigns sharing their budget, and the test would measure budget contention rather than
the strategy.

**Selection bug.** The nearest to the group mean rule picked whichever single campaign sat closest
regardless of size, so North America held out one campaign carrying **67 percent** of the group's
spend. Selection now excludes any campaign above 40 percent of its group and stops between 15 and
30 percent.

**Design A, hold out whole portfolios**

| portfolio | campaigns | spend 8w | share | CPC | bookings per 1k | group mix |
|---|---|---|---|---|---|---|
| OnD Tier 2 Mid Routes | 41 | 50,424 | 31.6% | 0.597 | 2.77 | North America 81% |
| OnD Tier 1 Routes | 96 | 48,352 | 30.3% | 0.260 | 1.63 | GCC 33%, Europe 23% |
| OnD Tier 2 Low Routes | 60 | 38,722 | 24.2% | 0.256 | 1.75 | GCC 52%, Europe 23% |
| OnD T3 Routes V2 | 69 | 10,312 | 6.5% | 0.264 | 1.69 | Europe 36%, GCC 26% |

Clean inference, no contention, but no balance: each portfolio has a different destination mix and
a different CPC, so holding one out does not hold out 20 percent of each group.

**Design B, campaign level stratified by destination group**

| group | campaigns | held out | spend held | share | CPC gap | booking rate gap | budgets shared |
|---|---|---|---|---|---|---|---|
| North America | 47 | 22 | 8,635 | 15.1% | **-61%** | -26% | 5 |
| GCC and Middle East | 39 | 1 | 6,971 | 17.7% | -1% | +3% | 1 |
| Europe excl UK+IE | 134 | 10 | 6,023 | 16.0% | -2% | -25% | 3 |
| UK+IE | 46 | 1 | 4,359 | 27.7% | -5% | -2% | 1 |
| Africa | 31 | 2 | 1,202 | 20.7% | +2% | +11% | 2 |
| Oceania | 5 | 3 | 361 | 12.0% | -7% | -100% | 0 |

GCC and Middle East, UK+IE and Africa match well on both measures. **North America cannot be
balanced**: `Google|IN|O&D|Country|IN|US|EN|MOD` is 67 percent of the group's spend at a CPC of
0.90 against 0.30 for the rest, so whichever arm holds it sets that arm's CPC. It has to be its own
stratum or stay in the treated arm with the group read excluding it. Oceania has too few campaigns
and no bookings in the holdout arm.

### i72_guardrails.py
Weekly bookings per 1,000 clicks, 8 weeks, with the exact Garwood one sided 90 percent Poisson
lower bound. The chi square quantile is inverted in the script with the regularised incomplete
gamma and a bisection, so nothing had to be installed.

| group | clicks 8w | ledger bookings | ledger mean | **ledger bound** | attributed mean | **attributed bound** | usable |
|---|---|---|---|---|---|---|---|
| North America | 112,065 | 58 | 0.52 | **0.43** | 2.36 | 2.17 | yes |
| Europe excl UK+IE | 151,647 | 49 | 0.32 | **0.27** | 2.04 | 1.90 | yes |
| UK+IE | 58,391 | 24 | 0.41 | **0.31** | 2.23 | 1.98 | yes |
| GCC and Middle East | 169,236 | 5 | 0.03 | 0.01 | 1.34 | 1.22 | **no** |
| Africa | 24,711 | 2 | 0.08 | 0.02 | 1.94 | 1.59 | **no** |
| Oceania | 11,805 | 1 | 0.08 | 0.01 | 2.63 | 2.04 | **no** |
| other | 3,899 | 1 | 0.26 | 0.03 | 3.33 | 2.22 | **no** |

**Only three of seven groups have a usable transaction based guardrail.** GCC and Middle East is
the sharpest case: 169,236 clicks, more than any other group, and **5 real bookings in 8 weeks**.
Its ledger bound of 0.01 per 1,000 clicks is a number nothing could ever breach, so it is not a
guardrail at all.

Those four groups can only be watched on the attributed number, which runs about 7 times the
ledger and is 95 to 98 percent cross-device modelled in exactly those groups. A guardrail written
against one measure and watched on the other would never fire, so each threshold above is labelled
with the measure it belongs to.

---

## Verification

`scripts/i90_verify.py` re-derives every headline number in `FINDINGS_india.md` from the clean
CSVs, independently of the scripts that produced them, and fails loudly on disagreement.

**40 checks passed, 0 failures.** Covered: 12 week spend and group shares, ledger and attributed
counts and both inflation ratios, Performance Max share, the UK+IE calibration flag on both views
and that it is the only group flagged on both, the 11 zero-booking destinations with their clicks
and cost, reverse direction percentages, the 10 budgets and 104.4 percent utilisation, the 64
campaigns below PK's rank lost line with their spend, the reverse direction negative counts, all
10 portfolios having no target of any kind, the guardrail usability count, and both account ROAS
figures.

The last check is a privacy sweep over every file in `data/raw/` and `data/clean/` for `GA1.`,
`gclid`, `refresh_token`, `client_secret` and `Bearer `. **Zero hits.**

## Capability notes contributed back
`SA360_API_CAPABILITIES.md` in the PK folder updated with: the three shared-set resources that
return zero fields, five field name traps, the requirement to select a segment in order to filter
on it, the GA client ID hazard in `floodlight_order_id`, and what that order ID makes possible.
