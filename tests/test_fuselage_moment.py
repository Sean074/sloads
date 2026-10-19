"""Munk slender-body fuselage pitching-moment estimator (Step G4).

The estimator derives the fuselage's contribution to the airplane-less-tail
moment slope ``dCm/dalpha`` from the G1 fuselage outline, so a concept airplane
built from a planform can pick it up from geometry instead of hand-folding it
into the FLTLOADS input coefficients. It is off by default: on the FAR23 GA
Appendix A inputs (whose coefficients already include the fuselage) it is left
disabled and the V-n oracle is bit-for-bit unchanged.

Method + citation: Munk, NACA TR-184 (1924), Eq. (22) p. 13; the apparent-mass
factor ``(k2 - k1)`` is Lamb's closed form for the prolate spheroid, whose
printed oracles are TR-184 Table I (p. 20) and DATCOM Fig. 4.2.1.1-20a
(handbook page 4.2.1.1-20, the digitisation Digital DATCOM carries at
``datcom.f:2334-2335``). Derivation in ``reference/fuselage_pitching_moment.md``.
"""

import math
import os
import sys
from dataclasses import replace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import (
    FuselageMomentInput,
    FuselageOutline,
    FuselageSection,
    io,
)
from sloads import fuselage_moment as fm
from sloads.modules.flight_envelope import build_envelope

_EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_GA = os.path.join(_EXAMPLES, "ga6_normal.project.json")


def _cylinder_outline(length=200.0, diameter=20.0, n=21):
    """A constant-section circular body (width = height = diameter)."""
    return FuselageOutline(sections=[
        FuselageSection(x=length * i / (n - 1), width=diameter, height=diameter)
        for i in range(n)
    ])


# NACA TR-184 Table I, p. 20 (printed page; PDF p. 21): "Length (diameters)",
# K1 (longitudinal), K2 (transverse), K2 - K1 -- Lamb's exact ellipsoid values
# (TR-184 p. 12), printed to three decimals. Read from the page 2026-10-19.
_TR184_TABLE_I = (
    # l/d,  k1,    k2,    k2 - k1
    (1.00, 0.500, 0.500, 0.000),
    (1.50, 0.305, 0.621, 0.316),
    (2.00, 0.209, 0.702, 0.493),
    (2.51, 0.156, 0.763, 0.607),
    (2.99, 0.122, 0.803, 0.681),
    (3.99, 0.082, 0.860, 0.778),
    (4.99, 0.059, 0.895, 0.836),
    (6.01, 0.045, 0.918, 0.873),
    (6.97, 0.036, 0.933, 0.897),
    (8.01, 0.029, 0.945, 0.916),
    (9.02, 0.024, 0.954, 0.930),
    (9.97, 0.021, 0.960, 0.939),
)

# USAF DATCOM Fig. 4.2.1.1-20a, handbook page 4.2.1.1-20: k2 - k1 against
# fineness ratio 4-20, as Digital DATCOM digitises it (datcom.f:2334-2335) and
# as sloads.lateral_body_aero carries it for its own DATCOM oracle.
_DATCOM_FIG_20A = (
    (4.0, 0.77), (5.0, 0.825), (6.0, 0.865), (8.0, 0.91), (10.0, 0.94),
    (12.0, 0.955), (14.0, 0.965), (16.0, 0.97), (18.0, 0.973), (20.0, 0.975),
)


@pytest.mark.parametrize("fineness, k1, k2, diff", _TR184_TABLE_I)
def test_lamb_closed_form_reproduces_tr184_table_i(fineness, k1, k2, diff):
    # Oracle: every column of Table I to within 0.0025 -- the page prints three
    # decimals and Lamb's 1918 figures carry their own last-place rounding (the
    # l/d 1.5 row is the widest, 0.318 against the printed .316).
    got_k1, got_k2 = fm.prolate_spheroid_inertia_coefficients(fineness)
    assert math.isclose(got_k1, k1, abs_tol=0.0025), (fineness, got_k1, k1)
    assert math.isclose(got_k2, k2, abs_tol=0.0025), (fineness, got_k2, k2)
    assert math.isclose(fm.munk_k2_minus_k1(fineness), diff, abs_tol=0.0025)


@pytest.mark.parametrize("fineness, diff", _DATCOM_FIG_20A)
def test_lamb_closed_form_follows_datcom_figure_20a(fineness, diff):
    # Oracle: the DATCOM curve is the same function read off a chart. The
    # digitisation sits 0.6-1.2 % *below* Lamb at l/d 4-8 (0.770 against
    # TR-184's .778 at 4; 0.825 against .836 at 5) and 0.5 % above at 20, so
    # the gate is 1.5 %: a chart-reading band, not the closed form's.
    assert math.isclose(fm.munk_k2_minus_k1(fineness), diff, rel_tol=1.5e-2)


def test_datcom_oracle_rows_are_the_lateral_modules_own_copy():
    # One digitisation of Fig. 4.2.1.1-20a in the tree: the rows above are the
    # ones lateral_body_aero carries for the DATCOM Cn_beta oracle.
    from sloads import lateral_body_aero as lba
    assert tuple(zip(lba._K2K1_FINENESS, lba._K2K1_VALUES)) == _DATCOM_FIG_20A


def test_k_factor_limits():
    # Sphere (and anything oblate, which is not a fuselage): no free moment.
    assert fm.munk_k2_minus_k1(0.5) == 0.0
    assert fm.munk_k2_minus_k1(1.0) == 0.0
    # Slender limit: k1 -> 0, k2 -> 1 (TR-184 Table I's last row), monotone.
    assert math.isclose(fm.munk_k2_minus_k1(1e9), 1.0, abs_tol=1e-9)
    samples = [fm.munk_k2_minus_k1(1.0 + 0.25 * i) for i in range(200)]
    assert all(b > a for a, b in zip(samples, samples[1:]))
    assert fm.munk_k2_minus_k1(100.0) < 1.0


def test_estimate_matches_closed_form():
    # A 200 in long, 20 in diameter cylinder: Vol = A*L, A = pi/4*d^2; fineness
    # 200/20 = 10 -> (k2-k1) = 0.9395 (TR-184 Table I prints .939 at 9.97).
    # dCm/dalpha = k*Vol/(S_in2*mac)/57.2958.
    outline = _cylinder_outline(length=200.0, diameter=20.0)
    s_sqft, mac_in = 174.0, 58.0
    est = fm.estimate(outline, s_sqft, mac_in)
    assert est is not None

    vol = math.pi / 4.0 * 20.0 ** 2 * 200.0
    assert math.isclose(est.volume_in3, vol, rel_tol=1e-9)
    assert math.isclose(est.fineness_ratio, 10.0, rel_tol=1e-9)
    assert math.isclose(est.k2_minus_k1, 0.939, abs_tol=0.0025)
    assert est.k2_minus_k1 == fm.munk_k2_minus_k1(10.0)

    expected = est.k2_minus_k1 * vol / (s_sqft * 144.0 * mac_in) / (180.0 / math.pi)
    assert math.isclose(est.d_cm_dalpha, expected, rel_tol=1e-9)
    assert est.d_cm_dalpha > 0.0    # destabilizing (nose-up with alpha)


def test_estimate_returns_none_on_insufficient_geometry():
    assert fm.estimate(None, 174.0, 58.0) is None
    one = FuselageOutline(sections=[FuselageSection(x=0.0, width=20.0, height=20.0)])
    assert fm.estimate(one, 174.0, 58.0) is None                 # < 2 stations
    assert fm.estimate(_cylinder_outline(), 0.0, 58.0) is None   # S <= 0
    assert fm.estimate(_cylinder_outline(), 174.0, 0.0) is None  # mac <= 0


def test_disabled_fuselage_moment_leaves_oracle_unchanged():
    # The Appendix A GA project has no fuselage_moment; adding a *disabled* one
    # (or an enabled one with a zero increment) must not perturb the V-n matrix.
    base = build_envelope(io.load_project(_GA))
    base_by_case = {p.case: p for p in base.vn}

    for fmi in (
        FuselageMomentInput(enabled=False, d_cm_dalpha=0.123),   # off -> ignored
        FuselageMomentInput(enabled=True, d_cm_dalpha=0.0),      # zero -> no change
    ):
        proj = io.load_project(_GA)
        assert proj.aero_coeffs is not None
        proj.aero_coeffs = replace(proj.aero_coeffs, fuselage_moment=fmi)
        env = build_envelope(proj)
        for p in env.vn:
            b = base_by_case[p.case]
            assert p.m_wf == b.m_wf
            assert p.lt == b.lt
            assert p.nz == b.nz


def test_enabled_fuselage_moment_shifts_balanced_tail_load():
    # Enabling a positive (destabilizing) fuselage dCm/dalpha must change the
    # pitching moment M(W+F) and hence the balancing tail load -- i.e. the wiring
    # actually reaches the balance. (Balance targets the same NZ, so NZ is held.)
    base = {p.case: p for p in build_envelope(io.load_project(_GA)).vn}

    proj = io.load_project(_GA)
    proj.aero_coeffs = replace(
        proj.aero_coeffs,
        fuselage_moment=FuselageMomentInput(enabled=True, d_cm_dalpha=0.01),
    )
    env = {p.case: p for p in build_envelope(proj).vn}

    # At least one aero-limited (non-stall) point must move its tail load.
    moved = [c for c in env if abs(env[c].lt - base[c].lt) > 1.0]
    assert moved, "enabled fuselage moment did not change any balancing tail load"


def test_serialization_round_trips_fuselage_moment(tmp_path):
    proj = io.load_project(_GA)
    proj.aero_coeffs = replace(
        proj.aero_coeffs,
        fuselage_moment=FuselageMomentInput(enabled=True, d_cm_dalpha=0.0042),
    )
    path = os.path.join(tmp_path, "with_fus_moment.project.json")
    io.save_project(proj, path)
    back = io.load_project(path)
    assert back.aero_coeffs.fuselage_moment is not None
    assert back.aero_coeffs.fuselage_moment.enabled is True
    assert math.isclose(back.aero_coeffs.fuselage_moment.d_cm_dalpha, 0.0042, rel_tol=1e-12)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            if "tmp_path" in getattr(fn, "__code__", type("x", (), {"co_varnames": ()})).co_varnames:
                import tempfile
                with tempfile.TemporaryDirectory() as d:
                    fn(d)
            else:
                fn()
            print(f"ok  {name}")
    print("all fuselage-moment tests passed")
