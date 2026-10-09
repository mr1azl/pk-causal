# Review of round 8: market profiles, test power and pairing

*8 Oct 2026.*

**Inputs:**
- Agent protocol: `docs/agent_findings/sa360_round8_market_profile/PROTOCOLE_APPARIEMENT.md`.
- Agent data: `data/sa360/round8_market_profile/` (`s1` accounts, `s3` 12-week profile, `s4` pre-launch profile,
  `s5` power, `s6` pairings).

**What the agent did.** It profiled 13 markets on six dimensions: CPC dispersion, rank lost, budget lost,
impression share, searches per booking and cross-device share.
- The 4 launched markets (PK, SA, CA, MY) are measured on 16 Jul to 1 Sep.
- The 9 candidates (FR, ES, IT, PL, JP, KR, BR, OM, AE) are measured on 16 Jul to 7 Oct.

From these profiles it (1) sized a test for each market, and (2) paired each candidate with its nearest launched
market, using that market's outcome as a prior.

## 1. What reproduces

- **Distances:** recomputed from `s4` (six dimensions, the two ratios in logs, z-scored on the 13 markets). Every
  distance and ratio in `s6` matches to two decimals. For example, AE is 1.28 from SA and 2.55 from MY, a ratio of
  1.99.
- **Power:** the target is a 30% drop at 80% power, two-sided 5%, on the log rate ratio.
  - 50/50 split: `Var = 1/c_control + 1/c_treated`, so about 300 bookings in total and about 150 in the control
    arm. CA needs 4.7 weeks, matching `s5`.
  - 20% holdout: 6.6 weeks for CA, **1.40 times** the 50/50 duration.
  - The claim that a 20% holdout is slower than a 50/50 split is right. It corrects the holdout design I suggested
    for India.

## 2. What I accept

1. **Volume is the first constraint, not calibration.** This is the most useful result of the round. Five of nine
   candidates (BR, IT, PL, KR, JP) are at about 5 ledger bookings a week or fewer. No test on them can read a 30%
   effect within a year. For those, decide by guardrails and say so; do not pretend to measure.
2. **If a market is tested, use 50/50, not a 20% holdout.**
3. **Read nothing on data younger than 14 days** (round 7c: a 14-day window sees 88.5% of its bookings). This is
   consistent with the g1 reconciliation and with the fresh review.
4. **Watch budget lost and rank lost together.** Rank lost falling to zero while budget lost rises is a fair
   description of PK in September.
5. **KR at 0% cross-device needs a tagging check** before anything else.

## 3. What I do not accept: the outcome labels behind the priors

The pairing gives each candidate the outcome of its nearest launched market as a prior:
PK -63%, SA +20%, CA -26%, MY -29%.

These are round 6 figures: attributed bookings per 1,000 searches, **20 Sep to 5 Oct** against 13 Jun to 19 Aug.
That window is the one already shown to be unusable:

- `data/sa360/round6_CA_MY/g1_window_reconciliation.csv`: CA's -26% and MY's -29% come from the last 16 days of
  attributed conversions. Over the full 2 Sep to 5 Oct window they read **+17% and +10%**. The protocol notes this
  in its limits, then uses the -26% and -29% anyway.
- The fresh review (`11_FRESH_REVIEW.md` s5, `scripts/pk_fresh_review.py` section I) measured Adobe orders per
  dollar over the full post window. On that basis the order is close to reversed:

| Market | Round 6 label (used as prior) | Adobe orders per $ | Adobe revenue per $ |
|---|---:|---:|---:|
| SA | **+20%** (the "only winner") | **-21%** (worst of the four) | -36% |
| CA | -26% | +38% | +70% |
| MY | -29% | +203% | +169% |
| PK | -63% | +2% | -17% |

- "Bookings per 1,000 searches" is also not a business outcome under VBB. The bidder is paid for searches, so
  buying more searches lowers the ratio by construction, whatever happens to bookings per dollar.

**Result:** the "+20% prior" for AE, OM, FR, ES, KR, PL and JP is not supported. On Adobe orders per dollar, the
same pairing would hand AE and OM a **-21%** prior.

## 4. The pairing itself carries little information

- **SA, CA and MY form one cluster.** The distances between them are 2.0 to 2.9. PK is the outlier at 4.6 to 5.9.
- **Inside that cluster, outcomes range from -21% to +203%** on Adobe orders per dollar. Whether a candidate's
  nearest neighbour is SA or MY says nothing useful about its result.
- **The ratio test is fragile.** It depends on scaling. With the two ratios left raw instead of logged:
  - KR's ratio rises from 1.47 to 1.67 and passes the 1.5 threshold;
  - FR's falls from 1.26 to 1.17;
  - BR's nearest neighbour becomes a tie between PK and SA.

**What the profile can say is how far a candidate is from PK**, since PK is the only clear failure in the panel
(it failed on the GB segment; see `12_RESPONSE`). On that reading:
- AE (5.2 from PK), JP (5.7) and IT (4.3) are far from PK;
- BR (3.3) and PL (3.4) are the closest.

That supports the agent's ordering (AE early, BR not first) without using any prior.

## 5. The four "PK risk signals": n = 1, and one is contradicted

Each threshold was set by looking at PK alone:
- CPC dispersion above 4;
- rank lost below 35%;
- more than 800 searches per booking;
- cross-device above 55%.

That is fine as a list of things to watch, but none is validated:

- **CPC dispersion above 4 is contradicted by CA.** CA was at 4.84 before the switch and gained 38% orders per
  dollar.
- The other three thresholds are PK-only, and PK's failure was concentrated in one segment (GB).
- The PK mechanism in the protocol ("a single CPC cap saved two thirds of the account and killed the other
  third") comes from round 7, which is not in this repo. Round 4 found no CPC cap on the PK portfolio as of early
  October, so this is either a simulation or a change made since. **Round 7 files are needed to check it.**

## 6. Caveats on the power numbers

- **The power figures assume Poisson bookings.** A campaign split is clustered: campaigns differ, and a few large
  campaigns (in PK, two GB country campaigns took 89% of GB spend) dominate each arm. Real variance is larger, so
  the week counts are a **lower bound**. Split by matched pairs of campaigns (same destination group, similar
  spend), not at random.
- **Bookings per week come from 8 weeks of ledger.** JP rests on 9 transactions and KR on 13.
- **Candidate profiles are 12 weeks and include September; launched profiles are 6.9 summer weeks.** Ratios are
  probably comparable; volumes are not.
- **Only the largest EN account per market is profiled.**

## 7. Revised read for the candidates

| Group | Markets | Read |
|---|---|---|
| Testable at account level within ~20 to 28 weeks | AE (19/wk), OM (12.6), FR (12.3) | 50/50 test on matched campaign pairs, read on ledger or Adobe orders per $ after 14 days of lag. No prior. |
| Slow | ES (8.7/wk, ~38 weeks) | Launch with guardrails, or test only if the business accepts the duration. |
| Not testable | BR, IT, PL, KR, JP (5/wk or fewer) | Decide on operational guardrails: CPC cap by destination group, budget lost and rank lost watch, Adobe orders per $ by group. Fix KR tagging first. |

Applies to all of them, from the PK work:
- ML or calibrated values;
- a target ROAS or a CPC cap set **per destination group** when CPC dispersion is high;
- a rollback list prepared in advance;
- no other changes within ±3 weeks.

**Order:** AE first, as the agent says. The reason is not that it resembles SA. It is the most testable
candidate, it is furthest from PK, and it has the healthiest profile:
- 191 searches per booking;
- 22% cross-device;
- low CPC dispersion.

## 8. Requests

1. **Round 7 files** (7, 7c, 7d), cited by the protocol and not in the repo: the CPC cap mechanism, lag curve and
   calibration dispersion.
2. **The launched-market outcomes recomputed with the round 8 method**, on ledger transactions per $ over
   2 Sep to 21 Sep, read after 14 days of lag, not attributed bookings per 1,000 searches. If the pairing is kept,
   it needs labels that do not depend on the window.
3. **Ledger bookings per week by destination group** for AE, OM and FR, to size group-level reads.
