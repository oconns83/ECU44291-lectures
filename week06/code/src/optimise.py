"""One-dimensional optimisation from first principles. Week 5 of ECU44291.

golden_section: bracketing without derivatives (bisection's cousin for maxima).
newton_max:     Newton on the first-order condition (needs f' and f'').
profit:         the running example, f(x) = 4 x^2 e^{-2x}, maximised at x = 1.
"""
import numpy as np

GOLDEN = (np.sqrt(5) - 1) / 2       # about 0.618


def golden_section(f, a, b, tol=1e-8, max_iter=200):
    """Maximise a unimodal f on [a, b]. Returns (x, brackets).

    Two interior points split the bracket in the golden ratio; after each
    evaluation one endpoint moves in and one interior point is reused, so the
    bracket shrinks by 0.618 per function evaluation.
    """
    c = b - GOLDEN * (b - a)
    d = a + GOLDEN * (b - a)
    fc, fd = f(c), f(d)
    brackets = [(a, b)]
    for _ in range(max_iter):
        if b - a < tol:
            return 0.5 * (a + b), brackets
        if fc > fd:                      # maximum is in [a, d]
            b, d, fd = d, c, fc
            c = b - GOLDEN * (b - a)
            fc = f(c)
        else:                            # maximum is in [c, b]
            a, c, fc = c, d, fd
            d = a + GOLDEN * (b - a)
            fd = f(d)
        brackets.append((a, b))
    raise RuntimeError("golden_section: no convergence")


def newton_max(fprime, fprime2, x0, tol=1e-10, max_iter=50):
    """Newton's method on f'(x) = 0. Finds a stationary point, not necessarily a maximum: check f''(x) < 0."""
    x = x0
    for _ in range(max_iter):
        d2 = fprime2(x)
        if d2 == 0 or not np.isfinite(d2):
            raise RuntimeError("newton_max: zero or non-finite second derivative")
        x_new = x - fprime(x) / d2
        if abs(x_new - x) < tol:
            if fprime2(x_new) >= 0:
                raise RuntimeError(f"newton_max: converged to a minimum or saddle at {x_new}")
            return x_new
        x = x_new
    raise RuntimeError("newton_max: no convergence")


def profit(x):
    return 4 * x**2 * np.exp(-2 * x)


def profit_prime(x):
    return 8 * np.exp(-2 * x) * x * (1 - x)


def profit_prime2(x):
    return 8 * np.exp(-2 * x) * (1 - 4 * x + 2 * x**2)
