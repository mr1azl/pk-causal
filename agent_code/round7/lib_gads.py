"""Google Ads API client for the PK re-analysis.

Why this exists: SA360's Reporting API has no change_event, no search_term_view
and no shared_set, so rounds 3 to 6 inferred dates from daily series and could
not read shared negative lists at all. The same account ids work against the
Google Ads API, which has all three.

Credentials are read through lib_sa360._env, which checks the environment then
walks parent directories for a .env. No value is ever printed, logged or written.
"""
import json, datetime, time, urllib.request, urllib.error
from urllib.parse import urlencode
from pathlib import Path
from lib_sa360 import _env

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN = ROOT / "data/raw", ROOT / "data/clean"
RAW.mkdir(parents=True, exist_ok=True); CLEAN.mkdir(parents=True, exist_ok=True)

# v22 to v25 are live as of 8 Oct 2026. v21 and below are sunset and return
# Google's HTML 404 page for every path, which looks exactly like a credential
# failure and is not. Probe the range if this ever stops working.
VERSION = "v25"
BASE = f"https://googleads.googleapis.com/{VERSION}"

ACCOUNTS = {
    "pk_nonbrand": "4851538229",      # Google-GCCLI-PK-EN
    "pk_brand":    "1423602235",      # Google-GCCLI-PK-EN-Brand
    "sa":          "7879272266",
    "ca":          "4096344384",
    "my":          "9880134221",
    "in_nonbrand": "4034062923",
}

_tok = {}


def token():
    now = time.time()
    if _tok.get("exp", 0) > now:
        return _tok["v"]
    body = urlencode({"client_id": _env("GOOGLE_ADS_CLIENT_ID"),
                      "client_secret": _env("GOOGLE_ADS_CLIENT_SECRET"),
                      "refresh_token": _env("GOOGLE_ADS_REFRESH_TOKEN"),
                      "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen(
            urllib.request.Request("https://oauth2.googleapis.com/token", data=body),
            timeout=60) as r:
        d = json.loads(r.read().decode())
    _tok["v"] = d["access_token"]; _tok["exp"] = now + d.get("expires_in", 3600) - 60
    return _tok["v"]


def _headers():
    return {"Authorization": "Bearer " + token(),
            "developer-token": _env("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "login-customer-id": "".join(c for c in _env("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
                                         if c.isdigit()),
            "Content-Type": "application/json"}


def _err(body):
    """Google Ads errors nest three deep. Return the human message or the raw body."""
    try:
        e = json.loads(body)["error"]
        d = e.get("details", [{}])[0].get("errors", [{}])[0]
        return d.get("message") or e.get("message") or body[:300]
    except Exception:
        return body.strip()[:300]


def search(customer_id, query, page_limit=None):
    """googleAds:search with cursor paging.

    pageSize is rejected outright ("Search Responses will have fixed page size
    of 10000 rows"), so paging is by nextPageToken only and LIMIT goes in the
    query. Returns (rows, None) or (None, message).
    """
    url = f"{BASE}/customers/{customer_id}/googleAds:search"
    out, tokn, pages = [], None, 0
    while True:
        payload = {"query": query}
        if tokn:
            payload["pageToken"] = tokn
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {_err(e.read().decode())}"
        except Exception as e:
            return None, f"transport: {e}"
        out += d.get("results", [])
        pages += 1
        tokn = d.get("nextPageToken")
        if not tokn or (page_limit and pages >= page_limit):
            return out, None


def fields(where, select="name, selectable, filterable, data_type, category"):
    """GoogleAdsFieldService, the equivalent of searchAds360Fields:search.
    Zero rows back means the resource does not exist in this API."""
    url = f"{BASE}/googleAdsFields:search"
    req = urllib.request.Request(
        url, data=json.dumps({"query": f"SELECT {select} WHERE {where}"}).encode(),
        headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode()).get("results", []), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {_err(e.read().decode())}"


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    return len(rows)


def chunks(d1, d2, days=30):
    a = datetime.date.fromisoformat(d1); b = datetime.date.fromisoformat(d2)
    while a <= b:
        c = min(a + datetime.timedelta(days=days - 1), b)
        yield a.isoformat(), c.isoformat()
        a = c + datetime.timedelta(days=1)


# the four periods used throughout rounds 3 to 6, kept identical for comparability
PERIODS = [("13 Jun-19 Aug", "2026-06-13", "2026-08-19"),
           ("20 Aug-1 Sep", "2026-08-20", "2026-09-01"),
           ("2-19 Sep", "2026-09-02", "2026-09-19"),
           ("20 Sep-5 Oct", "2026-09-20", "2026-10-05")]
