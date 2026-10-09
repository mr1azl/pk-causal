# Round 7c: the order ID across markets, and the lag finally measured

Written 8 October 2026.

---

## 1. The order ID format is universal

Sampled 22 Sep to 5 Oct on every market's Google non-brand account.

| market | account | VBB rows | types | OnD parses | search mean | sales mean |
|---|---|---|---|---|---|---|
| Canada EN | 4096344384 | 3,000 | search 2,986, sales 14 | **91.6%** | 46.51 | 1,910.64 |
| Germany EN | 3218295582 | 3,000 | search 2,967, sales 33 | **94.2%** | 52.76 | 1,106.68 |
| Germany DE | 4116587214 | 123 | search 123, **sales 0** | 95.1% | 47.14 | none |
| Canada FR | 9362154318 | **0** | none | | | |
| PK | 4851538229 | 3,000 | search 2,992, sales 8 | 91.9% | 33.71 | 1,251.28 |
| India | 4034062923 | 3,000 | search 2,999, sales 1 | 93.9% | 29.01 | 800.48 |

**`{search,sales}-OnD-cookie` is the standard, not a PK and India convention.**
It parses on 91.5 to 95.1 percent of rows in every market. So the destination
level calibration done in round 7b can be run anywhere without new work.

**`QR_Booking` is an opaque hash in every single market**, 0 percent OnD, with no
exception. The VBB sales rows remain the only route from booking value to a
destination.

**ML and base agree on sales everywhere.** Canada 1,910.64 against 1,910.64 to
the cent, PK 1,251.28 against 1,251.28, Germany 1,106.68 against 1,093.21 on one
row fewer. On searches ML is consistently lower: 0.69 of base in Canada, 0.61 in
Germany EN, 0.58 in PK and India. The two variants are the same tag on bookings
and two models on searches, confirmed on four markets rather than two.

**Two things worth raising with whoever owns the tagging.**

`Google-AMER-CA-FR` returns **zero rows on all three actions**. Round 6 found the
FR Canada account carries zero spend, so this is consistent rather than alarming,
but a market with a live account and no tag at all should be a deliberate choice.

`Google-NSW-DE-DE`, the German language account, has **123 VBB rows and not one
sales row** in two weeks, against 3,000 and 33 for the English account. If the
readiness report's "Germany outage on 30 September" refers to the DE-DE account,
that account is close to dormant and the outage may be a much smaller event than
its 1,169 modified campaigns suggest. Worth confirming which account was meant.

---

## 2. The lag, measured instead of asserted

I have twice cited booking lag as a reason a ratio was understated without ever
measuring it. Here it is, from `conversion_visit_date_time` to
`conversion_date_time` on 1,135 bookings across four markets.

### Click to booking

| market | n | median | mean | p90 | p99 | within 24h |
|---|---|---|---|---|---|---|
| PK | 80 | **1.5 h** | 63.1 h | 266.9 h | 581.7 h | 75.0% |
| India | 237 | **1.2 h** | 63.0 h | 212.3 h | 614.0 h | 71.7% |
| Canada | 471 | **0.9 h** | 43.3 h | 120.6 h | 660.8 h | 77.3% |
| Germany | 347 | **0.95 h** | 55.4 h | 187.8 h | 626.7 h | 72.6% |

**Half of all bookings land within an hour of the click. Three quarters within a
day.** The mean is 2 to 3 days only because a thin tail runs to 25 to 28 days.

Cumulative share of bookings observed, all four markets pooled:

| 1 h | 1 d | 2 d | 3 d | 5 d | 7 d | 10 d | 14 d | 21 d | 28 d |
|---|---|---|---|---|---|---|---|---|---|
| 49% | 74% | 80% | 82% | 87% | 90% | 93% | 95% | 97% | **100%** |

The curve is effectively closed at 28 days in every market.

### What that does to my own numbers

Converting the curve into window completeness, averaged across the window:

| window | complete | understates bookings by |
|---|---|---|
| 7 days | 84.0% | 16.0% |
| 14 days | 88.5% | **11.5%** |
| 28 days | 92.9% | 7.1% |
| **54 days** | **96.3%** | **3.7%** |
| 90 days | 97.8% | 2.2% |

**This corrects two things I wrote.**

The 8 week window behind the FSV work is **96.3 percent complete**. I said lag
"truncates the window from the left, which inflates the ratios further",
implying a material correction. It is worth **3.7 percent**, which is noise next
to a 15x to 27x mispricing. That caveat was overstated and I am withdrawing it.

Round 3 said the post cap booking gap had an "honest range of roughly 15 to 43
percent" because a two week read was left truncated. A 14 day window is **88.5
percent complete**, so the maturation correction is **11.5 percent, not the
28 point spread I allowed for**. The honest range was closer to **33 to 43
percent**, and the true figure sits near the top of it, not the bottom. The
direction of my caution was right, the size was not.

### A method note that matters more than the numbers

I also tried to measure search to booking lag directly, by joining VBB search
rows to VBB sales rows inside one hashed journey. It returned a median of
**0.01 to 0.02 days**, about 15 to 30 minutes, with 100 percent booking inside a
day in all four markets.

**That result is an artefact and should not be quoted.** The join key is
`cookieid_session`, and a session is short by construction, so any booking in a
later session gets a different key and never links. The join can only ever see
same session bookings, which are fast by definition. It measures session length,
not consideration time.

This is also why section 4 of round 7b, the journey level rank test, is
conservative: it sees only the same session journeys, so the 1.88x and 3.27x
separation between bookers and non bookers excludes every user who thought about
it overnight. Measure A above is the one to use for lag.

---

## 3. What this changes

**Nothing in the conclusions, something in the confidence.**

The 54 day FSV window is sound. The destination mispricing in round 7b stands at
full size, with only a 3.7 percent correction available to it rather than the
material one I implied.

**For the India guardrails**, this gives the right waiting period. A group needs
**14 days to be 88.5 percent read and 28 days to be 93 percent read**. Judging a
VBB launch on a 7 day window means acting on 84 percent of the evidence, and the
missing 16 percent all points the same way: it makes a launch look worse than it
is. The two consecutive week rule in `FINDINGS_india.md` is about right, and it
should be stated as two weeks of data at least 14 days old, not simply two weeks
after launch.

---

## Limits

- 1,135 bookings pooled; PK alone has 80, so the PK curve is indicative.
- `conversion_visit_date_time` is the click, not the first search, so measure A
  is click to booking, which is shorter than true consideration time.
- The tail is bounded by the 54 day pull window. A booking more than 54 days
  after its click cannot appear, so 28 days is a floor for curve closure.
- Lag is measured on `QR_Booking`, which excludes bookings that never fire that
  tag.
