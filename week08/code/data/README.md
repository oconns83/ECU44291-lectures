# Calibration data for Ireland

These CSV files hold the data the engine is calibrated to. They were pulled on **11 November 2026** by `fetch_data.py`, which is in this folder. To rebuild them from the sources, run this from the project folder (you need an internet connection):

```
python data/fetch_data.py
```

It uses only the standard library, numpy and pandas. If a source revises its figures, rerunning the script changes the numbers. Record in your report the date you ran it.

Any series your extension needs beyond these, you fetch yourself and document in the same way: source, table code, date pulled, and the query.

## Read this first: Irish GDP

Irish GDP is inflated by multinational companies. They book profits from intellectual property in Ireland, own leased aircraft through Irish companies, and send most of that income abroad. In 2015 alone, nominal GDP rose by 36%. The CSO publishes **modified gross national income (GNI\*)**, which removes these effects, as a better measure of the domestic economy. In 2025 GNI\* was 55% of GDP. Any ratio with GDP in it (capital-output, labour share, pension spending) looks very different depending on which denominator you use. Decide which one fits your model, and say why.

## Files

| File | What it holds |
|---|---|
| `gdp_gni_star.csv` | GDP, GNI and GNI\*, 1995-2025 |
| `capital_output_cso.csv` | CSO net capital stock relative to GDP and to GNI\*, 2000-2025 |
| `capital_output_pwt.csv` | Penn World Table capital-output ratio, 2000-2023 |
| `capital_share_pwt.csv` | Penn World Table labour share and capital share alpha, 2000-2023 |
| `depreciation_pwt.csv` | Penn World Table depreciation rate delta, 2000-2023 |
| `population_by_age.csv` | Population by single year of age, April 2026 |
| `dependency_projections.csv` | Projected dependency ratios to 2057, three migration scenarios |
| `pension_parameters.csv` | State pension rate, pension age, average weekly earnings, replacement rate |

---

### `gdp_gni_star.csv`

**Measures:** Ireland's gross domestic product, gross national income and modified gross national income, at current market prices.
**Source:** CSO, Annual National Accounts, table **NA001** (Modified Gross National Income at Current Market Prices), items 1 (GDP), 6 (GNI) and 10 (GNI\*). Table updated 2 July 2026.
**URL:** https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/NA001/JSON-stat/2.0/en
**Columns:** `year`; `gdp_eur_m`, `gni_eur_m`, `gni_star_eur_m` in euro million at current prices; `gni_star_over_gdp` is the ratio.
**Caveat:** These are nominal figures, so do not read growth rates off them without deflating. To get from GNI to GNI\*, the CSO subtracts the factor income of redomiciled companies, the depreciation on R&D service imports and trade in intellectual property, and the depreciation on aircraft leasing (NA001 items 7-9).

### `capital_output_cso.csv`

**Measures:** The net stock of fixed capital in Ireland at the end of each year, divided by GDP and by GNI\* for the same year.
**Source:** CSO, Estimates of the Capital Stock of Fixed Assets, table **CSA02**, statistic CSA02C01 (Net Capital Stock Held at End of Year at Current Prices), all NACE sectors. Table updated 10 November 2026 (this release revised the figures from 2012 on and added 2025). GDP and GNI\* come from NA001, as above.
**URL:** https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/CSA02/JSON-stat/2.0/en
**Columns:** `year`; `net_capital_stock_eur_m` (all fixed assets, euro million, current prices); three components of that total, also in euro million: `of_which_dwellings_eur_m`, `of_which_intangibles_eur_m` (software and R&D) and `of_which_transport_equipment_eur_m`; then `gdp_eur_m`, `gni_star_eur_m`, `k_over_gdp` and `k_over_gni_star` (ratios).
**Caveats:**
- The stock includes housing (dwellings) and public capital.
- The multinational distortion shows up in the stock as well as in output. Intangibles jump from about 37 billion to 293 billion euro in 2015, when intellectual property moved onshore. Transport equipment includes the aircraft owned by Irish-based leasing companies. GNI\* takes these activities out of income, but the stock in `net_capital_stock_eur_m` still contains them. So `k_over_gni_star` divides a stock that includes them by an income that excludes them. The component columns let you build your own adjusted stock if you want one. If you do, say exactly what you removed. The CSO does not publish a GNI\*-consistent capital stock.
- The stock is measured at the end of the year. Output is a flow over the year.

### `capital_output_pwt.csv`

**Measures:** Capital stock over real GDP, both at constant 2021 national prices, from the Penn World Table. Included for comparison with the CSO ratios.
**Source:** Penn World Table **11.0** (Feenstra, Inklaar and Timmer; Groningen Growth and Development Centre, published 7 October 2025), variables **`rnna`** (capital stock at constant 2021 national prices) and **`rgdpna`** (real GDP at constant 2021 national prices), country IRL.
**URL:** https://www.rug.nl/ggdc/productivity/pwt/ (Stata file: https://dataverse.nl/api/access/datafile/554030)
**Columns:** `year`; `rnna_usd2021_m`, `rgdpna_usd2021_m` (million 2021 US dollars); `k_over_y`.
**Caveats:** PWT builds its own capital stock from investment data by asset, so it does not match the CSO stock. The denominator is GDP, with all the distortion described above. The latest year is 2023. This is PWT 11.0, not 10.01. Version 11.0 replaced 10.01 and covers more recent years.

### `capital_share_pwt.csv`

**Measures:** The share of labour compensation in GDP (`labsh`), and the capital share `alpha = 1 - labsh` used in the Cobb-Douglas production function.
**Source:** Penn World Table 11.0, variable **`labsh`** (share of labour compensation in GDP at current national prices), country IRL. URL as above.
**Columns:** `year`; `labsh`; `alpha` (both fractions, 0 to 1).
**Caveat:** Ireland's measured labour share fell from about 0.45 to about 0.34 in 2015, and to 0.27-0.31 since 2021. Wages did not collapse. GDP, the denominator, now includes large multinational profits. So the implied alpha (about 0.69 in 2023) is far above the 0.3-0.4 usually used for advanced economies. Before 2015 it was roughly 0.47-0.55. Choose a period or an adjustment, and justify it.

### `depreciation_pwt.csv`

**Measures:** The average depreciation rate of the capital stock, `delta`, as a fraction of the stock per year.
**Source:** Penn World Table 11.0, variable **`delta`** (average depreciation rate of the capital stock), country IRL. URL as above.
**Columns:** `year`; `delta`.
**Caveat:** Delta roughly doubles, from about 0.04 before 2014 to about 0.075 from 2020. Software and R&D assets wear out fast, and their share of the Irish stock grew after 2015. The rate is annual, which matches the model's annual periods.

### `population_by_age.csv`

**Measures:** The population of Ireland in April 2026, both sexes, by single year of age. Use it for cohort sizes.
**Source:** CSO, Population and Migration Estimates, table **PEA11** (Population estimates from 1926), latest year in the table, both sexes. Table updated 24 August 2026.
**URL:** https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/PEA11/JSON-stat/2.0/en
**Columns:** `year`; `age` (0 = under 1 year); `age_label` (CSO's label); `persons` (number of people).
**Caveats:** The top age is **99 and over** (`age = 99`). The CSO does not publish single years beyond that. The total is 5,525,578. These are annual CSO estimates (revised after Census 2022), not a census count. PEA11 also has males and females separately if you need them.

### `dependency_projections.csv`

**Measures:** Projected dependency ratios for Ireland every five years from 2022 to 2057, under three migration scenarios. The old-age ratio is "the population aged 65 years and over expressed as a percentage of the population aged 15-64 years". The young ratio is the population aged 0-14 over the population aged 15-64. The total is the sum of the two.
**Source:** CSO, Population and Labour Force Projections 2023-2057 (released 16 July 2024), table **PEC22** (Projected Dependency Ratios from 2022). This is the most recent edition.
**URL:** https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/PEC22/JSON-stat/2.0/en ; release: https://www.cso.ie/en/releasesandpublications/ep/p-plfp/populationandlabourforceprojections2023-2057/
**Columns:** `year`; `scenario`; `ratio` (`old`, `young` or `total`); `value_pct` (percent).
**Scenarios:** All three assume net migration of +75,000 in 2022, then:
- M1 (high) falls to +45,000 a year by 2027.
- M2 (moderate) falls to +30,000 a year by 2032.
- M3 (low) falls to +10,000 a year by 2032.

All three share the same fertility assumption (the total fertility rate falls from 1.55 to 1.3 by 2037) and the same mortality assumption.
**Caveat:** The CSO ratio uses 65+ and 15-64. In the model, households enter at 21 and retire at 66, so the model's own retiree-to-worker ratio is not the same object. Compute the model's ratio before you compare the two.

### `pension_parameters.csv`

**Measures:** The parameters of the State Pension (Contributory), and average weekly earnings, so that a replacement rate can be computed. One row per parameter.
**Columns:** `parameter`, `value`, `unit`, `period`, `source`, `url`.
**Rows and sources:**
- `state_pension_contributory_max_weekly`: the maximum personal weekly rate at age 66 (no increases for dependants). The 2025 rate (289.30 euro) is from the Social Welfare Act 2024, Schedule 1. The 2026 rate (299.30 euro, from January 2026) is from the Social Welfare and Automatic Enrolment Retirement Savings System (Amendment) Act 2025, Schedule 1. Both were read from the Irish Statute Book on 4 November 2026 (and checked against the pages again on 11 November) and entered by hand in `fetch_data.py`. The script checks both against the web pages each time it runs.
- `pension_age`: 66. "'Pensionable age' means the age of 66 years", Social Welfare Consolidation Act 2005, section 2 (revised), read 4 November 2026.
- `average_weekly_earnings`: CSO Earnings and Labour Costs (EHECS), table **EHQ53**, statistic EHQ53C02 (Average Weekly Earnings), all employees, all NACE Rev 2.1 sectors B to T. The 2025 figure is the simple mean of the four quarters. The 2026 figure is the mean of the quarters published so far (Q1 and Q2; Q2 is preliminary). Table updated 25 August 2026.
- `replacement_rate`: the pension rate divided by average weekly earnings in the same period.

**Caveats:** The maximum rate requires a full contribution record, so many pensioners receive less. The rate is a flat amount, not linked to a person's own earnings. Average weekly earnings are gross, cover employees only, and are a mean, which sits above the median. People who defer the pension to 67 or 68 get higher rates (listed in the same schedules). Budget announcements for 2027 are not law until the next Social Welfare Act, so they are not included.

## Not yet included

Nothing from the list for this folder is missing.
