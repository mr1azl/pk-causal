# Round 7: PK re-analysed through the Google Ads API

Account `Google-GCCLI-PK-EN` (4851538229), read through
`googleads.googleapis.com/v25` instead of SA360. Data to 5 October 2026.
Written 8 October 2026.

The SA360 Reporting API has no `search_term_view`, no `change_event`, no
`change_status` and no `shared_set`. Rounds 3 to 6 therefore inferred every date
from daily series, could not see negative keyword lists at all, and never knew
what the campaigns were matching. All four are readable here.

---

## The headline: the UK zero has a mechanical explanation

Rounds 3 and 4 eliminated geography, device, structure, settings, keywords,
audiences, bid modifiers, ads, landing pages, demographics and brand migration.
What was left was the one thing SA360 could not show. Here it is.

**UK auctions cost four to six times more than the rest of the PK account.**

| segment | 13 Jun-19 Aug | 20 Aug-1 Sep | 2-19 Sep | 20 Sep-5 Oct |
|---|---|---|---|---|
| **UK+IE CPC** | **1.040** | 0.434 | 2.225 | **0.417** |
| long-haul CPC | 0.238 | 0.211 | 1.511 | 0.456 |
| regional CPC | 0.173 | 0.177 | 1.313 | 0.336 |

The 20 September CPC cap flattened all three onto roughly the same price, about
0.42. For long-haul and regional, whose clearing price was 0.17 to 0.24, a cap
near 0.42 is not binding and they recovered. **For UK+IE, whose clearing price
was 1.04, a cap at 0.42 is a 60 percent cut below what it took to win.**

Spend per day, which is the test that matters because the four periods are 68,
13, 18 and 16 days long:

| segment | baseline | after the cap | against baseline |
|---|---|---|---|
| **UK+IE** | **250** | **37** | **-85%** |
| long-haul | 125 | 144 | **+15%** |
| regional | 132 | 150 | **+14%** |

**UK+IE is the only segment that did not recover.** The other two are above
baseline. And it is not short of queries any more: its distinct search terms per
day went 136 at baseline, down to 63 during the switch, back to 153 after the
cap. The query footprint recovered. The spend did not.

A campaign that matches as many queries as it used to and spends 15 percent of
what it used to is not being starved of inventory. It is being outbid, at a
price it is no longer permitted to pay.

**The cap that rescued the cheap two thirds of the account priced the expensive
third out of its own auctions.** That is one account-wide number set for a 0.22
market and applied to a 1.04 market.

### Why this was invisible for four rounds
Round 3 measured impression share and found UK rank-lost at 0.0 percent after
the cap, and read that as healthy. Rank-lost near zero with spend at 15 percent
of baseline is not health, it is a campaign that is barely entering auctions at
all. The search term data makes the difference visible because it counts the
queries matched, not the share of the ones entered.

---

## What the real change log shows

SA360 has no change log. Google Ads has two, with different windows, both
discovered by probing:

| resource | window | gives |
|---|---|---|
| `change_status` | **90 days**, back to about 10 Jul | what changed and when, including budgets, criteria and shared sets |
| `change_event` | **30 days only**, back to 9 Sep | who changed what, with old and new values |

So `change_event` cannot reach the 20 August budget cut or the 2 September
switch. `change_status` covers both.

### The switch, dated from the log rather than inferred

| date | changes | what moved |
|---|---|---|
| 19 Aug | 195 | CAMPAIGN_BUDGET 58, CAMPAIGN_CRITERION 54 |
| **20 Aug** | **5,043** | AD_GROUP_CRITERION 3,737, CAMPAIGN_BUDGET 545, CAMPAIGN 544, CAMPAIGN_SHARED_SET 120 |
| **2 Sep** | **774** | CAMPAIGN_BUDGET 539, CAMPAIGN_SHARED_SET 112, CAMPAIGN 46 |
| **3 Sep** | **5,397** | AD_GROUP_CRITERION 3,300, CAMPAIGN_SHARED_SET 974, CAMPAIGN_BUDGET 551, CAMPAIGN 544 |
| 17 Sep | 1,121 | CAMPAIGN_BUDGET 544, CAMPAIGN 544 |
| 25 Sep | 762 (event) | AD_GROUP 682, AD_GROUP_CRITERION 79, one user |

**This corrects a round 4 finding.** Round 4 reported "not one keyword was
modified in any market", read from `last_modified_time`. That field keeps only
the most recent edit per object, so any edit later overwritten is invisible to
it. `change_status` shows **3,300 ad group criteria changed on 3 September** and
3,737 on 20 August, all with status CHANGED rather than ADDED or REMOVED.

The correction is narrower than it looks. The criteria were changed, not added
or removed, and the changes fall across the account in proportion to size
(long-haul 1,603, regional 1,482, UK+IE 156 on 3 September), so this is not a
UK specific intervention. Round 4's conclusion, that no structural edit explains
the UK zero, survives. Its stated evidence does not.

### An automated script is managing this account daily
`change_event` shows **CAMPAIGN_BUDGET/UPDATE on 24 of the 29 days** in the 30
day window, one to four per day, via `GOOGLE_ADS_SCRIPTS` and `INTERNAL_TOOL`,
across four distinct users. Rounds 3 to 6 described a "fixed shared budget". It
is not fixed. It is being rewritten almost every day by automation.

That does not change the round 3 mechanism, since a budget adjusted daily can
still be exhausted daily, but it does mean any analysis that treats the budget
as a constant is describing something that does not exist. **What that script
optimises for is the most important open question left in PK.**

### The 20 September CPC cap is not in this account's log
Only two CAMPAIGN_BUDGET/UPDATE events appear on 20 September and three on
21 September. No bid strategy change. The cap was set on the MCC-owned
portfolio, so the change is logged in the manager account, not here.

---

## Shared negative lists: visible for the first time

PK has **42 shared sets, 67,543 criteria, and 6,283 attachments across all 544
enabled campaigns**, about 11.5 lists per campaign. Every segment is fully
covered. SA360 cannot see any of it.

Largest live lists: `MSS | QR Flight Codes | Numbers | Status` (6,562),
`Negative List FY1516` (6,203), `Generic RMKT keywords` (5,138),
`QR_Display_Keyword_Exclusion_List_26082024_A` (4,998),
`Negatives -June 15 (1/2)` (4,890). 566 of the 67,543 criteria are reverse
direction.

**The lists churn.** On 3 September, 487 campaigns each had one shared set
removed and one added, proportionally across all segments. All of the sets
involved that day **no longer exist**: created, attached, detached and deleted
inside the 90 day window. Combined with the daily budget rewrites, this is an
account under continuous automated management, not a stable configuration.

---

## This corrects the India findings too

`FINDINGS_india.md` says "1,021 of 1,021 campaigns have no reverse direction
negative", and flagged it as the one claim not to act on without a UI check,
because SA360 cannot read shared lists. The flag was right and the claim was
wrong as stated.

**India has 40 shared sets, 12 of them attached to enabled campaigns (11 with
any content, one is empty), 10,836 attachments covering all 1,022 campaigns,
28,469 criteria. 908 of the 1,022 are
covered by a list containing at least one "to India" negative.**

But the substance holds, and now it is measured rather than asserted. Those
reverse direction negatives number **48 distinct terms**, and they are nearly
all brand qualified: "qatar airways flights to india", "doha to delhi qatar
airways". They do nothing against a generic query.

Tested directly against the 1,000 reverse direction search terms that actually
spent money:

| | |
|---|---|
| reverse direction spend measured | 4,301 USD over 4 weeks |
| blocked by an attached negative | **584 USD, 13.6%** |
| **not blocked** | **3,717 USD, 86.4%** |

Nothing blocks "dubai to mumbai flight" (90 USD), "dubai to delhi flight" (75),
"toronto to delhi flight" (44), "london to delhi flight" (39). The lists exist,
they are attached, and they are the wrong lists.

**The corrected statement for India:** every campaign carries shared negative
lists, but those lists stop 13.6 percent of the reverse direction spend. The
recommendation does not change; its justification does.

---

## What the Google Ads API adds over SA360, for the record

| resource | SA360 | Google Ads |
|---|---|---|
| `search_term_view` | does not exist | 4 fields, works |
| `change_event` | does not exist | 13 fields, 30 day window |
| `change_status` | does not exist | 21 fields, 90 day window |
| `shared_set` | 0 fields | 8 fields |
| `shared_criterion` | 0 fields | 33 fields |
| `campaign_shared_set` | 0 fields | 4 fields |
| `campaign` | 67 fields | **141 fields** |
| `ad_group_ad` | fewer | **218 fields** |
| `campaign_budget` | 4 fields, no name | 18 fields |
| `click_view`, `geographic_view`, `landing_page_view` | partial | all present |

Version trap worth repeating: **v21 and below are sunset and return an HTML 404
for every path**, which looks exactly like a credential failure. v22 to v25 are
live. On 7 October I reported the developer token as the blocker; it was the
version, and I was wrong.

---

## What this changes, and what it does not

**Changes.** The UK zero now has a mechanism: a single account-wide CPC cap set
for a 0.22 market, applied to a 1.04 market. It is testable and reversible: lift
the cap on UK+IE campaigns alone and watch whether spend per day returns toward
250 while booking rate holds.

**Does not change.** The round 3 chain stands: no target ROAS on a shared budget
drove CPC up 6.6 times and pinned budget-lost impression share above 90 percent.
The four market comparison stands. The cross-device finding stands, and nothing
here touches it.

**New and unresolved.** An automated script rewrites budgets daily and recreates
shared negative lists every few days. Nobody in this analysis knows what it
optimises for. Until that is known, no recommendation about budgets or negatives
in this account can be guaranteed to survive the next automated run.

---

## Limits

- `change_event` reaches back only 30 days, so the 20 August cut and the
  2 September switch have dates and resource counts but no old and new values.
- `change_status` says what changed, never to what.
- The sets swapped on 3 September are deleted, so their contents cannot be read.
- Search terms exclude queries below Google's disclosure threshold, so the
  footprint counts are a floor.
- The reverse direction labels on a PK origin account are a weak guide: a
  diaspora market legitimately buys both directions, and "london to islamabad"
  from a searcher in Pakistan is an ordinary inbound leg, not waste.
- User emails on `change_event` are personal data. They were hashed in the
  script before anything was written; four distinct users appear, as hashes.
