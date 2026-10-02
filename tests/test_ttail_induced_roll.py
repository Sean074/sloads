"""The T-tail's horizontal-tail asymmetry at the fin (design note 51 §9, #328).

No printed oracle covers a T-tail (Appendix A is a conventional empennage; AC
23-9 ¶3), so rule 2's second branch applies: every gate here is an identity or a
closure, with the note's expected figures pinned beside it.

* **G-51.1** the deck's 23.427(a) case carries the (b) roll at the fin root,
  exactly, in both hands.
* **G-51.1a** a one-engine-out fin result pairs with the deck's own 1 g parent.
* **G-51.2** ``HTAIL UNSYM``'s tip roll is its h-tail table's ``Σ fz·y``, and
  the applied-load row carries it.
* **G-51.3** the deck never carries ``HTAIL UNSYM``, and carries exactly one
  induced couple per T-tail lateral or one-engine-out case.
* **G-51.4** ``M_r = 0.3 q S_H b_H beta`` (AC 23-9 ¶5a p3) and its beta rule.
* **G-51.5** its sense is the fin's own root rolling moment's (¶5d p5-6).
* **G-51.6** the deck's fin root carries its own load plus ``M_r``, exactly.
* **G-51.7** the fin view's root rolling moment with the tip set.
* **G-51.8** the AC's own 4-6x band on the pure-attitude conditions.
* **G-51.9** the horizontal-tail check (D-51.7): the ATR's VD engine-out warns.
* **G-51.10** the Mach and dihedral limits (D-51.8).
* **G-51.11** a conventional tail is untouched by all of it.
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
    build_tail_span,
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
#: within 0.05 %.
_M_R = {
    "concept_regional_jet": {
        "SUDDEN RUDDER": 266_727, "YAW TO SIDESLIP": 137_013,
        "YAW 15 NEUTRAL": 310_569, "SIDE GUST": 373_565,
    },
    "atr42_100": {
        "SUDDEN RUDDER": 112_543, "YAW TO SIDESLIP": 53_894,
        "YAW 15 NEUTRAL": 128_028, "SIDE GUST": 162_118,
        "ONE ENGINE OUT — VC (ultimate) (engine 1)": 328_765,
        "ONE ENGINE OUT — VD (limit) (engine 1)": 458_984,
        "ONE ENGINE OUT — VC (ultimate) (engine 2)": 328_765,
        "ONE ENGINE OUT — VD (limit) (engine 2)": 458_984,
    },
}

#: G-51.7: the fin view's root rolling moment with the tip set, airplane axes.
_ROOT_WITH_TIP = {
    "concept_regional_jet": {
        "SUDDEN RUDDER": -706_830, "YAW TO SIDESLIP": +363_087,
        "YAW 15 NEUTRAL": +823_013, "SIDE GUST": -824_818,
    },
    "atr42_100": {
        "SUDDEN RUDDER": -328_155, "YAW TO SIDESLIP": +157_144,
        "YAW 15 NEUTRAL": +373_307, "SIDE GUST": -389_728,
        "ONE ENGINE OUT — VD (limit) (engine 1)": +1_348_459,
        "ONE ENGINE OUT — VD (limit) (engine 2)": -1_348_459,
    },
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
def test_the_deck_carries_one_induced_couple_and_never_the_lumped_set(name):
    """G-51.3 and G-51.6, on every lateral and engine-out case."""
    project = _project(name)
    model = build_lra_model(project)
    fins = {r.case: r for r in build_tail_span(project)["vtail"]}
    cases = build_balanced_cases(project)
    assert not any(c.label == HTAIL_UNSYM_LABEL for c in cases), name
    seen = 0
    for c in cases:
        couples = [ld for ld in c.loads if ld.source == INDUCED_ROLL_SOURCE]
        if not (is_lateral(c) or is_engine_out(c)):
            assert not couples, (name, c.label)
            continue
        assert len(couples) == 1, (name, c.label, c.hand)
        m_r = couples[0].mx
        fin = fins[c.label]
        # The computed hand is the fin result's own; the twin is its mirror.
        sign = 1.0 if abs(m_r - fin.tip_transfer.induced.m_r) < 1e-6 else -1.0
        assert m_r == pytest.approx(sign * fin.tip_transfer.induced.m_r, rel=1e-12)
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
def test_the_htail_check_warns_on_the_atrs_vd_engine_out_alone():
    """G-51.9 (D-51.7): 142.2 % on the VD engine-out case, on one factor basis;
    the VC case is ultimate (SF 1.0) and so sits at 67.9 %, not 101.8 %."""
    ratios = {}
    for name in _T_TAILS:
        for label, r in _fins(name).items():
            i = r.tip_transfer.induced if r.tip_transfer else None
            if i is not None:
                ratios[(name, label)] = i.htail_ratio
    assert ratios[("atr42_100", "ONE ENGINE OUT — VD (limit) (engine 1)")] == \
        pytest.approx(1.422, rel=1e-3)
    assert ratios[("atr42_100", "ONE ENGINE OUT — VC (ultimate) (engine 1)")] == \
        pytest.approx(0.679, rel=1e-3)
    over = {k for k, v in ratios.items() if v > 1.0}
    assert over == {("atr42_100", "ONE ENGINE OUT — VD (limit) (engine 1)"),
                    ("atr42_100", "ONE ENGINE OUT — VD (limit) (engine 2)")}
    assert max(v for (n, _), v in ratios.items() if n == "concept_regional_jet") == \
        pytest.approx(0.534, rel=1e-3)
    warned = [w for w in consistency_warnings(_project("atr42_100"))
              if w.code == "ttail_induced_roll_sizes_htail"]
    assert len(warned) == 2 and all("VD" in w.message for w in warned)


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
