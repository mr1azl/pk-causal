# Round 7 run log: PK through the Google Ads API

Same rules as rounds 3 to 6. Scripts saved before they run, raw output in
`data/raw/`, clean tables in `data/clean/`. No credentials, no order IDs, no client IDs, no
gclids. Credentials are read through `lib_sa360._env` and never printed, logged or written.
User emails on `change_event` are personal data and are hashed inside the script before any write.

## Setup
`lib_gads.py`: token caching, cursor paging, three-deep error unwrapping, the same `PERIODS` and
`segment()` helpers as rounds 3 to 6 so tables line up.

**Version trap, logged because it cost a day.** `v21` and below are sunset and return Google's HTML
404 page for every path including the root, which is indistinguishable from a credential failure.
Probing v15 to v30 shows **v22 to v25 live, v26 and above not yet existing**. On 7 October I
reported the developer token as the blocker. It was the version. Using v25.

Other mechanics: `pageSize` is rejected ("fixed page size of 10000 rows"), so paging is by
`nextPageToken` and `LIMIT` goes in the query. `change_status` additionally requires an explicit
`LIMIT` of at most 10,000.

## r01_capability_gap.py
23 resources probed. Present in Google Ads and absent from SA360: `change_event` (13 fields),
`change_status` (21), `search_term_view` (4), `shared_set` (8), `shared_criterion` (33),
`campaign_shared_set` (4). `campaign` has 141 fields against SA360's 67, `ad_group_ad` 218,
`campaign_budget` 18 against 4. Only `search_term_insight` does not exist.

Windows found by probing, not from documentation:
- `change_event` refuses any start older than **30 days**: earliest 2026-09-09.
- `change_status` refuses any start older than **90 days**: earliest about 2026-07-10.

So the 20 August cut and the 2 September switch are reachable only through `change_status`, which
says what changed but never to what.

## r02_changes.py
`change_status` 2026-07-11 to 2026-10-07 in 7 day chunks: **77,121 rows**.
`change_event` 2026-09-09 to 2026-10-07: **862 rows**, emails hashed at write time.

Key days: 20 Aug 5,043 changes; 2 Sep 774; 3 Sep 5,397; 17 Sep 1,121; 24 Sep 1,125; 1 Oct 1,126;
6 Oct 1,185.

`change_event` shows **CAMPAIGN_BUDGET/UPDATE on 24 of 29 days**, 1 to 4 per day, client types
`INTERNAL_TOOL` 806 and `GOOGLE_ADS_SCRIPTS` 56, four distinct users. On 25 September one user made
682 AD_GROUP/UPDATE and 79 AD_GROUP_CRITERION/UPDATE in a single day.

No bid strategy change appears on 20 September, so the CPC cap was set on the MCC-owned portfolio
and is logged in the manager account, not here.

## r03_switch_forensics.py
**Corrects round 4.** Round 4 said "not one keyword was modified", read from `last_modified_time`,
which keeps only the most recent edit per object. `change_status` shows **3,300 AD_GROUP_CRITERION
changes on 3 September** and 3,737 on 20 August, all with status CHANGED.

Distribution on 3 September: long-haul 1,603, regional 1,482, UK+IE 156. Proportional to segment
size, so not a UK specific intervention. Round 4's conclusion survives, its evidence does not.

## r04, r05, r06: shared negative lists, invisible to SA360
On 3 September, **487 campaigns each had one shared set REMOVED and one ADDED**, and 56 of each on
2 September. Every set involved on 3 September **no longer exists**, so they were created,
attached, detached and deleted inside the 90 day window.

Current state: **42 shared sets, 67,543 criteria, 6,283 attachments across all 544 enabled
campaigns**, about 11.5 lists each. 566 criteria are reverse direction. Coverage is complete in
every segment, so the "does PK have directional negatives" question is answered: yes, in shared
lists, which SA360 could not show.

## r07, r08: this corrects FINDINGS_india.md
India has **40 shared sets, 12 attached (11 non-empty), 10,836 attachments covering all 1,022
enabled campaigns, 28,469 criteria**. 908 campaigns are covered by a list containing a "to India"
negative. My "0 of 1,021 have a reverse direction negative" was **wrong as stated**, and the
caveat I attached to it was right.

The substance survives, now measured. The reverse direction negatives are **48 distinct terms**,
nearly all brand qualified. Tested against the 1,000 reverse direction terms that actually spent:
**584 USD blocked, 13.6 percent; 3,717 USD not blocked, 86.4 percent.** Nothing blocks
"dubai to mumbai flight", "toronto to delhi flight" or "london to delhi flight".

## r09, r10, r11: PK search terms, the UK zero
492,946 rows, 2026-06-13 to 2026-10-05, 14 day chunks. The first run exceeded the 120s shell limit
after 4 chunks; the script is resumable and the rerun completed the remaining 5.

Per day, because the periods are 68, 13, 18 and 16 days long:

| segment | baseline | 20 Aug-1 Sep | 2-19 Sep | 20 Sep-5 Oct | vs baseline |
|---|---|---|---|---|---|
| UK+IE spend/day | 250 | 76 | 51 | **37** | **-85%** |
| long-haul | 125 | 77 | 100 | 144 | +15% |
| regional | 132 | 153 | 212 | 150 | +14% |
| **UK+IE CPC** | **1.040** | 0.434 | 2.225 | **0.417** |
| long-haul CPC | 0.238 | 0.211 | 1.511 | 0.456 |
| regional CPC | 0.173 | 0.177 | 1.313 | 0.336 |
| UK+IE terms/day | 136 | 213 | 63 | 153 |

**UK auctions clear at 1.04 against 0.17 to 0.24 for the rest of the account.** The 20 September cap
flattened all three to about 0.42. Not binding on the cheap two thirds, a 60 percent cut on UK+IE.
UK+IE recovered its query footprint, 153 terms per day against 136 at baseline, and did not recover
its spend. A campaign matching as many queries as before and spending 15 percent of what it used to
is being outbid at a price it is no longer allowed to pay.

## r12_verify.py
Re-derives every headline number from the clean tables independently of the scripts that produced
them. **39 checks passed, 0 failures.** One failure was found and fixed on the first run: I wrote
"12 attached lists" while the criteria table contains 11, because one attached list has zero
members. Both numbers are true and the findings now say so.

The last check sweeps every file in `data/raw/` and `data/clean/` for `refresh_token`,
`client_secret`, `developer-token`, `Bearer ` and anything shaped like an email address.
**Zero hits.**

---

## Round 7b: the VBB order ID, and the FSV calibration question

Prompted by the format you gave me, `{search,sales}-OnD-cookieid_session`.

### What that format means
**The VBB Floodlight tag fires on bookings as well as searches.** The `sales`
rows carry the OnD and the real transaction value. `QR_Booking`'s own
`floodlight_order_id` is a single 64 character hash with no structure, so until
now booking value could not be attributed to a destination at all. This can, on
the same key, from the same tag, in the same window.

Verified first: PK QR_FlightSearch_VBB over one week, 3,987 rows typed `search`
and 13 typed `sales`, with sales mean revenue 974.36 against search mean 35.04.
The PK QR_Booking rows in the same window show the same values (2774.02, 223.28),
so VBB sales rows and QR_Booking rows are the same transactions.

### r14_pull_vbb.py
PK and India, both models, 13 Aug to 5 Oct, weekly chunks: **346,862 rows**.
Privacy: only tokens 0, 1 and 2 are read, OnD tokens are accepted only if they
match three lowercase letters, and the cookie and session tail is hashed in the
script before any write. Nothing identifying reaches disk.

### r15_fsv_alignment.py, four results

**A. ML and non-ML differ only on searches.** Sales medians are identical
(PK 826.59 against 827.97, India 574.63 against 574.63) and the total gap is
three missing rows. Search values: **ML is 0.56 of base in PK, 0.66 in India**.

**B. The proxy runs an order of magnitude high.** Search value over booking
value within the same tag: PK base 15.22x, PK ml 8.78x, India base 26.89x,
India ml 17.84x. Two corrections pull the other way, the tag's sales rows
undercount the ledger by a third to a half and booking lag truncates the window,
so the honest read is about 10x in PK and 15x in India. The ML model halves the
error and does not remove it.

**C. The relative calibration by destination is the part that changes
behaviour.** India spread is **62 to 1**: BER 89.51, SFO 71.61, LHR 52.55,
MAN 52.41, median 18.16, PHL 1.45. PK: LHE 16.35, **LHR 14.02**, median 10.89,
KHI 5.32.

**This strengthens the India UK+IE flag rather than correcting it.** On campaign
name I measured UK+IE at 1.35 to 1.44 times the median. On the destination the
user actually searched, with real booking values, **LHR and MAN are at 2.89
times**. I understated it, which is the opposite of the search term correction.
In PK, LHR is the second most over-valued destination.

**D. The proxy ranks correctly even though it is not calibrated.** Journeys that
booked carried 1.88x (PK) and 3.27x (India) the search value of journeys that did
not. The signal has rank power; the scale and the cross-destination pricing are
what is wrong.

### r16_verify_fsv.py
44 checks, recomputed from the raw rows independently of r15. **One failure on
the first run, and it was mine:** I wrote 346,502 rows into the findings when
the files hold 346,862. I had written a number I never saw printed, because the
r15 output was tailed past it. Corrected. Final run: 44 passed, 0 failures,
including a sweep for `GA1.`, `gclid`, `refresh_token`, `client_secret` and
`Bearer ` across every file written. Zero hits.

### click_view
19 fields, 90 day window, one day per query, carries a gclid so it is personal
data. It returns **no cost and no conversion metrics**, so it is a dimension
table rather than a performance table and most of it duplicates what we have.

The one genuinely unique thing in it is `location_of_presence` against
`area_of_interest` per click, at city, metro, region and country level, which
separates a user physically in the UK from a user asking about the UK. Round 4
answered the PK geography question another way, so there is nothing to chase
now. Recorded in case a geography question turns sharp again.

---

## Round 7c: order ID across markets, and the lag measured

### r17_orderid_ca_de.py
`{search,sales}-OnD-cookie` is **universal, not a PK and India convention**. OnD
parses on 91.5 to 95.1 percent of VBB rows in Canada EN, Germany EN, Germany DE,
PK and India. **`QR_Booking` is an opaque single hash in every market, 0 percent
OnD, no exception**, so the VBB sales rows stay the only route from booking value
to a destination.

ML equals base on sales in every market (CA 1,910.64 against 1,910.64 to the
cent, PK 1,251.28 identical, DE 1,106.68 against 1,093.21 on one row fewer) and
is lower on searches everywhere: 0.69 of base in CA, 0.61 DE EN, 0.58 PK and IN.
Confirmed on four markets rather than two.

Two things to raise with tagging:
- `Google-AMER-CA-FR` returns **zero rows on all three actions**. Consistent with
  round 6, which found that account carries no spend, but it should be deliberate.
- `Google-NSW-DE-DE` has **123 VBB rows and zero sales rows** in two weeks
  against 3,000 and 33 for DE-EN. If the readiness report's Germany outage refers
  to DE-DE, that account is close to dormant and the event may be far smaller
  than 1,169 modified campaigns suggests.

### r18_lag.py and r19_truncation.py
1,135 bookings across four markets, `conversion_visit_date_time` to
`conversion_date_time`.

| market | n | median | mean | p90 | within 24h |
|---|---|---|---|---|---|
| PK | 80 | 1.5 h | 63.1 h | 266.9 h | 75.0% |
| IN | 237 | 1.2 h | 63.0 h | 212.3 h | 71.7% |
| CA | 471 | 0.9 h | 43.3 h | 120.6 h | 77.3% |
| DE | 347 | 0.95 h | 55.4 h | 187.8 h | 72.6% |

Pooled cumulative: 1h 49%, 1d 74.5%, 3d 82%, 7d 90%, 14d 95%, 21d 97%, 28d 100%.

Window completeness: 7d 84.0%, **14d 88.5%**, 28d 92.9%, **54d 96.3%**, 90d 97.8%.

**Two of my own caveats withdrawn or corrected.**

The 8 week FSV window is **96.3 percent complete**. I wrote that lag "truncates
the window from the left, which inflates the ratios further", implying a material
correction. It is worth **3.7 percent** against a 15x to 27x mispricing.
Withdrawn.

Round 3's "honest range of roughly 15 to 43 percent" on the post cap booking gap
rested on a two week read being badly truncated. A 14 day window is **88.5
percent complete**, so the correction is **11.5 points, not 28**. The honest
range was closer to **33 to 43 percent** and the truth sits near the top. The
caution was right in direction and too large in size.

**Method note, important.** The direct search to booking join inside one hashed
journey returned a median of 0.01 to 0.02 days with 100 percent booking inside a
day in all four markets. **That is an artefact and must not be quoted.** The join
key is `cookieid_session` and a session is short by construction, so only same
session bookings can ever link. It measures session length, not consideration
time. It also means round 7b section 4's 1.88x and 3.27x rank separation is
conservative, since it excludes everyone who slept on it.

### r20_verify_lag.py
44 checks. **Two failures on the first run, both mine, both rounding:** I wrote
Germany's median as 1.0 h when it is 0.95, and the pooled one day figure as 75
percent when it is 74.5. Both corrected in the findings. Final run: 44 passed.

---

## Round 7d: the control test

You asked whether CA and DE are as badly calibrated, because if they are and
they did not collapse, calibration cannot be the cause. **You were right, and
this round withdraws part of round 7b.**

### r21, r22, r23. 505,765 VBB rows, four markets, same window and method.

| market | inflation base | ML | destinations | p90/p10 spread | booking rate vs baseline |
|---|---|---|---|---|---|
| PK | 15.22x | 8.78x | 4 | **3.1x** | **-63%** |
| IN | 26.89x | 17.84x | 15 | 9.1x | not launched |
| CA | 4.74x | 3.10x | 28 | **8.7x** | **-26%** |
| DE | 4.79x | 3.07x | 33 | 4.3x | not measured |

**PK has the lowest destination spread of the four and the worst outcome.**

Bootstrapped to 4 destinations each, 2,000 draws: PK 3.1, DE 3.5, CA 4.3,
IN 6.5. Germany sits right beside PK and 56 percent of its random draws are
worse than PK's figure, so PK's calibration is ordinary rather than unusually
good. Either way it is not unusually bad, which is what the test needed.

### The decomposition that reframes round 7b section 2
inflation = (mean search value / mean sale value) x (searches per sale)

| market | value ratio | searches per sale | inflation |
|---|---|---|---|
| PK | 0.0293 | 519 | 15.22 |
| IN | 0.0249 | 1,080 | 26.89 |
| CA | 0.0276 | 172 | 4.74 |
| DE | 0.0467 | 103 | 4.79 |

**The tag values a search at 2.5 to 4.7 percent of a booking in every market.**
That rule is near constant. Searches per booking varies **tenfold**. So the 5.7x
spread in apparent inflation is a market conversion rate difference the tag does
not account for, not a tagging error that differs by market.

The honest finding is **the tag is market blind**, which is sharper and more
useful than what I wrote in 7b, and not the same claim.

### Three corrections entered
1. Round 7b section 2's "order of magnitude too high" framing: reframed, and a
   pointer added at the top of that section in the file.
2. Round 7b's implication that destination miscalibration contributed to PK:
   **withdrawn**, with a note added beside the PK line in that file.
3. Round 7b's "corroborates the UK flag" claim: still true for India on India's
   own numbers, says nothing about PK.

### What survives
The round 7 mechanism is untouched: UK auctions clear at 1.04, the rest of the
account at 0.17 to 0.24, the 20 September cap flattened everything to about 0.42,
not binding on the cheap two thirds and a 60 percent cut on UK+IE, which
recovered its query footprint and not its spend. That is a structural fact about
auction prices, not a tagging fact.

Also standing, on their own terms: India's 9.1x spread with LHR and MAN at 2.89x
is a real reason to recalibrate before launch, and Canada's 8.7x is worth
attention given Canada has already launched.

### r24_verify_control.py
**52 checks, 0 failures**, including the inflation identity recomputed from the
decomposition and both the raw and bootstrapped spread orderings.
