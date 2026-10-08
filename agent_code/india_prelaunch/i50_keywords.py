"""I5a: keyword inventory for India non-brand. Text, match type, status, by
campaign, plus broad match share of clicks by destination group.
Resumable: writes one JSONL per chunk."""
import json, sys, collections
from lib_sa360 import stream, RAW, IN_ACCOUNT

path = RAW / "i5_keywords.jsonl"
if not path.exists():
    c, rows = stream(IN_ACCOUNT,
        "SELECT campaign.id, campaign.name, ad_group.id, "
        "ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
        "ad_group_criterion.keyword.match_type, ad_group_criterion.status, "
        "ad_group_criterion.negative "
        "FROM keyword_view WHERE campaign.status = 'ENABLED' "
        "AND ad_group.status = 'ENABLED'")
    if c != 200:
        sys.exit(f"keyword_view failed: {c} {rows}")
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows")
else:
    print(f"   skip {path.name} ({sum(1 for _ in open(path, encoding='utf-8')):,d} rows)")
