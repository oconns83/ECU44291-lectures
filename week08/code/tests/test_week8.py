"""Checks on the calibration data. Run from lectures/lecture08/code: uv run pytest

Each test asserts something that must be true of the files if they were built correctly:
the derived columns agree with the columns they come from, the years are complete,
and every share or rate is in a range it could possibly take.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

DATA = Path(__file__).resolve().parents[1] / "data"


def load(name):
    return pd.read_csv(DATA / name)


@pytest.mark.parametrize("name", ["gdp_gni_star.csv", "capital_output_cso.csv", "capital_output_pwt.csv",
                                  "capital_share_pwt.csv", "depreciation_pwt.csv", "population_by_age.csv",
                                  "dependency_projections.csv"])
def test_no_missing_values(name):
    assert not load(name).isna().any().any()


@pytest.mark.parametrize("name", ["gdp_gni_star.csv", "capital_output_cso.csv", "capital_output_pwt.csv",
                                  "capital_share_pwt.csv", "depreciation_pwt.csv"])
def test_years_are_consecutive(name):
    years = load(name).year
    assert (np.diff(years) == 1).all()


def test_gni_star_ratio_and_ordering():
    g = load("gdp_gni_star.csv")
    assert np.allclose(g.gni_star_eur_m / g.gdp_eur_m, g.gni_star_over_gdp, atol=0.0006)
    assert (g.gni_star_eur_m <= g.gdp_eur_m).all()          # GNI* removes income, never adds it


def test_capital_output_ratios_recompute():
    c = load("capital_output_cso.csv")
    assert np.allclose(c.net_capital_stock_eur_m / c.gdp_eur_m, c.k_over_gdp, atol=0.0006)
    assert np.allclose(c.net_capital_stock_eur_m / c.gni_star_eur_m, c.k_over_gni_star, atol=0.0006)
    parts = c.of_which_dwellings_eur_m + c.of_which_intangibles_eur_m + c.of_which_transport_equipment_eur_m
    assert (parts < c.net_capital_stock_eur_m).all()        # components are part of the total


def test_cso_income_matches_national_accounts():
    c, g = load("capital_output_cso.csv"), load("gdp_gni_star.csv")
    m = c.merge(g, on="year", suffixes=("", "_na"))
    assert len(m) == len(c)
    assert (m.gdp_eur_m == m.gdp_eur_m_na).all() and (m.gni_star_eur_m == m.gni_star_eur_m_na).all()


def test_pwt_ratio_recomputes():
    p = load("capital_output_pwt.csv")
    assert np.allclose(p.rnna_usd2021_m / p.rgdpna_usd2021_m, p.k_over_y, atol=0.0006)


def test_shares_and_rates_in_range():
    s, d = load("capital_share_pwt.csv"), load("depreciation_pwt.csv")
    assert np.allclose(s.alpha + s.labsh, 1.0, atol=1e-4)
    assert ((s.alpha > 0) & (s.alpha < 1)).all()
    assert ((d.delta > 0) & (d.delta < 0.2)).all()


def test_population_by_single_year_of_age():
    pop = load("population_by_age.csv")
    assert list(pop.age) == list(range(100))                # 0 to 98, then 99 and over
    assert pop.persons.sum() == 5_525_578                   # the README's total
    assert (pop.persons > 0).all()


def test_projections_complete_and_add_up():
    d = load("dependency_projections.csv")
    assert len(d) == 3 * 8 * 3                              # scenarios x years x ratios
    wide = d.pivot_table(index=["year", "scenario"], columns="ratio", values="value_pct")
    assert np.allclose(wide.old + wide.young, wide.total, atol=0.15)


def test_replacement_rate_is_pension_over_earnings():
    p = load("pension_parameters.csv")
    val = {(r.parameter, r.period): r.value for r in p.itertuples()}
    repl = val[("replacement_rate", "2025")]
    assert repl == pytest.approx(val[("state_pension_contributory_max_weekly", "2025")]
                                 / val[("average_weekly_earnings", "2025")], abs=0.0006)
    assert 0 < repl < 1
