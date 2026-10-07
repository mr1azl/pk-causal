# PK VBB investigation: handover to Cowork (SA360 API on the laptop)

*Written 5 Oct 2026. Audience: Cowork running on the user's laptop with SA360 Reporting API access.
Background: `value_audit/PK_DE_FSV_REPORT.md` and the six-market deck (`deck/QR_JF_VBB_Six_Markets_Review.pptx`).*

---

## 0. Instructions for Cowork (read first)

**Everything stays on this laptop.** No uploads, no pastebins, no cloud notebooks, no emailing data out.

1. **Create one working folder** and keep everything in it:

   ```
   ~/pk_vbb_investigation/
     README.md          what the folder is, how to re-run everything (keep it current)
     LOG.md             running log: one entry per check (date, query file, result, conclusion)
     FINDINGS.md        final answers, one section per check below (C1 to C10)
     config/
       settings.example.env   template of the env vars (no secrets)
     scripts/           every script and query used, numbered by check (c01_setup.py, c02_....sql, ...)
     data/raw/          untouched API responses (CSV or JSONL), file name = check + date range
     data/clean/        derived tables
     outputs/           charts and tables used in FINDINGS.md
   ```

2. **Store every script and every query as a file in `scripts/`** before running it. No one-off code typed
   only in the chat. Each script must run again from the command line and write its output to `data/` or
   `outputs/`. Put the exact command at the top of the script as a comment.
3. **Credentials**: read them from environment variables or the existing local OAuth setup. **Never write a
   token, client secret or password into a script, notebook, log or output** (an earlier notebook in this
   project leaked a credential this way). `config/settings.example.env` lists variable names only.
4. **Log as you go**: after every check, append to `LOG.md`: what was run, the row count, the date range
   actually returned, the key number, and what it means. If a field name was wrong or a query failed,
   log that too, with the fix.
5. **Raw conversion-level data holds order IDs with GA client IDs: personal data.** Keep it in
   `data/raw/` only. Never copy it into `FINDINGS.md` or a chart. Hash order IDs before any shared output.
6. **Before the first real query, check field names** with the API's field service
   (`searchAds360Fields.search`, for example `SELECT name, selectable, filterable WHERE name LIKE 'conversion.%'`).
   The field names in this document are a best guess from the API reference. Fix them if they differ and note the
   change in `LOG.md`.
7. **Post a short progress note to the user every two or three checks** (what finished, what is next).
8. **Writing style for anything the user sees**: no em dashes; use commas, colons or full stops.
9. **At the end**, `FINDINGS.md` answers the five questions in section 2 with numbers, and `README.md` lists
   the scripts in run order.

---

## 1. What we already know (do not re-derive, use as the reference)

| Fact | Value | Source |
|---|---|---|
| PK switch to VBB | 2 Sep 2026, Maximise Conversion Value, rule-based floodlight `QR_FlightSearch_VBB`, no target ROAS (client-confirmed) | client |
| Bid strategy before | Maximise Conversions, no target | client |
| PK portfolio | `PK_FlightSearch_VBB - Conv Value Δ`, holds every PK non-brand search campaign | SA360 export |
| Shared budget | $508.30 a day today; cut around 20 Aug (before VBB) | SA360 export |
| Bookings a day (non-brand VBB portfolio) | 9.5 before the cut (17 May to 19 Aug), 5.9 after the cut (21 Aug to 1 Sep), 4.4 after the switch (2 to 27 Sep) | daily monitoring report |
| Spend a day | $904, $417, $513 for the same three periods | same |
| Searches a day | 886 before, 164 after the switch (-82%) | campaign export |
| Cost per click | $0.23 before, x7.2 in week 1 (x13 on 8 Sep), $0.38 on 27 Sep | daily report |
| **Zero-revenue bookings** | share of bookings on days with bookings but $0 revenue: 4% Jun to Jul, 6% Aug, **68% 2 to 13 Sep**, 28% 14 to 27 Sep. No other big unit above 5% | daily report |
| VBB value fallback | 24% of PK searches valued at $0.50 on 1 Sep (route has no Firestore document, empty OND, multi-leg OND) | conversion export, 1 Sep |
| Value per search | -40% in launch week (same 48 campaigns); 11.9% of searches with zero value vs 0.4% before | campaign export |

**The open issue**: PK bookings fell a little at the switch (-15% net, within noise) but **PK revenue
cannot be trusted since 2 Sep**, and the bidder optimises on value. The checks below aim to find out (a) why
bookings arrive with no revenue, (b) whether the bidding has recovered, and (c) whether the value feed the
bidder sees is sound.

---

## 2. The five questions FINDINGS.md must answer

1. Why do PK non-brand bookings arrive with $0 revenue since 2 Sep, and is it still happening?
2. Exactly what changed in the PK account, and when (bid strategy, conversion goals, budget, campaigns)?
3. What does the PK portfolio actually optimise on (which conversion actions, primary or not)?
4. Has PK recovered since 27 Sep (cost per click, searches, bookings, revenue per $)?
5. Is the value sent to SA360 for PK searches sound (fallback share, zero values, duplicates)?

---

## 3. Setup (C0)

- **C0.1 List accounts**: run on the manager account, find the PK account(s) (name contains `PK`) and the
  control accounts (PK brand, and if possible DE and CA for comparison).
  ```sql
  SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager,
         customer_client.status, customer_client.currency_code, customer_client.time_zone
  FROM customer_client
  ```
  Log the PK customer ID, its **currency** and **time zone** (a PKR account or a non-Doha time zone changes
  how revenue and dates read).
- **C0.2 Custom columns**: list the account's custom columns (`customColumns.list`) and find the IDs of
  **Bookings (FL)** and **Revenue (FL)**. Log their formulas: which floodlight activity, which attribution
  model, conversion date or click date. These are the two success metrics.

---

## 4. Checks

Date range for every daily query: **2026-08-01 to yesterday**, so August is the clean baseline.
Segment by `segments.date` unless stated.

### C1. Zero-revenue bookings (top priority)

Goal: find where the revenue disappears.

- **C1.1 Daily booking count vs revenue, per conversion action, PK non-brand.**
  ```sql
  SELECT segments.date, campaign.id, campaign.name, segments.conversion_action_name,
         metrics.all_conversions, metrics.all_conversions_value
  FROM campaign
  WHERE segments.date BETWEEN '2026-08-01' AND '<yesterday>'
  ```
  Output: per day, bookings and revenue for the booking floodlight. Recompute the zero-revenue share
  (bookings on days with bookings but $0 revenue). It should match 6% in Aug, 68% 2 to 13 Sep, 28% 14 to
  27 Sep. Extend it to today: is it still happening?
- **C1.2 Same with the custom columns** Bookings (FL) and Revenue (FL). If C1.1 has revenue but C1.2 does not
  (or the reverse), the issue is the **column definition** (attribution, date basis), not the tag.
- **C1.3 Conversion-level rows for the booking activity** (the strongest check).
  ```sql
  SELECT conversion.id, conversion.advertiser_conversion_id, conversion.floodlight_order_id,
         conversion.conversion_date_time, conversion.conversion_visit_date_time,
         conversion.conversion_revenue_micros, conversion.floodlight_original_revenue,
         conversion.conversion_quantity, conversion.status, conversion.attribution_type,
         campaign.name
  FROM conversion
  WHERE conversion.conversion_date_time BETWEEN '2026-08-01' AND '<yesterday>'
  ```
  (filter to the booking floodlight activity; field names to confirm in C0). For each day: rows, rows with
  revenue 0 or null, and `floodlight_original_revenue` vs `conversion_revenue_micros`.
  Read it this way:
  | What you see | Likely cause | Next step |
  |---|---|---|
  | Booking rows exist, revenue 0 **and** original revenue 0 | the tag fires without a revenue value (site or tag change around 2 Sep, PK site or PK locale) | ask the web/tag team for floodlight booking-tag changes 1 to 3 Sep; compare with Adobe sales for the same days |
  | Original revenue > 0, reported revenue 0 | currency conversion or revenue cap/filter in SA360 | check the floodlight activity's currency and revenue settings; log the PK account currency |
  | Revenue present at conversion level but missing in daily report | attribution or date basis | compare conversion date vs click date; check the custom column |
  | Status = removed / adjusted | conversion adjustments or restatements | list the adjustments and when they were applied |
  | Duplicate order IDs, one with revenue, one without | double firing | count duplicates per day |
- **C1.4 Is it PK only?** Run C1.1 for PK brand, and if time allows DE and CA VBB portfolios.
  Earlier result: DE, CA and SA stayed clean through their own switches, and FR (never VBB) went to 33%
  from 14 Sep. If PK brand also shows zero revenue, it is a **site/tag** issue, not VBB.
- **C1.5 Split** the zero-revenue rows by engine (Google vs Microsoft), device, and campaign type
  (Dest/City, Dest/Country, O&D/Country, O&D/Routes). One concentrated cell points to the cause.

### C2. What changed, and when (change history)

- **C2.1** Try the change history through the API (`change_event` or equivalent; may not be exposed in the
  SA360 Reporting API). If it is not available, export **Change history** from the SA360 UI (and from the
  Google Ads UI for the PK sub-account) for **1 Aug to today** into `data/raw/` as CSV, and parse it with a
  script.
- List with dates: bid strategy changes, portfolio membership, **conversion goal / conversion action
  changes**, budget amount changes, campaign status changes, floodlight/conversion action edits.
- Answer: exact switch date and time, exact budget-cut date and from/to amount, anything else changed
  between 1 and 13 Sep (the window when revenue went missing).

### C3. What the PK portfolio optimises on

- **C3.1 Portfolio snapshot**:
  ```sql
  SELECT bidding_strategy.id, bidding_strategy.name, bidding_strategy.type, bidding_strategy.status,
         bidding_strategy.maximize_conversion_value.target_roas, bidding_strategy.campaign_count
  FROM bidding_strategy
  ```
  Confirm: Maximise Conversion Value, **no target ROAS**.
- **C3.2 Conversion actions**:
  ```sql
  SELECT conversion_action.id, conversion_action.name, conversion_action.status,
         conversion_action.type, conversion_action.include_in_conversions_metric,
         conversion_action.floodlight_settings.activity_id
  FROM conversion_action
  ```
  Answer: is `QR_FlightSearch_VBB` the only action included? **Is `QR_FlightSearch_VBB_ML` also included**
  (double counting the value)? Is the booking floodlight included (it is already inside the VBB value as
  "sales" rows, so including it again would double count bookings)?
- **C3.3** If the goal settings are not visible through the API, take them from the portfolio's settings page
  in the UI and record them in `FINDINGS.md`.

### C4. Recovery since the switch

- **C4.1 Daily performance, PK non-brand portfolio and PK brand**:
  ```sql
  SELECT segments.date, campaign.id, campaign.name, campaign.bidding_strategy,
         metrics.cost_micros, metrics.clicks, metrics.impressions,
         metrics.search_impression_share, metrics.search_budget_lost_impression_share,
         metrics.search_rank_lost_impression_share
  FROM campaign
  WHERE segments.date BETWEEN '2026-08-01' AND '<yesterday>'
  ```
  Plus searches (the VBB conversion count) and bookings/revenue from C1.
  Output a weekly table: spend, clicks, cost per click (cost / clicks, click-weighted), searches, bookings,
  revenue, revenue per $, budget-lost and rank-lost impression share.
- **C4.2 Compare** with the three reference periods in section 1. Is cost per click back near $0.23 to
  $0.40? Are bookings back near 5.9 a day (post-cut level) at the same spend?
- **C4.3 Bid strategy status** per campaign (learning, limited, eligible) if exposed; otherwise from the UI.

### C5. Budget

- **C5.1**
  ```sql
  SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
         campaign_budget.explicitly_shared, campaign_budget.status
  FROM campaign_budget
  ```
  Today's amount should be $508.30. Combine with C2 for the history.
- **C5.2** Daily spend / daily budget: is PK spending the full budget every day (budget-limited) or not?

### C6. The value feed the bidder sees

- **C6.1 Daily value distribution of the search conversions** (`QR_FlightSearch_VBB`, conversion level,
  PK non-brand): count, share at exactly **$0.50** (fallback), share at **$0** or null, median value,
  value per search. Earlier: $0.50 on 24% of PK searches (1 Sep), zero-value 11.9% in the week of 6 Sep.
- **C6.2 Order ID** = `{type} - {ond} - {GA client id} - {unix s}`; type `search` (value = FSV) or `sales`
  (booking revenue, sent to both VBB actions). The ML action writes `search ` with a trailing space.
  Per day: rows of type `sales` vs bookings in C1 (do the booking revenues reach the VBB action even when the
  booking floodlight shows $0?). Duplicates per order ID.
- **C6.3** Top 30 PK ONDs at $0.50 since 2 Sep (to send to the FSV team). Compare with
  `value_audit/pk_fallback_onds.csv` from 1 Sep.

### C7. Where the spend went (optional)

Daily spend, clicks, VBB value and bookings by campaign family (Dest/City, Dest/Country, O&D/Country,
O&D/Routes, and destination). Earlier: spend moved to the campaigns with most VBB value per $; UK country
fell from $258 to $15 a day. Check it still holds and whether bookings followed.

---

## 5. Order of work

1. C0 (setup, IDs, currency, custom columns).
2. **C1** (zero revenue) and **C2** (change history): together they should explain the issue.
3. C3 (what it optimises on).
4. C4 and C5 (recovery, budget).
5. C6, then C7 if time allows.
6. Write `FINDINGS.md` (one section per question in section 2, with the number, the script that produced it
   and the conclusion) and update `README.md`.

## 6. What to hand back

- `FINDINGS.md` and `outputs/` (no raw data, no order IDs).
- A short list of asks for the client or tag team, for example: "booking floodlight on the PK site sends no
  revenue since X", "VBB_ML action included in the PK goal", "budget cut on X from $A to $B".

---

## 7. Prompt to paste into Cowork

> Read `COWORK_HANDOVER_PK.md` (attached) and follow it. Work only on this laptop: create
> `~/pk_vbb_investigation/` with the folder layout in section 0, save every script and query in `scripts/`
> before running it, keep raw API outputs in `data/raw/`, and log every check in `LOG.md` as you go. Never
> write credentials into any file. Use my existing SA360 API access. Start with C0, then C1 and C2. Give me
> a short progress update every two or three checks. Finish with `FINDINGS.md` answering the five questions
> in section 2, and a `README.md` listing the scripts in run order. No em dashes in anything you write for me.
