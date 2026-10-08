"""I3c, second pass. The first pass overstated off-route traffic because it
counted a country code and a city inside that country as a mismatch
(AE against DXB, CDG against PAR, LHR against LON). Those are the same place
written at different granularity, not the bidder buying the wrong route.

This pass resolves every code to a place key first: a city resolves to its
country, a metro code resolves to its metro, and only then are the two compared.
A residual mismatch is then a genuinely different destination.
"""
import csv, json, glob, collections
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand, dest_code

# city or airport -> country, for every code that appears in the data with volume.
CITY_COUNTRY = {
    "LHR": "GB", "LGW": "GB", "LON": "GB", "MAN": "GB", "BHX": "GB", "EDI": "GB",
    "GLA": "GB", "ABZ": "GB", "NCL": "GB", "BFS": "GB", "BHD": "GB", "CWL": "GB",
    "INV": "GB", "IOM": "GB", "DUB": "IE", "ORK": "IE",
    "CDG": "FR", "ORY": "FR", "PAR": "FR", "NCE": "FR", "LYS": "FR", "MRS": "FR",
    "TLS": "FR", "BOD": "FR",
    "FRA": "DE", "MUC": "DE", "BER": "DE", "TXL": "DE", "DUS": "DE", "HAM": "DE",
    "STR": "DE", "HAJ": "DE",
    "MAD": "ES", "BCN": "ES", "AGP": "ES", "VLC": "ES", "PMI": "ES", "ALC": "ES",
    "SVQ": "ES", "IBZ": "ES", "LPA": "ES", "SDR": "ES", "LEI": "ES",
    "FCO": "IT", "MXP": "IT", "LIN": "IT", "VCE": "IT", "PSA": "IT", "NAP": "IT",
    "SUF": "IT", "AHO": "IT",
    "LIS": "PT", "OPO": "PT", "AMS": "NL", "BRU": "BE", "LUX": "LU",
    "ZRH": "CH", "GVA": "CH", "BSL": "CH", "VIE": "AT",
    "ARN": "SE", "GOT": "SE", "OSL": "NO", "BGO": "NO", "SVG": "NO", "TRD": "NO",
    "KRS": "NO", "HAU": "NO", "TOS": "NO", "LYR": "NO",
    "CPH": "DK", "AAL": "DK", "AAR": "DK", "HEL": "FI", "OUL": "FI", "RVN": "FI",
    "WAW": "PL", "KRK": "PL", "GDN": "PL", "POZ": "PL", "WRO": "PL",
    "PRG": "CZ", "BUD": "HU", "OTP": "RO", "SOF": "BG", "VAR": "BG",
    "BEG": "RS", "ZAG": "HR", "DBV": "HR", "SPU": "HR", "LJU": "SI",
    "ATH": "GR", "SKG": "GR", "JTR": "GR", "JMK": "GR", "MLA": "MT", "LCA": "CY",
    "ECN": "CY", "KEF": "IS", "RIX": "LV", "TLL": "EE", "VNO": "LT",
    "TIA": "AL", "SJJ": "BA", "SKP": "MK", "KIV": "MD", "MSQ": "BY",
    "KBP": "UA", "ODS": "UA", "SVO": "RU", "DME": "RU", "MOW": "RU", "LED": "RU",
    "IST": "TR", "SAW": "TR", "AYT": "TR", "ADA": "TR", "ADB": "TR", "ESB": "TR",
    "HTY": "TR", "TZX": "TR", "BJV": "TR", "XIR": "TR",
    "TBS": "GE", "EVN": "AM", "GYD": "AZ", "BAK": "AZ",
    "DXB": "AE", "AUH": "AE", "SHJ": "AE", "RKT": "AE", "DWC": "AE", "AAN": "AE",
    "RUH": "SA", "JED": "SA", "DMM": "SA", "MED": "SA", "TUU": "SA", "ELQ": "SA",
    "GIZ": "SA", "YNB": "SA", "HAS": "SA", "RSI": "SA", "TIF": "SA", "ULH": "SA",
    "AHB": "SA", "EAM": "SA", "HOF": "SA", "SHW": "SA", "AQI": "SA", "ZUL": "SA",
    "KWI": "KW", "DOH": "QA", "BAH": "BH", "MCT": "OM", "SLL": "OM", "OHS": "OM",
    "KHS": "OM", "AMM": "JO", "AQJ": "JO", "BEY": "LB",
    "BGW": "IQ", "BSR": "IQ", "EBL": "IQ", "ISU": "IQ", "NJF": "IQ", "XNH": "IQ",
    "IKA": "IR", "THR": "IR", "MHD": "IR", "SYZ": "IR", "IFN": "IR", "TBZ": "IR",
    "TLV": "IL", "SAH": "YE", "ADE": "YE", "DAM": "SY", "ALP": "SY",
    "JNB": "ZA", "CPT": "ZA", "DUR": "ZA", "PZB": "ZA", "PLZ": "ZA",
    "NBO": "KE", "MBA": "KE", "DAR": "TZ", "JRO": "TZ", "ZNZ": "TZ",
    "LUN": "ZM", "NUM": "ZM", "ZMB": "ZM", "MPM": "MZ", "BEW": "MZ",
    "LOS": "NG", "ABV": "NG", "KAN": "NG", "PHC": "NG", "ABJ": "CI", "ACC": "GH",
    "ADD": "ET", "CAI": "EG", "HBE": "EG", "SSH": "EG", "ALG": "DZ",
    "CMN": "MA", "RAK": "MA", "RBA": "MA", "TUN": "TN", "KRT": "SD", "MGQ": "SO",
    "JIB": "DJ", "ASM": "ER", "KGL": "RW", "EBB": "UG", "HRE": "ZW", "GBE": "BW",
    "WDH": "NA", "MSU": "LS", "SEZ": "SC", "MRU": "MU", "LAD": "AO", "FIH": "CD",
    "ROB": "LR", "TNR": "MG", "BLZ": "MW", "LLW": "MW", "DLA": "CM", "LBV": "GA",
    "DKR": "SN",
    "AKL": "NZ", "CHC": "NZ", "WLG": "NZ", "ZQN": "NZ",
    "SYD": "AU", "MEL": "AU", "BNE": "AU", "PER": "AU", "ADL": "AU", "CBR": "AU",
    "DRW": "AU", "OOL": "AU",
    "YYZ": "CA", "YTO": "CA", "YUL": "CA", "YVR": "CA", "YYC": "CA", "YHZ": "CA",
    "YOW": "CA", "YTZ": "CA", "YQY": "CA", "YWG": "CA", "YEG": "CA", "YSJ": "CA",
    "YYT": "CA", "YYJ": "CA", "YQG": "CA", "YQM": "CA", "YFC": "CA", "YQB": "CA",
    "YDF": "CA", "YYG": "CA", "YLW": "CA",
    "DEL": "IN", "BOM": "IN", "BLR": "IN", "MAA": "IN", "HYD": "IN", "CCU": "IN",
    "AMD": "IN", "COK": "IN", "TRV": "IN", "GOI": "IN", "ATQ": "IN", "NAG": "IN",
    "CCJ": "IN", "PNQ": "IN", "LKO": "IN", "IXC": "IN", "JAI": "IN", "VTZ": "IN",
    "IXE": "IN", "TRZ": "IN", "IXM": "IN", "BBI": "IN", "GAU": "IN", "VNS": "IN",
    "SXR": "IN", "IXB": "IN", "RPR": "IN", "IDR": "IN", "BHO": "IN", "PAT": "IN",
    "ISB": "PK", "KHI": "PK", "LHE": "PK", "DAC": "BD", "CMB": "LK", "KTM": "NP",
    "MLE": "MV", "BKK": "TH", "HKT": "TH", "SIN": "SG", "KUL": "MY", "PEN": "MY",
    "CGK": "ID", "DPS": "ID", "SGN": "VN", "HAN": "VN", "DAD": "VN",
    "MNL": "PH", "CEB": "PH", "CRK": "PH", "DVO": "PH", "RGN": "MM", "PNH": "KH",
    "PEK": "CN", "PVG": "CN", "CAN": "CN", "HKG": "HK", "TPE": "TW", "ICN": "KR",
    "HND": "JP", "NRT": "JP", "KIX": "JP", "TYO": "JP", "ULN": "MN",
    "ALA": "KZ", "NQZ": "KZ", "TAS": "UZ", "FRU": "KG", "DYU": "TJ", "ASB": "TM",
    "GRU": "BR", "GIG": "BR", "BSB": "BR", "CNF": "BR", "POA": "BR", "REC": "BR",
    "FOR": "BR", "SDU": "BR", "IOS": "BR", "VIX": "BR", "CWB": "BR",
    "CCS": "VE", "BOG": "CO", "SCL": "CL", "LIM": "PE", "MVD": "UY", "ASU": "PY",
    "EZE": "AR", "MEX": "MX", "GDL": "MX", "CUN": "MX", "MTY": "MX", "SJD": "MX",
    "SJO": "CR", "PTY": "PA", "UIO": "EC", "GYE": "EC",
}
# metropolitan area codes seen in the searched field, which the first pass
# counted as mismatches against the airport or country code in the campaign
CITY_COUNTRY.update({
    "MIL": "IT", "ROM": "IT", "RIO": "BR", "SAO": "BR", "BUH": "RO", "STO": "SE",
    "OLA": "NO", "OSL": "NO", "CPH": "DK", "BJS": "CN", "SEL": "KR", "TYO": "JP",
    "NYC": "US", "CHI": "US", "WAS": "US", "QLA": "US", "YMQ": "CA", "YTO": "CA",
    "BER": "DE", "MOW": "RU", "LON": "GB", "PAR": "FR", "MXP": "IT", "FCO": "IT",
    "TCI": "ES", "BUE": "AR", "JKT": "ID", "OSA": "JP",
})

# everything else in IN_NORTH_AMERICA that is a US airport resolves to US
from lib_sa360 import IN_NORTH_AMERICA
for c in IN_NORTH_AMERICA:
    if c not in CITY_COUNTRY and c not in ("US", "CA"):
        CITY_COUNTRY.setdefault(c, "US")


def place(code):
    c = (code or "").upper()
    return CITY_COUNTRY.get(c, c)


def same_place(a, b):
    return place(a) == place(b)


rows = [json.loads(l) for p in sorted(glob.glob(str(RAW / "i3_vbb_*.jsonl")))
        for l in open(p, encoding="utf-8")]
rows = [r for r in rows if is_non_brand(r["campaign"]) and r["dest"]]

G = collections.defaultdict(lambda: collections.Counter())
pair = collections.Counter()
for r in rows:
    cd = dest_code(r["campaign"])
    if not cd:
        continue
    g = in_dest_group(r["campaign"]); sd = r["dest"].upper()
    a = G[g]; a["n"] += 1; a["val"] += r["rev"]
    if same_place(cd, sd):
        a["match"] += 1; a["match_val"] += r["rev"]
    else:
        a["miss"] += 1; a["miss_val"] += r["rev"]
        pair[(cd, sd)] += 1
    if place(sd) == "IN":
        a["reverse"] += 1; a["reverse_val"] += r["rev"]

out = []
print("=== VBB search value against the campaign's destination, country resolved ===")
print(f"{'group':<28}{'rows':>9}{'same place':>12}{'different':>11}"
      f"{'value off route':>17}{'reverse dir':>13}")
print("-" * 92)
for g, a in sorted(G.items(), key=lambda kv: -kv[1]["n"]):
    print(f"{g:<28}{a['n']:>9,d}{a['match']/a['n']*100:>11.1f}%{a['miss']/a['n']*100:>10.1f}%"
          f"{a['miss_val']/a['val']*100:>16.1f}%{a['reverse']/a['n']*100:>12.1f}%")
    out.append({"dest_group": g, "rows": a["n"],
                "same_place_pct": round(a["match"] / a["n"] * 100, 2),
                "different_place_pct": round(a["miss"] / a["n"] * 100, 2),
                "value_total": round(a["val"], 2),
                "value_off_route": round(a["miss_val"], 2),
                "value_off_route_pct": round(a["miss_val"] / a["val"] * 100, 2) if a["val"] else "",
                "reverse_direction_pct": round(a["reverse"] / a["n"] * 100, 2),
                "reverse_direction_value": round(a["reverse_val"], 2)})

with open(CLEAN / "i3_route_match_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print("\ntop 25 genuine destination mismatches, country resolved")
print(f"{'campaign':<12}{'searched':<12}{'rows':>8}")
print("-" * 32)
for (cd, sd), n in pair.most_common(25):
    print(f"{cd:<12}{sd:<12}{n:>8,d}")
with open(CLEAN / "i3_route_mismatch_pairs.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["campaign_dest", "searched_dest", "campaign_place",
                                    "searched_place", "rows"])
    for (cd, sd), n in pair.most_common(500):
        w.writerow([cd, sd, place(cd), place(sd), n])
print("\nwrote i3_route_match_by_group.csv and i3_route_mismatch_pairs.csv")
