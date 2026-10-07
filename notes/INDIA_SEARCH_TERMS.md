# India search terms (non-brand and brand), May to 7 Oct 2026: risks before a VBB launch

*Source: Google Ads search terms reports for India non-brand (1.1M rows, about $343k of search spend shown,
about 75% of account search cost) and India brand. India has not switched, so every month is pre-launch.
Script: `scripts/india_search_terms.py`; classified data in `data/india/`. Monthly granularity, cost and clicks
only (no conversions in the export).*

## Summary

1. **12% of India non-brand search spend already goes to off-target queries** ($41k of $343k since May):
   reverse direction (destination to India) $24k, third-country routes and generic queries the rest. In PK the
   switch pushed UK campaigns from about 6% to 22-28% off-target. India starts from a higher base.
2. **Reverse-direction queries are a VFR problem, concentrated in a few large campaigns.** 9% of clicks on
   North America, UK+IE and GCC campaigns; 37% on the Canada country campaign, 38% on Kuwait, 27% on UAE,
   23% on GB, 15% on the US country campaign ($21k spend). A reverse search made on the India site still
   carries the full route value, so VBB will value these clicks like outbound ones.
3. **Some broad-match city campaigns are already mostly generic,** the same pattern PK's Manchester campaign
   developed after the switch: Riyadh city 70% generic (95% broad), Zurich 42%, Toronto 37%, Manchester 33%.
4. **Performance Max is 19% off-target by cost** (reverse queries such as "madrid to india flights",
   "auckland to mumbai", "toronto to hyderabad"; competitor names 8% of clicks in some months).
5. **Brand cost per click rose in India too, with no switch.** `Brand|Qatar` CPC went 0.15 (Jul) to 0.28 (Aug)
   to 0.39 (Sep); `Brand|Airways` ramped from August as in PK. So the brand CPC rise seen in PK in September is
   not caused by PK's VBB switch; it is market or programme wide. Brand leakage (queries without a brand
   word) is small, and non-brand campaigns buy almost no brand queries, as in PK.

## 1. Query direction by destination group (search campaigns, all months)

| Group | Clicks | Outbound | Destination only | Reverse | Third-country | Generic | Broad match |
|---|---:|---:|---:|---:|---:|---:|---:|
| North America | 237,292 | 71.5% | 12.7% | 9.0% | 3.5% | 1.9% | 27% |
| Europe | 222,442 | 68.7% | 20.3% | 5.7% | 2.9% | 1.7% | 32% |
| GCC/Middle East | 208,846 | 64.1% | 15.9% | 9.2% | 5.9% | 3.8% | 32% |
| UK+IE | 134,644 | 70.6% | 15.0% | 9.3% | 3.0% | 0.6% | 29% |
| Turkey/Caucasus | 33,238 | 72.3% | 19.4% | 3.5% | 3.7% | 0.1% | 20% |
| Oceania | 31,723 | 75.7% | 16.5% | 2.9% | 4.0% | 0.0% | 16% |
| Africa | 24,151 | 76.5% | 16.4% | 3.5% | 2.8% | 0.0% | 26% |

By month the mix is stable (outbound 62% to 71%, reverse 7% to 12%), so this is a standing property of the
account, not a recent change.

## 2. Off-target cost by group, May to 7 Oct

| Group | Cost | Off-target cost | Of which reverse | Off-target share |
|---|---:|---:|---:|---:|
| North America | $140,277 | $13,772 | $8,626 | 9.8% |
| Europe | $67,202 | $7,197 | $4,094 | 10.7% |
| UK+IE | $51,452 | $7,455 | $5,437 | 14.5% |
| GCC/Middle East | $48,754 | $9,164 | $4,471 | 18.8% |
| Performance Max | $10,340 | $1,932 | $964 | 18.7% |
| **Total** | **$343,288** | **$41,232** | **$24,391** | **12.0%** |

## 3. Campaigns to clean before launch (largest off-target spend)

| Campaign | Cost | Off-target | Reverse | Generic | Broad |
|---|---:|---:|---:|---:|---:|
| `Dest\|Country\|US` | $21,409 | 21% | 15% | 0% | 31% |
| Performance Max | $10,340 | 31% of clicks | 15% | 2% | n/a |
| `Dest\|Country\|AE` | $6,907 | 41% | 27% | 1% | 50% |
| `Dest\|Country\|GB` | $8,901 | 29% | 23% | 0% | 39% |
| `Dest\|City\|YYZ` (MOD) | $3,703 | 65% | 24% | 37% | 74% |
| `Dest\|Country\|CA` | $5,352 | 43% | 37% | 0% | 43% |
| `Dest\|City\|RUH` | $2,436 | 74% | 3% | 70% | 95% |
| `Dest\|Country\|DE` | $5,477 | 24% | 17% | 0% | 32% |
| `Dest\|City\|LHR` | $4,779 | 26% | 20% | 0% | 27% |
| `Dest\|Country\|KW` | $2,400 | 45% | 38% | 0% | 33% |
| `Dest\|City\|LGW` | $3,993 | 25% | 20% | 0% | 32% |
| `Dest\|City\|ZRH` | $1,886 | 47% | 3% | 42% | 79% |

`O&D|Country|IN|US`, the biggest campaign ($79k), is clean (2% off-target): route campaigns that name India
as origin attract few reverse queries. Destination-only campaigns are where reverse and generic queries enter.

## 4. Brand (India)

| Campaign | CPC Jun | Jul | Aug | Sep |
|---|---:|---:|---:|---:|
| `Brand\|Hero` (exact, about 90% of clicks) | 0.08 | 0.08 | 0.07 | 0.07 |
| `Brand\|Qatar` | 0.17 | 0.15 | 0.28 | **0.39** |
| `Brand\|Airways` (phrase, ramped from Aug) | 0.01 | 0.01 | 0.13 | 0.18 |

- Same `Brand|Qatar` and `Brand|Airways` pattern as PK, without a switch: the PK brand CPC rise is not a VBB
  effect. (PK `Brand|Hero` CPC rose 27% in September while India's did not; that part remains unexplained.)
- Queries without a brand word: under 0.3% of brand clicks (misspellings, Arabic and Japanese brand names,
  "doha airlines"). Non-brand campaigns buy almost no brand queries.

## 5. What to do before launching India

1. **Reverse-direction negatives on destination campaigns**, starting with US, CA, GB, AE, KW, DE, LHR, LGW,
   YYZ, JFK, IE: "to india", "to delhi", "to mumbai", "to hyderabad", "to amritsar", "to kochi", "to chennai",
   "to bangalore", "to ahmedabad", and "<destination> to" phrasing. A shared negative list makes this one change.
2. **Generic-heavy broad city campaigns** (RUH, ZRH, YYZ MOD, MAN): move to phrase or add generic negatives
   ("flight ticket", "flight booking", "cheap flights", "air ticket").
3. **Keep Performance Max out of the VBB test**, or exclude it from the read: it is 19% off-target and its
   query mix shifts month to month.
4. **Do the cleanup at least two weeks before the switch**, so it does not confound the launch read (the PK
   lesson about the 20 Aug budget cut).
5. **Evaluate on brand and non-brand together.** Brand CPC is moving for its own reasons in both markets, so
   brand is not a clean control.
