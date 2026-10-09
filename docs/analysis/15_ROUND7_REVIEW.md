# Review of round 7 (Google Ads API) and the India pre-launch handover

*8 Oct 2026.*

**Agent findings reviewed:** `docs/agent_findings/sa360_round7/`
- `FINDINGS_round7.md`;
- `7b` (VBB order ID and search value calibration);
- `7c` (lag);
- `7d` (four-market control);
- `LOG.md`.

**Data:** `data/sa360/round7/`.

**Agent code:** `agent_code/round7/`.

**India handover:** the data, log and scripts behind `docs/agent_findings/sa360_india_prelaunch/FINDINGS.md`
(already reviewed in `10_INDIA_PRELAUNCH_REVIEW.md`), now in `data/sa360/india_prelaunch/` and
`agent_code/india_prelaunch/`. Its FINDINGS file is identical to the one in the repo.

Round 7 reads the PK account through the Google Ads API, which gives what SA360 cannot:
- search terms;
- `change_status` (90 days) and `change_event` (30 days);
- shared negative lists;
- the VBB order ID, which carries the searched route on search and sales rows.

## 1. Accepted

1. **The lag curve (7c).** Half of bookings land within an hour of the click, 74% within a day and 95% within
   14 days. This is consistent with the fresh review (96% within 16 days). Read nothing on data younger than
   14 days.
2. **ML and base are the same tag on bookings.** They are two models on searches, with ML at 0.56 to 0.69 of base
   at account level in four markets.
3. **The tag is market blind (7d).** A search is valued at 2.5% to 4.7% of a booking in every market, while
   searches per booking vary tenfold: 103 in DE, 172 in CA, 519 in PK, 1,080 in India.
   - Without a target ROAS this has no effect.
   - With a target, it decides everything. A target must come from the realised return on whichever signal the
     portfolio reads, never from booking economics.
4. **An automated process rewrites budgets daily.** `CAMPAIGN_BUDGET/UPDATE` events appear on every one of the 24
   days the `change_event` pull actually covered, via Google Ads scripts and an internal tool. The 5 missing days (15, 22, 29 Sep, 6 and 7 Oct)
   are the last days of the query windows, which the date filter skipped (see item 5), not quiet days. This is the most important
   operational finding: any budget set for a test (including the GB switchback in `13`) can be overwritten.

   Who owns this automation, and what it optimises for, is now an open question for PK.
5. **Round 4's "no keyword modified" rested on `last_modified_time`, which keeps only the last edit.** That
   criticism is right. **But the `change_status` daily counts cannot date anything either** (corrected 9 Oct,
   after a second reader's check), so I withdraw the "3,737 criteria on 20 Aug, 3,300 on 3 Sep" dating and the
   link to the 20 Aug budget event. In `r02_changes.py` and `r2_change_status_by_day.csv`:
   - the 7-day windows filter `<= 'end date'`, which stops at midnight, so the last day of every window (a
     Friday) was never queried; no Friday appears in the output;
   - the first five windows return exactly 10,000 rows, the query `LIMIT`, so they are truncated;
   - counts pile onto Thursdays (36,082 of 77,121 rows), including 20 Aug, 27 Aug and 3 Sep;
   - `change_status` holds the latest change per resource, not a log of events.

   Round 4's conclusion (no UK-specific structural edit) still stands, on the proportional spread across segments.
   The dates do not.
6. **India negatives.** Every campaign carries shared lists, but those lists block only 13.6% of reverse-direction
   spend ($584 of $4,301 in 4 weeks), because the reverse negatives are brand-qualified. This corrects the
   wording in the India findings ("no reverse-direction negative"); the recommendation to add generic reverse
   negatives stands.
7. **Tagging oddities to raise.** `Google-AMER-CA-FR` has no VBB rows at all. `Google-NSW-DE-DE` has 123 search
   rows and no sales rows in two weeks.

## 2. Rejected: the "20 Sep CPC cap" mechanism

The Google Ads API is the better source, and everything in section 1 rests on it. The cap is the exception: it was
not read from the Google Ads data. The change log shows no bid strategy change on 20 Sep, and the agent inferred
the cap from the CPC flattening. The decisive check is a single read of the current portfolio setting at MCC level:
`bidding_strategy.maximize_conversion_value.cpc_bid_ceiling_micros` for `12222452141` (request 2 below).

Round 7's headline:
- UK auctions clear at 1.04 while the rest of PK clears at 0.17 to 0.24;
- a CPC cap set on 20 Sep "flattened everything to about 0.42";
- that cap priced UK+IE out of its own auctions.

The data do not support it.

- **There is no evidence of a cap.**
  - The user's first review (`docs/reviews/01_user_review_of_cowork_round1.md`) had already flagged it as
    unsupported.
  - Round 4 found no CPC ceiling on the PK portfolio.
  - Round 7's own log finds no bid strategy change on 20 Sep and assumes it happened at MCC level.
- **Campaign CPCs above 0.42 continue after 20 Sep.** Campaign-days with at least 5 clicks
  (`data/sa360/round3/pk_nb_traffic_2026.parquet`):
  - 20 to 26 Sep: max 4.75, p99 2.80, 37% above 0.50;
  - 27 Sep to 5 Oct: max 3.73, p99 1.16, 10% above 0.50.

  Restricted to the 543 enabled campaigns on the VBB portfolio (`biddingStrategies/12222452141`, at least 3 clicks):
  - 20 to 26 Sep: max 8.52, 187 campaign-days above 0.60;
  - 27 Sep to 5 Oct: max 4.47, 109 campaign-days above 0.60.

  A bid ceiling near 0.42 cannot produce average CPCs of 1 to 4 on a campaign-day. Cost and clicks are the same
  numbers in SA360 and Google Ads, so this does not depend on which API was used. Daily CPC falls gradually from
  about 14 Sep to 26 Sep, which looks like the end of the learning period, not a step.
- **The GB zero predates 20 Sep.** UK+IE had 0 Adobe bookings in 2 to 19 Sep (`11_FRESH_REVIEW.md` s3.1). Nothing
  set on 20 Sep can explain it.
- **Most of the UK spend fell at the 20 Aug cut, not later.** The agent's own `r11_cost_per_day.csv` shows UK+IE
  at -70% in the cut fortnight and -80% in 2 to 19 Sep, before the claimed cap. The "-85% against baseline"
  headline compares the June to August baseline with late September and skips both steps in between.
- **1.04 is not UK's clearing price.**
  - In the cut fortnight (20 Aug to 1 Sep), under the old strategy, UK+IE bought 259 clicks a day at a CPC of
    0.44 and booked 11, its best rate of the summer.
  - After 20 Sep it bought 129 clicks a day at 0.42, a similar price for half the volume.
  - The 1.04 baseline reflects the summer push on the GB country campaigns, not a price floor.

  The late-September shortfall is the bidder allocating away from UK, as the fresh review found (section K), not
  a ceiling.
- **"Rank lost at zero means barely entering auctions" is wrong.** UK+IE impression share was 55% in 20 Sep to
  5 Oct (round 3).

- **The lost bookings are not the lost spend** (added 9 Oct). Split of the GB campaigns, SA360 cost and Adobe
  bookings by click day (`13_uk_switchback_campaigns.csv`, `pk_nb_traffic_2026.parquet`):

| Segment | Cost/day Jun-Aug | Cut fortnight | 2 Sep-5 Oct | CPC Jun-Aug / cut / 2-19 Sep / 20 Sep-5 Oct | Bookings Jun-Aug / cut / after | Expected after |
|---|---:|---:|---:|---|---|---:|
| 2 GB country campaigns | $419 | $53 | $16 | 1.41 / 0.53 / 1.66 (whole post) | 16 / 4 / 0 | 0.3 |
| 58 other GB campaigns | $51 | $58 | $46 | 0.42 / 0.39 / 2.22 / 0.40 | 21 / 5 / 0 | 5.5 (per click) to 9 (per $) |
| 10 Ireland campaigns | $5 | $4 | $4 | 0.27 / 0.31 / 0.65 (whole post) | 7 / 2 / 1 | 1 to 3 |

  - The spend collapse is the two GB country campaigns, cut on 20 Aug, which cost about $1,780 per booking; their
    loss explains almost none of the gap.
  - The 58 other GB campaigns kept their spend and, after 20 Sep, their CPC (0.40, against 0.42 before), and
    booked 0 against about 5.5 expected even on a per-click basis (Poisson p about 0.004).
  - So no ceiling at 0.42 could have bound them, and the problem is what VBB buys in GB, not how much it spends.
    The mechanism behind that (which queries, which users) is still not shown.
- **Round 7's spend table is search-term cost**, which covers 51% to 73% of SA360 cost by segment and period. On
  full cost, long-haul (237 against 242 a day) and regional (206 against 216) are back at baseline, not 14% to 15%
  above it.

The round 3 chain (no target, shared budget, CPC spike, budget-limited serving) is unaffected by this. "Lift the
cap on UK+IE" is moot. Moving the GB campaigns off the portfolio onto their own budget (`13`) is still the action.

## 3. Partly accepted: "calibration is not the cause" (7d)

7d argues that PK has the lowest destination spread of the four markets (p90/p10 3.1x vs CA 8.7x) and the worst
outcome, so destination calibration cannot explain PK. The agent deserves credit for testing its own claim
against controls. But the test does not answer the PK question:

- **The outcome labels are round 6's**: PK -63%, CA -26%. Those are already shown to depend on the last 16 days
  (`g1`; `14_ROUND8_PAIRING_REVIEW.md` s3). On Adobe orders per dollar, PK is +2% and CA +38%.
- **PK's problem is GB-specific.** The right test is UK against the rest of PK, not PK's spread against other
  markets' spread. On that question 7b points the same way as the earlier analysis:
  - LHR is the second most over-valued PK destination (1.29x median), on 4 destinations and 53 sales;
  - the group-level ratio from `QR_Booking` rates UK at 5.0 against long-haul 3.8 and regional 2.9 (`11` s4.3).
- **"Nothing changes if the portfolio reads ML" does not follow.** 0.56 is an account-level mean. At group level
  in PK, ML relative to base is 0.44 for UK, 0.63 for long-haul and 0.69 for regional (`11` s4.3, from the
  `pk_nb_daily` values). So ML is not a uniform rescale: it cuts UK the most. The VBB search rows by destination
  can confirm this directly (request below).

**Net:** the over-rating of UK is real but modest, and it is not proven as the cause. It stays an unproven
mechanism, as `12_RESPONSE` already says.

## 4. India: what the handover data add

- **The holdout design is not matched** (`i7_holdout_match_quality.csv`):
  - North America holdout CPC is 61% below the treated arm, with booking rate 26% lower;
  - UK+IE has 1 holdout campaign against 45 treated;
  - GCC has 1 against 38;
  - 12 budgets are shared between arms.

  With round 8 (50/50 split, matched pairs), the holdout needs redesigning before launch.
- **Guardrails** (`i7_guardrails.csv`): only Europe (49), North America (58) and UK+IE (24) have 10 or more ledger
  bookings in 8 weeks. GCC (5 on 169k clicks), Africa, Oceania and other cannot be read.
- **Target ROAS** (`i8_target_roas.csv`):
  - 38.2x on base VBB search value is the realised return;
  - on ledger revenue the account returns 0.83, and GCC 0.28;
  - if the portfolio reads ML, the target must be recomputed on ML values (about 0.66 of base, so roughly 25x).
- **Destination calibration on searched routes (7b):**
  - BER 4.9x, SFO 3.9x, LHR and MAN 2.9x the median ratio;
  - PHL 0.08x;
  - 3 to 11 sales each, so the direction is reliable and the size is indicative.

## 5. What changes

1. **PK switchback (`13`):** unchanged, plus one condition. Exclude the GB budget from the budget automation, or
   confirm with its owner that it will not be rewritten. Otherwise the test is not controlled.
2. **Checklist:** add "identify any script or tool that changes budgets, bids or negatives, and freeze it for the
   test campaigns".
3. **README:** the 20 Sep cap is not part of the explanation; the budget automation is a new open question.

## 6. Requests

1. The owner and logic of the Google Ads script and internal tool that rewrite PK budgets daily.
2. From the MCC, through the Google Ads API: `bidding_strategy.maximize_conversion_value.cpc_bid_ceiling_micros`
   and `target_roas` for the PK portfolio (`12222452141`), plus its `change_status` rows around 20 Sep. If a ceiling
   is set, its value settles the cap question; section 2 is revised if it is near 0.42.
3. ML vs base search value by destination group in PK from the VBB search rows (round 7b script, grouped like
   `11` s4.3).
4. GB bookings by channel in Adobe, still outstanding from `12_RESPONSE`.
