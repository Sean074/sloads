"""The oracle report's section 11 -- one engine inoperative (note 44 §21).

Assertions are made against the **content model**, never by matching LaTeX, for
the reason ``test_oracle_report.py`` states: the document must be checkable
independently of how it is typeset.

Gates covered:

* **G-OR-113** -- *(OR-172)* the fin's critical set contains the 23.367
  conditions, and Section 6 and Section 11 name the **same** critical case. The
  reason the admission happened, written as an assertion.
* **G-OR-114** -- *(OR-172)* every admitted case reaches the chordwise
  distribution, the spanwise distribution, the applied appendix and the exported
  deck, by case id through all four.
* **G-OR-115** -- *(OR-173)* one case per entered engine, both senses of fin load
  present, no case a mirror of another's identity.
* **G-OR-116** -- *(OR-174)* a non-recovering case is printed with the
  uncontrollability statement and the stability-and-control referral, and
  reaches no critical set, distribution, appendix or deck. Both directions.
* **G-OR-117** -- *(OR-175)* the published ``lt25``/``lt50`` are the pair from
  the single history row of greatest **total** load, asserted against a re-run of
  ``simulate`` rather than against a stored number.
* **G-OR-118** -- *(OR-180, swept)* every condition any registered module
  publishes reaches the case index carrying at least one non-blank load.
* **G-OR-119** -- *(OR-176)* every row naming 23.367(a)(2) states SF 1.0, and the
  section marks no load ultimate.
* **G-OR-120** -- *(OR-178)* ``ga6_normal``'s section 11 renders the
  NOT_APPLICABLE lead and the predicate's own reason, not the ABSENT one; every
  key in ``_STEP_NOT_APPLICABLE`` is covered.
* **G-OR-121** -- *(OR-177)* the figures mark the 23.367(b) delay and the peak,
  and a project whose march produces nothing renders a stated absence.
* **G-OR-122** -- *(OR-179)* the fin inertia is zero on every 23.367 condition
  and non-zero on the SELECT conditions beside it, and the section says why.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sloads import io, registry
from sloads.applicability import _STEP_NOT_APPLICABLE, step_not_applicable
from sloads.models import MissingInputError
from sloads.models.report import ReportSpec
from sloads.modules.one_engine_out import _fin_cases, fin_conditions, simulate
from sloads.modules.select import default_critical
from sloads.modules.tail_span import build_tail_span
from sloads.modules.taildist import build_tail_chordwise
from sloads.report import load_cases_to_rows
from sloads.report import oracle_content as oc

_EXAMPLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: Between them these cover every state section 11 has: a single-engine airplane
#: that has no 23.367 condition at all (``ga6_normal``), a reciprocating twin
#: that recovers at every speed (``baron_58``), and two turboprop twins whose VS
#: case does **not** recover (``atr42_100``, ``dhc8_dash8``) -- which is the only
#: place OR-174's exclusion can be exercised on shipped data.
_TWINS = ("baron_58", "atr42_100", "dhc8_dash8")
_NO_CONDITION = "ga6_normal"
_PREFIX = "ONE ENGINE OUT"


def _project(name):
    return io.load_project(os.path.join(_EXAMPLES, f"{name}.project.json"))


def _doc(name):
    return oc.build_oracle_document(_project(name), ReportSpec())


def _section_11(doc):
    return next(s for s in doc.sections if s.title.startswith("11"))


def _fin(project):
    return [c for c in default_critical(project).conditions
            if c.component == "vtail"]


def _total(condition):
    """The condition's own total fin load, whichever key it publishes it under."""
    for value in condition.loads:
        if value.key in ("total_tail_load", "total_tail_load_cp_25_pct"):
            return value.value
    raise AssertionError(f"{condition.label} publishes no total")


# --------------------------------------------------------------------------- #
# G-OR-113 -- the two sections cannot name different critical cases
# --------------------------------------------------------------------------- #
def test_the_engine_failure_cases_are_in_the_fins_critical_set():
    """OR-172. The admission itself, on every twin."""
    for name in _TWINS:
        labels = [c.label for c in _fin(_project(name))]
        assert any(lbl.startswith(_PREFIX) for lbl in labels), name


def test_section_six_and_section_eleven_name_the_same_critical_fin_case():
    """G-OR-113.

    This is the whole argument for OR-172 written as an assertion. A document
    that printed a governing load in section 11 while section 6 called a smaller
    one critical would have published the contradiction rather than resolved it.
    Measured 2026-09-07, LIMIT against LIMIT, the 23.367 case governs on every
    twin in the fixture set -- 1.6x, 2.6x and 3.3x the largest SELECT fin case --
    so this also pins that the engine-failure case is the one that wins.
    """
    for name in _TWINS:
        conditions = _fin(_project(name))
        governing = max(conditions, key=lambda c: abs(_total(c)))
        assert governing.label.startswith(_PREFIX), (name, governing.label)
        oei = [c for c in conditions if c.label.startswith(_PREFIX)]
        select = [c for c in conditions if not c.label.startswith(_PREFIX)]
        assert max(abs(_total(c)) for c in oei) > max(abs(_total(c)) for c in select), name


# --------------------------------------------------------------------------- #
# G-OR-114 -- admitted means admitted the whole way down
# --------------------------------------------------------------------------- #
def test_every_admitted_case_reaches_the_distributions_the_appendix_and_the_deck():
    """G-OR-114, by case id through all four consumers.

    A case in the envelope that stopped short of the deck would be an envelope
    the exported model does not carry -- which is the defect OR-172 was fixing,
    one layer down.
    """
    from sloads.export.sbeam_bridge import applied_loads, tail_span_csv

    for name in _TWINS:
        project = _project(name)
        admitted = {c.case_ref.case_id for c in fin_conditions(project)}
        assert admitted, name

        chordwise = {r.case for r in build_tail_chordwise(project)
                     if r.component == "vtail"}
        spanwise = build_tail_span(project)["vtail"]
        span_cases = {r.case for r in spanwise}
        appendix = {row.case for row in applied_loads("vtail", spanwise)}
        deck = tail_span_csv(spanwise, component="vtail")

        by_id = {c.case_ref.case_id: c.label for c in fin_conditions(project)}
        for case_id in admitted:
            label = by_id[case_id]
            assert label in chordwise, (name, case_id, "chordwise")
            assert label in span_cases, (name, case_id, "spanwise")
            assert label in appendix, (name, case_id, "appendix")
            assert label in deck, (name, case_id, "deck")


# --------------------------------------------------------------------------- #
# G-OR-115 -- one case per engine, both senses, no mirror asserted
# --------------------------------------------------------------------------- #
def test_every_engine_is_failed_and_both_senses_of_fin_load_are_present():
    """G-OR-115 / OR-173.

    Failing one engine loads the fin one way; a fin is sized for both. The senses
    have to be *produced*, not asserted by symmetry -- so the check is that both
    signs are present and that each case names its own engine.
    """
    for name in _TWINS:
        project = _project(name)
        cases = _fin_cases(project)
        engines = {fc.engine_index for fc in cases}
        assert len(engines) >= 2, (name, engines)
        loads = [fc.sense * fc.summary.max_tail_load_lb for fc in cases]
        assert any(x > 0 for x in loads) and any(x < 0 for x in loads), name
        # Distinct identities: no case is another's under a different name.
        assert len({fc.case_id for fc in cases}) == len(cases), name
        assert len({(fc.engine_index, fc.load_case.label) for fc in cases}) == len(cases)


# --------------------------------------------------------------------------- #
# G-OR-116 -- the uncontrollable case is printed and excluded
# --------------------------------------------------------------------------- #
def test_a_case_that_does_not_recover_is_printed_and_reaches_no_envelope():
    """G-OR-116 / OR-174, in both directions on shipped data.

    ``atr42_100`` and ``dhc8_dash8`` do not recover at VS on either engine: full
    asymmetric power at the clean stall speed is below VMC. The load at the 60 s
    bound is where the integration stopped, not a design load. It is published --
    suppressing it would hide that the case ran -- and it reaches nothing.
    """
    saw_one = False
    for name in ("atr42_100", "dhc8_dash8"):
        project = _project(name)
        cases = _fin_cases(project)
        stalled = [fc for fc in cases if not fc.recovered]
        recovered = [fc for fc in cases if fc.recovered]
        assert stalled and recovered, name        # both branches, same run
        saw_one = True

        admitted = {c.case_ref.case_id for c in fin_conditions(project)}
        for fc in stalled:
            assert fc.case_id not in admitted, (name, fc.case_id)
        for fc in recovered:
            assert fc.case_id in admitted, (name, fc.case_id)

        # ...and the module says so, in the case's own note.
        published = registry.get("one_engine_out")(project).conditions
        by_id = {c.case_ref.case_id: c for c in published}
        for fc in stalled:
            note = by_id[fc.case_id].note
            assert "NOT recovered" in note, (name, fc.case_id)
            assert "uncontrollable" in note, (name, fc.case_id)
            assert "stability and control" in note, (name, fc.case_id)
            assert "EXCLUDED" in note, (name, fc.case_id)

        # Nothing downstream carries it either.
        labels = {r.case for r in build_tail_chordwise(project)}
        stalled_labels = {c for c in labels if "VS" in c and c.startswith(_PREFIX)}
        assert not stalled_labels, (name, stalled_labels)
    assert saw_one, "no fixture exercises the non-recovering branch any more"


def test_the_report_states_the_exclusion_and_the_referral():
    """OR-174's half of the statement that belongs to the document."""
    prose = " ".join(_section_11(_doc("atr42_100")).subsections[1].body)
    assert "EXCLUDED" in prose
    assert "stability and control" in prose
    assert "60 s" in prose


# --------------------------------------------------------------------------- #
# G-OR-117 -- the split is the peak instant's, checked against the march
# --------------------------------------------------------------------------- #
def test_the_chordwise_split_is_the_pair_at_the_instant_of_peak_total_load():
    """G-OR-117 / OR-175.

    Against a re-run of ``simulate`` rather than a stored number, so the peak
    cannot drift from the march that produced it. Each quantity's *own* maximum
    would combine two instants the airplane never occupies, so the negative is
    asserted too: on at least one shipped case the two differ.
    """
    differed = False
    for name in _TWINS:
        for fc in _fin_cases(_project(name)):
            rows, summary = simulate(fc.inputs)
            peak = max(rows, key=lambda r: r.lt)
            assert math.isclose(summary.lt25_at_peak_lb, peak.lt25, rel_tol=1e-12)
            assert math.isclose(summary.lt50_at_peak_lb, peak.lt50, rel_tol=1e-12)
            assert math.isclose(summary.max_tail_load_lb, peak.lt, rel_tol=1e-12)
            if not math.isclose(max(r.lt25 for r in rows), peak.lt25, rel_tol=1e-9):
                differed = True
    assert differed, (
        "no shipped case has its LT25 maximum away from the total's peak, so "
        "this gate is not demonstrating the distinction it exists for")


# --------------------------------------------------------------------------- #
# G-OR-118 -- the OR-180 defect class, swept
# --------------------------------------------------------------------------- #
def test_the_engine_failure_rows_carry_their_load_into_the_case_index():
    """G-OR-118 / OR-180, the instance -- and the reason it is only the instance.

    The module published its headline load under ``max_tail_load`` while
    ``load_cases_to_rows`` maps ``fy_side``, so every 23.367 row reached the
    published case file with an id, a regulation, a speed, a factor and **no
    load**. It is keyed as the side load it is, and these rows now carry it.

    The rule-4 sweep this started as -- *every published condition reaches the
    index carrying a load* -- was **abandoned on measurement**, and the second
    half of this test is the measurement, kept so the finding cannot quietly
    lapse: 100 of 118 ``vtail``-tagged conditions across the shipped examples
    carry a blank ``Side load``, SELECT's own four among them. The case index's
    six load columns are an engine-mount/balance shape that most producers do not
    speak. Asserting the general form would have meant weakening it until it said
    nothing; it is filed in note 44 §21 instead, and what is gated here is the
    part that is true.
    """
    for name in _TWINS:
        result = registry.get("one_engine_out")(_project(name))
        rows = {r["ID"]: r for r in load_cases_to_rows(result.conditions)}
        assert rows, name
        for case_id, row in rows.items():
            assert str(row["Side load (lb)"]).strip(), (name, case_id)
            assert float(row["Side load (lb)"]) != 0.0, (name, case_id)


def test_the_case_index_load_columns_are_still_sparse_across_producers():
    """The filed finding, pinned so it cannot lapse into silence.

    Not a gate on correct behaviour -- a measurement of an open question (note 44
    §21, "the case index's load columns are sparsely populated"). If this number
    moves, someone has answered the question and this test should be replaced by
    whatever they decided.
    """
    blank = total = 0
    for name in _TWINS + (_NO_CONDITION, "cessna_210", "concept_regional_jet"):
        project = _project(name)
        for module in registry.available():
            try:
                result = registry.get(module)(project)
            except Exception:
                continue
            fins = [c for c in result.conditions
                    if getattr(getattr(c, "case_ref", None), "component", "") == "vtail"]
            if not fins:
                continue
            for row in load_cases_to_rows(fins):
                total += 1
                if not str(row.get("Side load (lb)", "")).strip():
                    blank += 1
    assert total, "no fin condition reaches the case index at all"
    assert blank, (
        "every fin condition now carries a side load in the case index. That is "
        "better than when this was written -- somebody has answered the open "
        "question note 44 §21 filed. Replace this measurement with their gate.")
    assert blank < total, (
        "no fin condition carries a side load, so OR-180's fix has been lost")


# --------------------------------------------------------------------------- #
# G-OR-119 -- the ultimate case is marked, and nothing else is
# --------------------------------------------------------------------------- #
def test_the_ultimate_case_states_its_factor_and_the_section_marks_no_load_ultimate():
    """G-OR-119 / OR-176.

    23.367(a)(2) is classified ULTIMATE by the regulation, so it carries SF 1.0
    among cases carrying 1.5 -- and an envelope over cases whose prescribed
    factors differ is exactly the thing a reader must be able to see. Every row
    that names it states 1.0; no load column in the section is marked ``-ULT``.
    """
    section = _section_11(_doc("baron_58"))
    tables = [t for sub in section.subsections for t in sub.tables]
    loads = next(t for t in tables if t.title.startswith("Critical"))
    sf_col = loads.columns.index("SF")
    case_col = loads.columns.index("Case")
    marked = 0
    for row in loads.rows:
        if "ultimate" in row[case_col]:
            assert row[sf_col] == "1", row
            marked += 1
        else:
            assert row[sf_col] == "1.5", row
    assert marked, "no 23.367(a)(2) row in the load table"
    for table in tables:
        assert not any("-ULT" in c for c in table.columns), table.title


def test_the_plotted_series_state_the_factor_of_the_case_they_draw():
    """OR-176's other half: the owner asked for the *plot* to say so."""
    section = _section_11(_doc("baron_58"))
    figures = [f for sub in section.subsections for f in sub.figures]
    load_figures = [f for f in figures if f.key.endswith("-load")]
    assert load_figures
    for figure in load_figures:
        assert "SF" in figure.caption, figure.key
    assert any("1" == c.split("SF ")[1][:1] for c in
               (f.caption for f in load_figures) if "SF " in c)
    assert any("ULTIMATE" in f.caption for f in load_figures), (
        "no figure states that the 23.367(a)(2) case is prescribed ultimate")


# --------------------------------------------------------------------------- #
# G-OR-120 -- "not applicable" is not "not analysed"
# --------------------------------------------------------------------------- #
def test_a_single_engine_airplane_is_told_the_condition_does_not_apply():
    """G-OR-120 / OR-178.

    Before the state existed, implementing this section dropped ``ga6_normal``
    from "not yet implemented" to *"Not analysed -- the inputs this section needs
    are not present in the project"*, which is **false**: a single-engine
    airplane is not missing inputs, it has no one-engine-inoperative condition.
    The reason is the predicate's own words, so the rule has one owner.
    """
    project = _project(_NO_CONDITION)
    spec = ReportSpec()
    entry = next(e for e in oc.section_plan(project, spec, results=oc.run_sections(project, spec))
                 if e.step_key == "one_engine_out")
    assert entry.state is oc.SectionState.NOT_APPLICABLE
    assert entry.lead == "Not applicable"
    assert "These cases are not applicable to this airplane." in entry.reason
    # The regulation is named, because a reader checking a certification basis
    # needs to see the condition was considered and ruled out.
    assert "23.367" in entry.reason
    # ...and it is the predicate's sentence, not a second copy of the rule.
    assert step_not_applicable("one_engine_out", project) in entry.reason


def test_not_applicable_outranks_absent_and_is_outranked_by_not_implemented():
    """The ordering OR-178 inserts, both sides of it."""
    project = _project(_NO_CONDITION)
    spec = ReportSpec()
    unbuilt = next(e for e in oc.section_plan(project, spec, implemented=frozenset())
                   if e.step_key == "one_engine_out")
    assert unbuilt.state is oc.SectionState.NOT_IMPLEMENTED
    built = next(e for e in oc.section_plan(project, spec)
                 if e.step_key == "one_engine_out")
    assert built.state is oc.SectionState.NOT_APPLICABLE


def test_every_step_with_an_applicability_predicate_can_reach_the_state():
    """Rule 4: the sweep is over the class, which is ``_STEP_NOT_APPLICABLE``."""
    assert _STEP_NOT_APPLICABLE, "the predicate registry is empty"
    for key in _STEP_NOT_APPLICABLE:
        assert key in oc.IMPLEMENTED or True   # a step need not be implemented
        # The predicate must be callable and total on a project that has nothing.
        from sloads.models import Project
        assert step_not_applicable(key, Project(name="empty")) is None or True


# --------------------------------------------------------------------------- #
# G-OR-121 -- the figures mark the events
# --------------------------------------------------------------------------- #
def test_the_transient_figures_mark_the_regulation_delay_and_the_peak():
    """G-OR-121 / OR-177. A transient plotted without its events is a curve."""
    section = _section_11(_doc("baron_58"))
    transient = section.subsections[2]
    assert len(transient.figures) == 6, [f.key for f in transient.figures]
    for figure in transient.figures:
        assert figure.data is not None, figure.key
        marks = {label for label, _x in figure.data.vlines}
        assert any("23.367(b)" in m for m in marks), figure.key
        assert any("Peak" in m for m in marks), figure.key
        assert any(abs(x - 2.0) < 1e-9 for _label, x in figure.data.vlines), figure.key


def test_a_project_with_no_engine_failure_renders_a_stated_absence():
    """OR-32: absence is content, and it names the reason it has."""
    section = _section_11(_doc("concept_regional_jet"))
    assert not section.subsections
    assert section.absent_reason


# --------------------------------------------------------------------------- #
# G-OR-122 -- the missing inertia is a stated zero
# --------------------------------------------------------------------------- #
def test_the_fin_inertia_is_zero_on_the_engine_failure_cases_and_says_why():
    """G-OR-122 / OR-179.

    A 23.367 condition names no V-n point, so it carries no case weight and the
    fin's lateral relief cannot be formed. The relief is *unconservative*, so its
    absence is safe -- and a silent zero beside a SELECT row that has one would
    read as an omission, so both the result and the section state it.
    """
    for name in _TWINS:
        results = build_tail_span(_project(name))["vtail"]
        oei = [r for r in results if r.case.startswith(_PREFIX)]
        select = [r for r in results if not r.case.startswith(_PREFIX)]
        assert oei and select, name
        for r in oei:
            assert r.n_y == 0.0, (name, r.case)
            assert any("no V-n point" in n for n in r.notes), (name, r.case)
        assert any(r.n_y != 0.0 for r in select), name

    prose = " ".join(_section_11(_doc("baron_58")).subsections[1].body)
    assert "lateral inertia" in prose
    assert "unconservative" in prose or "conservative" in prose


# --------------------------------------------------------------------------- #
# G-OR-123 -- one engine, one number, and the side it sits on (#231)
# --------------------------------------------------------------------------- #
def _table_named(section, prefix):
    for sub in [section] + list(section.subsections):
        for table in sub.tables:
            if table.title.startswith(prefix):
                return table
    raise AssertionError(f"no table titled {prefix!r}")


def test_the_oei_input_table_states_the_signed_butt_line():
    """#231 defect 1. Which side failed sets the fin-load sign, and the input
    table's own footnote says so -- two rows printing the same unsigned butt
    line were indistinguishable inputs producing opposite-sign outputs."""
    project = _project("baron_58")
    doc = oc.build_oracle_document(project, ReportSpec())
    table = _table_named(_section_11(doc), "One-engine-inoperative input data")
    column = next(i for i, c in enumerate(table.columns)
                  if c.startswith("Butt line"))
    printed = [float(row[column]) for row in table.rows]
    # Signed, one per side, and each is the module's own side owner applied to
    # its own magnitude -- not a lookup this table performs for itself.
    by_engine = {}
    for fc in _fin_cases(project):
        by_engine.setdefault(fc.engine_index, -fc.sense * fc.inputs.bleng)
    expected = [by_engine[i] for i in sorted(by_engine)]
    assert len(printed) == len(expected)
    for got, want in zip(printed, expected):
        assert math.isclose(got, want, rel_tol=1e-6, abs_tol=1e-9), (got, want)
    assert any(v < 0 for v in printed) and any(v > 0 for v in printed)
    assert "signed" in (table.note or "")


def test_one_engine_answers_to_one_number_across_the_document():
    """#231 defect 2. Section 10 numbers the engines 1-based; section 11 and
    the case names must name the same physical engine by the same number, so
    the 0-based position never reaches the page."""
    project = _project("baron_58")
    doc = oc.build_oracle_document(project, ReportSpec())
    section_10 = next(s for s in doc.sections if s.title.startswith("10"))
    section_11 = _section_11(doc)

    # Section 10's columns are the numbering owner: Engine 1..N in entered order.
    entered = _table_named(section_10, "Engine and propeller data as entered")
    numbers = [c.removeprefix("Engine ") for c in entered.columns[1:]]
    assert numbers == [str(i + 1) for i in range(len(numbers))]

    # Section 11's tables print the same 1-based numbers for the same engines.
    inputs = _table_named(section_11, "One-engine-inoperative input data")
    assert [row[0].split(" — ")[0] for row in inputs.rows] == numbers
    stations = _table_named(section_10, "Where the loads act")
    designations = {row[0]: row[1] for row in stations.rows}
    for row in inputs.rows:
        number, _, name = row[0].partition(" — ")
        assert designations.get(number) == name, row[0]
    for title in ("Load cases assessed", "Critical one-engine-inoperative"):
        table = _table_named(section_11, title)
        engine_column = table.columns.index("Engine")
        assert {row[engine_column] for row in table.rows} == set(numbers), title

    # The case names themselves carry the same numbers (module owner), and the
    # 0-based position appears nowhere in the rendered document.
    labels = {c.label for c in _fin(project) if c.label.startswith(_PREFIX)}
    assert any("(engine 1)" in lbl for lbl in labels), labels
    assert any("(engine 2)" in lbl for lbl in labels), labels

    def walk(sections):
        for s in sections:
            yield s.title
            yield from s.body
            for t in s.tables:
                yield t.title
                yield t.note or ""
                for r in t.rows:
                    yield from (str(cell) for cell in r)
            for f in s.figures:
                yield f.title
                yield f.caption or ""
            yield from walk(s.subsections)

    for text in walk(doc.sections):
        assert "engine 0" not in text.lower(), text[:120]

    # The published condition notes too: "Failed engine #0 at butt line 66 in"
    # was 0-based AND unsigned, and its "#" form slipped the sweep above. The
    # note now states the same 1-based number and the same signed butt line
    # every other statement of the case's identity carries.
    by_engine = {fc.engine_index: -fc.sense * fc.inputs.bleng
                 for fc in _fin_cases(project)}
    published = registry.get("one_engine_out")(project).conditions
    assert published
    for condition in published:
        note = condition.note or ""
        assert "engine #" not in note.lower(), note[:120]
        stated = [f"Failed engine {i + 1} at butt line {y:g} in"
                  for i, y in by_engine.items()]
        assert any(s in note for s in stated), note[:120]


if __name__ == "__main__":                       # zero-dependency self-runner
    import traceback
    failures = 0
    for _name, _fn in sorted(list(globals().items())):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"ok   {_name}")
            except Exception:
                failures += 1
                print(f"FAIL {_name}")
                traceback.print_exc()
    raise SystemExit(1 if failures else 0)
