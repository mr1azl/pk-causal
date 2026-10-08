# Round 7b: the VBB order ID, and whether the FSV proxy is calibrated

Written 8 October 2026, after you pointed out the order ID format
`{search,sales}-OnD-cookieid_session`.

That format matters more than it looks. It means **the VBB Floodlight tag fires
on bookings as well as searches**, and the sales rows carry both the OnD and the
real transaction value. `QR_Booking`'s own order ID is a single opaque hash, so
until now booking value could not be attributed to a destination at all. Now it
can, on the same key, from the same tag, in the same window.

Window 13 Aug to 5 Oct, PK and India, both models. 346,862 rows.
Privacy: only tokens 0, 1 and 2 are read; the cookie and session are hashed in
the script before any write, so journeys can be joined without storing identity.

---

## 1. The ML and non-ML models differ only on searches

| market | type | model | rows | mean | median | total |
|---|---|---|---|---|---|---|
| PK | sales | base | 53 | 1,141.84 | 826.59 | 60,517 |
| PK | sales | ml | 50 | 1,166.51 | 827.97 | 58,326 |
| PK | search | base | 27,511 | **33.47** | 20.70 | 920,850 |
| PK | search | ml | 27,471 | **18.64** | 15.57 | 512,157 |
| IN | sales | base | 135 | 1,025.96 | 574.63 | 138,504 |
| IN | sales | ml | 133 | 1,031.55 | 574.63 | 137,196 |
| IN | search | base | 145,772 | **25.55** | 13.58 | 3,724,110 |
| IN | search | ml | 145,737 | **16.80** | 12.58 | 2,447,870 |

Sales values are the same in both models; the medians are identical to the cent
(826.59 against 827.97 in PK, 574.63 against 574.63 in India) and the small
totals gap is three missing rows, not a different valuation. **ML and non-ML are
the same tag on bookings and two different models on searches**, with ML valuing
a search at **0.56 of base in PK and 0.66 in India**.

So the question "which variant does the portfolio read" is purely a question
about search valuation. On bookings it makes no difference.

---

## 2. The proxy is an order of magnitude too high

> **Reframed on 8 October by the four market control test in
> `FINDINGS_round7d_control.md`. Read that before using this section.** The
> inflation ratio decomposes into the per search value ratio times the number of
> searches needed per booking. The value ratio is near constant across markets at
> 2.5 to 4.7 percent; searches per booking varies tenfold, 103 in Germany to
> 1,080 in India. So the apparent spread in inflation is a market conversion rate
> difference the tag ignores, not a tagging error that differs by market. The
> correct statement is that the tag is market blind.

A flight search value is meant to proxy the booking value those searches will
produce. Compare the two sides of the same tag:

| market | model | searches | search value | sales | sales value | **search value over booking value** |
|---|---|---|---|---|---|---|
| PK | base | 27,511 | 920,850 | 53 | 60,517 | **15.22x** |
| PK | ml | 27,471 | 512,157 | 50 | 58,326 | **8.78x** |
| IN | base | 145,772 | 3,724,110 | 135 | 138,504 | **26.89x** |
| IN | ml | 145,737 | 2,447,870 | 133 | 137,196 | **17.84x** |

**Read this as an order of magnitude, not a precise multiple.** Two things pull
it the other way: the tag's sales rows capture roughly half to two thirds of the
bookings in the transaction ledger (PK 53 here against about 87 ledger rows in a
comparable window; India 135 against 243), and booking lag truncates the window
from the left. Correcting for both still leaves the proxy roughly **10 times too
high in PK and 15 times in India**.

The ML model halves the error and does not remove it.

**What this does and does not matter for.** Under Maximize Conversion Value with
no target ROAS, absolute scale barely matters: the bidder spends the budget and
maximises value, so multiplying every value by ten changes nothing. **It matters
enormously the moment a target ROAS is set.** The 38x target I proposed for
India in `FINDINGS_india.md` was computed on the realised return against the
same inflated signal, so it is self-consistent, but anyone who sets a target by
reasoning from real booking economics will be wrong by a factor of fifteen.

---

## 3. The relative calibration by destination, which is what actually hurts

This is the part that changes behaviour, because the bidder allocates between
destinations on these values.

**PK, 4 destinations with 3 or more sales, median ratio 10.89**

| dest | searches | search value | sales | sales value | ratio | x median | scale needed |
|---|---|---|---|---|---|---|---|
| LHE | 1,114 | 64,721 | 4 | 3,958 | 16.35 | 1.50 | 0.67 |
| **LHR** | 762 | 56,684 | 5 | 4,043 | **14.02** | **1.29** | 0.78 |
| JFK | 485 | 64,156 | 6 | 8,273 | 7.75 | 0.71 | 1.40 |
| KHI | 544 | 24,839 | 4 | 4,670 | 5.32 | 0.49 | 2.05 |

**India, 15 destinations with 3 or more sales, median ratio 18.16**

| dest | searches | search value | sales | sales value | ratio | x median | scale needed |
|---|---|---|---|---|---|---|---|
| BER | 2,292 | 148,444 | 4 | 1,658 | **89.51** | **4.93** | 0.20 |
| SFO | 2,020 | 204,902 | 3 | 2,861 | **71.61** | **3.94** | 0.25 |
| **LHR** | 3,266 | 138,005 | 5 | 2,626 | **52.55** | **2.89** | 0.35 |
| **MAN** | 934 | 49,910 | 3 | 952 | **52.41** | **2.89** | 0.35 |
| DOH | 1,256 | 134,827 | 8 | 3,783 | 35.64 | 1.96 | 0.51 |
| FRA | 1,284 | 75,126 | 5 | 2,635 | 28.51 | 1.57 | 0.64 |
| HYD | 1,445 | 71,084 | 5 | 3,001 | 23.69 | 1.30 | 0.77 |
| CDG | 809 | 33,952 | 3 | 1,870 | 18.16 | 1.00 | 1.00 |
| DUB | 1,834 | 119,997 | 11 | 7,286 | 16.47 | 0.91 | 1.10 |
| BLR | 1,135 | 52,930 | 3 | 3,814 | 13.88 | 0.76 | 1.31 |
| CCU | 759 | 28,264 | 3 | 3,590 | 7.87 | 0.43 | 2.31 |
| PHL | 310 | 8,323 | 3 | 5,746 | 1.45 | 0.08 | 12.54 |

**The spread is 62 to 1 across destinations in India.** Berlin searches are
valued at 89.5 times the booking value they produce; Philadelphia at 1.45. A
value bidder reading this signal will systematically overbuy Berlin, San
Francisco, London and Manchester, and underbuy Philadelphia, Kolkata and
Bangalore. That is not a modelling subtlety, it is a four-to-one misallocation
inside one account.

**This corroborates and strengthens the UK flag in `FINDINGS_india.md`.** There
I measured UK+IE at 1.35 to 1.44 times the median, using the destination named
in the campaign. Measured on the destination the user actually searched, with
real booking values from the same tag, **LHR and MAN are at 2.89 times the
median**. My India finding was right in direction and **understated**, which is
the opposite of what happened with the search term correction.

And in PK, LHR is the second most over-valued destination, at 1.29 times the
median, on a four destination base.

> **Do not read the PK line as a cause of the PK collapse.** The control test in
> `FINDINGS_round7d_control.md` compares all four markets and finds PK has the
> **lowest** destination spread of the four, 3.1x against Canada's 8.7x, and the
> worst outcome. That survives bootstrapping to equal destination counts.
> Destination miscalibration does not explain PK. The India conclusion above is
> unaffected, because it stands on India's own numbers.

---

## 4. The proxy ranks correctly even though it is not calibrated

Joining search rows to sales rows on the hashed journey:

| market | journeys | with a sale | mean search value, booked | did not book | ratio |
|---|---|---|---|---|---|
| PK | 24,110 | 51 | 71.78 | 38.19 | **1.88x** |
| IN | 131,213 | 132 | 92.65 | 28.36 | **3.27x** |

Journeys that ended in a booking carried roughly two to three times the search
value of journeys that did not. **The signal has real rank power.** It is not
noise, and it should not be discarded.

The conclusion is narrower and more useful than "the proxy is broken":

> **The FSV proxy ranks users well and prices destinations badly.** Within a
> destination it tells you who is worth bidding for. Across destinations it is
> wrong by up to five times, and that is the axis a value bidder allocates on.

---

## 5. What to do with this

1. **Recalibrate per destination before setting any target ROAS.** The scale
   column above is the multiplier each destination's search values need to sit
   on the account median. India's four worst need 0.20 to 0.35.
2. **Prefer the ML variant if one must be chosen.** It halves the absolute
   error, 8.78x against 15.22x in PK, and leaves booking values untouched.
3. **Do not set a target ROAS from booking economics.** It has to be derived
   from the realised return against whichever signal the portfolio actually
   reads, which is still a UI question.
4. Re-run this monthly. Every ratio here rests on 3 to 11 sales per destination.

---

## On click_view, since you asked

It exists, 19 fields, 90 days, and it must be queried one day at a time. It
carries a gclid, so it is personal data and nothing from it should be written
without hashing.

**Mostly not worth it for this investigation.** It returns no cost and no
conversion metrics, so it is a dimension table, not a performance table, and
most of what it offers is already covered.

One thing in it is genuinely unique and worth keeping in mind:
`location_of_presence` against `area_of_interest`, per click, at city, metro,
region and country level. That separates "the user is physically in the UK" from
"the user is asking about the UK", which no aggregate report distinguishes.
Round 4 answered the PK geography question a different way and found that
out-of-country share reverted below baseline, so there is nothing to chase now.
If a geography question ever turns sharp again, that is the field to use.

---

## Limits

- 3 to 11 sales per destination. Direction is reliable, magnitude is indicative,
  and nothing here should be actioned at destination level without re-running.
- The VBB sales rows undercount the transaction ledger by a third to a half. The
  absolute ratios in section 2 are therefore upper bounds.
- Booking lag truncates the window from the left, which inflates the same ratios
  further.
- Journey joins use a hashed cookie, so a user across two devices is two
  journeys. Given the cross-device finding in round 6, section 4's ratios are
  conservative.
- Only PK and India were pulled. SA, CA and MY would run on the same script.
