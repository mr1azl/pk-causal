# SA360 agent code (round 3)

Scripts written and run by the user's SA360 Reporting API agent for round 3 (seasonality, booking definitions).
Kept for reference and reproduction; they need SA360 API credentials in the environment
(`CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`, read by `lib_sa360.py`; never stored here).

- `lib_sa360.py`: auth, `searchStream` wrapper, date chunking, `dest_code()` parser for both campaign naming
  conventions, destination groups.
- `s01` to `s07`: setup, seasonality pull and comparison (A), conversion actions, conversion rows and booking
  analysis (B).

Round 7 code (Google Ads API, `lib_gads.py`, `r01` to `r24`) is in `agent_code/round7/`; India pre-launch code
(`i00` to `i90`) in `agent_code/india_prelaunch/`. Both read credentials from the environment or a local `.env`,
never stored here. Code for rounds 4 to 6 (`d*`, `e*`, `f*`, `g*` scripts) was not handed over; their outputs are in
`data/sa360/` and their findings and logs in `docs/agent_findings/`. API behaviour and limits are documented in
`docs/source_material/SA360_API_CAPABILITIES.md`.
