"""Lecture 7 tests. Run from lectures/lecture07/code: python -m pytest -q tests

The two-period tests are public. The economy tests check the M3 engine (held until after the M3
deadline) and are the first draft of the M3 hidden tests.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import olg2  # noqa: E402


def test_pension_at_old_prices():
    p0, p1 = olg2.params(), olg2.params(tau_p=0.3)
    _, w0, R0 = olg2.prices(olg2.solve_by_root(p0), p0)
    assert olg2.savings(w0, R0, p1) == pytest.approx(0.0620, abs=5e-5)


def test_pension_general_equilibrium_below_partial():
    p0, p1 = olg2.params(), olg2.params(tau_p=0.3)
    _, w0, R0 = olg2.prices(olg2.solve_by_root(p0), p0)
    assert olg2.solve_by_root(p1) < olg2.savings(w0, R0, p1)


