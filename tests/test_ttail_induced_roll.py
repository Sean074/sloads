"""The T-tail's horizontal-tail asymmetry at the fin (design note 51 §9, #328;
§10, #334).

No printed oracle covers a T-tail (Appendix A is a conventional empennage; AC
23-9 ¶3), so rule 2's second branch applies: every gate here is an identity or a
closure, with the note's expected figures pinned beside it.

* **G-51.1** the deck's 23.427(a) case carries the (b) roll at the fin root,
  exactly, in both hands.
* **G-51.1a** a one-engine-out fin result pairs with the deck's own 1 g parent.
* **G-51.2** ``HTAIL UNSYM``'s tip roll is its h-tail table's ``Σ fz·y``, and
  the applied-load row carries it.
* **G-51.3** the deck never carries ``HTAIL UNSYM``, and carries exactly one
  induced set per T-tail lateral or one-engine-out case (G-51.15).
* **G-51.4** ``M_r = 0.3 q S_H b_H beta`` (AC 23-9 ¶5a p3) and its beta rule.
* **G-51.5** its sense is the fin's own root rolling moment's (¶5d p5-6).
* **G-51.6** the deck's fin root carries its own load plus ``M_r``, exactly.
* **G-51.7** the fin view's root rolling moment with the tip set.
* **G-51.8** the AC's own 4-6x band on the pure-attitude conditions.
* **G-51.9** retired with D-51.7 (D-51.7a): replaced by G-51.14.
* **G-51.10** the Mach and dihedral limits (D-51.8).
* **G-51.11** a conventional tail is untouched by all of it.
* **G-51.12** each induced set: ``Σ fz = 0``, ``Σ fz·y = M_r``, ``±M_r/2`` a root.
* **G-51.13** each ``INDUCED ROLL`` h-tail condition's per-side root bending.
* **G-51.14** the ATR's governing h-tail root bending is ONE ENGINE OUT VD.
* **G-51.15** the deck's strips close exactly as the retired fin-tip couple did.
* **G-51.16** the h-tail condition's trim part is the fin transfer's pairing.
"""

import copy
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io
from sloads.constants import AC23_9_MACH_WARN, DEG_PER_RAD, IN2_PER_FT2, IN_PER_FT, dynamic_pressure_psf
from sloads.export.coordinates import ttail_transfer_to_airplane
from sloads.export.lra_model import _member_key, build_lra_model
from sloads.models import TailType
from sloads.modules.balance import (
    INDUCED_ROLL_SOURCE,
    build_balanced_cases,
    is_engine_out,
    is_lateral,
    is_unsymmetrical_htail,
)
from sloads.modules.select import (
    _avt,
    _effectv,
    default_critical,
    effective_vtail_inputs,
    vn_points,
)
from sloads.modules.tail_span import (
    HTAIL_UNSYM_LABEL,
    INDUCED_ROLL_LABEL,
    build_tail_span,
    htail_root_bending,
    vtail_root_roll,
    vtail_root_roll_with_tip,
)
from sloads.tail_geometry import resolve_tail_planform
from sloads.validation import consistency_warnings

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
_T_TAILS = ("concept_regional_jet", "atr42_100")

#: Design note 51 §9.1: ``M_r`` per fin condition (lb-in, magnitude), the
#: measured table the note agreed. The RJ reproduces §4's original figures to
#: within 0.05 %. The ATR's engine-out rows re-pinned at #333 (ruling 4): the
#: march now sizes on the ``aft gross`` FLIGHT loading, not WTONECG's all-items
#: one, +0.36 % (VC 328,765 -> 329,944) and +0.29 % (VD 458,984 -> 460,327).
_M_R = {
    "concept_regional_jet": {
        "SUDDEN RUDDER": 266_727, "YAW TO SIDESLIP": 137_013,
        "YAW 15 NEUTRAL": 310_569, "SIDE GUST": 373_565,
    },
    "atr42_100": {
        "SUDDEN RUDDER": 112_543, "YAW TO SIDESLIP": 53_894,
        "YAW 15 NEUTRAL": 128_028, "SIDE GUST": 162_118,
        "ONE ENGINE OUT — VC (ultimate) (engine 1)": 329_944,
        "ONE ENGINE OUT — VD (limit) (engine 1)": 460_327,
        "ONE ENGINE OUT — VC (ultimate) (engine 2)": 329_944,
        "ONE ENGINE OUT — VD (limit) (engine 2)": 460_327,
    },
}

#: G-51.7: the fin view's root rolling moment with the tip set, airplane axes.
#: The ATR's engine-out rows re-pinned at #333 (1,348,459 -> 1,352,404, the
#: mass basis above).
_ROOT_WITH_TIP = {
    "concept_regional_jet": {
        "SUDDEN RUDDER": -706_830, "YAW TO SIDESLIP": +363_087,
        "YAW 15 NEUTRAL": +823_013, "SIDE GUST": -824_818,
    },
    "atr42_100": {
        "SUDDEN RUDDER": -328_155, "YAW TO SIDESLIP": +157_144,
        "YAW 15 NEUTRAL": +373_307, "SIDE GUST": -389_728,
        "ONE ENGINE OUT — VD (limit) (engine 1)": +1_352_404,
        "ONE ENGINE OUT — VD (limit) (engine 2)": -1_352_404,
    },
}

#: G-51.13 (note 51 §10.1): each ``INDUCED ROLL`` h-tail condition's larger
#: per-side root bending (lb-in, LIMIT), measured 2026-10-04; the ATR's
#: engine-out rows hold for each engine.
_INDUCED_BENDING = {
    "concept_regional_jet": {
        "SUDDEN RUDDER": 148_657, "YAW TO SIDESLIP": 83_801,
        "YAW 15 NEUTRAL": 170_579, "SIDE GUST": 291_033,
    },
    "atr42_100": {
        "SUDDEN RUDDER": 66_980, "YAW TO SIDESLIP": 37_655,
        "YAW 15 NEUTRAL": 74_723, "SIDE GUST": 110_703,
        "ONE ENGINE OUT — VC (ultimate) (engine 1)": 173_864,
        "ONE ENGINE OUT — VD (limit) (engine 1)": 233_122,
        "ONE ENGINE OUT — VC (ultimate) (engine 2)": 173_864,
        "ONE ENGINE OUT — VD (limit) (engine 2)": 233_122,
    },
}

#: G-51.14: the governing per-side h-tail root bending (raw LIMIT, lb-in) and
#: the condition it comes from. The RJ's does not move with D-51.12.
_GOVERNING = {
    "concept_regional_jet": ("GUST DN RETRACTED", 349_920),
    "atr42_100": (f"{INDUCED_ROLL_LABEL} — ONE ENGINE OUT — VD (limit) (engine 1)", 233_122),
}

#: G-51.1 / G-51.2: the 23.427(a) case's net roll about the centreline.
_UNSYM_ROLL = {"concept_regional_jet": 72_547, "atr42_100": -30_622}


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _fins(name):
    return {r.case: r for r in build_tail_span(_project(name))["vtail"]}


def _fin_root_mx(case, model):
    """The deck's fin-root rolling moment: every load on the h-tail and fin
    members, about the fin's lowest node. The fin is a determinate cantilever and
    the T-tail's h-tail rides its tip, so this is the internal moment there."""
    root = min(model.members["vtail"], key=lambda n: n.pos[2])
    mx = 0.0
    for ld in case.loads:
        if _member_key(ld, model.members) not in ("htail", "vtail"):
            continue
        mx += ((ld.y - root.pos[1]) * ld.fz - (ld.z - root.pos[2]) * ld.fy + ld.mx)
    return mx


# --------------------------------------------------------------------------- #
# G-51.1 / G-51.3 / G-51.6 -- the deck
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _T_TAILS)
def test_the_deck_carries_the_unsymmetrical_roll_at_the_fin_root(name):
    """G-51.1: Gap 1 was closed in the deck by construction, and ungated."""
    project = _project(name)
    model = build_lra_model(project)
    unsym = next(r for r in build_tail_span(project)["htail"]
                 if r.case == "UNSYMMETRICAL")
    roll = math.fsum(st.fz * st.y for st in unsym.stations)
    assert roll == pytest.approx(_UNSYM_ROLL[name], abs=0.5), name
    cases = [c for c in build_balanced_cases(project) if is_unsymmetrical_htail(c)]
    assert {c.hand for c in cases} == {"R", "L"}, name
    for c in cases:
        want = roll if c.hand == "R" else -roll
        assert _fin_root_mx(c, model) == pytest.approx(want, rel=1e-9), (name, c.hand)


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_deck_carries_one_induced_set_and_never_the_lumped_set(name):
    """G-51.3, G-51.6 and G-51.15's shape (D-51.4b), on every lateral and
    engine-out case: exactly one induced set, on the h-tail member, with no net
    lift, no pitch and the fin condition's ``M_r`` as its roll."""
    project = _project(name)
    model = build_lra_model(project)
    fins = {r.case: r for r in build_tail_span(project)["vtail"]}
    cases = build_balanced_cases(project)
    assert not any(c.label == HTAIL_UNSYM_LABEL for c in cases), name
    seen = 0
    for c in cases:
        strips = [ld for ld in c.loads if ld.source == INDUCED_ROLL_SOURCE]
        if not (is_lateral(c) or is_engine_out(c)):
            assert not strips, (name, c.label)
            continue
        fin = fins[c.label]
        assert len(strips) == len(fin.tip_transfer.induced.stations), (name, c.label, c.hand)
        assert {_member_key(ld, model.members) for ld in strips} == {"htail"}
        assert not [ld for ld in c.loads if ld.source == "vtail-induced-roll"]
        assert math.fsum(ld.fz for ld in strips) == pytest.approx(0.0, abs=1e-6)
        assert math.fsum(ld.fz * ld.x for ld in strips) == pytest.approx(0.0, abs=1e-3)
        assert math.fsum(ld.my for ld in strips) == pytest.approx(0.0, abs=1e-3)
        m_r = math.fsum(ld.fz * ld.y for ld in strips)
        # The computed hand is the fin result's own; the twin is its mirror.
        sign = math.copysign(1.0, m_r * fin.tip_transfer.induced.m_r)
        assert m_r == pytest.approx(sign * fin.tip_transfer.induced.m_r, rel=1e-9)
        own = _fin_root_mx(c, model) - m_r
        assert own == pytest.approx(sign * vtail_root_roll(fin.stations, air_only=True),
                                    rel=1e-9), (name, c.label, c.hand)
        # ...and the couple adds to the fin's own bending (AC ¶5d).
        assert m_r * own > 0.0, (name, c.label, c.hand)
        seen += 1
    assert seen, name


# --------------------------------------------------------------------------- #
# G-51.1a / G-51.2 -- the fin view's pairings
# --------------------------------------------------------------------------- #
def test_an_engine_out_fin_result_pairs_with_the_decks_parent():
    """G-51.1a: one owner (``oei_parent_point``), so one flight state."""
    from sloads.mass_distribution import tail_surface_weight

    project = _project("atr42_100")
    points = {p.case: p for p in vn_points(project)}
    weight = tail_surface_weight(project, "htail")
    deck = {c.label: c for c in build_balanced_cases(project) if is_engine_out(c)}
    engine_out = [r for r in build_tail_span(project)["vtail"]
                  if r.case.startswith("ONE ENGINE OUT")]
    assert engine_out
    for r in engine_out:
        t = r.tip_transfer
        assert t is not None and t.paired_case is not None, r.case
        if r.case in deck:
            assert t.paired_case == deck[r.case].vn_case, r.case
        point = points[t.paired_case]
        assert math.isclose(t.air_lb, point.lt, rel_tol=1e-12), r.case
        assert math.isclose(t.inertia_lb, -point.nz * weight, rel_tol=1e-12), r.case


@pytest.mark.parametrize("name", _T_TAILS)
def test_htail_unsym_carries_the_htail_tables_own_set(name):
    """G-51.2: fz, myy and mxx summed from the 23.427(a) table's stations."""
    project = _project(name)
    spans = build_tail_span(project)
    unsym = next(r for r in spans["htail"] if r.case == "UNSYMMETRICAL")
    fin = next(r for r in spans["vtail"] if r.case == HTAIL_UNSYM_LABEL)
    t = fin.tip_transfer
    x_tip = fin.stations[-1].x
    assert t.mxx == pytest.approx(math.fsum(st.fz * st.y for st in unsym.stations),
                                  rel=1e-9)
    assert t.mxx == pytest.approx(_UNSYM_ROLL[name], abs=0.5)
    assert t.fz == pytest.approx(math.fsum(st.fz for st in unsym.stations), rel=1e-12)
    assert t.myy == pytest.approx(math.fsum(
        (x_tip - st.x) * st.fz + st.myy_free for st in unsym.stations), rel=1e-12)
    assert t.induced is None
    assert fin.case_ref.case_id == "VT-20" and fin.case_ref.far_reference == "23.427(c)"
    assert fin.safety_factor == unsym.safety_factor
    assert fin.lt25 == fin.lt50 == 0.0     # no air load on the fin of its own
    _, moment = ttail_transfer_to_airplane(t.fz, t.myy, t.mxx)
    assert moment[0] == t.mxx


# --------------------------------------------------------------------------- #
# G-51.4 / G-51.5 / G-51.7 / G-51.8 -- the moment
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _T_TAILS)
def test_the_induced_moment_is_the_ac_formula_on_one_beta_rule(name):
    """G-51.4: AC 23-9 ¶5a p3, ``M_r = 0.3 q S_H b_H beta`` (lb-ft, radians).

    The formula is the definition, so the identity is to 1e-9; the note's
    measured figures are pinned to ±0.1 %. beta is the fin's own load as an
    angle, which reproduces the three 23.441 rules exactly (D-51.3a).
    """
    project = _project(name)
    vt = effective_vtail_inputs(project)
    ht = resolve_tail_planform(project, "htail")
    s_h, b_h = ht.area / IN2_PER_FT2, 2.0 * ht.span / IN_PER_FT
    beta_rudder = (vt.rudder_deflection_deg * vt.rudder_large_deflection_factor
                   * _effectv(vt))
    fins = _fins(name)
    for label, want in _M_R[name].items():
        i = fins[label].tip_transfer.induced
        assert abs(i.m_r) == pytest.approx(
            0.3 * i.q_psf * s_h * b_h * math.radians(i.beta_deg) * IN_PER_FT,
            rel=1e-9), label
        assert abs(i.m_r) == pytest.approx(want, rel=1e-3), (name, label)
        if label == "SUDDEN RUDDER":
            assert i.beta_deg == pytest.approx(beta_rudder, rel=1e-9)
        elif label == "YAW TO SIDESLIP":
            assert i.beta_deg == pytest.approx(19.5 - beta_rudder, rel=1e-9)
        elif label == "YAW 15 NEUTRAL":
            assert i.beta_deg == pytest.approx(15.0, rel=1e-9)
        elif label == "SIDE GUST":
            # 1.2 U/V, U and V equivalent (ft/s): not SELECT's alleviated angle.
            assert "1.2 U/V" in i.basis
        else:
            cond = next(c for c in default_critical(project).conditions
                        if c.label == label)
            q = dynamic_pressure_psf(cond.case_ref.speed_kt)
            load = abs(cond.lt25 + cond.lt50)
            assert i.beta_deg == pytest.approx(
                load / (_avt(vt) / DEG_PER_RAD * q * vt.vtail_area_sqft), rel=1e-9)


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_induced_moment_adds_to_the_fins_own_bending(name):
    """G-51.5: AC 23-9 ¶5d p5-6, "the moment due to the horizontal surface adds
    to the moment due to the vertical tail load"."""
    for label, r in _fins(name).items():
        i = r.tip_transfer.induced if r.tip_transfer else None
        if i is None:
            continue
        assert i.m_r * vtail_root_roll(r.stations, air_only=True) > 0.0, (name, label)


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_fin_view_states_its_root_with_the_tip_set(name):
    """G-51.7 (D-51.10), the note's figures, airplane axes."""
    fins = _fins(name)
    for label, want in _ROOT_WITH_TIP[name].items():
        assert vtail_root_roll_with_tip(fins[label]) == pytest.approx(want, rel=1e-3), (
            name, label)


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_pure_attitude_moments_sit_in_the_acs_band(name):
    """G-51.8: AC 23-9 ¶5d, "4 to 6 times the value produced by a 100-80 percent
    distribution". Gated on the two pure-attitude conditions; the rudder-affected
    and engine-out ratios fall outside by construction and are only stated."""
    fins = _fins(name)
    unsym = abs(_UNSYM_ROLL[name])
    for label in ("YAW 15 NEUTRAL", "SIDE GUST"):
        ratio = abs(fins[label].tip_transfer.induced.m_r) / unsym
        assert 4.0 <= ratio <= 6.0, (name, label, ratio)


# --------------------------------------------------------------------------- #
# G-51.9 / G-51.10 -- the stated limits
# --------------------------------------------------------------------------- #
def test_the_htail_check_is_retired():
    """G-51.9 retired (D-51.7a, #334): the horizontal tail carries the moment,
    so no ratio is formed and no fixture warns that the moment sizes it."""
    for name in _T_TAILS:
        for r in _fins(name).values():
            i = r.tip_transfer.induced if r.tip_transfer else None
            assert i is None or not hasattr(i, "htail_ratio"), (name, r.case)
        assert not [w for w in consistency_warnings(_project(name))
                    if w.code == "ttail_induced_roll_sizes_htail"], name


# --------------------------------------------------------------------------- #
# G-51.12 ... G-51.16 -- the horizontal tail carries M_r (note 51 §10)
# --------------------------------------------------------------------------- #
def _induced_htails(spans):
    """``{fin condition: its INDUCED ROLL h-tail result}``."""
    prefix = f"{INDUCED_ROLL_LABEL} — "
    return {r.case[len(prefix):]: r for r in spans["htail"] if r.case.startswith(prefix)}


@pytest.mark.parametrize("name", _T_TAILS)
def test_each_induced_set_carries_m_r_and_no_lift(name):
    """G-51.12 (D-51.12 (iii)): ``Σ fz = 0``, ``Σ fz·y = M_r``, and each root
    carries ``M_r/2`` -- chord-proportional at 25 % chord, antisymmetric."""
    spans = build_tail_span(_project(name))
    carriers = [r for r in spans["vtail"] if r.tip_transfer and r.tip_transfer.induced]
    assert carriers, name
    for fin in carriers:
        i = fin.tip_transfer.induced
        st = i.stations
        assert st, (name, fin.case)
        assert math.fsum(s.fz for s in st) == pytest.approx(0.0, abs=1e-9 * abs(i.m_r))
        assert math.fsum(s.fz * s.y for s in st) == pytest.approx(i.m_r, rel=1e-9)
        stbd = math.fsum(s.fz * s.y for s in st if s.y > 0.0)
        port = math.fsum(s.fz * s.y for s in st if s.y < 0.0)
        assert stbd == pytest.approx(0.5 * i.m_r, rel=1e-9), (name, fin.case)
        assert port == pytest.approx(0.5 * i.m_r, rel=1e-9), (name, fin.case)
        assert all(s.f_inertia == 0.0 for s in st)


@pytest.mark.parametrize("name", _T_TAILS)
def test_each_induced_roll_condition_bends_the_htail_as_measured(name):
    """G-51.13 (note 51 §10.1, ±0.1 %): one ``INDUCED ROLL`` h-tail condition
    per fin condition carrying ``M_r``, with that fin condition's factor, the
    23.427(c) reference and an id in the HT-20 band."""
    from sloads.case_ids import HTAIL_BAND_TTAIL

    spans = build_tail_span(_project(name))
    fins = {r.case: r for r in spans["vtail"]}
    htails = _induced_htails(spans)
    assert set(htails) == set(_INDUCED_BENDING[name]), name
    ids = []
    for fin_case, want in _INDUCED_BENDING[name].items():
        r = htails[fin_case]
        assert htail_root_bending(r) == pytest.approx(want, rel=1e-3), (name, fin_case)
        assert r.safety_factor == fins[fin_case].safety_factor, (name, fin_case)
        assert r.case_ref.far_reference == "23.427(c)"
        assert r.case_ref.component == "htail"
        ids.append(r.case_ref.case_id)
    assert sorted(ids) == [f"HT-{HTAIL_BAND_TTAIL + k:02d}" for k in range(len(ids))]


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_governing_htail_bending_moves_on_the_atr_alone(name):
    """G-51.14 (replaces G-51.9): the ATR's governing per-side h-tail root
    bending is ONE ENGINE OUT VD's 233,122 lb-in (+44.4 % on GUST DN
    RETRACTED's 161,404); the RJ's stays GUST DN RETRACTED's 349,920."""
    spans = build_tail_span(_project(name))
    label, want = _GOVERNING[name]
    governing = max(spans["htail"], key=htail_root_bending)
    assert governing.case == label, name
    assert htail_root_bending(governing) == pytest.approx(want, rel=1e-3), name


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_strips_close_exactly_as_the_fin_tip_couple_did(name, monkeypatch):
    """G-51.15 (D-51.4b): rebuild the deck with D-51.4a's fin-tip couple in
    place of the strips, and every lateral and engine-out case's ``p_dot``,
    ``q_dot`` and ``r_dot`` -- and the fin-root rolling moment -- are the
    same. Moving the moment onto the horizontal tail moves no closure."""
    from sloads.export.coordinates import tail_station_to_airplane
    from sloads.models import BalancedLoad
    from sloads.modules.balance import air
    from sloads.tail_geometry import VTAIL

    project = _project(name)
    model = build_lra_model(project)
    after = {(c.label, c.hand): c for c in build_balanced_cases(project)
             if is_lateral(c) or is_engine_out(c)}
    real = air.vtail_sets

    def with_couple(result):
        loads = [ld for ld in real(result) if ld.source != INDUCED_ROLL_SOURCE]
        t = result.tip_transfer
        if t is not None and t.induced is not None and result.stations:
            tip = result.stations[-1]
            x, y, z = tail_station_to_airplane(tip.x, tip.y, VTAIL, root_z=tip.z)
            loads.append(BalancedLoad(x=x, y=y, z=z, mx=t.induced.m_r,
                                      source="vtail-induced-roll", side="C"))
        return loads

    monkeypatch.setattr(air, "vtail_sets", with_couple)
    before = {(c.label, c.hand): c for c in build_balanced_cases(project)
              if is_lateral(c) or is_engine_out(c)}
    assert before.keys() == after.keys() and after, name
    for key, a in after.items():
        b = before[key]
        for q in ("p_dot", "q_dot", "r_dot"):
            assert getattr(a, q) == pytest.approx(getattr(b, q), rel=1e-9, abs=1e-12), (key, q)
        assert _fin_root_mx(a, model) == pytest.approx(_fin_root_mx(b, model), rel=1e-9), key


@pytest.mark.parametrize("name", _T_TAILS)
def test_the_trim_part_is_the_fin_transfers_pairing(name):
    """G-51.16 (one pairing owner): take the induced set out of an ``INDUCED
    ROLL`` condition and what is left is the fin transfer's own -- its total
    ``fz`` (trim plus inertia) and its trim load's moment about the fin tip at
    the published centre of pressure. The inertia is smeared at each strip's
    reference axis, as on every h-tail condition and HTAIL UNSYM (D-51.2a),
    not at the transfer's mid-chord lumped station."""
    spans = build_tail_span(_project(name))
    fins = {r.case: r for r in spans["vtail"]}
    for fin_case, r in _induced_htails(spans).items():
        t = fins[fin_case].tip_transfer
        induced = {(s.x, s.y): s for s in t.induced.stations}
        trim = [(s, induced[(s.x, s.y)]) for s in r.stations]
        fz = math.fsum(s.fz - i.fz for s, i in trim)
        assert fz == pytest.approx(t.fz, rel=1e-9), (name, fin_case)
        air_myy = math.fsum((t.x_tip - s.x) * (s.fz - s.f_inertia - i.fz)
                            + s.myy_free - i.myy_free for s, i in trim)
        assert air_myy == pytest.approx((t.x_tip - t.x_air) * t.air_lb, rel=1e-9), \
            (name, fin_case)


def test_the_mach_limit_warns_on_the_rjs_side_gust_alone():
    """G-51.10 (D-51.8 i): the RJ's side gust is at Mach 0.692."""
    for name in _T_TAILS:
        codes = [w for w in consistency_warnings(_project(name))
                 if w.code == "ttail_induced_roll_mach"]
        if name == "concept_regional_jet":
            assert len(codes) == 1 and "SIDE GUST" in codes[0].message
        else:
            assert not codes, name
    i = _fins("concept_regional_jet")["SIDE GUST"].tip_transfer.induced
    assert i.mach == pytest.approx(0.692, abs=1e-3) and i.mach > AC23_9_MACH_WARN


def test_an_entered_dihedral_is_stated_and_warned_but_scales_nothing():
    """G-51.10 (D-51.8 ii): the AC has no dihedral effect and no method for one."""
    project = _project("concept_regional_jet")
    before = {k: r.tip_transfer.induced.m_r for k, r in _fins("concept_regional_jet").items()
              if r.tip_transfer and r.tip_transfer.induced}
    tilted = copy.deepcopy(project)
    tilted.geometry.parametric.htail_dihedral_deg = 6.0
    after = {r.case: r for r in build_tail_span(tilted)["vtail"]}
    for label, m_r in before.items():
        i = after[label].tip_transfer.induced
        assert i.m_r == m_r and i.dihedral_deg == 6.0, label
        assert any("dihedral 6.00 deg" in n for n in after[label].notes), label   # the deg row (#312)
    assert [w for w in consistency_warnings(tilted) if w.code == "ttail_htail_dihedral"]
    assert not [w for w in consistency_warnings(project) if w.code == "ttail_htail_dihedral"]


def test_a_refused_build_is_stated_and_the_dihedral_still_warns():
    """#344. The spanwise build refusing a present-but-invalid input used to
    switch all three T-tail warnings off. It is now stated, quoting the
    refusal, and the dihedral warning -- read from the entered field, not from
    a resolved fin condition -- still fires. A chain that does not exist yet
    (``MissingInputError``) adds nothing."""
    from unittest import mock

    from sloads.models import MissingInputError
    tilted = copy.deepcopy(_project("atr42_100"))
    tilted.geometry.parametric.htail_dihedral_deg = 3.0

    def codes(side_effect=None, value=None):
        with mock.patch("sloads.modules.tail_span.build_tail_span",
                        side_effect=side_effect, return_value=value):
            return {w.code: w.message for w in consistency_warnings(tilted)
                    if w.code.startswith("ttail_")}

    refused = codes(side_effect=ValueError("a stubbed tail-span refusal"))
    assert "a stubbed tail-span refusal" in refused["ttail_induced_roll_unchecked"]
    assert "ttail_htail_dihedral" in refused
    absent = codes(side_effect=MissingInputError("no flight envelope"))
    assert set(absent) == {"ttail_htail_dihedral"}
    unresolved = codes(value={"vtail": [], "htail": []})     # no fin condition resolves
    assert set(unresolved) == {"ttail_htail_dihedral"}


# --------------------------------------------------------------------------- #
# G-51.11 -- isolation
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", _T_TAILS)
def test_a_conventional_tail_carries_none_of_it(name):
    """G-51.11: flipping the layout removes every new load, row and warning."""
    project = copy.deepcopy(_project(name))
    project.geometry.parametric.tail_type = TailType.CONVENTIONAL
    fins = build_tail_span(project)["vtail"]
    assert all(r.tip_transfer is None for r in fins), name
    assert not any(r.case == HTAIL_UNSYM_LABEL for r in fins), name
    assert not _induced_htails(build_tail_span(project)), name
    for c in build_balanced_cases(project):
        assert not any(ld.source == INDUCED_ROLL_SOURCE for ld in c.loads), (name, c.label)
    assert not [w for w in consistency_warnings(project) if w.code.startswith("ttail_")]


# --------------------------------------------------------------------------- #
# One owner each (rule 3)
# --------------------------------------------------------------------------- #
def test_the_gust_velocity_rule_has_one_owner():
    """``constants.gust_ude_fps`` holds the 23.333(c) taper, which four modules
    spelled until #328 (``flight_envelope``, ``vn_diagram`` and ``select`` twice).
    An AST scan for its 30,000 ft span, so a docstring may still quote it."""
    import ast

    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "sloads")
    offenders = []
    for folder, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".py") or f == "constants.py" and folder == root:
                continue
            path = os.path.join(folder, f)
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and node.value in (30000.0, 30000):
                    offenders.append(f"{path}:{node.lineno}")
    assert not offenders, offenders


if __name__ == "__main__":
    import traceback

    runs = []
    for key, fn in sorted(globals().items()):
        if not key.startswith("test_") or not callable(fn):
            continue
        if fn.__code__.co_argcount:
            runs += [(f"{key}[{n}]", fn, (n,)) for n in _T_TAILS]
        else:
            runs.append((key, fn, ()))
    failed = 0
    for label, fn, args in runs:
        try:
            fn(*args)
            print(f"PASS {label}")
        except Exception:
            failed += 1
            print(f"FAIL {label}")
            traceback.print_exc()
    print(f"\n{len(runs) - failed}/{len(runs)} passed")
    sys.exit(1 if failed else 0)
