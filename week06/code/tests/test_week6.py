"""Tests for Week 6: optimisation, interpolation, fitted VFI, Euler errors, continuous household."""
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.interpolate import lagrange

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from optimise import golden_section, newton_max, profit, profit_prime, profit_prime2  # noqa: E402
from interp import interp_linear, runge  # noqa: E402
from fitted_vfi import params, fitted_vfi, discrete_vfi, closed_form_policy, euler_errors, share_on_nodes  # noqa: E402
import lifecycle as lc  # noqa: E402


def test_golden_section_finds_the_profit_maximum():
    x, brackets = golden_section(profit, 0.1, 3.0)
    assert x == pytest.approx(1.0, abs=1e-6)
    assert 30 < len(brackets) < 60


def test_newton_max_from_a_good_start():
    assert newton_max(profit_prime, profit_prime2, 0.7) == pytest.approx(1.0, abs=1e-8)


def test_newton_max_refuses_a_minimum():
    with pytest.raises(RuntimeError):
        newton_max(profit_prime, profit_prime2, 0.05)      # heads for the stationary point at 0


def test_interp_linear_matches_numpy_on_and_off_grid():
    xp = np.linspace(0, 1, 11)
    fp = np.sin(3 * xp)
    x = np.array([-0.5, 0.0, 0.05, 0.37, 1.0, 1.7])
    assert np.allclose(interp_linear(x, xp, fp), np.interp(x, xp, fp))


def test_interp_linear_clamps_outside_the_grid():
    xp = np.array([0.0, 1.0])
    fp = np.array([0.0, 2.0])
    assert interp_linear(5.0, xp, fp) == 2.0                # silently flat beyond the grid


def test_runge_high_order_polynomial_is_worse_than_linear():
    nodes = np.linspace(-1, 1, 11)
    x = np.linspace(-1, 1, 401)
    err_lin = np.max(np.abs(interp_linear(x, nodes, runge(nodes)) - runge(x)))
    err_lag = np.max(np.abs(lagrange(nodes, runge(nodes))(x) - runge(x)))
    assert err_lag > err_lin


@pytest.fixture(scope="module")
def vfis():
    p = params(n_k=100)
    return p, discrete_vfi(p), fitted_vfi(p, kind="linear"), fitted_vfi(p, kind="pchip")


def test_linear_interpolation_snaps_to_nodes_and_pchip_does_not(vfis):
    p, d, f_lin, f_pchip = vfis
    assert share_on_nodes(f_lin["k"], f_lin["policy"]) > 0.5
    assert share_on_nodes(f_pchip["k"], f_pchip["policy"]) < 0.05


def test_pchip_policy_is_on_the_closed_form(vfis):
    p, d, f_lin, f_pchip = vfis
    truth = closed_form_policy(f_pchip["k"], p)
    interior = (f_pchip["k"] > 0.05) & (f_pchip["k"] < 0.45)
    assert np.max(np.abs(f_pchip["policy"] - truth)[interior]) < 1e-4
    assert np.max(np.abs(f_lin["policy"] - truth)[interior]) > 1e-3     # linear: still within a grid step, no better


def test_euler_errors_two_orders_better_with_a_smooth_interpolant(vfis):
    p, d, f_lin, f_pchip = vfis
    ee_d = euler_errors(d["k"], d["policy"], p).mean()
    ee_lin = euler_errors(f_lin["k"], f_lin["policy"], p).mean()
    ee_pchip = euler_errors(f_pchip["k"], f_pchip["policy"], p).mean()
    assert abs(ee_lin - ee_d) < 0.5                        # linear buys almost nothing
    assert ee_pchip < ee_d - 2.0                            # pchip buys two orders of magnitude


def test_continuous_household_matches_two_period_closed_form():
    y1, y2, R, beta = 1.0, 0.3, 1.04, 0.96
    cf = lc.two_period_closed_form(y1, y2, R, beta)
    a = np.linspace(0, 1, 50)
    V2 = np.log(R * a + y2)
    from scipy.optimize import minimize_scalar
    from scipy.interpolate import PchipInterpolator
    V_hat = PchipInterpolator(a, V2)
    res = minimize_scalar(lambda s: -(np.log(y1 - s) + beta * V_hat(s)), bounds=(0, y1 - 1e-9), method="bounded",
                          options={"xatol": 1e-10})
    assert res.x == pytest.approx(cf["s"], abs=1e-4)      # far below the grid step of 0.02
    res_lin = minimize_scalar(lambda s: -(np.log(y1 - s) + beta * np.interp(s, a, V2)), bounds=(0, y1 - 1e-9),
                              method="bounded", options={"xatol": 1e-10})
    assert abs(res_lin.x - cf["s"]) > 1e-3                # linear: snapped to a node


