"""Conformance with sstandards Rev B (design note 68, #354; CONVENTIONS.md §0).

sstandards is the shared frames/signs/units standard for the sconfig -> sloads ->
sbeam chain. It ships no code (its §0.1); a complying project keeps a **copy** of
``conventions_vectors.json`` at the revision it states and checks its own code
owners against the blocks that apply. The copy is ``tests/data/sstandards_rev_B.json``
(D-68.2/D-68.8) -- never imported or fetched from the sibling repository.

Every vector block is either tested against its sloads owner (D-68.3) or skipped
with its reason (D-68.4), and every key of the ``constants`` block is either bound
to an owner or declared ownerless with its reason (D-68.9), so a block or key a
later revision adds fails here until it is decided. The two recorded deviations,
D-SL1 and D-SL2 (D-68.5), are asserted **at their deviated values**: moving either
toward the standard breaks the Appendix A oracles, moving it anywhere else breaks
the record. Rev B's practice clauses are not re-tested; their existing gates are
named and asserted present (D-68.10).
"""

import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import constants as C
from sloads import units as U
from sloads.derived_geometry import MacReference, pct_mac_to_station, station_to_pct_mac
from sloads.models.inputs import SurfaceInput
from sloads.modules.wing_geometry import surface_properties

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVISION = "B"
with open(os.path.join(_ROOT, "tests", "data", f"sstandards_rev_{REVISION}.json"),
          encoding="utf-8") as _f:
    VECTORS = json.load(_f)

TESTED = {"constants", "angles", "mac", "percent_mac"}
SKIPPED = {
    "frame_A_to_B": "sloads has no frame-B code; every delivered quantity is frame A "
                    "(CONVENTIONS.md §1)",
    "moment_transfer": "the ported FAR23 modules form scalar per-axis moments per the .BAS "
                       "listings and are oracle-locked, and the export channel is the §6.1 "
                       "identity, so no single M = (r - o) x F helper exists to bind "
                       "(a skip, not a deviation: note 68 Q1)",
}

#: ``constants`` keys -> the sloads owner's value (D-68.3, D-68.9).
OWNERS = {
    "g0_m_s2": U.G_MM_S2 / 1000.0,
    "g0_ft_s2": C.G,                       # 32.174, 1.5e-6 from exact: inside the block's tolerance
    "g0_in_s2": U.G_IN_S2,
    "kt_to_ft_s": C.KT_TO_FPS,
    "in_per_ft": C.IN_PER_FT,
    "in2_per_ft2": C.IN2_PER_FT2,
    "m_per_in": U.IN_TO_MM / 1000.0,
    "m_per_ft": U.FT_TO_M,
    "hp_to_ft_lbf_s": C.FT_LB_S_PER_HP,
    "lbf_to_N": U.LBF_TO_N,
    "deg_to_rad": C.RAD_PER_DEG,
    "lbm_to_kg": U.LB_TO_KG,
    "hp_to_W": U.HP_TO_KW * 1000.0,
    "psi_to_Pa": U.PSI_TO_MPA * 1.0e6,
}
#: Keys whose sloads owner differs from the standard by a recorded deviation.
DEVIATIONS = {
    "rho0_slug_ft3": ("D-SL1", C.RHO_SL, 0.002378),
}
#: Keys sloads has no owner for, each with its reason.
NO_OWNER = {
    "rho0_kg_m3": "the atmosphere is Imperial-internal (constants.RHO_SL, D-SL1); no SI "
                  "density is formed",
    "us_gal_to_L": "sloads states no volume; fuel enters as weight (lb)",
    "kt_to_m_s": "airspeed stays kt in every system (Rev B §5.8; CONVENTIONS.md §2's "
                 "airspeed/altitude carve-out)",
}

#: Rev B practice clauses and the existing gates that hold them (D-68.10).
CITED_GATES = {
    "5.1 one owner per direction": [
        "tests/test_units.py::test_si_round_trip_reproduces_imperial",
        "tests/test_app_components.py::test_converted_field_round_trips_to_imperial",
    ],
    "5.6 every delivered file states its units and frame": [
        "tests/test_deliverable_units.py::test_every_bundle_channel_carries_the_unit_statement",
        "tests/test_delivered_frame_statement.py::test_every_stamped_channel_states_which_way_the_axes_point",
    ],
    "5.9 two channels, derived units checked": [
        "tests/test_deliverable_units.py::test_solver_set_is_dimensionally_consistent",
        "tests/test_deliverable_units.py::test_human_set_is_not_dimensionally_consistent_in_si",
    ],
    "5.10 no Imperial number in an SI output": [
        "tests/test_si_artifacts.py::test_no_si_solver_file_states_an_imperial_number",
        "tests/test_si_artifacts.py::test_no_si_issue_package_states_an_imperial_number",
    ],
    "5.11 precision is a property of the quantity": [
        "tests/test_platform_stability.py::test_every_delivered_cell_prints_at_its_units_precision",
    ],
    "6.1/6.3 frame A is CID 0, loads physical and unfactored": [
        "tests/test_limit_channel.py::test_no_path_in_sloads_multiplies_a_load_by_a_safety_factor",
    ],
}


def _close(actual: float, expected: float, rel: float) -> bool:
    return math.isclose(actual, expected, rel_tol=rel, abs_tol=1e-12 if expected == 0 else 0.0)


def test_compliance_statement_matches_vendored_revision():
    with open(os.path.join(_ROOT, "docs", "10_standard", "CONVENTIONS.md"), encoding="utf-8") as f:
        doc = f.read()
    assert f"Complies with sstandards Rev {REVISION}" in doc
    assert VECTORS["standard"] == "sstandards"
    assert VECTORS["revision"] == REVISION and VECTORS["status"] == "ISSUED"
    # D-68.5: each deviation is recorded in the conventions doc beside the statement.
    for dev in ("D-SL1", "D-SL2"):
        assert dev in doc, f"{dev} is not recorded in CONVENTIONS.md"


def test_every_block_is_tested_or_skipped_with_a_reason():
    blocks = {k for k, v in VECTORS.items() if isinstance(v, dict) and "sections" in v}
    decided = TESTED | SKIPPED.keys()
    assert blocks == decided, f"decide each block: {sorted(blocks ^ decided)}"
    assert not TESTED & SKIPPED.keys()
    assert all(reason.strip() for reason in SKIPPED.values())


def test_every_constant_is_bound_deviated_or_ownerless():
    """D-68.9: no key of the ``constants`` block is passed over in silence."""
    keys = set(VECTORS["constants"]["values"])
    decided = OWNERS.keys() | DEVIATIONS.keys() | NO_OWNER.keys()
    assert keys == decided, f"decide each constant: {sorted(keys ^ decided)}"
    assert not (OWNERS.keys() & DEVIATIONS.keys()) and not (OWNERS.keys() & NO_OWNER.keys())
    assert all(reason.strip() for reason in NO_OWNER.values())


def test_constants():
    """Rev B §5.7: sloads' owners against the exact-SI values, at the block's tolerance."""
    block = VECTORS["constants"]
    v, rel = block["values"], block["rel_tol"]
    bad = {k: (got, v[k]) for k, got in OWNERS.items() if not _close(got, v[k], rel)}
    assert not bad, f"outside rel_tol {rel}: {bad}"


def test_pound_force_over_pound_mass_is_standard_gravity():
    """Rev B §5.5: lbf_to_N / lbm_to_kg = g0, so g0 cancels on an SI mass input."""
    g0 = VECTORS["constants"]["values"]["g0_m_s2"]
    assert _close(U.LBF_TO_N / U.LB_TO_KG, g0, 1e-12)
    assert _close(U.LBF_TO_N / U.LB_TO_KG, U.G_MM_S2 / 1000.0, 1e-12)


def test_the_recorded_deviations_hold_their_recorded_values():
    """D-68.5: D-SL1 and D-SL2 sit at the values recorded in sstandards §8, and both
    are outside the block's tolerance -- otherwise they would not be deviations."""
    block = VECTORS["constants"]
    v, rel = block["values"], block["rel_tol"]
    for key, (dev, got, recorded) in DEVIATIONS.items():
        assert got == recorded, f"{dev}: {key} moved from its recorded {recorded} to {got}"
        assert not _close(got, v[key], rel), f"{dev}: {key} now conforms; retire the deviation"
    # D-SL2: the suite's knot survives beside the exact one, which conforms (test_constants).
    assert C.KT_TO_FPS_SUITE == 1.15 * 88.0 / 60.0
    assert not _close(C.KT_TO_FPS_SUITE, v["kt_to_ft_s"], rel)


def test_angles():
    """Rev B §5.4: degrees at I/O, radians inside trigonometry -- through the one
    factor (``constants.RAD_PER_DEG``) and ``math.radians``, both ways."""
    for case in VECTORS["angles"]["cases"]:
        rel = VECTORS["angles"]["rel_tol"]
        assert _close(case["deg"] * C.RAD_PER_DEG, case["rad"], rel), case
        assert _close(math.radians(case["deg"]), case["rad"], rel), case
        assert _close(case["rad"] * C.DEG_PER_RAD, case["deg"], rel), case


def test_mac_and_lemac():
    """Rev B §4.1: MAC = ∫c² dy / ∫c dy and x_LEMAC = ∫x_LE·c dy / ∫c dy, through
    WINGGEOM's closed-form integrator (the owner behind ``derived_geometry.wing_reference``)."""
    block = VECTORS["mac"]
    surf = SurfaceInput(name="wing",
                        leading_edge=[(x, y) for x, y in block["le"]],
                        trailing_edge=[(x, y) for x, y in block["te"]])
    got = {v.key: v.value for v in surface_properties(surf).values}
    exp, rel = block["expected"], block["rel_tol"]
    assert _close(got["area_per_side"], exp["area_one_side_in2"], rel)
    assert _close(got["mac"], exp["mac_in"], rel)
    assert _close(got["yle_mac_butt_line_of_mac"], exp["y_mac_in"], rel)
    assert _close(got["xle_mac_station_of_mac_le"], exp["x_lemac_in"], rel)


def test_percent_mac():
    """Rev B §4.2: a ``_pct_mac`` value is a percent, and sloads' converters are
    each other's inverse about XLEMAC."""
    rel = VECTORS["percent_mac"]["rel_tol"]
    for case in VECTORS["percent_mac"]["cases"]:
        ref = MacReference(case["x_lemac_in"], case["mac_in"], "override", "wing")
        assert _close(station_to_pct_mac(case["x_cg_in"], ref), case["pct_mac"], rel), case
        assert _close(station_to_pct_mac(case["x_cg_in"], ref) / 100.0, case["fraction"], rel), case
        assert _close(pct_mac_to_station(case["pct_mac"], ref), case["x_cg_in"], rel), case


def test_the_cited_gates_still_exist():
    """D-68.10: Rev B's practice clauses rest on gates elsewhere in the suite. A gate
    renamed or deleted breaks the compliance claim here instead of silently."""
    missing = []
    for clause, gates in CITED_GATES.items():
        for gate in gates:
            path, name = gate.split("::")
            with open(os.path.join(_ROOT, path), encoding="utf-8") as f:
                src = f.read()
            if not re.search(rf"^def {re.escape(name)}\(", src, re.MULTILINE):
                missing.append(f"{clause}: {gate}")
    assert not missing, missing


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
