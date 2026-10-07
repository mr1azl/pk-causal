# Round 6: Canada and Malaysia, and the four market picture

Same test set as PK, same four periods, same scripts. One parameterised runner,
`scripts/f01_market.py`, so every market gets identical treatment.

| market | account | id | campaigns with spend | cost 13 Jun-5 Oct | enabled |
|---|---|---|---|---|---|
| Canada | `Google-AMER-CA-EN` | 4096344384 | 359 | 246,297 | 619 |
| Malaysia | `Google-EASWP-MY-EN` | 9880134221 | 360 | 75,043 | 420 |

The FR variants of Canada carry zero spend and zero enabled campaigns.

**Grouping caveat.** UK+IE, long-haul and regional are defined from a Pakistan origin and are
reused unchanged so markets stay comparable. From a Canada or Malaysia origin the labels do not
carry their usual commercial meaning. They are consistent buckets, not market specific
segmentations.

---

## Every market switched the same way, on the same days, with the same gap

| market | portfolio | owner | target ROAS | CPC ceiling | switch dates |
|---|---|---|---|---|---|
| PK | `PK_FlightSearch_VBB - Conv Value Δ` | MCC | **not set** | not set | 2 and 3 Sep |
| SA | `SA_FlightSearch_VBB_ML - Conv Value Δ` | MCC | **not set** | not set | 2, 3 and 14 Sep |
| CA | `CA_FlightSearch_VBB - Conv Value Δ` | MCC | **not set** | not set | 2, 3 and 13 Sep |
| MY | `MY_FlightSearch_VBB_ML - Conv Value Δ` | MCC | **not set** | not set | 2 and 3 Sep |

Four markets, four MCC owned portfolios, **none with a target ROAS and none with a CPC ceiling**,
all switched on 2 and 3 September. This is a programme, not a local decision.

## The bidding pathology is universal

At the switch, 20 Aug-1 Sep against 2-19 Sep:

| | PK | SA | CA | MY |
|---|---|---|---|---|
| cost per click | 0.225 to **1.479** | 0.317 to **0.673** | 0.419 to **0.718** | 0.379 to **0.915** |
| lost to **rank** | 21.7% to **0.7%** | 53% to **1%** | 52% to **4%** | 38% to **11%** |
| lost to **budget** | 10.5% to **72%** | 14% to **61%** | 12% to **57%** | 13% to **62%** |

**All four stopped losing auctions on rank and started running out of money.** None was outbid.
Every one bid itself out of volume against a fixed budget. The effect is a property of the
strategy as configured, reproduced four times independently.

PK is the extreme on price, 6.6 times against 1.7 to 2.4 elsewhere.

## The conversion damage is not universal, but it is not unique to PK either

Bookings per 1,000 searches:

| market | 13 Jun-19 Aug | 20 Aug-1 Sep | 2-19 Sep | **20 Sep-5 Oct** | **against baseline** |
|---|---|---|---|---|---|
| **PK** | 7.4 | 8.0 | 6.8 | **2.7** | **-63%** |
| SA | 8.16 | 10.89 | 13.83 | **9.76** | **+20%** |
| CA | 5.95 | 4.38 | 9.18 | **4.39** | **-26%** |
| MY | 5.57 | 6.55 | 9.67 | **3.93** | **-29%** |

**This corrects round 5.** With SA alone it looked as though the switch cost no conversion rate
anywhere but PK. Canada and Malaysia show real damage, around 26 to 29 percent each. So the
strategy does cost conversion rate in most markets.

**PK is still the outlier, at roughly twice the damage of CA and MY**, and SA is the only one that
came through ahead.

Note also that every market's rate **rose** during the switch window itself and fell afterwards.
That is consistent with the collapse in volume buying only the best inventory for a few weeks,
then the recovery reintroducing the rest.

## Only PK has a destination that went to zero and stayed there

| market, UK+IE | pre-cut | post-cut | switch | now |
|---|---|---|---|---|
| **PK** | 157 | 16 | **0** | **0** |
| SA | 4 | 0 | 2 | 3 |
| MY | 8 | 0 | 2 | 2 |
| CA | no UK+IE bookings in any period | | | |

SA and MY both show a zero in one period and recover. **PK goes to zero and stays there**, which
no other market does.

## The change audit says the same thing in all four

| market | keywords | modified 15 Aug-5 Oct |
|---|---|---|
| PK (UK scope) | 1,188 | **0** |
| SA | 1,593,182 | **0** |
| CA | 864,779 | **0** |
| MY | 1,116,089 | **0** |

**Not one keyword was modified in any market.** Campaign edits are the switch itself. Ad group
edits are 917 in CA (29 and 25 Sep), 443 in MY (5 Sep), 42 in SA, 72 in PK, and in PK those were
verified to be dormant ad groups carrying no traffic.

## Cross-device inflation differs sharply by market

all_conversions against the actual transaction ledger, regional, before 2 September:

| market | all / ledger | cross-device share | same device / ledger |
|---|---|---|---|
| **PK** | **9.77x** | **82.7%** | 1.69x |
| MY | 4.83x | 66% | 1.67x |
| CA | 2.59x | 45% | 1.43x |
| SA | 2.15x | 25% | 1.60x |

Strip cross-device and all four converge between 1.43 and 1.69. **The entire spread is Google
modelling device-switching journeys at wildly different rates by market**, from a quarter of
conversions in SA to four fifths in PK.

Booking numbers are therefore **not comparable across these four markets at face value** in any
report. That is a finding in its own right, independent of the investigation.

Ledger structure is identical everywhere: `conversion_quantity` is 1000 on all 144 CA rows and all
39 MY rows, as in PK and SA, so one row is one transaction. Zero revenue runs 2.2 percent in PK,
2.7 in SA, 3.5 in CA, 7.7 in MY. Duplicate order IDs: 1 in PK, 1 in SA, **0 in CA, 0 in MY**.

---

## What this means

**The bid strategy is a real and repeated problem.** Four markets, no ROAS target, no CPC ceiling,
all four bid themselves into budget exhaustion within days. That is worth raising as a programme
level issue, not a PK one.

**It costs conversion rate in most markets**, 26 to 29 percent in CA and MY. PK's 63 percent is
roughly double, so PK has something additional wrong, but the strategy is not blameless anywhere.

**PK remains the only market with a destination level zero that persists.** Rounds 3 and 4 ruled
out geography, device, structure, settings, keywords, audiences, ads, landing pages, demographics
and brand migration. Three further markets now show the strategy alone does not produce a
persistent zero. The UK specific cause in PK stands as the open question.

**The cross-device gap is a separate and probably more urgent reporting problem**, since it makes
market comparisons invalid today regardless of what happens with PK.

## Caveats

- Destination groups are PK centric, see above.
- CA and MY booking ledgers are small, 144 and 39 rows, and the MY by group figures rest on 3 to
  12 rows each. Treat direction as reliable and magnitude as indicative.
- Attributes are current, not historical.
- `last_modified_time` records only the most recent edit per object.
- Brand accounts were not examined for CA or MY.
- Unexplained and not chased: 172 SA campaigns modified 14 Sep, 20 CA campaigns 13 Sep,
  619 CA ad groups 29 Sep, 443 MY ad groups 5 Sep.
