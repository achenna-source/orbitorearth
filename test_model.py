"""Self-consistency and sanity tests for the OrbitOrEarth core model.

Run with:  pytest -q
"""
import numpy as np

import model as m


def _params():
    return m.load_params("params.yaml")


def test_reproduces_brief_table():
    """The model must reproduce the brief's preliminary envelope within 0.01."""
    assert m.selfcheck(_params(), verbose=False, tol=0.01)


def test_break_even_positive():
    p = m.resolve(_params(), "embodied_included")
    assert m.break_even_intensity(p) > 0


def test_verdict_flips_around_threshold():
    p = m.resolve(_params(), "embodied_included")
    istar = m.break_even_intensity(p)
    assert m.orbit_wins(p, istar + 0.05)                 # dirtier grid -> orbit wins
    assert not m.orbit_wins(p, max(istar - 0.05, 0.0))   # cleaner grid -> ground wins


def test_mass_monotonic():
    """Heavier system -> higher break-even (orbit harder to justify)."""
    p = m.resolve(_params(), "embodied_included")
    light = dict(p, system_mass_per_kw=50.0)
    heavy = dict(p, system_mass_per_kw=150.0)
    assert m.break_even_intensity(heavy) > m.break_even_intensity(light)


def test_lifetime_monotonic():
    """Longer GPU life -> lower break-even (embodied launch amortized)."""
    p = m.resolve(_params(), "embodied_included")
    short = dict(p, gpu_lifetime_years=2.0)
    longer = dict(p, gpu_lifetime_years=5.0)
    assert m.break_even_intensity(longer) < m.break_even_intensity(short)


def test_monte_carlo_shape_and_center():
    params = _params()
    s = m.monte_carlo_break_even(params, "embodied_included", n=20000, seed=0)
    assert s.shape == (20000,)
    assert np.all(s > 0)
    point = m.break_even_intensity(m.resolve(params, "embodied_included"))
    assert 0.3 * point < np.median(s) < 3.0 * point
