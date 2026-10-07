# PK-UK on Google Flights (GFS): price, visibility and demand around the switch

*7 Oct 2026. Run of `notebooks/GFS_PK_UK.ipynb`, outputs in `data/gfs/`. GFS data 18 Feb 2025 to 4 Oct 2026.
Run with `USER_COUNTRY = None` (all Google Flights users); Pakistan users are about 70% of the weight on
PK-origin routes. Weekly, Sunday-start weeks. GFS is Google Flights behaviour only, not bookings.*

## Summary

**GFS shows no UK-specific price, visibility or demand shock at the 2 Sep switch.** The external
explanation for the UK booking zero (a fare, inventory or demand collapse on PK-UK) is not supported.
Two changes are visible, but neither fits:

1. **A UK-specific weakening in Google Flights rank and selection, but from mid-August, before the switch.**
   In the weeks of 16 and 23 Aug 2026, QR's average rank on PK-UK went from 2.8 to 4.5 and its selection
   rate when shown from 0.40 to 0.21. The same weeks of 2025 show a smaller seasonal version (rank 3.6 to
   4.2, selection 0.36 to 0.27). Paid search UK bookings were still normal in late August (9 by click date
   in the week of 24 Aug), so this does not line up with the 2 Sep cliff. By September, UK is only modestly
   worse than September 2025 (rank about 4.5 against 4.1, selection about 0.21 against 0.23).
2. **QR became less often the cheapest from the week of 20 Sep, on UK and other routes alike.** Share of
   searches where QR is cheapest fell to 0.23 to 0.41 on UK and 0.17 to 0.36 on other destinations. Not UK
   specific, and after the UK cliff had already started; other destinations kept converting.

## Headline: 4 weeks before vs 4 weeks from 2 Sep, change in each year

| Metric | UK+IE 2025 | UK+IE 2026 | Other 2025 | Other 2026 |
|---|---:|---:|---:|---:|
| QR cheapest share (points) | +4.9 | -9.8 | +2.0 | -10.8 |
| Price gap when more expensive (points) | -0.9 | -6.0 | -7.0 | -14.8 |
| Demand weight per day | -62% | -51% | -81% | -47% |
| Average rank (higher is worse) | +0.21 | **+1.07** | +0.64 | +0.04 |
| Selection rate when shown (points) | -8.1 | -10.9 | -5.6 | -4.2 |
| Shopping volume per day | -35% | -26% | -20% | -16% |

- **Demand:** Google Flights interest in PK-UK falls from August to September every year, and fell less in
  2026 (-51%) than in 2025 (-62%). No demand collapse.
- **Price:** the cheapest-share drop in 2026 is the same on UK and other routes; the price gap when QR is
  more expensive narrowed on UK.
- **Rank and selection:** the one UK-specific change, about one rank position and three points of
  selection rate worse than the 2025 seasonal pattern, and it starts in mid-August.

## Routes

Across the main PK-UK routes (LHE-LHR, ISB-MAN, ISB-LHR, KHI-LHR, LHE-MAN, ISB-BHX; the top 10 are 55% of
demand), QR's cheapest share moved between -0.20 and +0.14 against 2025, in both directions. No route
shows QR becoming uncompetitive. Full table: `data/gfs/q3_routes_summary.csv`.

## Limits

- **No competitor data.** Both tables hold QR rows only (`q0c`, `q0d`), so a new competitor on PK-UK cannot
  be seen here. `operating_airline` exists in the competitiveness table and may help.
- `participation_rate_weight` is zero on these rows, so participation is empty in the competitiveness table.
  The shopping table's participation (0.70 to 0.81) drifts down slowly from August, without a step.
- The table has `trip_type`, `days_until_departure_bucket` and `client_device_type`, unused so far.
- A rerun with `USER_COUNTRY = "PK"` would match the paid-search audience exactly; with 70% of the weight
  already from PK users, it is unlikely to change the picture.

## What it means

With seasonality, measurement, user location, device, campaign edits, keyword mix and now the Google
Flights market all checked, the UK zero after 2 Sep remains unexplained by anything outside the bidding.
The mid-August GFS weakening could have made UK a little harder, but UK paid search kept booking through
the end of August. The experiment (UK campaigns back to Maximise Conversions on flight searches for two
to three weeks) is the remaining direct test.
