# Round 5 log: the SA market

Account **`Google-GCCLI-SA-EN-2`, 7879272266**, USD, Asia/Qatar. Same test set as PK rounds 3
and 4, same four periods, same scripts and helpers carried over from round 4.

## Which account "SA-2" is

45 accounts in the MCC carry "SA" in the name, and two end in "-2". Resolved by liveness rather
than by guessing:

| account | id | campaigns with spend | cost 13 Jun-5 Oct | QR_Booking |
|---|---|---|---|---|
| **Google-GCCLI-SA-EN-2** | **7879272266** | **811** | **35,444** | **490** |
| Google-GCCLI-SA-AR-2 | 1947951243 | 0 | 0 | 0 |
| Google-GCCLI-SA-AR | 6387598825 | 1 | 28,779 | 705 |
| Google-GCCLI-SA-EN | 4167318331 | 0 | 0 | 0 |

`SA-AR-2` has zero enabled campaigns, so SA-2 is unambiguously the EN account.

## Setup

14,443 campaigns, 14,441 non-brand (the |Brand| filter excludes 2, brand sits in its own account
as in PK). Status: 2,404 ENABLED, 487 PAUSED, 11,550 REMOVED. Pipe naming on 2,610 of 14,441, so
the same two-convention problem as PK and the same parser handles it.

Destination groups: regional 9,616, long-haul 4,260, UK+IE 404, UK+IE outside the brief list 156,
none 5.

**All 2,404 enabled campaigns sit on one MCC owned portfolio, `SA_FlightSearch_VBB_ML - Conv Value Δ`**,
type MAXIMIZE_CONVERSION_VALUE, **no target ROAS, no CPC ceiling**. Note the name carries `_ML`
where PK's is plain `PK_FlightSearch_VBB`.

**SA switched on the same dates as PK**, read from campaign `last_modified_time`: 99 campaigns on
2 Sep, 2,133 on 3 Sep, plus a further 172 on 14 Sep that PK has no equivalent of. So the PK period
boundaries apply unchanged and the two markets are directly comparable.

---

## E1 to E3. Performance by period

`e02_sa_pull.py`, `e03_sa_summary.py`. Dates returned **2026-06-13 to 2026-10-05, 113 days**,
no gaps. 67,252 traffic rows, 99,481 conversion rows.

| period | cost/day | clicks/day | CPC | searches/day | bookings/day | **bookings per 1k searches** | IS | budget lost | rank lost | VBB value per search |
|---|---|---|---|---|---|---|---|---|---|---|
| 13 Jun-19 Aug | 291 | 955 | 0.305 | 566 | 4.62 | **8.16** | 35% | 10% | 55% | 68.46 |
| 20 Aug-1 Sep | 230 | 726 | 0.317 | 403 | 4.38 | **10.89** | 33% | 14% | 53% | 67.31 |
| **2-19 Sep** | 363 | 539 | **0.673** | 301 | 4.17 | **13.83** | 37% | **61%** | **1%** | 82.33 |
| 20 Sep-5 Oct | 384 | 533 | 0.720 | 282 | 2.75 | **9.76** | 37% | 39% | 24% | 71.20 |

**The bidding mechanism is identical to PK.** Cost per click roughly doubles, impression share lost
to rank collapses from 53 to **1 percent**, and lost to budget jumps from 14 to **61**. Same
signature: not outbid, simply out of money.

**The outcome is not.** Bookings per thousand searches went **up** through the switch, 10.89 to
13.83, and sits at 9.76 now against an 8.16 baseline. Bookings per day fell from 4.62 to 2.75, a
40 percent fall, against PK's collapse of roughly 80 percent on a far worse conversion rate.

### By destination group: nothing went to zero

| group | period | cost/day | CPC | searches/day | bookings | bk/1k searches |
|---|---|---|---|---|---|---|
| **UK+IE** | 13 Jun-19 Aug | 15 | 0.416 | 20 | 4.0 | 2.91 |
| **UK+IE** | 20 Aug-1 Sep | 15 | 0.492 | 18 | 0.0 | 0.00 |
| **UK+IE** | 2-19 Sep | 29 | 1.099 | 17 | **2.0** | 6.67 |
| **UK+IE** | 20 Sep-5 Oct | 26 | 0.914 | 17 | **3.0** | 11.11 |
| long-haul | 20 Aug-1 Sep | 48 | 0.412 | 67 | 3.0 | 3.42 |
| long-haul | 2-19 Sep | 88 | 0.904 | 64 | 13.0 | 11.36 |
| long-haul | 20 Sep-5 Oct | 116 | 0.891 | 79 | 13.0 | 10.33 |
| regional | 20 Aug-1 Sep | 167 | 0.289 | 317 | 54.0 | 13.11 |
| regional | 2-19 Sep | 247 | 0.592 | 221 | 60.0 | 15.08 |
| regional | 20 Sep-5 Oct | 242 | 0.646 | 186 | 28.0 | 9.40 |

**SA's UK+IE went up, not to zero**: 1 booking in the ledger before 2 September and **5 after**.
Volumes are small, 17 to 20 searches a day, so read it as "no collapse" rather than as growth.

---

## E4. Booking ledger

`e04_sa_ledger_and_changes.py`. 67,234 conversion rows scanned, **184 booking rows**,
1 Aug to 5 Oct. Order IDs SHA-256 hashed before any write.

Structurally identical to PK: **`conversion_quantity` is 1000 on all 184 rows**, so one row is one
transaction with quantity one. 5 rows of 184 carry zero revenue (2.7 percent against PK's 2.2).
183 distinct order IDs with **1 duplicated**, the same negligible rate as PK.

### But the attribution inflation is far smaller than PK

| group | period | ledger rows | all_conversions | cross-device | all / ledger | same device / ledger |
|---|---|---|---|---|---|---|
| UK+IE | pre 2 Sep | 1 | 1.0 | 0.0 | **1.00x** | 1.00x |
| UK+IE | from 2 Sep | 5 | 5.0 | 0.0 | **1.00x** | 1.00x |
| long-haul | pre 2 Sep | 7 | 11.0 | 1.0 | 1.57x | 1.43x |
| long-haul | from 2 Sep | 23 | 26.0 | 2.0 | 1.13x | 1.04x |
| **regional** | pre 2 Sep | 88 | 189.0 | 48.0 | **2.15x** | 1.60x |
| regional | from 2 Sep | 60 | 88.0 | 28.0 | 1.47x | 1.00x |

PK regional ran at **9.77x** with cross-device at 82.7 percent of all conversions. SA regional runs
at **2.15x** with cross-device at 25 percent. Same metric, same action, same period, one quarter
the inflation. That is a market level measurement difference worth raising on its own.

---

## E5. Change audit, 15 Aug to 5 Oct

| level | objects | modified in window | when |
|---|---|---|---|
| campaign | 2,893 | 2,610 | 109 on 2 Sep, 2,329 on 3 Sep, 172 on 14 Sep |
| ad group | 106,982 | **42** | 41 on 18 Sep, 1 on 1 Sep |
| keyword | **1,593,182** | **0** | nothing since 4 Aug |

Same conclusion as PK: **the only change of substance is the bid strategy**. Not one of 1.59
million keywords was modified in the window, and 42 of 107,000 ad groups.

SA has one extra event PK does not: **172 campaigns modified on 14 September**, mid switch window.
Not investigated further in this round.
