"""Rebuild the calibration CSV files in this folder from their sources.

Run from anywhere:

    python data/fetch_data.py

It needs an internet connection and only the standard library plus numpy
and pandas. Each function below writes one CSV next to this script. The
README in this folder says what each file measures and where it comes from.

Sources
- CSO PxStat (Central Statistics Office, Ireland), JSON-stat 2.0 API:
  https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<TABLE>/JSON-stat/2.0/en
- Penn World Table 11.0 (Groningen Growth and Development Centre), Stata file
  linked from https://www.rug.nl/ggdc/productivity/pwt/
- Irish Statute Book (state pension rates and pension age), see PENSION below.
"""

import io
import itertools
import json
import re
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CSO_URL = ("https://ws.cso.ie/public/api.restful/"
           "PxStat.Data.Cube_API.ReadDataset/{}/JSON-stat/2.0/en")
PWT_URL = "https://dataverse.nl/api/access/datafile/554030"  # PWT 11.0, Stata
FIRST_YEAR = 2000


# --------------------------------------------------------------------------
# Download helpers
# --------------------------------------------------------------------------
def download(url, timeout=300):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def cso_table(code):
    """Return a CSO PxStat table as a long DataFrame.

    One column per dimension holding its codes (suffix '_code') and one
    holding its labels, plus 'value'.
    """
    d = json.loads(download(CSO_URL.format(code)))
    dims = d["id"]
    cats = []
    for k in dims:
        c = d["dimension"][k]["category"]
        labels = c.get("label", {})
        cats.append([(i, labels.get(i, i)) for i in c["index"]])
    values = d["value"]
    rows = []
    for n, combo in enumerate(itertools.product(*cats)):
        v = values[n] if isinstance(values, list) else values.get(str(n))
        rows.append([c[0] for c in combo] + [c[1] for c in combo] + [v])
    names = [d["dimension"][k]["label"] for k in dims]
    cols = [nm + "_code" for nm in names] + names + ["value"]
    df = pd.DataFrame(rows, columns=cols)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def write(df, name):
    path = HERE / name
    df.to_csv(path, index=False)
    print(f"wrote {name:32s} {len(df):4d} rows")


# --------------------------------------------------------------------------
# National accounts: GDP, GNI and GNI* (CSO NA001)
# --------------------------------------------------------------------------
def national_income():
    df = cso_table("NA001")
    item = {"01": "gdp_eur_m", "06": "gni_eur_m", "10": "gni_star_eur_m"}
    df = df[df["Item_code"].isin(item)]
    out = (df.pivot(index="Year", columns="Item_code", values="value")
             .rename(columns=item)[list(item.values())])
    out = out.astype(int)
    out.index = out.index.astype(int)
    out.index.name = "year"
    out["gni_star_over_gdp"] = (out["gni_star_eur_m"] / out["gdp_eur_m"]).round(3)
    return out.reset_index()


# --------------------------------------------------------------------------
# Capital stock (CSO CSA02) relative to GDP and GNI*
# --------------------------------------------------------------------------
def capital_output_cso(income):
    df = cso_table("CSA02")
    df = df[(df["Statistic_code"] == "CSA02C01")                 # net, current prices
            & (df["Industry Sector NACE Rev 2_code"] == "-")]     # all sectors
    asset = {"All fixed assets": "net_capital_stock_eur_m",
             "Dwellings, excluding land": "of_which_dwellings_eur_m",
             "Intangible fixed assets including computer software and "
             "research and development": "of_which_intangibles_eur_m",
             "Transport equipment": "of_which_transport_equipment_eur_m"}
    df = df[df["Fixed Asset"].isin(asset)]
    k = (df.pivot(index="Year", columns="Fixed Asset", values="value")
           .rename(columns=asset)[list(asset.values())] / 1000.0)   # EUR thousand -> million
    k.index = k.index.astype(int)
    k.index.name = "year"
    k = k.round(0).astype(int).reset_index()
    out = k.merge(income[["year", "gdp_eur_m", "gni_star_eur_m"]], on="year")
    out = out[out["year"] >= FIRST_YEAR]
    out["k_over_gdp"] = (out["net_capital_stock_eur_m"] / out["gdp_eur_m"]).round(3)
    out["k_over_gni_star"] = (out["net_capital_stock_eur_m"]
                              / out["gni_star_eur_m"]).round(3)
    return out


# --------------------------------------------------------------------------
# Penn World Table 11.0: K/Y, labour share, depreciation for Ireland
# --------------------------------------------------------------------------
def pwt_ireland():
    pwt = pd.read_stata(io.BytesIO(download(PWT_URL)))
    ie = pwt[(pwt["countrycode"] == "IRL") & (pwt["year"] >= FIRST_YEAR)].copy()
    ie["year"] = ie["year"].astype(int)
    return ie.sort_values("year")


def capital_output_pwt(ie):
    out = ie[["year", "rnna", "rgdpna"]].copy()
    out["k_over_y"] = (out["rnna"] / out["rgdpna"]).round(3)
    out["rnna"] = out["rnna"].round(0).astype(int)
    out["rgdpna"] = out["rgdpna"].round(0).astype(int)
    return out.rename(columns={"rnna": "rnna_usd2021_m",
                               "rgdpna": "rgdpna_usd2021_m"})


def capital_share_pwt(ie):
    out = ie[["year", "labsh"]].copy()
    out["alpha"] = 1.0 - out["labsh"]
    return out.round(4)


def depreciation_pwt(ie):
    return ie[["year", "delta"]].round(4)


# --------------------------------------------------------------------------
# Population by single year of age, latest year (CSO PEA11)
# --------------------------------------------------------------------------
def population_by_age():
    df = cso_table("PEA11")
    df = df[df["Sex_code"] == "-"]                     # both sexes
    year = df["Year"].astype(int).max()
    df = df[df["Year"].astype(int) == year]
    total = df.loc[df["Single Year of Age_code"] == "-", "value"].item()
    df = df[df["Single Year of Age_code"] != "-"].copy()
    special = {"200": 0, "646": 99}                    # 'Under 1 year', '99 years and over'
    df["age"] = [special.get(c, c) for c in df["Single Year of Age_code"]]
    out = pd.DataFrame({"year": year, "age": df["age"].astype(int),
                        "age_label": df["Single Year of Age"],
                        "persons": df["value"].astype(int)})
    out = out.sort_values("age").reset_index(drop=True)
    assert out["persons"].sum() == total, "ages do not add to the CSO total"
    return out


# --------------------------------------------------------------------------
# Projected dependency ratios, Population and Labour Force Projections
# 2023-2057 (CSO PEC22, released 16 July 2024)
# --------------------------------------------------------------------------
def dependency_projections():
    df = cso_table("PEC22")
    ratio = {"02": "old", "01": "young", "-": "total"}
    scen = {"Method - M1": "M1", "Method - M2": "M2", "Method - M3": "M3"}
    out = pd.DataFrame({
        "year": df["Year"].astype(int),
        "scenario": df["Criteria for Projection"].map(scen),
        "ratio": df["Dependents Status_code"].map(ratio),
        "value_pct": df["value"],
    })
    order = {"old": 0, "young": 1, "total": 2}
    out = out.sort_values(["ratio", "scenario", "year"],
                          key=lambda s: s.map(order) if s.name == "ratio" else s)
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------
# Pension parameters and average weekly earnings
# --------------------------------------------------------------------------
# Hand-entered from the Irish Statute Book, read 4 November 2026.
# State Pension (Contributory), maximum personal weekly rate at age 66
# ("Age referenced rate for age 66 years", Schedule 2 Part 1 item 3(a)(i)
# of the Social Welfare Consolidation Act 2005 as substituted each year).
PENSION = {
    2025: (289.30, "https://www.irishstatutebook.ie/2024/en/act/pub/0036/sched1.html"),
    2026: (299.30, "https://www.irishstatutebook.ie/eli/2025/act/19/schedule/1/enacted/en/html"),
}
# Pensionable age: "'pensionable age' means the age of 66 years",
# Social Welfare Consolidation Act 2005, s. 2 (revised), read 4 November 2026:
PENSION_AGE = (66, "https://revisedacts.lawreform.ie/eli/2005/act/26/section/2/revised/en/html")


def check_pension_constants():
    """Re-read the statute pages and warn if a rate no longer matches."""
    pat = re.compile(r"Age referenced rate for age 66 years ([0-9]+\.[0-9]{2})")
    for year, (rate, url) in PENSION.items():
        try:
            text = re.sub(r"<[^>]+>", " ", download(url, 60).decode("utf-8", "replace"))
            m = pat.search(re.sub(r"\s+", " ", text))
            found = float(m.group(1)) if m else None
        except Exception as e:                       # offline, page moved, ...
            print(f"  could not check {year} pension rate ({e})")
            continue
        flag = "ok" if found == rate else "CHECK BY HAND"
        print(f"  pension {year}: constant {rate}, page {found}  {flag}")


def pension_parameters():
    df = cso_table("EHQ53")
    df = df[(df["Statistic_code"] == "EHQ53C02")                     # avg weekly earnings
            & (df["Type of Employee_code"] == "-")                    # all employees
            & (df["NACE Rev 2.1 Economic Sector_code"] == "ZZ210218")]  # all sectors B-T
    q = df.set_index("Quarter")["value"]
    awe_2025 = q[[f"2025Q{i}" for i in range(1, 5)]].mean()
    q2026 = [k for k in q.index if k.startswith("2026") and not np.isnan(q[k])]
    awe_2026 = q[q2026].mean()
    ehq = CSO_URL.format("EHQ53")
    rows = [
        ("state_pension_contributory_max_weekly", PENSION[2025][0], "EUR per week",
         "2025", "Social Welfare Act 2024, Schedule 1, Part 1, item 3(a)(i)", PENSION[2025][1]),
        ("state_pension_contributory_max_weekly", PENSION[2026][0], "EUR per week",
         "2026", "Social Welfare and Automatic Enrolment Retirement Savings System "
         "(Amendment) Act 2025, Schedule 1, Part 1, item 3(a)(i)", PENSION[2026][1]),
        ("pension_age", PENSION_AGE[0], "years", "2026",
         "Social Welfare Consolidation Act 2005, s. 2 (revised)", PENSION_AGE[1]),
        ("average_weekly_earnings", round(awe_2025, 2), "EUR per week", "2025",
         "CSO EHQ53, mean of 2025Q1-2025Q4", ehq),
        ("average_weekly_earnings", round(awe_2026, 2), "EUR per week",
         f"2026 ({q2026[0]}-{q2026[-1]})", f"CSO EHQ53, mean of {', '.join(q2026)}", ehq),
        ("replacement_rate", round(PENSION[2025][0] / awe_2025, 3), "ratio", "2025",
         "pension rate / average weekly earnings, same year", ""),
        ("replacement_rate", round(PENSION[2026][0] / awe_2026, 3), "ratio",
         f"2026 ({q2026[0]}-{q2026[-1]})",
         "pension rate / average weekly earnings (part year)", ""),
    ]
    cols = ["parameter", "value", "unit", "period", "source", "url"]
    return pd.DataFrame(rows, columns=cols, dtype=object)


# --------------------------------------------------------------------------
def main():
    income = national_income()
    write(income, "gdp_gni_star.csv")
    write(capital_output_cso(income), "capital_output_cso.csv")

    ie = pwt_ireland()
    write(capital_output_pwt(ie), "capital_output_pwt.csv")
    write(capital_share_pwt(ie), "capital_share_pwt.csv")
    write(depreciation_pwt(ie), "depreciation_pwt.csv")

    write(population_by_age(), "population_by_age.csv")
    write(dependency_projections(), "dependency_projections.csv")

    write(pension_parameters(), "pension_parameters.csv")
    check_pension_constants()


if __name__ == "__main__":
    main()
