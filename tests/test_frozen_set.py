"""The 0.8.2 freeze is a manifest, not a promise (design note 44 §6, G-OR-9).

Milestone 0.8.2 builds the oracle technical report — a *view* of an analysis
that is already oracle-locked (note 44 OR-6). Building a view is not an occasion
to adjust what is being viewed, so OR-13 freezes the solver (``sloads/modules``)
and the existing oracle GUI (``oracle_app``'s pages) for the milestone's
duration, additive work excepted.

A prose freeze would not hold. The Appendix A oracles catch a solver change that
moves a printed number, and nothing catches the ones that do not: a rename, a
reordered expression, a formatter's hand. This test hashes every frozen path and
fails on any difference, which is what ``CLAUDE.md`` rule 3 asks of a
cross-cutting convention — a code owner and a drift guard, never a rule alone.

**Updating the manifest is the exception mechanism, not a workaround.** Three
authorities admit a change to a frozen file (OR-13): a new file (not frozen at
all, so not here), the single OR-3 docstring amendment in ``Oracle.py``, and a
blocking-defect fix admitted under OR-15. In every case the commit that changes
the file updates its hash here and names its authority in the commit message.
Regenerate a hash with::

    python -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('PATH').read_bytes()).hexdigest())"

This guard lapses at the 0.8.2 cut: note 44 §6 is milestone-scoped, and the
release that closes the milestone deletes this file.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

#: SHA-256 of every path frozen by note 44 OR-13, taken at the 0.8.2 branch open
#: (2026-08-30). Keys are repo-relative POSIX paths.
MANIFEST: dict[str, str] = {
    # --- the solver (OR-13, row 1) ---------------------------------------
    "sloads/modules/__init__.py": "ad862f182589947ad0d0aad539bd89a77013cf4644e9973bdb4c2227a64102c3",
    "sloads/modules/_vtail.py": "8233445eef930439c5e7e55908ea90b8ecbba278f9a71e1bb3ab38041005c950",
    "sloads/modules/aileron.py": "9b9868b55af4cad68380e82bbb88192d6f0cacbc8d9531e59088aa65d60e3eb6",
    "sloads/modules/airloads.py": "f1b648c5795be73e4fad00c9d78b64bde479637cd4b1050947b1aea7f233643d",
    "sloads/modules/balance.py": "94a2a8c7f40e97647f31834507bbb6b41edc212a22ec332ab169e4fa5c3c1bc2",
    "sloads/modules/balloads.py": "62137ed968f4d7d814b552c76fc0fa17edd56fb8777281357b5aa4f95f11c5ce",
    # OR-15 admission, granted by the owner 2026-09-05 (note 44 §15, OR-108):
    # ``run()`` publishes the four p198 conditions ``select_fuselage`` already
    # computed and this module discarded. Additive -- no value changes and
    # nothing is recomputed.
    "sloads/modules/body_loads.py": "9681f7baa70a5f4388236849c8967ce8d272234257347f3ed0012480f5811c39",
    "sloads/modules/configuration.py": "1c0cd2b1b21b04544eb919d69cfc48c6a151016be151ea4f77a261bf79549667",
    # OR-15 admission, granted by the owner 2026-09-07 (design note 53, D-53.5),
    # scoped to **the torque sign and nothing else** -- not a refactor, not a
    # rename, not formatting in the same file. ``torque_sense`` reads the new
    # ``EngineInput.prop_direction`` and is the one place it reaches a published
    # load; ``_floored_torque`` exists because BASIC's ``INT`` floors, so the
    # sign cannot be applied inside the flooring without a counter-clockwise
    # engine publishing a stoppage torque 1 ft-lb short. Clockwise is the
    # default, so every shipped project is bit-identical and the Appendix A
    # figures are untouched.
    "sloads/modules/engine.py": "73aa5d6019fc22c3c56d0545f4bad61afd2224565327f796f9a0b925fac65432",
    "sloads/modules/flap.py": "3bd3bfa06ddc4922227ee922dce85e46691daa528cca28ca582d18c19034ec52",
    "sloads/modules/flight_envelope.py": "acb92d1e78674588fcafb133903dc905c6e40dab05c0ea1afa6d606d60fcb067",
    # OR-15 admission, granted by the owner 2026-09-07 (design note 44 OR-190),
    # scoped to **two changes and nothing else**: ``_geometry`` becomes public as
    # ``landing_geometry`` so the oracle report's Section 12.1 can print the p230
    # lever-arm oracle from the function the reactions were computed by (a rename
    # and a docstring -- no arithmetic touched), and ``_critical`` becomes
    # ``critical_reaction``, gains a gear argument, and ``run`` emits the largest
    # main-gear *and* nose-gear reaction of each family instead of one row ranked
    # on ``max(main, nose)``. The old rank compared two different gears, so the
    # three-wheel level landing -- the largest nose reaction of its family, and
    # the condition the fuselage section forward-references -- appeared in no
    # summary at all. The shipped condition set goes from 40 to 42.
    "sloads/modules/landing.py": "aa23b91f343558f6d61c454ec99a869a5ffc39c805b153449e9b5f9716723d33",
    "sloads/modules/mach_limit.py": "118af4d9c35b2978d5ee204912329e6c5cf2d7b7381535300ea4ed48ef1b5859",
    "sloads/modules/net_loads.py": "d7566c492beb61207fe90d3c47bade599cd25e2d609403a69dd2129a185855ab",
    # OR-15 admission, granted by the owner 2026-09-07 (note 44 §21, OR-181),
    # scoped to four things and no others -- ``simulate`` and ``_moment``, which
    # are the march itself, are untouched. (1) ``fin_conditions`` publishes the
    # 23.367 cases as fin design conditions, because measured LIMIT against
    # LIMIT they are the *governing* fin load on every twin in the fixture set
    # -- 1.6x baron_58's largest SELECT case, 2.6x atr42_100's, 3.3x
    # dhc8_dash8's -- and the fin was being sized without them (OR-172).
    # (2) the headline load is keyed ``fy_side``, because under ``max_tail_load``
    # every 23.367 row reached the published case file with an ID, a regulation,
    # a speed, a factor and no load at all (OR-180). (3) ``recovered`` is carried
    # out so an uncontrollable case can be printed and *excluded* from the
    # envelope (OR-174). (4) every entered engine is failed in turn, because one
    # engine gives the fin one sense of load and a fin is sized for both
    # (OR-173).
    # OR-15 admission, granted by the owner 2026-09-08 (#231): ``_engine_label``
    # mints its case-name suffix 1-based (" (engine 1)"), because section 10
    # numbers the same engines "Engine 1 / Engine 2" and one physical engine
    # must not answer to two numbers in one document. Widened the same day to
    # the published condition note, which said "Failed engine #0 at butt line
    # 66 in" -- 0-based and unsigned, the same defect class. Those two sites
    # only; the 0-based ``engine_index`` and every computed quantity are
    # untouched.
    "sloads/modules/one_engine_out.py": "007b3f83d3764dd6db9129253cd3b63633ded098f5c92a318f85f287a30bb952",
    # OR-15 admission, granted by the owner 2026-09-05 (note 44 §15, OR-111):
    # the four maneuver conditions publish the unbalanced pitching moment about
    # the CG, whose equation is recovered from SELECT.BAS 5210/5262/5410/5560.
    # Additive -- a new ``LoadValue`` on each; no existing value moves.
    #
    # Second OR-15 admission, granted by the owner 2026-09-06 (note 44 §17,
    # OR-132): every tail condition states the load its control surface carries.
    # ``elevator_load`` was published on 2 of 9 h-tail conditions and
    # ``load_on_rudder`` on 2 of 4 vertical-tail ones, so the report's
    # critical-case tables would have carried a blank column on nine rows for no
    # reason the analysis could give -- both are pure functions of the 25 %/50 %
    # split every one of those conditions already holds. The h-tail half is
    # published in ``_htail_condition``, the one constructor they all pass
    # through, rather than at nine call sites. Additive: every new value is
    # appended, and the one insertion that would have moved an existing column
    # (``SIDE GUST``'s ``Yaw inertia IZZ``) was rewritten to append instead.
    # Second OR-15 admission, granted by the owner 2026-09-07 (note 44 §21,
    # OR-181): **one insertion point** in ``default_critical``, appending the
    # 23.367 fin conditions to the critical set through ``_with_engine_failure``.
    # Every consumer of the critical set already comes through that function
    # (M2R-8, review F-C6), which is what lets Section 6, the chordwise and
    # spanwise distributions, Appendix E and the exported v-tail deck pick the
    # cases up with no change to ``tail_span.py`` or ``taildist.py`` -- neither
    # of which is admitted, and neither of which is touched. The import is
    # function-local because ONENGOUT already reads ``effective_vtail_inputs``
    # from here and a module-level one would close a cycle.
    # Third OR-15 admission, granted by the owner 2026-09-07 (note 44 §23,
    # OR-203): **two lines and one import**. ``_stamp_case_refs`` appends to
    # ``VnPoint.case_refs`` instead of assigning ``case_ref`` -- clearing the
    # list first, so stamping one envelope twice equals stamping it once -- and
    # ``_condition``'s ``nx = -p.dx / _cg_weight(...)`` becomes the OR-198 owner
    # ``aero_curves.inertia_drag_factor``. No arithmetic is touched: the zero
    # branch of the new owner is unreachable from here, because ``_cg_weight``
    # raises on a zero or unknown weight before it. Not admitted and not
    # touched: every selection criterion, ``htail_balance``, ``elevator_load``,
    # the v-tail subroutine and the wing slot table. Measured consequence: none
    # -- the Imperial digests are unmoved.
    "sloads/modules/select.py": "1685e932f93bdb5ef2165747e23a12628281abe86bc713417fa022a91d3e2a55",
    "sloads/modules/structural_speeds.py": "8fdbc1cc6eb17dbbdda4f5f1b224c7d5d4b86dfe14c923457292db7e123814c1",
    "sloads/modules/tab.py": "f81ff82261cccabedef57491635b3f56767faa61bae31c2d0d0017fc3bcb07e7",
    "sloads/modules/tail_span.py": "22a7832553de87ef9826c6e869e8ec8f1fe4e39c04706224f6af63e0847212b5",
    "sloads/modules/taildist.py": "3848d95ed35894bfe58e16e2c2f6a21e12a93ea493e533ccfdf40bf4caead3fb",
    # Re-hashed 2026-08-31 under an OR-15 row 1 admission (issue #157, design
    # note 45): WTENV gained the aft edge of the loading envelope and the
    # per-vertex waterline, both of which WTENV.BAS computes and Appendix A p139
    # prints. Additive by construction and by test -- the four pre-existing
    # ConditionResults are unchanged (G-WE-2) and every prior oracle in
    # tests/test_weight_envelope.py passes unedited (G-WE-3).
    "sloads/modules/weight_envelope.py": "453b4613d98ae039101dbbdb0a3d6c5841651e348eb790a6304d0a477a2a6fa1",
    "sloads/modules/weight_estimate.py": "8439bb62fa62dd1e11e13efe603e2efad517584f5ca441ad52cbc49048c286fe",
    "sloads/modules/weight_onecg.py": "a306666ca1ca3b4bba0a783e424bdb0ed2bcaadb66480c29bbfadfcfe0e1cd24",
    "sloads/modules/wing_geometry.py": "aad13d5f7eb0dbed33b7cf1cab8c06a14be401f0b10a908a40e1fe8000708f4b",
    # Same OR-15 admission (note 44 §23, OR-203): **one line and one import**.
    # ``_case_from_vn``'s ``nx = -vp.dx / weight if weight else 0.0`` becomes
    # ``inertia_drag_factor(vp.dx, weight)`` -- the same expression, including
    # the tolerant zero, now read from the one owner instead of spelled here.
    # Nothing else in the file is admitted or touched.
    "sloads/modules/wing_inertia.py": "88b1f9369d0b08a43a54aa8a94fcaf66669c2da247475745f4f831c1f8c8c59c",
    # --- the existing oracle GUI (OR-13, row 2) ---------------------------
    "oracle_app/Oracle.py": "b478bf06fd1c998ffa9ee1eebbc51225c24a26a813840529105779b51f5085a1",
    "oracle_app/__init__.py": "bb3135345b421b8fac0f02226050b821770a53c647c4ead72c8dfbd2d156f3d0",
    # OR-15 admission, granted by the owner 2026-09-07 (design note 53, D-53.1),
    # scoped to **two ``MEMBER_LABELS`` rows and nothing else**: the engine's
    # thrust line is a composite field in the oracle input set, and this table
    # is the only place a composite's members are named -- unnamed it renders
    # as "1, 2". Additive; no existing field's behaviour changes.
    "oracle_app/form.py": "18d32966d2c91a280eb16cfe0103a7db028fed9901c70cb2200f76d96c22523e",
    "oracle_app/labels.py": "93e442a1fff2174fdd17dd56f8d0b5f91e071641ead341be3dc5b71ede7cebf9",
    "oracle_app/results.py": "b49e5a8676cc747e559579c8ca0f5f5f8b2e8d2be07903d8cdd4b214b5b46645",
}

#: Directories the manifest claims to cover completely, so that a *new* file
#: dropped into the solver cannot slip past the freeze unhashed. ``oracle_app``
#: is not here: OR-13 permits new files there (the report page is the
#: milestone's first commit), and only the listed ones are frozen.
SEALED_DIRS = ("sloads/modules",)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("rel", sorted(MANIFEST))
def test_frozen_file_unchanged(rel: str) -> None:
    """A frozen path still hashes to what note 44 OR-13 froze."""
    path = REPO_ROOT / rel
    assert path.exists(), (
        f"{rel} is frozen by design note 44 OR-13 but no longer exists. Deleting "
        "a frozen file needs the same authority as editing one."
    )
    assert _sha256(path) == MANIFEST[rel], (
        f"{rel} changed, and it is frozen for milestone 0.8.2 (design note 44 "
        "OR-13). Permitted changes are: the OR-3 docstring amendment in "
        "oracle_app/Oracle.py, or a blocking-defect fix admitted under OR-15 "
        "with an issue number. Either way, update this manifest in the same "
        "commit and name the authority in the commit message. A defect you "
        "found while writing the report is filed, not fixed (OR-14)."
    )


@pytest.mark.parametrize("sealed", SEALED_DIRS)
def test_no_unhashed_files_in_sealed_dirs(sealed: str) -> None:
    """A new file in a sealed directory is a freeze gap, so it fails here."""
    found = {
        p.relative_to(REPO_ROOT).as_posix()
        for p in (REPO_ROOT / sealed).glob("*.py")
    }
    missing = sorted(found - set(MANIFEST))
    assert not missing, (
        f"{missing} live in {sealed}/, which design note 44 OR-13 freezes whole, "
        "but carry no manifest hash. Adding a solver module during 0.8.2 is a "
        "change to the frozen set: it needs OR-15 authority and a hash here."
    )


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
