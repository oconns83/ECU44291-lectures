"""The life-cycle household, on the grid (Lecture 3) and with continuous choice (Lecture 6).

The continuous version is the M1 Part C task: an optimiser inside the age loop and the
continuation value interpolated between grid points. It and the Euler residuals are held
from the public repository until the M1 full submission (2 November).
"""
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import minimize_scalar

DEFAULT = dict(J=60, J_R=45, beta=0.96, R=1.04, sigma=2.0, w=1.0, tau=0.0,
               repl=0.4, a_max=25.0, n_a=300)


def params(**overrides):
    p = dict(DEFAULT)
    p.update(overrides)
    return p


def efficiency_profile(J, J_R):
    j = np.arange(1, J + 1)
    e = np.exp(0.06 * j - 0.0012 * j**2)
    e = e / e[:J_R].mean()
    e[J_R:] = 0.0
    return e


def income_profile(p):
    e = efficiency_profile(p["J"], p["J_R"])
    y = (1 - p["tau"]) * p["w"] * e
    y[p["J_R"]:] = p["repl"] * p["w"] * e[:p["J_R"]].mean()
    return y


def utility(c, sigma):
    c = np.asarray(c, dtype=float)
    return np.log(c) if sigma == 1.0 else c ** (1 - sigma) / (1 - sigma)


def solve_household_grid(p):
    """Week 3: choices on the grid."""
    J, R, beta, sigma = p["J"], p["R"], p["beta"], p["sigma"]
    a = np.linspace(0.0, p["a_max"], p["n_a"])
    y = income_profile(p)
    V = np.zeros((J + 1, len(a)))
    policy = np.zeros((J, len(a)))
    for j in range(J - 1, -1, -1):
        c = R * a[:, None] + y[j] - a[None, :]
        u = np.full(c.shape, -np.inf)
        u[c > 0] = utility(c[c > 0], sigma)
        value = u + beta * V[j + 1][None, :]
        policy[j] = a[value.argmax(axis=1)]
        V[j] = value.max(axis=1)
    return dict(a_grid=a, V=V, policy=policy, y=y)


def simulate_profile(sol, p, a0=0.0):
    """Follow the policy from a0, interpolating the policy function between grid points."""
    a, policy, y, R = sol["a_grid"], sol["policy"], sol["y"], p["R"]
    assets, cons = [a0], []
    cur = a0
    for j in range(p["J"]):
        nxt = np.interp(cur, a, policy[j])
        cons.append(R * cur + y[j] - nxt)
        assets.append(nxt)
        cur = nxt
    return np.array(assets), np.array(cons)


def two_period_closed_form(y1, y2, R, beta):
    c1 = (y1 + y2 / R) / (1 + beta)
    s = max(y1 - c1, 0.0)
    return dict(c1=y1 - s, c2=R * s + y2, s=s)
