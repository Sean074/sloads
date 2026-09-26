"""The rolling conditions arrive complete (design note 52, #306): gates G-52.1-13.

FAR 23.349 builds two wing cases the suite always selected but never delivered
whole. **ACRL** (23.349(a)) modifies symmetric condition A -- 100 % of its air
load on the governing side, ``p`` % on the other -- and reacts the unbalanced
rolling moment ``UNB = (1 - p/100) * condition A root Mxx`` through WINGINER's
unit-roll inertia. **TORS** (23.349(b)) adds ``Δcm = -0.01 * δ`` over the
aileron to the steady-roll air load.

Oracle policy (``CLAUDE.md``): Appendix A was run at the manual's pre-1996
70->75 % rule (71.03 % on the GA6); 23.349(a)(2) as amended by Amdt 23-48 is
75 % flat, registered in ``docs/20_theory/02_approved_corrections.md``
§23.349(a)(2). So the printed case 160 is held here by a **test-built case**
at the printed inputs (G-52.12, D-52.12) -- the ``.BAS`` math stays locked
whatever the rule -- and the shipped fixture, whose ACRL row is derived since
#306, is asserted at the amended figures, each computed here and stated
beside the printed one.

Reference: Ref 1 Ch 12 pp. 91-93, Ch 13 pp. 95-96; Appendix A pp. 212, 216,
219, 225, 226.
"""

import math
import os
import re
import sys
from dataclasses import replace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import WingLoadCase, io
from sloads import mass_distribution as md
from sloads.constants import ROLL_OTHER_SIDE_PERCENT, UnsupportedCategoryError, other_side_percent
from sloads.derived_geometry import wing_plane
from sloads.models import VnPoint
from sloads.modules.airloads import air_load_distribution
from sloads.modules.flight_envelope import build_envelope
from sloads.modules.net_loads import build_net_loads
from sloads.modules.rolling import (
    accel_roll_unbalanced_moment,
    aileron_cm_increment,
    condition_a_root_mxx,
    roll_acceleration,
    steady_roll_aero,
)
from sloads.modules.select import build_critical
from sloads.modules.wing_inertia import inertia_units, wing_inertia_distribution
from sloads.modules.wing_variants import wing_variant_table

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GA = os.path.join(_ROOT, "examples", "ga6_normal.project.json")


def _oracle(actual, printed, rel=1e-3, abs_=2.0):
    """Note 52 §4: oracle pins at ±0.1 %, with the printed integers' own floor."""
    return math.isclose(actual, printed, rel_tol=rel, abs_tol=abs_)


def _ga6():
    return io.load_project(_GA)


def _units(p):
    wm = p.wing_mass
    return inertia_units(p.geometry.by_name(wm.surface), wm, *wing_plane(p, wm.surface),
                         panel_weight_lb=md.panel_weight(p))


def _air(p, cl, v):
    wm = p.wing_mass
    return air_load_distribution(p.geometry.by_name(wm.surface), p.aero.by_name(wm.surface),
                                 cl, v, *wing_plane(p, wm.surface))


def _condition_a_142() -> VnPoint:
    """Appendix A case 142 Pt A -- condition A at CG2, 12,000 ft (p. 208), at
    its printed CL and speed (the air run of case 160, p. 212)."""
    return VnPoint(case=142, condition="STALL +N", config="CRUISE", cg="CG2",
                   altitude_ft=12000.0, v_eas_kt=116.0, nz=3.8, alpha_deg=0.0,
                   g_corr=1.0, cl=1.55, m_wf=0.0, lzw=0.0, lt=0.0, dx=0.0)


# --------------------------------------------------------------------------- #
# G-52.2, G-52.13 -- one percentage, acrobatic flagged
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("weight", [800.0, 1000.0, 3400.0, 12500.0, 40000.0])
@pytest.mark.parametrize("category", ["N", "U", "C", " n "])
def test_the_percentage_is_75_flat(weight, category):
    """**G-52.2** (D-52.11): 23.349(a)(2) as amended by Amdt 23-48 -- 75 % at
    every weight, where the manual's rule gave 71.04 % at 3400 lb."""
    assert other_side_percent(weight, category) == ROLL_OTHER_SIDE_PERCENT == 75.0


def test_an_acrobatic_project_is_flagged_not_defaulted():
    """**G-52.2/G-52.13** (D-52.7): the owner refuses by name, and FLTLOADS --
    which reads it for the AC ROLL factor -- refuses with it."""
    with pytest.raises(UnsupportedCategoryError, match=r"23\.349\(a\)\(1\)"):
        other_side_percent(3400.0, "A")
    p = _ga6()
    p.speeds.category = "A"
    with pytest.raises(UnsupportedCategoryError):
        build_envelope(p)


# --------------------------------------------------------------------------- #
# G-52.1, G-52.12 -- the derivation, and the printed case 160 held
# --------------------------------------------------------------------------- #
def test_the_condition_a_root_is_the_printed_one():
    """The air run UNB is derived from: case 160's airloads *are* condition A
    (case 142 Pt A, p. 208), root Mxx +514,475 (p. 212)."""
    assert _oracle(condition_a_root_mxx(_ga6(), _condition_a_142()), 514475)


def test_the_derived_unb_is_the_amended_quarter_of_the_root():
    """**G-52.1**: ``(1 - 0.75) * 514,475 = 128,619`` lb-in, WINGINER's sign.
    The manual's 149,043 (pp. 96, 219) is the 71.03 % figure the register
    records as the original."""
    root = condition_a_root_mxx(_ga6(), _condition_a_142())
    unb = accel_roll_unbalanced_moment(root, other_side_percent(3400.0, "N"))
    assert _oracle(unb, -128619)
    # The same owner at the manual's percentage reproduces the print.
    assert _oracle(accel_roll_unbalanced_moment(root, 71.03), -149043)


def test_the_printed_case_160_is_held_by_a_test_built_case():
    """**G-52.12** (D-52.12): case 160 built from its printed inputs -- nz
    -3.25, nx +0.4009, UNB -149,043, CL 1.55 at 116 kt -- reproduces the
    printed WINGINER (p. 219) and NETLOADS (p. 225) root rows. The fixture no
    longer enters this case; the ``.BAS`` math is locked here instead.

    WINGINER is held at ±0.1 %; the net rows at the NETLOADS oracle tests'
    0.2 % band (``test_net_loads._close``): the air at CL 1.55 / 116 kt is
    514,061 against the printed 514,475, -0.08 %, and that same 414 lb-in is
    -0.11 % of the smaller net."""
    p = _ga6()
    u = _units(p)
    case = WingLoadCase("160", nz=-3.25, nx=0.4009, unbal_moment=-149043.0)
    inertia = wing_inertia_distribution(case, u).stations[0]
    air = _air(p, 1.55, 116.0).stations[0]
    assert _oracle(roll_acceleration(-149043.0, u.iwxx), -13.287, abs_=0.0)
    assert _oracle(inertia.sz, -1126) and _oracle(inertia.mxx, -124095)
    assert _oracle(inertia.myy, 30410)
    assert _oracle(air.mxx, 514475)
    net = {q: getattr(air, q) + getattr(inertia, q) for q in ("sz", "mxx", "myy", "mzz")}
    assert _oracle(net["sz"], 5310, rel=2e-3) and _oracle(net["mxx"], 390380, rel=2e-3)
    assert _oracle(net["myy"], -48306, rel=2e-3) and _oracle(net["mzz"], -87026, rel=2e-3)


def test_winginer_at_the_derived_unb():
    """**G-52.3**: the same case at the amended couple -- ``θ̈ = UNB*g/Iwxx``
    ≈ -11.47 (128,619 * 386 / 4,330,081) beside the printed -13.287, and the
    root row it drives at the printed factors (computed here: Sz -1046.3,
    Mxx -114,286; the note's -1058 / -115,500 were hand estimates)."""
    p = _ga6()
    u = _units(p)
    unb = accel_roll_unbalanced_moment(514475.0, 75.0)
    assert math.isclose(roll_acceleration(unb, u.iwxx), -11.468, rel_tol=1e-3)
    root = wing_inertia_distribution(
        WingLoadCase("160", nz=-3.25, nx=0.4009, unbal_moment=unb), u).stations[0]
    assert math.isclose(root.sz, -1046.3, rel_tol=1e-3)
    assert math.isclose(root.mxx, -114286.3, rel_tol=1e-3)


# --------------------------------------------------------------------------- #
# G-52.4, G-52.6, G-52.10, G-52.11 -- what the GA6 delivers
# --------------------------------------------------------------------------- #
def _delivered(label):
    loads = build_net_loads(_ga6())
    return tuple(next(r for r in fam if r.case == label)
                 for fam in (loads.wing_air, loads.wing_inertia, loads.wing_net))


def test_the_delivered_acrl_air_is_condition_as():
    """**G-52.10**: on the delivered run, the air is condition A's -- the
    ``STALL +N`` point at the picked AC ROLL point's weight, altitude, CG and
    configuration -- to the identity, on the variant table and on NETLOADS
    alike, never the roll point's airplane-average lift."""
    p = _ga6()
    env = build_envelope(p)
    vn = {q.case: q for q in env.vn}
    table = wing_variant_table(p, env)
    for v in table.by_slot("ACRL"):
        pick = vn[v.case]
        cond_a = vn[v.cond_a_case]
        assert (cond_a.condition, cond_a.cg, cond_a.altitude_ft, cond_a.config) == \
            ("STALL +N", pick.cg, pick.altitude_ft, pick.config)
        assert (v.cl, v.v_eas_kt) == (cond_a.cl, cond_a.v_eas_kt)
        assert math.isclose(v.air_root_mxx, condition_a_root_mxx(p, cond_a), rel_tol=1e-9)
        assert math.isclose(v.unbal_moment, -0.25 * v.air_root_mxx, rel_tol=1e-12)
    gov = table.governing()["ACRL"]
    air, _, _ = _delivered("ACRL")
    assert math.isclose(air.stations[0].mxx, gov.air_root_mxx, rel_tol=1e-9)


def test_the_delivered_acrl_pick_and_its_numbers():
    """**G-52.11 / G-52.4**, as measured. The AC ROLL point is balanced at
    ``0.875 * 3.8 = 3.325`` (D-52.11), and SELECT's largest-LZW criterion
    among the CG2 roll points is then a 0.13 % tie across altitude -- inside
    the balance's own 0.5 % -- which sea level (V-n case 40, 117.45 kt)
    takes from the 12,000 ft point the manual prints (case 160, 116 kt; CL
    1.328 printed, 1.361 at the amended factor). Condition A there is CL
    1.519 at 117.45 kt (the case 22 air, p. 206), root 516,566; the 100 %
    side's net root bending is +400,817 against the printed +390,380: +2.7 %,
    the amendment's +2 % and the air point's +0.4 % together."""
    crit = build_critical(_ga6())
    acrl = next(c for c in crit.conditions if c.component == "wing" and c.label == "ACRL")
    got = {lv.key: lv.value for lv in acrl.loads}
    assert math.isclose(got["load_factor_nz"], 3.325, abs_tol=0.005 * 3.325)
    assert math.isclose(got["v_eas"], 117.45, rel_tol=2e-3)
    assert got["other_side_percent"] == 75.0
    assert math.isclose(got["condition_a_cl"], 1.519, rel_tol=5e-3)
    assert math.isclose(got["unbalanced_rolling_moment"], -129141.6, rel_tol=1e-3)
    assert math.isclose(got["roll_acceleration"], -11.515, rel_tol=1e-3)
    _, _, net = _delivered("ACRL")
    root = net.stations[0]
    assert math.isclose(root.sz, 5404.4, rel_tol=1e-3)
    assert math.isclose(root.mxx, 400817.0, rel_tol=1e-3)
    assert math.isclose(root.myy, -50188.0, rel_tol=1e-3)


@pytest.mark.parametrize("label", ["ACRL", "TORS"])
def test_air_plus_inertia_is_net_on_the_rolling_cases(label):
    """**G-52.6**: the station-sum identity on both delivered rolling cases."""
    air, inertia, net = _delivered(label)
    for a, i, n in zip(air.stations, inertia.stations, net.stations):
        for q in ("sz", "sx", "mxx", "myy", "mzz"):
            assert math.isclose(getattr(n, q), getattr(a, q) + getattr(i, q), abs_tol=1e-6)


def test_the_printed_knit_checks():
    """**G-52.6**'s knit checks on the printed rows: 514,475 - 124,095 =
    390,380 (MX), -78,716 + 30,410 = -48,306 (MY), -57,444 + 11,161 = -46,283
    (case 138 MY) -- the print is internally consistent, so G-52.12's lock is
    one statement, not three."""
    assert 514475 - 124095 == 390380
    assert -78716 + 30410 == -48306
    assert -57444 + 11161 == -46283


# --------------------------------------------------------------------------- #
# G-52.5, G-52.7, G-52.8 -- the steady roll and its cm increment
# --------------------------------------------------------------------------- #
def test_tors_with_blank_butt_lines_is_the_printed_run():
    """**G-52.5 / G-52.8**: blank aileron butt lines reduce to exactly the
    printed path -- the aero surface is the fixture's own object -- and the
    net case 138 root is p. 226's (Sz +3823, MX +282,393, MY -46,283) in the
    printed-integer band the NETLOADS oracle tests use."""
    p = _ga6()
    assert p.aileron_loads.inboard_y_in is None
    aero = p.aero.by_name("wing")
    assert steady_roll_aero(p, aero, "TORS", None, []) is aero
    _, _, net = _delivered("TORS")
    root = net.stations[0]
    assert _oracle(root.sz, 3823, rel=2e-3) and _oracle(root.mxx, 282393, rel=2e-3)
    assert _oracle(root.myy, -46283, rel=2e-3)


def test_tors_with_the_aileron_entered_carries_the_increment():
    """**G-52.7** (D-52.5): the aileron at BL 109.28-201 (the planform's own,
    pp. 203, 213) and δ = SELECT's schedule at the case's speed (10.7065°,
    printed 10.703, p. 93) put ``Δcm = -0.107`` over it. Root ΔMyy is
    -18,667 lb-in nose-down, computed here; the note's hand estimate was
    -19,035 from a linear chord and the unstripped integral, 2 % coarser.
    Every other channel is untouched: the increment is a pure moment."""
    base = _delivered("TORS")
    p = _ga6()
    p.aileron_loads = replace(p.aileron_loads, inboard_y_in=109.28, outboard_y_in=201.0)
    loads = build_net_loads(p)
    net = next(r for r in loads.wing_net if r.case == "TORS")
    b, g = base[2].stations[0], net.stations[0]
    assert math.isclose(g.myy - b.myy, -18667.2, rel_tol=1e-3)
    assert (g.sz, g.mxx, g.mzz) == (b.sz, b.mxx, b.mzz)
    crit = build_critical(p)
    tors = next(c for c in crit.conditions if c.component == "wing" and c.label == "TORS")
    delta = next(lv.value for lv in tors.loads if lv.key == "aileron_down_deflection")
    assert math.isclose(delta, 15.0 * 121.3 / 170.0, rel_tol=5e-3)


def test_the_increment_is_a_double_station_step():
    """The table the increment enters (the manual's flap-case pattern,
    pp. 165-166): base up to just inboard of the aileron, base + Δcm from its
    inboard butt line to the tip, and nothing outside it."""
    rows = aileron_cm_increment([(0.0, -0.03), (201.0, -0.03)], 109.28, 201.0, 10.0, 201.0)
    assert rows == [(0.0, -0.03), (109.279, pytest.approx(-0.03)),
                    (109.28, pytest.approx(-0.13)), (201.0, pytest.approx(-0.13))]
    inner = aileron_cm_increment([(0.0, -0.03), (201.0, -0.03)], 50.0, 150.0, 10.0, 201.0)
    assert inner[0] == (0.0, -0.03) and inner[-1] == (201.0, pytest.approx(-0.03))
    assert (150.001, pytest.approx(-0.03)) in inner


# --------------------------------------------------------------------------- #
# G-52.9 -- drift guards
# --------------------------------------------------------------------------- #
def _sources():
    pkg = os.path.join(_ROOT, "sloads")
    for dirpath, _, files in os.walk(pkg):
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as fh:
                    yield os.path.relpath(path, _ROOT), fh.read()


def test_the_retired_rule_lives_nowhere():
    """**G-52.9**: the manual's 70 -> 75 % rule (``70 + 5*(W - 1000)/11500``,
    FLTLOADS's ``1.7 + 0.05*(W - 1000)/11500``) is not computed anywhere; the
    one owner's docstring may name it, in a comment."""
    rule = re.compile(r"11500|1\.7 \+ 0\.05|0\.85 \* np")
    for path, text in _sources():
        code = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
        hits = [ln for ln in code if rule.search(ln) and "``" not in ln]
        assert not hits, f"{path} computes the retired 23.349 percentage: {hits}"


def test_one_producer_of_the_derived_couple():
    """**G-52.9**: ``accel_roll_unbalanced_moment`` is called from the rolling
    owner alone, and FLTLOADS reads ``other_side_percent`` rather than a
    literal."""
    for path, text in _sources():
        if path.endswith(os.path.join("modules", "rolling.py")):
            continue
        assert "accel_roll_unbalanced_moment(" not in text, path
    with open(os.path.join(_ROOT, "sloads", "modules", "flight_envelope.py"),
              encoding="utf-8") as fh:
        assert "other_side_percent(w, cat)" in fh.read()


def test_the_wing_loads_page_states_the_couple():
    """D-52.6's GUI half: the NETLOADS block caption states UNB and θ̈ beside
    the ACRL rows -- derived on the GA6, as entered on the RJ -- and nothing
    where the table runs no accelerated roll (the Baron's filter list)."""
    from sloads.units import UnitSystem
    from oracle_app.results import MODULE_ADVISORIES

    caption = MODULE_ADVISORIES["net_loads"]
    ga6 = caption(_ga6(), UnitSystem.IMPERIAL)
    assert "UNB = -129142 lb-in" in ga6 and "-11.515 rad/s" in ga6
    rj = caption(io.load_project(os.path.join(_ROOT, "examples",
                                              "concept_regional_jet.project.json")),
                 UnitSystem.IMPERIAL)
    assert "-600000 lb-in, as entered" in rj
    assert caption(io.load_project(os.path.join(_ROOT, "examples", "baron_58.project.json")),
                   UnitSystem.IMPERIAL) == ""
