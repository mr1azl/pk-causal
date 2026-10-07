# Handover: Adobe Analytics data pull for the SA360 Causal Impact study

Oct 7, 2026 · @Marouane

## Summary

The Adobe daily pull works, but the output is not ready for the Causal Impact models yet. One parsing fix and one sanity check come first.

**What is in place**

- A three-cell notebook, `aa_v84_daily_pull.ipynb`, pulls the raw SA360 tracking ID (v84) from the Adobe Analytics API one day at a time and parses it in Python.
- The first full run covered 1 May to 5 October 2026 (158 days) for six markets: Germany, Canada, Saudi Arabia, Pakistan, Malaysia and Singapore.
- The output file `aa_daily_market_group.csv` has 1,896 rows: 158 days x 6 markets x Brand / Non-brand.
- Every day reconciles to Adobe's own daily total. No day has low-traffic bucketing or duplicate keys.
- The Brand rule agrees with the `-Brand` account suffix on all but 6,178 of 84.8 million in revenue.

**What must happen before the data is used**

- **Fix the account rule.** The account `Google-ME_CAUCASUS-SA-EN-2` (410,924 in revenue) is not recognised as Saudi Arabia. Saudi non-brand shows 29,100 for the whole period and is understated by up to that amount. It is a one-line change; only the third cell needs re-running.
- **Run the Germany sanity check from the spec.** Germany non-brand averages 2,705 a day over the period. The spec expects about 14,000 a day in September (2.5 x the 5,611 Floodlight figure). The period average is not the September figure, but the gap is large enough to suspect missing accounts or a currency difference.

The unresolved question of why Account and Campaign show as Unspecified in Adobe is parked. The pipeline no longer depends on those fields.

## Background and goal

The goal is to re-run the SA360 Causal Impact analysis on Adobe Analytics data, so the result no longer depends on Floodlight alone.

The Floodlight analysis measured Germany at +70% and Canada at +153% on revenue after the bidding change. Floodlight captures roughly 40% of Germany's Adobe revenue and 16% of Pakistan's. That gap is the biggest open question in the project.

The design, as stated in the export spec:

- **Treated group:** non-brand campaigns, which moved to the new bidding. Germany switched on 30 July 2026.
- **Control group:** brand campaigns, which stayed on the old bidding throughout.
- **Excluded:** Performance Max, left out of both groups.

**What the spec asks Adobe for**

| Requirement | Detail |
| --- | --- |
| Shape | One row per day, per market, per campaign group |
| Columns | Day, Market, Campaign group, Flight Search Visits, Bookings, Revenue |
| Granularity | Daily. The model needs about 45 pre-period points as a floor |
| Split | Brand / Non-brand, paid search only, Performance Max excluded |
| Window | 1 May to 5 October 2026 preferred (158 days), 13 June at minimum |
| Size | 6 markets x 2 groups x 158 days = 1,896 rows |

**Three corrections to the spec text**

- It says "Five columns" but the table has six.
- The row check of 158 per market per group only holds for the 1 May start. From 13 June the correct count is 115.
- Non-brand is defined as "everything else" before the Performance Max exclusion. It should read "everything else, excluding Performance Max".

## What was done

All of this happened on 7 October 2026, in the order below.

| Step | What happened | Outcome |
| --- | --- | --- |
| 1. Spec review | Read the export spec and checked its numbers | Numbers hold. Three text corrections, listed above |
| 2. Workspace export | Downloaded the freeform table as CSV | Unusable. The CSV holds only the rows expanded on screen, and the panel was set to October only |
| 3. Account and Campaign | Looked at the Account breakdown in the export | Account is Unspecified for 2.93 of 3.12 million of US paid search revenue, 1 to 7 October (94%) |
| 4. Regex test | Ran the unclassified tracking IDs through the regex from the May 2025 email thread | All match and give the right account and campaign. The regex and the SA360 macro are not the cause |
| 5. Decision | Agreed to stop relying on Account and Campaign | Parse the raw v84 string in Python instead |
| 6. Original notebook | Reviewed `aa_breakdown_16_2.ipynb`, a multi-level breakdown runner | Too heavy for this need, and it had problems. See the note below |
| 7. New notebook | Wrote `aa_v84_daily_pull.ipynb`: config, daily pull, parse and aggregate | Tested against a simulated Adobe API before handover |
| 8. Access | Documented how to generate a token | See Reference |
| 9. First full run | Ran the notebook on the real API for 158 days | Succeeded. Results below |

**Findings on the original notebook**

- Its saved run stopped at "Step 4, Executing paginated breakdown" with no rows and no error.
- The main report call used `/api/qatara1/qatarairways-prod/reports`. The new notebook uses `/api/qatara1/reports`, which worked.
- It retried bad requests (400, 404) like outages, waiting 150 seconds before reporting. A config error looked like a hang.
- It walked every channel and used the Account and Campaign fields, which are mostly Unspecified.
- It wrote to Excel, which stops at about 1 million rows.

## The pipeline

The notebook `aa_v84_daily_pull.ipynb` has three code cells, run in order.

1. **Config.** Token, client ID, dates, metrics, segments and the market list. It is the only cell to edit.
2. **Pull.** One API report per day with raw v84 as the only dimension. It saves one CSV per day and skips days already saved, so an interrupted run continues where it stopped.
3. **Parse and aggregate.** Reads the daily files one at a time, splits each tracking ID, assigns market and group, writes the final table and prints four checks.

**How a tracking ID is parsed**

A v84 value has six parts separated by pipes: account, campaign, ad group, keyword, gclid, gclsrc. The campaign itself contains pipes in the new naming, so the split takes the first part as account and the last four as the rest.

```
Google-AMERICAS-US-EN-Brand|Google|US|Brand|Hero|XXX|XXX|EN|EXT|Brand Hero|qatar airways|Cj0KCQjw...|aw.ds
```

| Field | Rule in the notebook |
| --- | --- |
| Account | First part of the string |
| Campaign | Everything between the account and the last four parts |
| Market | Country code in the account name, pattern `Engine-Region-CC-LANG[-Brand]`. `Google-Europe-DE-DE` gives Germany |
| PMAX | Campaign contains `perf_max` or `pmax`, any case |
| Brand | Campaign contains `\|Brand\|`, or starts like the legacy `US-Brand-Hero-EN_exact` |
| Non-brand | Any other parsed campaign |
| Unparsed | The string does not have the six-part structure |

The final table keeps only Brand and Non-brand for the six markets. PMAX, Unparsed and accounts of other markets are left out but shown in the checks.

**Files it writes**

| File | Contents |
| --- | --- |
| `aa_v84_raw/v84_YYYY-MM-DD.csv` | One per day: the untouched v84 string and the three metrics |
| `aa_v84_raw/totals.csv` | One line per day with Adobe's own totals, used for reconciliation |
| `aa_daily_market_group.csv` | Final table: day, market, campaign\_group, flight\_search\_visits, bookings, revenue |

The raw daily files are never merged. Changing a parsing rule only needs the third cell re-run, not a new pull.

**The market filter in Adobe**

The pull uses two segments: BUGs Excluded, and a Workspace quick segment on v84. When last seen, the quick segment was defined as hits where v84 contains any of `-MY-EN -SA-EN -PK-EN -DE-EN CA-EN -SG-EN`. Confirm it was not changed before the run.

## Results of the first full run

The run produced 1,896 rows for 158 days and reconciles exactly to Adobe. Brand carries 95% of the revenue and Non-brand 2%.

**Revenue by market and group, 1 May to 5 October 2026**

Revenue is SalesIncYQ as Adobe reports it. The currency is not confirmed.

| Market | Brand | Non-brand | Non-brand per day | PMAX | Unparsed |
| --- | --: | --: | --: | --: | --: |
| Saudi Arabia | 28,731,565 | 29,100 | 184 | 0 | 0 |
| Canada | 20,370,255 | 323,486 | 2,047 | 1,301,450 | 0 |
| Germany | 13,431,692 | 427,457 | 2,705 | 684,947 | 0 |
| Malaysia | 9,584,804 | 197,009 | 1,247 | 309,441 | 0 |
| Singapore | 7,405,195 | 105,842 | 670 | 290,914 | 0 |
| Pakistan | 5,242,087 | 273,757 | 1,733 | 0 | 0 |
| Other (not in the final table) | 63,402 | 462,433 |  | 797 | 53,596 |
| **Total** | **84,829,000** | **1,819,084** |  | **2,587,549** | **53,596** |

The Saudi Arabia non-brand figure is wrong. Most of the Other non-brand revenue belongs to a Saudi account the rule did not recognise. See Known issues.

**What the checks showed**

| Check | Result |
| --- | --- |
| Rows add up to Adobe's daily total | Yes, on all 158 days. Differences are zero to rounding |
| Low-traffic bucketing | None. The risk that v84 would exceed Adobe's unique-value limit did not show up in this segment |
| Duplicate keys within a day | None |
| Unparsed keys | 17 days have some, 53,596 in total (0.06% of revenue). Largest: 15,452 on 6 September and 12,821 on 24 August |
| Brand rule against the `-Brand` account suffix | All 84,829,000 of Brand revenue sits in `-Brand` accounts. Only 6,178 of Non-brand revenue sits in a `-Brand` account |
| Daily volume | Between about 9,600 and 14,000 tracking IDs a day on the days inspected |

**Largest accounts the market rule put in Other**

| Account | Revenue |
| --- | --: |
| Google-ME\_CAUCASUS-SA-EN-2 | 410,924 |
| Bing-AMERICAS-US-EN | 23,294 |
| Google-Europe-GB-EN-Brand | 17,139 |
| Google-AMERICAS-BR-EN-Brand | 9,838 |
| Bing-Europe-GB-EN | 9,633 |

Apart from the first, these are accounts of other markets that passed the Adobe segment. They total about 116,000 (0.13% of revenue) and are correctly left out. Why they match the segment is not established.

## Known issues and fixes

Four issues are known. The first changes the numbers and must be fixed before the file is used.

**1. The Saudi account with a numeric suffix is not recognised**

The market rule accepts account names ending in the language code or in `-Brand`. The account `Google-ME_CAUCASUS-SA-EN-2` ends in `-2`, so its 410,924 of revenue went to Other. Saudi Arabia non-brand is understated by up to that amount.

The fix is one line in the third cell. Replace the `ACCOUNT_RE` line with:

```python
ACCOUNT_RE = r"^[^-]+-[^-]+-([A-Z]{2})-[A-Za-z]{2}(?:-Brand|-\d+)*$"     # Engine-Region-CC-LANG[-Brand][-2]
```

Then re-run the third cell only. No new pull is needed. The corrected rule was tested on the account names seen so far.

One related name is still unrecognised: `Google-Europe-sa-EN-Brand` (2,063), with a lower-case country code. Whether it is a Saudi account needs confirming before it is mapped.

**2. Local edits in the copy that was run**

The copy used for the run differs from the delivered notebook in three ways, all in `post_report`:

- `print(URL, HEADERS, body)` writes the bearer token into the cell output on every call. Remove it, and clear the outputs before sharing the notebook.
- `verify=False` turns off certificate checking. The intended route is the `CA_BUNDLE` path in the config cell.
- `timeout=60` was removed, so a stalled call would wait forever.

**3. Unparsed keys are not inspected yet**

53,596 of revenue sits on tracking IDs that do not have the six-part structure. The amount is small, but the cause is unknown. This lists them from the raw files:

```python
import glob, pandas as pd
raw = pd.concat(pd.read_csv(f, dtype={"v84": str}, keep_default_na=False) for f in glob.glob("aa_v84_raw/v84_*.csv"))
bad = raw[~raw["v84"].str.match(KEY_RE)]
bad.groupby("v84")["revenue"].sum().sort_values(ascending=False).head(30)
```

**4. The market filter is a quick segment**

The segment ID `s1952_6ac61c1d36a75d75a5b13658` belongs to a Workspace quick segment. It worked through the API, but it lives inside one project and can be edited or lost with it. Saving it as a normal segment makes the pull reproducible.

## Open questions

Seven questions are open. The first two decide whether the current file can be trusted.

**1. Does Germany non-brand match the expectation?**

The spec's test: Germany non-brand September revenue in Adobe should be about 2.5 x the 5,611 a day measured in Floodlight, so about 14,000 a day. A result near 1.0x or 10x means the segment is wrong.

Over the whole period Germany non-brand averages 2,705 a day, about 0.5x the Floodlight figure. September alone has not been computed. This does it from the output file:

```python
import pandas as pd
d = pd.read_csv("aa_daily_market_group.csv")
sep = d[(d.market == "Germany") & (d.campaign_group == "Non-brand") & d.day.between("2026-09-01", "2026-09-30")]
print(sep.revenue.mean(), sep.revenue.mean() / 5611)
```

**2. Does the Adobe segment cover every account of the six markets?**

The segment matches account names containing codes such as `-DE-EN`. Other accounts seen in the data follow a country-language pattern (`Europe-IT-IT`, `Europe-CH-DE`), so accounts like `-DE-DE`, `-CA-FR` or `-SA-AR` may exist and would be excluded. Accounts the segment misses never reach the raw files, so the checks cannot reveal them.

To test it, pull one day with a wider segment, or none, and list revenue by account. A missing German account would also explain question 1.

**3. What currency is SalesIncYQ in?**

The Floodlight figures are in dollars. If Adobe reports another currency, the 2.5x comparison does not apply as written.

**4. Which attribution does the pull use?**

Revenue is credited to whatever v84 value is on the booking hit. That depends on how eVar84 is configured in Adobe (allocation and expiry), which has not been looked up. The pull also has no channel filter; it relies on v84 being set only by SA360 clicks. The spec asks for the attribution model to be written down.

**5. Is the market definition the same as in the SA360 analysis?**

The notebook takes the market from the country code in the account name. The alternatives are the market code inside the campaign name or Adobe's Origin Country. Whoever ran the SA360 side should confirm which one matches.

**6. Is Non-brand volume high enough to model?**

Non-brand runs from 184 to 2,705 in revenue a day depending on the market, before the Saudi fix. The spec notes several markets at 2 to 5 bookings a day. The share of zero-booking days per market should be checked before modelling.

**7. Why are Account and Campaign Unspecified in Adobe? (parked)**

This is not resolved and no longer blocks the work. What is established: the unclassified tracking IDs are well formed and match the regex. What was observed on a small sample: the classified IDs came from older clicks (6 June, 6 September) and the unclassified ones from 29 September onward, which would point to a processing job that stopped. Marouane's view is that the parsing is a calculated field in Adobe, so click date cannot be the cause. Both readings are untested.

## Next steps

The first four steps need no new pull and should take under an hour. Modelling comes last, after the checks.

- [ ] Apply the `ACCOUNT_RE` fix and re-run the third cell. Confirm the Saudi Arabia non-brand total rises and Other falls by about 411,000.
- [ ] Run the Germany September check and record the ratio to the Floodlight figure.
- [ ] List the unparsed tracking IDs and decide whether any rule needs extending.
- [ ] Remove the debug `print`, restore `timeout=60` and the CA bundle in `post_report`, and clear the notebook outputs.
- [ ] Test segment coverage: pull one day with a wider segment and list revenue by account for the six markets. If accounts are missing, widen the segment and re-pull into a new raw folder.
- [ ] Save the quick segment as a normal segment and put its ID in the config.
- [ ] Confirm the currency of SalesIncYQ, the eVar84 allocation and expiry, and the market definition used on the SA360 side.
- [ ] Check the share of zero-booking days per market for Non-brand.
- [ ] Run the Causal Impact models on the Adobe file, side by side with the Floodlight versions, starting with Germany and Canada.
- [ ] Optional: ask the Adobe admin why Account and Campaign are Unspecified, with the evidence in this document.

Switch dates for the markets other than Germany (30 July 2026) are not recorded here and are needed for the models.

## Reference

**Adobe identifiers**

| Item | Value |
| --- | --- |
| Global company ID | `qatara1` |
| Report suite | `qatarairways-prod` (Qatar Airways, Prod) |
| API endpoint | `https://analytics.adobe.io/api/qatara1/reports` |
| Dimension | `variables/evar84`, SA360\_TrackingID (v84) |
| Revenue | `metrics/event17`, SalesIncYQ |
| Flight search visits | `metrics/event14`, Flight Search Visits (IBE Visits) |
| Bookings | `metrics/event27`, a raw count |
| Segment, BUGs Excluded | `s1952_619e30e8d9c5253ca2de761e` |
| Segment, market filter (quick segment) | `s1952_6ac61c1d36a75d75a5b13658` |
| Markets | DE Germany, CA Canada, SA Saudi Arabia, PK Pakistan, MY Malaysia, SG Singapore |

**Files**

| File | Role |
| --- | --- |
| `aa_v84_daily_pull.ipynb` | The working notebook |
| `aa_breakdown_16_2.ipynb` | The original multi-level notebook, superseded for this task |
| `aa_v84_raw/` | Daily raw files and `totals.csv` |
| `aa_daily_market_group.csv` | Final table for the models |
| Export spec | The text that defines what the models need |
| "Adobe Analytics SEM Reporting" email thread, May 2025 | History of the Adobe-side regex |

**Getting a token**

1. Open the project with the Adobe Analytics API in the [Adobe Developer Console](https://developer.adobe.com/console).
2. Open the OAuth Server-to-Server credential and click **Generate access token**.
3. Paste the token into `ACCESS_TOKEN` and the Client ID from the same page into `CLIENT_ID`.

The token lasts about 24 hours and there is no refresh token. A 403 means the credential is not on a product profile with access to the report suite. Details are in Adobe's [Server-to-Server guide](https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/implementation).

**History of the Adobe-side regex**

| Date | Event |
| --- | --- |
| 13 May 2025 | Regex updated to allow an empty gclid: `^([^\|]+)\\|(.+)\\|([^\|]+)\\|([^\|]+)\\|([^\|]*)\\|([^\|]+)$` |
| 13 May 2025 | Qatar Airways reported the account name captured with the campaign name when the gclid was blank |
| 9 May 2025 | New regex confirmed working |
| 7 May 2025 | New regex sent to cover the old and new naming conventions |

The notebook uses a more tolerant version, which also accepts an empty ad group, keyword or gclsrc.

**People in the May 2025 thread**

- Suhail Rafique Parkar, Qatar Airways: applied the regex in Adobe.
- Amad Uddin Ahmed, Qatar Airways: organised the work and reported the blank gclid issue.
- Sanjoy Kumar Banerjee, Qatar Airways: in copy.

**Adobe documentation consulted**

- [Classification Rule Builder overview (legacy)](https://experienceleague.adobe.com/en/docs/analytics/components/classifications/classifications-rulebuilder/classification-rule-builder)
- [Classification rule definitions (legacy)](https://experienceleague.adobe.com/en/docs/analytics/components/classifications/classifications-rulebuilder/classification-rule-definitions)
- [Classification sets rules](https://experienceleague.adobe.com/en/docs/analytics/components/classifications/sets/set/rules)
