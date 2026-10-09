"""SA360 Reporting API access, round 5. Market is Saudi Arabia, account 7879272266.

Aucun identifiant n'est ecrit ici. Les valeurs sont lues dans l'environnement,
sinon dans le .env local (Documents/cc/.env), jamais journalisees ni affichees.

Usage: import depuis scripts/, par exemple
    from lib_sa360 import stream, ACCOUNTS, MCC
"""
import json, os, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

MCC = "1144701035"            # Qatar Airways, compte manager
SA = "7879272266"   # Google-GCCLI-SA-EN-2
ACCOUNTS = {           # PK, kept for reference
    "pk_nonbrand": {"id": "4851538229", "name": "Google-GCCLI-PK-EN"},
    "pk_brand":    {"id": "1423602235", "name": "Google-GCCLI-PK-EN-Brand"},
}

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN, OUT = ROOT / "data/raw", ROOT / "data/clean", ROOT / "outputs"


def _env(name):
    if os.environ.get(name):
        return os.environ[name]
    for d in (ROOT, *ROOT.parents):
        f = d / ".env"
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            n, _, v = line.partition("=")
            if n.strip().removeprefix("export ").strip() == name:
                return v.strip().strip("\"'")
    raise SystemExit(f"variable {name} introuvable (ni environnement, ni .env)")


_cache = {"token": None, "exp": 0.0}


def token():
    """Access token, mis en cache en memoire pour sa duree de vie. Jamais sur disque."""
    if _cache["token"] and time.time() < _cache["exp"]:
        return _cache["token"]
    body = urllib.parse.urlencode({
        "client_id": _env("CLIENT_ID"), "client_secret": _env("CLIENT_SECRET"),
        "refresh_token": _env("REFRESH_TOKEN"), "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        # On lit le code et le champ error, jamais le corps de la requete envoyee.
        err = json.loads(e.read() or b"{}")
        raise SystemExit(
            f"echec du refresh token ({e.code} {err.get('error')}). "
            "Si c'est invalid_grant, il faut relancer le consentement et remplacer REFRESH_TOKEN."
        )
    _cache["token"] = d["access_token"]
    _cache["exp"] = time.time() + int(d.get("expires_in", 3600)) - 60
    return _cache["token"]


def _post(url, payload):
    h = {"Authorization": "Bearer " + token(), "Content-Type": "application/json",
         "login-customer-id": MCC}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=h)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return 200, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        # searchStream renvoie ses erreurs dans un tableau JSON, pas un objet.
        try:
            d = json.loads(body)
            if isinstance(d, list):
                d = d[0]
            errs = d["error"]["details"][0]["errors"]
            msg = "; ".join(
                f"{list(x.get('errorCode', {}).values())[0]}: {x.get('message', '')}"
                for x in errs)
        except Exception:
            msg = body[:400]
        return e.code, msg


def stream(customer_id, query):
    """searchStream. Retourne (200, [lignes]) ou (code, message d'erreur)."""
    url = f"https://searchads360.googleapis.com/v0/customers/{customer_id}/searchAds360:searchStream"
    code, data = _post(url, {"query": query})
    if code != 200:
        return code, data
    return 200, [row for chunk in data for row in chunk.get("results", [])]


def fields(where, select="name, category, selectable, filterable"):
    """Service de champs, pour verifier un nom avant de l'utiliser (regle 0.6)."""
    url = "https://searchads360.googleapis.com/v0/searchAds360Fields:search"
    code, data = _post(url, {"query": f"SELECT {select} WHERE {where}", "pageSize": 1000})
    if code != 200:
        return code, data
    return 200, data.get("results", [])


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def get(url):
    """GET authentifie, pour les endpoints REST hors searchStream."""
    h = {"Authorization": "Bearer " + token(), "login-customer-id": MCC}
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return 200, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


def chunks(d1, d2, days=31):
    """Split a date range into chunks so a single query does not time out."""
    import datetime
    a = datetime.date.fromisoformat(d1); b = datetime.date.fromisoformat(d2)
    while a <= b:
        c = min(a + datetime.timedelta(days=days - 1), b)
        yield a.isoformat(), c.isoformat()
        a = c + datetime.timedelta(days=1)


def is_non_brand(name):
    """PK non-brand: no |Brand| segment, not Performance Max."""
    n = (name or "")
    low = n.lower()
    return ("|brand|" not in low) and ("perf_max" not in low) and ("pmax" not in low)


import re as _re

LANGS = {"EN", "UR", "AR", "FR", "DE", "ES", "IT", "ZH", "JA", "MS", "ID", "TR", "PT", "RU"}


def dest_code(name):
    """Destination code from either naming convention used in the PK account.

    2026 pipe form   Google|PK|Dest|Country|XXX|GB|EN|MOD   -> field 6
    2025 legacy form _PK-Country-XXX-AU-EN_phrase           -> token before the language code
                     _PK-O&D-LHE-LHR-EN_exact               -> destination, not origin
    Returns "" when there is no destination, e.g. _PK-Generic-RMKT_Exact.
    """
    n = (name or "").strip()
    if "|" in n:
        p = n.split("|")
        return p[5].strip().upper() if len(p) > 5 else ""
    core = n.split("_")[1] if n.startswith("_") and "_" in n[1:] else n.strip("_")
    t = [x for x in core.split("-") if x]
    if len(t) >= 2 and t[-1].upper() in LANGS:
        c = t[-2].upper()
        if _re.fullmatch(r"[A-Z]{2,3}", c):
            return c
    return ""


# UK+IE exactly as the brief defines it. Other UK and IE codes found in the data
# (LON, GLA, BHD, NCL, ABZ, ORK) are listed separately and logged, not folded in.
UKIE = {"GB", "IE", "LHR", "LGW", "MAN", "BHX", "EDI", "DUB"}
UKIE_EXTRA = {"LON", "GLA", "BHD", "NCL", "ABZ", "ORK"}

NORTH_AMERICA = {
    "US", "CA", "NYC", "CHI", "YTO",
    "JFK", "EWR", "LGA", "IAD", "DCA", "BWI", "BOS", "PHL", "ATL", "MIA", "MCO", "TPA", "JAX",
    "ORD", "DTW", "MSP", "STL", "MCI", "CMH", "CLE", "PIT", "BUF", "MEM", "BHM", "LEX", "FSD",
    "DFW", "IAH", "AUS", "SAT", "DEN", "SLC", "PHX", "LAS", "LAX", "SFO", "SAN", "SEA", "PDX",
    "MSY", "RDU", "CLT", "YYZ", "YUL", "YVR", "YYC", "YHZ",
}
EUROPE = {   # excluding UK and IE by construction
    "FR", "DE", "ES", "IT", "NL", "BE", "CH", "AT", "SE", "NO", "DK", "FI", "PL", "PT", "GR",
    "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "LU", "LV", "LT", "EE", "MT", "IS", "CY", "RS",
    "CDG", "ORY", "PAR", "NCE", "TLS", "LYS", "MRS", "FRA", "MUC", "BER", "TXL", "DUS", "HAM",
    "MAD", "BCN", "AGP", "VLC", "PMI", "LIS", "OPO", "FCO", "MXP", "LIN", "VCE", "PSA", "NAP",
    "AMS", "BRU", "LUX", "ZRH", "GVA", "VIE", "ARN", "GOT", "OSL", "BGO", "SVG", "TRD", "CPH",
    "HEL", "OUL", "WAW", "KRK", "PRG", "BUD", "OTP", "SOF", "BEG", "ZAG", "LJU", "ATH", "JTR",
    "MLA", "LCA", "KEF", "RIX", "TLL", "VNO", "ECN",
}
OCEANIA = {"AU", "NZ", "SYD", "MEL", "BNE", "PER", "ADL", "CBR", "AKL", "CHC", "WLG", "DRW", "OOL"}


def dest_group(name):
    """UK+IE, long-haul (North America, Europe excluding UK and IE, Oceania),
    regional (everything else), or none when the name carries no destination."""
    c = dest_code(name)
    if not c:
        return "none"
    if c in UKIE:
        return "UK+IE"
    if c in UKIE_EXTRA:
        return "UK+IE (outside brief list)"
    if c in NORTH_AMERICA or c in EUROPE or c in OCEANIA:
        return "long-haul"
    return "regional"


GB_CUT_PREFIX = ("Google|PK|Dest|Country|XXX|GB|EN|", "Google|PK|O&D|Country|PK|GB|EN|")

PERIODS = [("13 Jun-19 Aug", "2026-06-13", "2026-08-19"),
           ("20 Aug-1 Sep", "2026-08-20", "2026-09-01"),
           ("2-19 Sep", "2026-09-02", "2026-09-19"),
           ("20 Sep-5 Oct", "2026-09-20", "2026-10-05")]


def segment(name):
    """UK+IE kept split into the two GB country campaigns cut on 20 Aug and the rest."""
    g = dest_group(name)
    if g == "UK+IE":
        return "GB country (cut 20 Aug)" if (name or "").startswith(GB_CUT_PREFIX) else "UK+IE rest"
    return g


SEGMENTS = ["GB country (cut 20 Aug)", "UK+IE rest", "long-haul", "regional", "none"]


SA_ACCOUNT = "7879272266"      # Google-GCCLI-SA-EN-2, the live SA market account


def sa_non_brand(name):
    """SA non-brand: no |Brand| segment, not Performance Max. Brand lives in its own account."""
    low = (name or "").lower()
    return ("|brand|" not in low) and ("perf_max" not in low) and ("pmax" not in low)
