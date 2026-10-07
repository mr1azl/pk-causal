# PK: what is actually wrong, whether to switch back, and what it means for India

*7 Oct 2026. Pulls together everything to date: Adobe click-level data 2025-2026, the Floodlight ledger,
SA360 rounds 3 to 6 (PK, SA, CA, MY), the search terms report, and Google Flights (GFS).
New scripts: `scripts/pk_search_terms.py`, `scripts/pk_booking_tags_by_group.py`.*

## 1. The answer in short

1. **PK is not broadly broken by VBB.** Outside the UK, PK non-brand bookings held through the switch
   on the same budget, and per click they improved. What makes PK look broken is (a) the 20 Aug budget cut,
   (b) the cost-per-click spike from bidding with no ROAS target, and (c) the UK.
2. **The UK problem is real but smaller than "zero".** On Google's own Booking tag, UK bookings per click
   fell 49% while long-haul rose 34% and regional held. The Floodlight and Adobe "zero" rests on about 5
   expected bookings.
3. **The cause is the value signal plus where it sends the bidder, on top of a weaker UK market.**
   - The UK search value is the most inflated relative to the bookings it produces.
   - So the bidder keeps buying UK clicks, including reverse-direction and generic searches that rarely book.
   - QR's Google Flights position on PK-UK weakened from mid-August, before the switch.
   - No single exotic cause is needed, and none of the remaining evidence points to a tracking break.
4. **Do not switch PK back wholesale.** Fix the UK and add a ROAS target. Switching everything back would give
   up the non-UK gains to fix a problem worth about $60 a day of spend.
5. **India can go, with guardrails** (section 6). The PK lessons are about configuration and measurement,
   and they are fixable before launch.

## 2. Outside the UK, VBB worked in PK

Adobe, PK Google non-brand, bookings by click date, per week:

| | Jul 5 to Aug 29 (8 weeks) | Sep 6 to Oct 3 (4 weeks) |
|---|---:|---:|
| Non-UK bookings a week | 7.0 | 7.3 |
| UK bookings a week | 4.3 | 0.3 |

- Non-UK bookings held while non-UK clicks fell by half or more. Against the budget-cut fortnight
  (20 Aug to 1 Sep), non-UK bookings a day rose from 0.69 to 1.0-1.1 on the same budget.
- On Google's Booking tag (independent of Floodlight): long-haul 3.15 to 4.22 bookings per 1,000 clicks,
  regional 1.26 to 1.30.
- The UK accounts for essentially the entire shortfall in PK non-brand bookings since the switch.

## 3. The UK: size of the problem

| UK+IE, per 1,000 clicks | 1 Jul to 1 Sep | 2 Sep to 5 Oct |
|---|---:|---:|
| QR_Booking (Floodlight, attributed) | 4.14 | 0.00 |
| Booking (Google Ads tag) | 4.33 | **2.20 (-49%)** |
| Adobe bookings (click date, own clicks) | about 5.6 | about 1.1 |

- After the switch Adobe saw about 900 UK clicks. At the July-August rate that predicts about 5 bookings;
  there was 1. That is significant (p about 0.04) but it is 4 to 5 bookings, not a collapse of a big
  stream. The Google tag, with more volume, puts the drop at about half.
- In money: UK spend after the switch is about $55 to $75 a day (12% to 15% of the $490 budget) for close to
  no booking revenue.

## 4. Why the UK

### 4.1 The value signal overrates UK the most

Search value per click against booking value per click, 1 Jul to 1 Sep (both from SA360):

| Group | Search value per click | Booking value per click | Ratio |
|---|---:|---:|---:|
| UK+IE | $27.0 | $4.76 | **5.7** |
| Long-haul | $19.5 | $4.19 | 4.6 |
| Regional | $11.1 | $3.76 | 3.0 |

The bidder is told a UK click is worth almost twice what a regional click is worth relative to the bookings
each produces. After the switch, UK search value per click is still the highest ($30) while UK booking value
is near zero. The bidder has no way to see that, because bookings are not in its objective (it was
rewarded on flight searches before the switch too, by count; now by value).

### 4.2 What the bidder buys on UK campaigns now (search terms)

UK+IE campaigns not cut on 20 Aug, share of clicks by query:

| Month | PK to UK (outbound) | UK only | UK to PK (reverse) | Generic, no place | UK to elsewhere |
|---|---:|---:|---:|---:|---:|
| Jun 2026 | 76.5% | 9.2% | 8.7% | 0.3% | 5.1% |
| Aug 2026 | 84.9% | 8.8% | 3.1% | 1.8% | 1.3% |
| **Sep 2026** | 65.8% | 12.3% | **9.6%** | **9.9%** | 2.1% |
| **Oct 2026** (1-7) | 60.8% | 10.8% | **8.9%** | **18.6%** | 0.9% |

- **Off-target UK clicks went from about 6% in August to 22% in September and 28% in October.**
- The generic queries are almost all one campaign, `Dest|City|XXX|MAN` on broad match: "cheap flights",
  "ticket booking", "flights", plus Pakistani OTA and agent names (faremakers, sasta tickets) and a
  competitor (flyjinnah).
- Reverse-direction queries ("manchester to islamabad", "london to lahore") tripled. A reverse search
  made on the PK site is valued at the full UK route value, so to the bidder it is as good as an
  outbound one.
- Generic buying is not new in itself (Indonesia, Barcelona and Perth campaigns bought more of it before
  the switch and still booked). What is new is UK campaigns buying it, with UK search values attached.

### 4.3 The market weakened for QR on PK-UK, from mid-August (GFS)

QR's Google Flights rank on PK-UK went from 2.8 to 4.5, and selection when shown from 0.40 to 0.21, in the
weeks of 16 and 23 Aug, against a smaller seasonal move in 2025 (0.36 to 0.27). Demand did not collapse and
price position held until 20 Sep. This is outside paid search and would lower UK conversion on any bid
strategy, by perhaps 20% to 25% beyond the seasonal norm.

### 4.4 Adding it up

Off-target clicks (about -20%) and the market (about -20% to -25%) together predict a fall of roughly 40%,
close to the -49% on the Google tag. The Floodlight and Adobe "zero" is that same fall on a handful of
expected bookings. No hidden mechanism is needed to explain it.

## 5. Where I disagree with the agent's conclusions (rounds 4 to 6)

1. **"Downstream of the click: the UK booking path or its measurement."** Measurement is ruled out
   (Adobe and Floodlight agree row by row, and the Google tag sees the same direction). The booking path
   is not needed to explain a ~50% fall that query drift and market position already account for. A test
   booking walk is cheap and worth doing, but it is not the lead.
2. **"Brand migration ruled out."** The check (`d6`) shows `QR_Booking` at 0 in the brand account in every
   period, including before the switch, so it could not detect migration. Brand bookings in Adobe rose in
   September 2026 (Aug to Sep +6%, booking rate +32%) against a fall in September 2025 (-24%). Some UK
   and other non-brand demand may now book through brand clicks. Not proven either way.
3. **"PK conversion -63%, CA -26%, MY -29%."** These use the last 16 days of attributed conversions, which
   are incomplete because Google's modelled cross-device conversions arrive late. The agent's own
   reconciliation (`g1`) shows CA at +17% and MY at +10% over the full post window. The "strategy costs
   conversion in most markets" correction should be withdrawn.
4. **"The strategy is exonerated" (round 5).** Too strong. The bidding pathology (cost per click up 2 to 7
   times, budget-limited) is universal and caused by the missing ROAS target. And the UK problem comes
   from the strategy's objective (search value) meeting a miscalibrated value for one destination.
   SA used ML values; PK uses rule-based values.
5. **"Do not move any UK campaign."** I would act on the UK first. It is where the spend is wasted.

## 6. What to do

### PK, now
1. **Do not revert the whole portfolio.** Non-UK is doing at least as well as before per click.
2. **Set a target ROAS on the portfolio** (start from the last 8 weeks' actual value per $ so it does not
   choke volume), or at minimum a max CPC limit. This removes the 2 to 7 times CPC spikes seen in every market.
3. **Fix the UK, one of two ways:**
   - **Preferred: recalibrate the UK search values.** Scale PK-to-UK route values so search value / booking
     value matches the other groups (about 40% to 50% lower). Then the bidder stops overpaying for UK searches.
   - **Faster: take the 66 UK+IE campaigns out of the portfolio** onto their own budget (about $60 a day) with
     a target CPA on bookings or Maximise Conversions on QR_Booking, so they are judged on bookings.
4. **Clean the UK queries:** negatives for reverse direction on UK campaigns ("to lahore", "to islamabad",
   "to karachi", "to pakistan", "london to", "manchester to", "birmingham to") and generic negatives on
   `Dest|City|XXX|MAN`, or move it from broad to phrase.
5. **Measure on the Floodlight ledger and Adobe, with the Google tag as the fast read.** Not "Bookings (FL)":
   it adds two systems and Google's cross-device modelling (83% of regional conversions in PK).
6. Ask the commercial team about PK-UK fares and capacity since mid-August (GFS weakening).

### India and similar markets
India shares PK's risk factors: VFR traffic to the UK, US, Canada and the Gulf (reverse-direction queries),
a large agent and OTA market (heavy searchers who book elsewhere), and long-haul routes with high search
values. Launch with:
1. **A target ROAS from day one**, not unconstrained Maximise Conversion Value.
2. **Value calibration by destination before launch:** search value per click / booking revenue per click
   should be similar across destination groups. Where one is out of line (PK UK was 5.7 against 3.0), scale it.
3. **Reverse-direction and agent/OTA negative lists** on every destination campaign.
4. **No budget changes in the two weeks either side of the switch** (PK's 20 Aug cut confounded everything).
5. **A holdout:** keep a matched set of campaigns (or a region) on the old strategy for 4 weeks, so the
   effect is measured, not inferred.
6. **A weekly guardrail by destination group** on the ledger or Adobe bookings per click, with a rule such
   as: a group below 50% of its 8-week rate for 2 weeks moves to target CPA.

## 7. Brand: search terms and bookings (redone in depth)

*First pass looked only at the under-1% of brand queries that name a destination; this replaces it.
Scripts: `scripts/pk_brand_search_terms.py`, `scripts/pk_brand_vs_nonbrand.py`.*

### 7.1 Brand search terms

| | Jul 2026 | Aug 2026 | Sep 2026 |
|---|---:|---:|---:|
| Brand clicks (search terms report) | 83,823 | 100,383 | 78,734 |
| Brand cost | $2,846 | $4,092 | $4,333 |
| CPC, `Brand\|Hero` (exact, 90% of clicks) | 0.029 | 0.030 | **0.038** |
| CPC, `Brand\|Qatar` | 0.142 | 0.177 | **0.255** |
| CPC, `Brand\|Airways` (phrase) | 0.009 | 0.115 | **0.147** |
| Clicks on queries naming the UK | 1 | 78 | 126 |

- **No UK demand visible in brand searches.** Queries naming the UK rose by 48 clicks in September, and those
  naming other long-haul destinations rose more (+122). Over 99% of brand clicks name no destination.
- **No overlap between the accounts.** The non-brand account buys almost no queries containing "qatar" or "qr"
  (at most a dozen clicks a month, before and after the switch). Brand campaigns buy almost no queries without
  a brand word (under 200 clicks a month). The VBB campaigns are not competing with brand.
- **The brand query mix is stable:** about 94% pure brand, 3% booking, 2% route or ticket, 1% price, each month.
- **Brand cost per click rose 27% to 44% in September on every query type,** pure "qatar airways" included
  (0.038 to 0.052), while brand clicks fell. Not explained by anything in these files. Candidates: competitors
  or OTAs bidding on Qatar brand terms, or a change to the brand campaigns' own bidding. Needs the brand
  account's bid strategy, impression share metrics and the auction insights report (UI).
  **India control (no switch):** India `Brand|Qatar` CPC rose 0.15 (Jul) to 0.28 (Aug) to 0.39 (Sep) and
  `Brand|Airways` ramped from August as in PK, so the brand CPC rise is market or programme wide, not caused
  by PK's VBB switch. Only PK `Brand|Hero` (+27% in Sep, flat in India) remains unexplained.
  See `notes/INDIA_SEARCH_TERMS.md`.

### 7.2 Brand and non-brand bookings together (Adobe, click date)

| | 2025 Aug | 2025 Sep | Change | 2026 Aug | 2026 Sep | Change |
|---|---:|---:|---:|---:|---:|---:|
| Brand bookings | 866 | 658 | -24% | 905 | 956 | **+6%** |
| Brand revenue | 852k | 557k | -35% | 965k | 841k | **-13%** |
| Brand bookings per 1k clicks | 18.6 | 19.2 | +3% | 24.3 | 30.9 | **+27%** |
| Non-brand bookings | 37 | 27 | -27% | 56 | 35 | -38% |
| Non-brand revenue | 32k | 18k | -45% | 51k | 28k | -46% |
| **Total bookings** | 903 | 685 | **-24%** | 961 | 991 | **+3%** |
| **Total revenue** | 884k | 575k | **-35%** | 1,016k | 869k | **-14%** |

- **Against its own seasonal pattern, PK paid search as a whole did better in September 2026 than in
  September 2025.** Non-brand fell about as much as it does every September (revenue -46% against -45%;
  bookings -38% against -27%). Brand beat its seasonal pattern by about 30 points.
- **Brand converted unusually well in September 2026** (+27% bookings per click against +3% a year earlier).
  Part of that may be non-brand demand finishing on a brand click: when the switch cut non-brand impression
  share (UK 68% to 27%), some searchers who would have clicked a non-brand ad may have searched "qatar
  airways" and booked through brand instead. The data cannot separate that from other brand effects, and the
  brand surplus (about 270 bookings above the 2025 pattern) is far larger than anything non-brand lost.
- The 2025 comparison has its own noise: 2025 non-brand spend also fell sharply in September.

### 7.3 What this changes

1. **"PK is not working" does not hold at the level that matters.** Total PK paid search bookings held in
   September 2026 while they normally fall by a quarter. The non-brand UK problem is real, but it is about 20
   bookings a month against about 990 in total.
2. **The Causal Impact readout used brand as the control for non-brand.** If the switch moves demand into
   brand, or brand changes for its own reasons at the same time (cost per click +27% to 44%, conversion +27%),
   the control is contaminated and the non-brand effect is understated. The PK result in the readout should
   not be used for the decision.
3. **Do not switch PK back on the evidence available.** Fix the UK and add a ROAS target (section 6).
4. **For India, measure brand and non-brand together** in the holdout, not non-brand against brand.

### 7.4 Brand checks still to run (SA360 agent or UI)

- Brand account bid strategy, portfolio, target and `last_modified_time` for every brand campaign.
- Brand impression share, top and absolute-top share, rank-lost and budget-lost by week, 1 Jul to 5 Oct.
- Auction insights for the brand campaigns (UI): which domains appear on Qatar brand terms, and whether that
  changed in September.
