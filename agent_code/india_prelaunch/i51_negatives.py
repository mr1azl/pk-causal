"""I5b: negative keywords at campaign, ad group and shared set level, and for
every destination campaign whether a reverse direction negative exists."""
import json, sys, collections
from lib_sa360 import stream, RAW, IN_ACCOUNT

PULLS = [
    ("i5_neg_campaign.jsonl",
     "SELECT campaign.id, campaign.name, campaign_criterion.criterion_id, "
     "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, "
     "campaign_criterion.negative, campaign_criterion.type "
     "FROM campaign_criterion WHERE campaign.status = 'ENABLED' "
     "AND campaign_criterion.negative = true"),
    ("i5_neg_adgroup.jsonl",
     "SELECT campaign.id, campaign.name, ad_group.id, "
     "ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
     "ad_group_criterion.keyword.match_type, ad_group_criterion.negative "
     "FROM keyword_view WHERE campaign.status = 'ENABLED' "
     "AND ad_group_criterion.negative = true"),
]
for fname, q in PULLS:
    path = RAW / fname
    if path.exists():
        print(f"   skip {path.name} ({sum(1 for _ in open(path, encoding='utf-8')):,d} rows)")
        continue
    c, rows = stream(IN_ACCOUNT, q)
    if c != 200:
        print(f"   {fname} FAILED: {c} {rows}"); continue
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows")

# shared negative keyword sets
for res, fname in (("shared_criterion", "i5_neg_shared.jsonl"),):
    path = RAW / fname
    if path.exists():
        print(f"   skip {path.name}"); continue
    c, rows = stream(IN_ACCOUNT,
        "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status, "
        "shared_criterion.criterion_id, shared_criterion.keyword.text, "
        "shared_criterion.keyword.match_type, shared_criterion.type "
        "FROM shared_criterion")
    if c != 200:
        print(f"   {fname} FAILED: {c} {rows}"); continue
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows")

# which shared sets are attached to which campaigns
path = RAW / "i5_campaign_shared_sets.jsonl"
if not path.exists():
    c, rows = stream(IN_ACCOUNT,
        "SELECT campaign.id, campaign.name, campaign_shared_set.shared_set, "
        "campaign_shared_set.status FROM campaign_shared_set "
        "WHERE campaign.status = 'ENABLED'")
    if c != 200:
        print(f"   campaign_shared_set FAILED: {c} {rows}")
    else:
        with open(path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, separators=(",", ":")) + "\n")
        print(f"   {path.name}: {len(rows):,d} rows")
else:
    print(f"   skip {path.name}")
