"""The governing safety-factor table is the authority (M4-8 / decision G-11).

CLAUDE.md practice 3: a cross-cutting convention gets a single-source code owner
**plus a drift-guard test** — a prose rule alone is what let the factor be decided
ad hoc in the first place. Four things are pinned here, and they are the whole
argument that :mod:`sloads.safety_factors` is an authority rather than a fifth
opinion:

1. **It reproduces every factor the producers mint today**, on every shipped
   fixture, case by case. This is the acceptance gate for the whole change: the
   table can only *be* the authority if adopting it moves no number.
2. **Nothing defaults.** An unclassified case takes 1.5 and is flagged rather than
   raising (user decision), which only stays meaningful if a flag is a red build.
   A produced FAR reference with no family is therefore a test failure.
3. **An override reaches every channel.** The report's SF column, the carrier the
   export scales by, and the methods stamp move together or the test fails —
   review finding F-R1's defect class ("a report figure and its bulk-data card
   cannot state different factors for one case") re-armed for the override path.
4. **No shipped fixture carries an override**, so the default table is the
   regulation's own and the bundles are byte-for-byte what they were.
"""

import glob
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sloads.modules  # noqa: F401
from sloads import io
from sloads.constants import ULTIMATE_FACTOR
from sloads.report import applied as ap
from sloads.report import tables as rt
from sloads.models import SafetyFactorOverride, SafetyFactorPolicyInput
from sloads.registry import run_all_modules
from sloads.report.content import build_report, component_loads
from sloads.report.methods import methods_statement
from sloads.safety_factors import (
    DERIVED_FACTOR,
    FAMILIES,
    GoverningTable,
    LoadClass,
    RowStatus,
    classify,
    prescribes_factor,
)
from sloads.units import NON_LOAD_QUANTITIES, is_load_unit
from sloads.validation import consistency_warnings

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLES = sorted(glob.glob(os.path.join(_ROOT, "examples", "*.project.json")))
_GA = os.path.join(_ROOT, "examples", "ga6_normal.project.json")


def _all_cases(project):
    """Every case-carrying result one run of this project produces."""
    groups = [mr.conditions for mr in run_all_modules(project)]
    comps = component_loads(project)
    groups += [comps.wing, comps.body, comps.tail, comps.control, comps.critical]
    return [item for g in groups for item in g]


# --------------------------------------------------------------------------- #
# The table itself
# --------------------------------------------------------------------------- #
def test_family_keys_are_unique_and_classes_resolve():
    keys = [f.key for f in FAMILIES]
    assert len(keys) == len(set(keys)), "duplicate family key in the governing table"
    for f in FAMILIES:
        assert f.load_class in DERIVED_FACTOR, f.key
        assert f.basis.strip(), f"{f.key} has no basis — every row must state one"
        assert f.far_reference.strip(), f.key


def test_limit_and_ultimate_are_the_two_layer_1_values():
    """Layer 1 of M4-8: 14 CFR 23.303/25.303 decides these two, not the tool."""
    assert DERIVED_FACTOR[LoadClass.LIMIT] == ULTIMATE_FACTOR == 1.5
    assert DERIVED_FACTOR[LoadClass.ULTIMATE] == 1.0


def test_an_exact_row_beats_the_range_it_sits_inside():
    """23.367(a)(2) is an ULTIMATE case inside the LIMIT flight-loads range.

    If the range out-voted the exact row, the engine-failure case would silently
    be factored a second time — 1.5x the load the regulation already calls
    ultimate.
    """
    class _C:
        far_reference = "23.367(a)(2)"
    assert classify(_C())[0] == "engine_ultimate"
    assert GoverningTable.for_project().factor_for(_C()).factor == 1.0

    class _Limit:
        far_reference = "23.367(a)(1)"
    assert GoverningTable.for_project().factor_for(_Limit()).factor == 1.5


def test_the_engine_failure_family_speaks_the_regulation_noun():
    """One noun for 23.367(a)(2), owned by the governing table (#233, #178).

    Three owners described the family with three nouns — "engine torque" (the
    report Introduction), "engine torque and engine-failure fin loads" (the
    methods statement) and "the sudden-stoppage torque case" (this table's own
    basis). The family's actual members are the OEI fin cases; every torque
    condition (23.361 mount torque, 23.361(b)(1) sudden stoppage) is LIMIT
    ×1.5 — so each torque noun invited exactly the backwards reading §10 warns
    about, a reader treating mount torque as already ultimate. 14 CFR
    23.367(a)(2)'s own subjects are "the loads resulting from the
    disconnection of the engine compressor from the turbine or from loss of
    the turbine blades" (CFR-2011-title14-vol1-sec23-367).
    """
    import re

    from sloads.report import oracle_content as oc
    from sloads.safety_factors import ENGINE_FAILURE_NOUN, family

    fam = family("engine_ultimate")
    # the basis restates the regulation's own subjects, and carries the noun
    assert "disconnection of the engine compressor" in fam.basis
    assert "loss of the turbine blades" in fam.basis
    assert ENGINE_FAILURE_NOUN in fam.basis
    # ...and no 23.361 noun anywhere in the family's self-description
    for text in (ENGINE_FAILURE_NOUN, fam.label, fam.basis):
        assert "torque" not in text.lower(), text
        assert "stoppage" not in text.lower(), text
    # both prose consumers state the owner's noun beside the reference
    intro = oc.default_introduction()
    stamp = methods_statement(io.load_project(_GA))
    assert f"23.367(a)(2) {ENGINE_FAILURE_NOUN}" in intro
    assert f"23.367(a)(2) {ENGINE_FAILURE_NOUN}" in stamp
    # ...and neither reattaches a torque noun to 23.367 in any clause
    for label, text in (("introduction", intro), ("methods", stamp)):
        for clause in re.finditer(r"23\.367[^.;]*", text):
            assert "torque" not in clause.group(0).lower(), (label,
                                                             clause.group(0))


def test_a_reference_naming_families_that_disagree_is_not_classified_by_word_order():
    """``"23.367(a)(1)/23.561"`` mixes a limit and an ultimate family.

    Taking the first would let word order in a prose field decide a deliverable's
    factor. It is left unclassified — and therefore flagged — instead.
    """
    class _C:
        far_reference = "23.341/23.561"
    key, _ = classify(_C())
    assert key is None
    assert GoverningTable.for_project().factor_for(_C()).is_defaulted


def test_a_multi_section_reference_that_agrees_resolves():
    class _C:
        far_reference = "23.333/23.337/23.341/23.345/23.421"
    key, _ = classify(_C())
    assert key is not None
    assert GoverningTable.for_project().factor_for(_C()).factor == 1.5


def test_the_case_ref_is_the_fallback_source_of_the_far_reference():
    """The distributed component results carry their FAR only on the case ref."""
    from sloads.models import CaseRef

    class _C:
        far_reference = ""
        case_ref = CaseRef("W-01", "wing", "PHAA", far_reference="23.337")
    assert classify(_C())[0] == "flight"


# --------------------------------------------------------------------------- #
# G-OR-46: what prescribes a factor, and what does not (#154, design note 48)
# --------------------------------------------------------------------------- #
def _has_load(item) -> bool:
    return any(is_load_unit(v.units, v.quantity or "")
               for v in (getattr(item, "values", None) or []))


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_the_factorless_rule_holds_in_both_directions(path):
    """Both halves of OR-83, on every shipped fixture.

    Forward: a condition the table resolves to *no* factor states no value in
    load units **and** carries no ``case_ref``. Reverse: a condition that states
    a load, or that identifies a case, resolves to a real factor. The reverse
    half is the one that matters -- it is what stops the rule blanking SELECT's
    critical wing conditions, whose loads live on ``WingLoadResult`` and whose
    bulk-data cards are factored.
    """
    project = io.load_project(path)
    table = GoverningTable.for_project(project)
    for item in _all_cases(project):
        resolved = table.factor_for(item)
        titled = f"{path}: {getattr(item, 'title', item)!r}"
        if resolved.factor is None:
            assert not _has_load(item), (
                f"{titled} prescribes no factor but states a load")
            assert getattr(item, "case_ref", None) is None, (
                f"{titled} prescribes no factor but identifies a case")
        else:
            assert _has_load(item) or getattr(item, "case_ref", None) is not None, (
                f"{titled} resolves SF={resolved.factor} but is neither a load "
                "nor a case -- prescribes_factor should have blanked it")


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_a_factorless_condition_keeps_no_factor_through_the_stamp(path):
    """The dataclass default alone would not survive ``run_all_modules``.

    ``registry.run_all_modules`` re-stamps every condition through
    ``GoverningTable.stamp``, so a ``None`` default is overwritten unless the
    table itself carries the concept. This asserts the shipped path, not the
    constructor.
    """
    project = io.load_project(path)
    for mr in run_all_modules(project):
        for c in mr.conditions:
            if not prescribes_factor(c):
                assert c.safety_factor is None, (
                    f"{path}: {c.title!r} was stamped SF={c.safety_factor} "
                    "though it prescribes no factor")


def test_the_case_ref_clause_protects_a_load_case_that_states_no_load():
    """SELECT's critical wing conditions: a case, with its loads carried elsewhere.

    The counter-example that rules out a content-only test. Blanking these would
    print N/A in the case index against six wing cases whose deck cards are
    factored -- a worse false claim than the one #154 was filed for.
    """
    project = io.load_project(_GA)
    select = [mr for mr in run_all_modules(project) if mr.module == "select"]
    assert select, "the GA fixture must still run SELECT"
    protected = [c for c in select[0].conditions
                 if c.case_ref is not None and not _has_load(c)]
    assert protected, "the fixture no longer exercises the case_ref clause"
    for c in protected:
        assert prescribes_factor(c), c.title
        assert c.safety_factor is not None, c.title


# --------------------------------------------------------------------------- #
# 1 + 2: the authority claim, on every shipped fixture
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_the_table_reproduces_every_minted_factor(path):
    """The acceptance gate: adopting the table moves no number, on any fixture.

    Not "the totals match" — every individual case is checked, so a family whose
    factor happened to coincide cannot hide a misclassification.
    """
    project = io.load_project(path)
    table = GoverningTable.for_project(project)
    for item in _all_cases(project):
        minted = getattr(item, "safety_factor", None)
        if minted is None:
            continue
        resolved = table.factor_for(item)
        assert resolved.factor == pytest.approx(minted, rel=0, abs=0), (
            f"{path}: case {getattr(item, 'title', item)!r} "
            f"({resolved.far_reference!r}) is minted at SF={minted} but the "
            f"governing table resolves {resolved.factor} via '{resolved.family_key}'")


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_no_shipped_fixture_produces_a_defaulted_case(path):
    """A 'defaulted' row is a defect in the table, not a footnote (G-11).

    The user's decision was that an unresolved case takes 1.5 and is flagged
    rather than raising. This test is what stops "flagged" from becoming "normal":
    add a module that mints a FAR reference no family covers and the build goes
    red here, naming the reference.
    """
    project = io.load_project(path)
    table = GoverningTable.for_project(project)
    for item in _all_cases(project):
        table.factor_for(item)
    assert table.defaulted == [], (
        f"{path}: unclassified FAR reference(s) {table.defaulted} — add a family "
        "to sloads.safety_factors.FAMILIES or correct the producer's reference")


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_every_result_the_table_is_handed_can_be_stamped(path):
    """The other silent skip in the same owner (review CR-B-6).

    ``stamp()`` writes the factor onto each result's ``safety_factor`` carrier,
    and used to pass over an item without one on a bare ``hasattr`` gate. An
    unstamped result is precisely a result whose report figure and whose
    bulk-data card can state different factors — the F-R1 defect class — so the
    skip is recorded like an unclassifiable case, and it is empty here.
    """
    project = io.load_project(path)
    cases = list(_all_cases(project))
    table = GoverningTable.for_project(project).stamp(cases)
    assert table.unstampable == [], (
        f"{path}: stamp() was handed {table.unstampable}, which carry no "
        "safety_factor — every result the governing table stamps must have the "
        "carrier, or the report and the deck can disagree about one case")


def test_an_item_without_the_carrier_is_recorded_not_passed_over():
    """The guard above only means something if the recording works."""

    class _NoCarrier:
        far_reference = "23.337"

    table = GoverningTable.for_project(None).stamp([_NoCarrier()])
    assert table.unstampable == ["_NoCarrier"]


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_no_shipped_fixture_overrides_the_regulation(path):
    """Mitigation 4: the default table is the regulation's, so the fixtures'
    exported bytes are unchanged by this feature existing."""
    project = io.load_project(path)
    assert project.safety_factors is None or not project.safety_factors.overrides
    table = GoverningTable.for_project(project)
    assert not table.has_overrides
    assert all(r.status == RowStatus.DERIVED for r in table.rows)


def test_the_override_layer_is_absent_from_a_written_fixture():
    """An empty policy and no policy are the same statement, so nothing new is
    written into a project.json that has no override — the byte-for-byte gate."""
    project = io.load_project(_GA)
    assert "safety_factors" not in io.project_to_dict(project)
    project.safety_factors = SafetyFactorPolicyInput()
    assert "safety_factors" not in io.project_to_dict(project)


# --------------------------------------------------------------------------- #
# 3: an override reaches every channel
# --------------------------------------------------------------------------- #
def _overridden(family="ground", factor=1.25, basis="Agreed with the authority."):
    project = io.load_project(_GA)
    project.safety_factors = SafetyFactorPolicyInput(
        [SafetyFactorOverride(family, factor, basis)])
    return project


def test_an_override_round_trips_through_json():
    project = _overridden()
    back = io.project_from_dict(io.project_to_dict(project))
    assert back.safety_factors.overrides[0].family == "ground"
    assert back.safety_factors.overrides[0].factor == 1.25
    assert back.safety_factors.overrides[0].basis


def test_an_override_moves_the_carrier_the_export_scales_by():
    """The carrier stays the carrier (M4-8) — the table writes to it.

    Without this the report's SF column would move and the deck's cards would not,
    which is exactly the defect class F-R1 closed on the report side.
    """
    project = _overridden("flight", 1.2)
    comps = component_loads(project)
    scaled = [c for c in comps.critical if c.safety_factor == 1.2]
    assert scaled, "no flight case took the overridden factor"


def test_an_override_is_declared_in_the_methods_stamp():
    """Mitigation 1: a reader of any single stamped file learns of the override."""
    plain = methods_statement(io.load_project(_GA))
    assert "SAFETY FACTOR OVERRIDES" not in plain

    text = methods_statement(_overridden())
    assert "SAFETY FACTOR OVERRIDES" in text
    assert "Agreed with the authority." in text
    assert "CERTIFICATION RISK" in text  # 1.25 is below the derived 1.5


def test_an_override_above_the_regulation_is_declared_without_a_risk_flag():
    text = methods_statement(_overridden("ground", 1.5, "House standard."))
    # 1.5 == derived: not an escalation, but still an explicitly declared row.
    assert "SAFETY FACTOR OVERRIDES" in text
    assert "CERTIFICATION RISK" not in text


def test_the_report_carries_the_table_and_flags_the_override():
    doc = build_report(_overridden())
    section = doc.section("Governing safety factors")
    assert section is not None
    labels = [r[0] for r in section.table.rows]
    assert [f.label for f in FAMILIES] == labels
    assert any(RowStatus.OVERRIDE in r for r in section.table.rows)
    assert any("overrides" in p for p in section.body)


def test_the_case_index_sf_column_is_a_view_of_the_table():
    """Supersedes the silent ``getattr(item, "safety_factor", ULTIMATE_FACTOR)``."""
    doc = build_report(_overridden("flight", 1.2))
    index = doc.section("Conditions analysed and FAR coverage").table
    sf_col = index.columns.index("SF")
    assert any(row[sf_col] == "1.2" for row in index.rows)


def test_the_companion_csv_states_the_derived_value_beside_the_override():
    """An override is self-evident in the file, not only in the prose beside it."""
    text = rt.safety_factors_csv(_overridden())
    assert "Derived SF" in text.splitlines()[0]
    row = next(ln for ln in text.splitlines() if ln.startswith("Ground"))
    assert "1.25" in row and "1.5" in row and RowStatus.OVERRIDE in row


def test_the_companion_csv_has_one_row_per_family():
    text = rt.safety_factors_csv(io.load_project(_GA))
    assert len(text.strip().splitlines()) == len(FAMILIES) + 1


# --------------------------------------------------------------------------- #
# Validation: the price of full editability
# --------------------------------------------------------------------------- #
def test_an_override_without_a_basis_is_rejected():
    codes = [w.code for w in consistency_warnings(_overridden(basis=""))]
    assert "safety_factor_override_without_basis" in codes


def test_an_override_below_the_regulation_raises_a_certification_risk_warning():
    warnings = consistency_warnings(_overridden("ground", 1.2))
    hit = [w for w in warnings if w.code == "safety_factor_below_regulation"]
    assert hit and "CERTIFICATION RISK" in hit[0].message


def test_an_override_naming_no_family_is_an_explicit_finding_not_silence():
    codes = [w.code for w in consistency_warnings(_overridden("wings"))]
    assert "safety_factor_override_unknown_family" in codes


def test_an_unmodified_project_raises_no_safety_factor_warning():
    codes = [w.code for w in consistency_warnings(io.load_project(_GA))]
    assert not [c for c in codes if c.startswith("safety_factor_override")]
    assert "safety_factor_below_regulation" not in codes



# --------------------------------------------------------------------------- #
# #170: a machine rating in load units is not a load (note 48 §1.2/§2.4)
# --------------------------------------------------------------------------- #
#: The engine's own torque ratings -- the *input* to a design torque. Each is
#: published in ``ft-lb`` beside the ``mx_mount_torque`` derived from it, which is
#: the load. Named here so the discrimination is asserted on the shipped fixtures
#: rather than trusted: a rating that loses its hint, or a mount torque that
#: gains one, fails below.
_ENGINE_RATINGS = {"mean_takeoff_torque", "max_continuous_torque",
                   "max_accelerating_torque"}

#: ``balance``'s pre-closure residuals -- the second half of the same finding
#: (review 2026-09-04 R-8). Equilibrium-quality diagnostics in load units, which
#: were factored and ``-ULT``-marked beside the applied loads of the case they
#: describe. Their percentage forms were never in load units, which is how the
#: pair came to be marked two different ways.
_CLOSURE_DIAGNOSTICS = {"balanced_residual_fz", "balanced_residual_my"}

#: Every key the class covers -- the rule-4 sweep, not the one filed row.
_NON_LOADS = _ENGINE_RATINGS | _CLOSURE_DIAGNOSTICS


def test_the_unit_alone_does_not_decide_what_a_load_is():
    """The predicate's two declarations, at the owner (#170).

    ``ft-lb`` is a load unit and stays one; the producer's hint is what removes a
    value from the class. Before #170 the test was on the unit alone, and an
    engine rating therefore took 14 CFR 23.303's factor -- 554.4 ft-lb of mean
    takeoff torque stated as 831.6 on the ultimate channel, a number with no
    meaning.
    """
    assert is_load_unit("ft-lb")                          # a moment is a load
    assert not is_load_unit("ft-lb", "characteristic")     # an engine rating is not
    assert not is_load_unit("lb", "mass")                  # a weight is not
    assert not is_load_unit("in")                          # nor is a station
    # every hint that removes a value from the class is in the owner's vocabulary
    assert {"mass", "characteristic"} <= NON_LOAD_QUANTITIES


def test_a_non_load_in_load_units_is_not_load_marked_but_its_neighbours_are():
    """The discrimination holds per value, across every fixture, both ways.

    The reverse half is the one that matters: a blanket exclusion of ``ft-lb`` in
    ENGLOADS would pass the forward assertion and silently drop the factor from
    the mount torque, the gyroscopic couples and the stoppage torque -- the real
    loads of the same conditions. Swept over all fixtures together rather than per
    fixture, because a concept example need not declare a powerplant at all.
    """
    ratings = mounts = 0
    for path in _EXAMPLES:
        for item in _all_cases(io.load_project(path)):
            for v in getattr(item, "values", None) or []:
                where = (os.path.basename(path), item.title, v.key)
                if v.key in _NON_LOADS:
                    assert v.quantity in NON_LOAD_QUANTITIES, where
                    assert not is_load_unit(v.units, v.quantity or ""), where
                    ratings += 1
                elif v.units == "ft-lb":
                    assert is_load_unit(v.units, v.quantity or ""), where
                    mounts += 1
    assert ratings and mounts, (ratings, mounts)   # neither half may empty out
    # and the class is swept, not sampled: every key of it was actually seen
    seen = {v.key for path in _EXAMPLES
            for item in _all_cases(io.load_project(path))
            for v in (getattr(item, "values", None) or [])}
    assert _NON_LOADS <= seen, _NON_LOADS - seen


@pytest.mark.parametrize("path", _EXAMPLES, ids=lambda p: os.path.basename(p))
def test_no_published_quantity_hint_is_outside_the_owners_vocabulary(path):
    """Drift guard on the hint itself (CLAUDE.md rule 3).

    ``quantity`` answers two questions -- SI dimension and load-ness -- and a hint
    invented at a producer without a row at an owner answers neither. A new value
    here must be added to :data:`sloads.units.NON_LOAD_QUANTITIES` or to the SI
    dimension table, deliberately.
    """
    from sloads.units import HUMAN_SI

    known = set(NON_LOAD_QUANTITIES) | set(HUMAN_SI)
    for item in _all_cases(io.load_project(path)):
        for v in getattr(item, "values", None) or []:
            if v.quantity:
                assert v.quantity in known, (item.title, v.key, v.quantity)


def test_an_engine_rating_states_no_factor_in_the_delivered_row():
    """The end of the channel, which is what #170 is about.

    ``results_to_rows`` is the delivered CSV/report row. The rating's ``SF`` cell
    is empty because nothing prescribes a factor for it; the mount torque's states
    the condition's own factor. Both rows sit in one condition, which is why a
    condition-level rule could never have fixed this.
    """
    from sloads.registry import get
    from sloads.report.render import results_to_rows

    engine = get("engine")(io.load_project(_GA))
    rows = {r["Quantity"]: r for r in results_to_rows(engine.conditions)}
    assert rows["Mean takeoff torque"]["SF"] == "", rows["Mean takeoff torque"]
    assert rows["Engine mount torque"]["SF"], rows["Engine mount torque"]
    # and the value itself is untouched -- the marker moved, not the number
    assert "-ULT" not in rows["Mean takeoff torque"]["Units"]


# --------------------------------------------------------------------------- #
# The comparison basis (note 58 D-58.2/D-58.3)
# --------------------------------------------------------------------------- #
def test_the_ultimate_basis_is_magnitude_times_the_prescribed_factor():
    """|value| x SF, sign-blind -- the quantity structure is sized to. On a
    uniform set it is the raw ranking scaled by a constant, which is why
    nothing moves anywhere factors agree."""
    from sloads.safety_factors import ultimate_basis

    assert ultimate_basis(100.0, 1.5) == 150.0
    assert ultimate_basis(-100.0, 1.5) == 150.0
    assert ultimate_basis(150.0, 1.0) == 150.0
    # The defect case note 58 exists for: 110 @ 1.5 outranks 150 @ 1.0.
    assert ultimate_basis(110.0, 1.5) > ultimate_basis(150.0, 1.0)


def test_uniform_factor_names_the_shared_factor_or_refuses():
    """The same-basis owner for cross-case value constructs -- distinct from
    shared_basis_factor, which answers the -ULT header-wording question and
    returns 1.0 or None only."""
    from sloads.safety_factors import uniform_factor

    assert uniform_factor([1.5, 1.5, 1.5]) == 1.5
    assert uniform_factor([1.0]) == 1.0
    assert uniform_factor([1.5, 1.0]) is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
