"""Interpolation from first principles. Week 5 of ECU44291."""
import numpy as np


def interp_linear(x, xp, fp):
    """Piecewise-linear interpolation of the points (xp, fp) at x, written by hand.

    xp must be increasing. Outside [xp[0], xp[-1]] the value is clamped to the
    end values, exactly as np.interp does. That clamping is silent, and it is
    the single most common way a value function goes wrong at the top of the grid.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    xp = np.asarray(xp, dtype=float)
    fp = np.asarray(fp, dtype=float)
    i = np.searchsorted(xp, x, side="right") - 1        # index of the bracket's left point
    i = np.clip(i, 0, len(xp) - 2)
    w = (x - xp[i]) / (xp[i + 1] - xp[i])                # position inside the bracket
    w = np.clip(w, 0.0, 1.0)                              # clamp outside the grid
    out = (1 - w) * fp[i] + w * fp[i + 1]
    return out if out.size > 1 else out[0]


def runge(x):
    """Runge's function, 1 / (1 + 25 x^2): smooth, and a disaster for high-order polynomials on equispaced nodes."""
    return 1.0 / (1.0 + 25.0 * np.asarray(x) ** 2)


def chebyshev_nodes(n, a=-1.0, b=1.0):
    k = np.arange(n)
    x = np.cos((2 * k + 1) * np.pi / (2 * n))
    return np.sort(0.5 * (a + b) + 0.5 * (b - a) * x)
