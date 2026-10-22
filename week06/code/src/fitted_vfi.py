"""Fitted value function iteration on the growth model, and Euler-equation errors.

Week 5 of ECU44291. Same model as Week 4 (log utility, full depreciation),
but the choice k' is continuous: an optimiser inside the sweep, and the
continuation value read between grid points by an interpolant.

The interpolant matters more than students expect. Linear interpolation keeps
the value function's shape but has kinks at every node, and the optimiser
snaps to the kinks: about three quarters of the choices land exactly on grid
points, so the policy is still mostly a staircase. A smooth interpolant
removes the kinks. PCHIP (a shape-preserving cubic) does so without the
overshoot a plain cubic spline can produce, and is the default here.
"""
import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.optimize import minimize_scalar

DEFAULT = dict(alpha=0.3, beta=0.9, k_min=0.02, k_max=0.5, n_k=200)


def params(**overrides):
    p = dict(DEFAULT)
    p.update(overrides)
    return p


def grid(p):
    return np.linspace(p["k_min"], p["k_max"], p["n_k"])


def make_interpolant(k, V, kind):
    """Return a callable V_hat(k') for kind in {'linear', 'pchip', 'cubic'}."""
    if kind == "linear":
        return lambda x: np.interp(x, k, V)
    if kind == "pchip":
        return PchipInterpolator(k, V)
    if kind == "cubic":
        return CubicSpline(k, V)
    raise ValueError(f"unknown interpolant {kind!r}")


def bellman_fitted(V, k, p, kind="pchip"):
    """One sweep with continuous choice. Returns (TV, policy values k')."""
    alpha, beta = p["alpha"], p["beta"]
    V_hat = make_interpolant(k, V, kind)         # built once per sweep, not once per state
    TV = np.empty(len(k))
    policy = np.empty(len(k))
    for i, ki in enumerate(k):
        y = ki ** alpha
        upper = min(y - 1e-10, k[-1])              # never ask the interpolant for a point beyond the grid

        def objective(kp):
            return -(np.log(y - kp) + beta * V_hat(kp))

        res = minimize_scalar(objective, bounds=(k[0], upper), method="bounded", options={"xatol": 1e-10})
        TV[i], policy[i] = -res.fun, res.x
    return TV, policy


def fitted_vfi(p, kind="pchip", tol=1e-6, max_iter=5000):
    k = grid(p)
    V = np.zeros(len(k))
    for it in range(max_iter):
        V_new, policy = bellman_fitted(V, k, p, kind)
        dist = np.max(np.abs(V_new - V))
        V = V_new
        if dist < tol:
            return dict(k=k, V=V, policy=policy, n_iter=it + 1, kind=kind)
    raise RuntimeError("fitted_vfi: no convergence")


def discrete_vfi(p, tol=1e-6, max_iter=10000):
    """Week 4's grid-choice VFI, for comparison."""
    k = grid(p)
    c = k[:, None] ** p["alpha"] - k[None, :]
    U = np.full(c.shape, -np.inf)
    U[c > 0] = np.log(c[c > 0])
    V = np.zeros(len(k))
    for it in range(max_iter):
        value = U + p["beta"] * V[None, :]
        V_new = value.max(axis=1)
        dist = np.max(np.abs(V_new - V))
        V = V_new
        if dist < tol:
            return dict(k=k, V=V, policy=k[value.argmax(axis=1)], n_iter=it + 1, kind="grid")
    raise RuntimeError("discrete_vfi: no convergence")


def closed_form_policy(k, p):
    return p["alpha"] * p["beta"] * k ** p["alpha"]


def share_on_nodes(k, policy, tol=1e-6):
    """Fraction of policy values that sit exactly on a grid point."""
    return float(np.mean(np.min(np.abs(policy[:, None] - k[None, :]), axis=1) < tol))


def euler_errors(k, policy, p, k_eval=None):
    """log10 of the relative Euler-equation error at points k_eval, grid midpoints by default.

    For log utility and full depreciation the Euler equation is
        1/c = beta * alpha * k'^(alpha-1) / c',
    with c = k^alpha - g(k), c' = k'^alpha - g(k'), k' = g(k). The policy is
    interpolated linearly between grid points to evaluate g off the grid.
    """
    alpha, beta = p["alpha"], p["beta"]
    if k_eval is None:
        k_eval = 0.5 * (k[:-1] + k[1:])
    g = lambda x: np.interp(x, k, policy)
    kp = g(k_eval)
    c = k_eval ** alpha - kp
    cp = kp ** alpha - g(kp)
    rhs = beta * alpha * kp ** (alpha - 1) / cp
    err = np.abs(1 - c * rhs)
    return np.log10(np.maximum(err, 1e-16))
