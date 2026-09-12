"""The deliverable tables that are not decks: the case index, the governing
safety-factor table, the gear report, and the export-scope filter they share.

**Why they live in `report/` (note 56 D-56.1).** They were written in
`export/sbeam_bridge.py` because that is where the first consumer happened to
be, and they stayed there through five milestones. None of them emits bulk data
or knows what a GRID is: the case index maps an ID to the condition that defines
it, the safety-factor table is a view of :mod:`sloads.safety_factors`' governing
rows, and the gear report is a per-leg load table. They are *documents*, and
`report/` is where documents are assembled -- which is why
:mod:`sloads.report.content` and the oracle sections were already reaching back
across the package to import them.

The move is a relocation and nothing else: every row, column, header and byte is
what it was, and the frozen Imperial digest is the proof. What changes is that
deleting the per-component solver decks (D-56.2) can no longer take these with
it.

Units: the tables that carry loads resolve the **solver** channel through
:func:`sloads.export.deck_format.solver_units`, the one owner of that choice,
and coordinates convert through :mod:`sloads.export.coordinates` -- so a table
and the deck beside it cannot state different units for one load.
"""

from __future__ import annotations

import csv
import io as _io
from typing import List, Optional, Sequence

from ..case_ids import ASSEMBLED_DECK, COMPONENT_DECK, deck_load_id
from ..export.coordinates import to_force, to_grid, to_moment
from ..export.deck_format import fmt, load_label, sf_str, solver_units
from ..models import Project
from ..units import DeliverableUnits, UnitSystem


# --------------------------------------------------------------------------- #
# Export-scope filter (Step D8.3): the Export page's "full set vs governing
# set" toggle, applied to any case-carrying result list whose ``case_ref``
# genuinely traces back to ``envelope.critical`` (fuselage/htail/vtail -- see
# the caller's own scoping note; wing/control-surface results are never passed
# through this since their case ids don't overlap ``envelope.critical``'s).
# --------------------------------------------------------------------------- #
def filter_by_selected_case_ids(results: Sequence, selected_ids) -> List:
    """``results`` filtered to items whose ``case_ref.case_id`` is in
    ``selected_ids``; a result with no ``case_ref`` is kept (defensive -- never
    silently drop an un-tagged case). ``selected_ids is None`` means "no
    filter", returning ``results`` unchanged."""
    if selected_ids is None:
        return list(results)
    ids = set(selected_ids)
    return [r for r in results if not r.case_ref or r.case_ref.case_id in ids]


# --------------------------------------------------------------------------- #
# Case-index table (ID -> component, condition, CG, speed, altitude, FAR)
# --------------------------------------------------------------------------- #
#: The index's deck-number column per deck family. **Two** columns, not one
#: (design note 17, user decision 2026-08-13): one case can hold a number in
#: both -- ``W-05`` is ``105`` in the wing component deck and ``5105`` in the
#: assembled full-span one -- so a single unqualified column would be silently
#: wrong for whichever family it was not quoting. Each header keeps the word
#: ``SUBCASE`` a consumer greps for beside the ``LOAD`` the card set is selected
#: by; they are one integer in the deck (``LOAD = 103`` inside ``SUBCASE 103``).
LOAD_ID_COLUMN = {
    COMPONENT_DECK: "LOAD/SUBCASE (component)",
    ASSEMBLED_DECK: "LOAD/SUBCASE (assembled)",
}


def case_index_rows_from(*groups: Sequence, assembled: Sequence = ()) -> List[dict]:
    """One row per distinct ``case_id`` across any number of case-carrying object
    groups (anything with a ``.case_ref`` -- ``WingLoadResult``, ``BodyLoadResult``,
    ``TailChordResult``, ``ControlSurfaceLoadResult``, ``CriticalCondition``,
    engine ``ConditionResult``, LANDLOAD ``GearReactionCase``, ...). Rows are
    emitted in first-seen order across the groups, in the order given; a
    ``case_id`` seen again (the same case appearing in multiple deliverables --
    e.g. a wing case in ``wing_air``, ``wing_inertia`` and ``wing_net``) is not
    repeated.

    **First-seen defines the row's flight condition**, so callers pass the
    **deck-exported load results before** SELECT's ``CriticalCondition``s (as
    :func:`case_index_rows` does, and as the report's case index and the Imperial
    baseline do). One ``case_id`` can be named at two conditions -- an entered
    ``WingLoadCase`` may restate the CL/V of a condition SELECT already picked
    (``atr42_100``'s ``PHAA``: 170 kt entered against SELECT's 185.85 kt V-n
    point) -- and this table is what a consumer joins ``SUBCASE 103`` to, so the
    condition it states is the one **the cards under that id were computed at**
    (user decision 2026-08-13; the case-side half is
    ``wing_inertia.wing_case_ref``). SELECT's own governing-loads row keeps its
    V-n point, which is what *its* numbers were computed at.

    ``assembled`` is the assembled full-span deck's own cases
    (``BalancedCaseResult``), passed separately because **which** deck column a
    row fills is a property of where the case is exported, not of its id: an id
    is quoted in a column only when it is actually in that deck. A handed id
    (``W-05R``) therefore fills the assembled column alone; a symmetric case that
    both stands as a component deck and assembles fills both, which is the point
    of carrying two columns (design note 17).
    """
    by_id: dict = {}
    rows: List[dict] = []

    def add(item, family: str, hand: str = "") -> None:
        ref = item.case_ref
        if ref is None:
            return
        row = by_id.get(ref.case_id)
        if row is None:
            row = {
                "ID": ref.case_id,
                # The deck-side identity of the same case (M4-2 decision 10): the
                # index is where a consumer joins "SUBCASE 103" to its condition.
                LOAD_ID_COLUMN[COMPONENT_DECK]: "",
                LOAD_ID_COLUMN[ASSEMBLED_DECK]: "",
                "Component": ref.component,
                "Condition": ref.condition,
                "CG": ref.cg,
                "Speed (kt)": f"{ref.speed_kt:.2f}" if ref.speed_kt is not None else "",
                "Altitude (ft)": f"{ref.altitude_ft:.0f}" if ref.altitude_ft is not None else "",
                "FAR": ref.far_reference,
            }
            by_id[ref.case_id] = row
            rows.append(row)
        column = LOAD_ID_COLUMN[family]
        if not row[column]:
            # The hand is read off the case, not off its id (G-8): the 23.485
            # side pair carries LANDLOAD's own unsuffixed ids, so parsing the id
            # would put both twins in the symmetric block and quote a SUBCASE the
            # assembled deck does not contain.
            row[column] = deck_load_id(ref.case_id, family, hand)

    # A component-deck result has no hand: the per-component decks are the
    # symmetric analysis views (CONVENTIONS §7.1), so the column takes the bare
    # id. Only the assembled ``BalancedCaseResult`` carries ``hand``, and it is
    # passed, not probed for (CH-2).
    for group in groups:
        for item in group:
            add(item, COMPONENT_DECK)
    for item in assembled:
        add(item, ASSEMBLED_DECK, hand=item.hand)
    return rows


def case_index_rows(project: Project, extra: Sequence = (),
                    assembled: Sequence = ()) -> List[dict]:
    """One row per distinct ``case_id`` across ``project``'s persisted result
    slices, plus any ``extra`` case-carrying objects (e.g. a run's engine
    ``ConditionResult``s or LANDLOAD ``GearReactionCase``s -- transient results
    not stored on ``Project``, so the caller passes them in when available).

    Rows are emitted in first-seen order: ``loads`` slices (wing_net -> body_net
    -> tail_chordwise -> control_surface), then ``envelope.critical`` (SELECT's
    own conditions -- since M4-2 a wing condition and the WINGINER/NETLOADS
    distribution derived from it share one ``case_id``, so the dedupe collapses
    them to a single row), then ``extra``, then ``assembled`` (the assembled
    full-span deck's own cases, which fill the assembled deck-number column --
    see :func:`case_index_rows_from`).
    """
    groups: List[Sequence] = []
    if project.loads is not None:
        groups += [project.loads.wing_net, project.loads.body_net,
                  project.loads.tail_chordwise, project.loads.control_surface]
    if project.envelope is not None and project.envelope.critical is not None:
        groups.append(project.envelope.critical.conditions)
    groups.append(extra)
    return case_index_rows_from(*groups, assembled=assembled)


_CASE_INDEX_FIELDS = ["ID", LOAD_ID_COLUMN[COMPONENT_DECK],
                      LOAD_ID_COLUMN[ASSEMBLED_DECK], "Component", "Condition",
                      "CG", "Speed (kt)", "Altitude (ft)", "FAR"]


def _rows_to_csv(rows: List[dict], header_comment: str = "") -> str:
    buf = _io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_CASE_INDEX_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return header_comment + buf.getvalue()


def case_index_csv(project: Project, extra: Sequence = (), header_comment: str = "",
                   assembled: Sequence = ()) -> str:
    """The case-index table (ID -> full definition) as CSV text, from ``project``'s
    persisted result slices."""
    return _rows_to_csv(case_index_rows(project, extra=extra, assembled=assembled),
                        header_comment)


def case_index_csv_from(*groups: Sequence, header_comment: str = "",
                        assembled: Sequence = ()) -> str:
    """The case-index table as CSV text, from explicit case-carrying object groups
    (for a caller -- e.g. the Export page -- that recomputes results live rather
    than reading them off ``Project``)."""
    return _rows_to_csv(case_index_rows_from(*groups, assembled=assembled),
                        header_comment)


_SAFETY_FACTOR_FIELDS = ["Family", "FAR", "Load class", "SF", "Derived SF",
                         "Status", "Basis"]


def safety_factors_csv(project: Project, header_comment: str = "") -> str:
    """The governing safety-factor table as CSV text (M4-8 / decision G-11).

    The companion file for the report's governing-factors section: it travels in
    the bundle and the manifest, stamped like every other channel, so the factor
    behind an exported deck is legible without the report beside it. ``Derived SF``
    is the regulation's own value, kept next to ``SF`` precisely so an override is
    self-evident in the file rather than only in the prose."""
    from ..safety_factors import GoverningTable

    buf = _io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_SAFETY_FACTOR_FIELDS)
    writer.writeheader()
    for r in GoverningTable.for_project(project).rows:
        writer.writerow({"Family": r.label, "FAR": r.far_reference,
                         "Load class": r.load_class, "SF": f"{r.factor:g}",
                         "Derived SF": f"{r.derived_factor:g}",
                         "Status": r.status, "Basis": r.basis})
    return header_comment + buf.getvalue()


# The row keys -- the stable programmatic vocabulary ``gear_report_rows``
# returns and the tests read. The *file* header is built per unit set by
# ``_gear_report_headers`` so the CSV states its own units (R6-C2); keeping the
# keys bare is what lets a consumer of the rows not care which system a bundle
# was rendered in.
_GEAR_REPORT_FIELDS = [
    "ID", "Case", "Condition", "FAR", "Loading", "Design weight",
    "Leg", "Wheel", "Carrier",
    "Strut state", "Ground angle (deg)", "Stroke", "Stroke (%)",
    "Patch X", "Patch Y", "Patch Z",
    "Ground-line V", "Ground-line D", "Ground-line S",
    "Datum Fx", "Datum Fy", "Datum Fz",
    "Ref point X", "Ref point Y", "Ref point Z",
    "Transfer Mx", "Transfer My", "Transfer Mz",
    "Leg weight", "Leg inertia Fz", "Net Fz above trunnion",
    "SF",
]


def _gear_report_headers(u: DeliverableUnits) -> List[str]:
    """The gear CSV's header row for unit set ``u`` (R6-C2).

    Every dimensional column carries its unit and, if it is a load, its ``-ULT``
    marker -- the same D-21 rule the span CSV follows, so this file states its
    own units instead of leaving them to the methods stamp. The weights
    (``Design weight``, ``Leg weight``) are inputs, not factored loads, so they
    carry the plain force unit; ``SF`` is the last column, exactly as on every
    sibling channel.
    """
    ln, fo = u.length.label, u.force.label
    fu, mu = load_label(fo), load_label(u.moment.label)
    labels = {
        "Design weight": f"Design weight ({fo})",
        "Stroke": f"Stroke ({ln})",
        "Patch X": f"Patch X ({ln})", "Patch Y": f"Patch Y ({ln})",
        "Patch Z": f"Patch Z ({ln})",
        "Ground-line V": f"Ground-line V ({fu})",
        "Ground-line D": f"Ground-line D ({fu})",
        "Ground-line S": f"Ground-line S ({fu})",
        "Datum Fx": f"Datum Fx ({fu})", "Datum Fy": f"Datum Fy ({fu})",
        "Datum Fz": f"Datum Fz ({fu})",
        "Ref point X": f"Ref point X ({ln})",
        "Ref point Y": f"Ref point Y ({ln})",
        "Ref point Z": f"Ref point Z ({ln})",
        "Transfer Mx": f"Transfer Mx ({mu})",
        "Transfer My": f"Transfer My ({mu})",
        "Transfer Mz": f"Transfer Mz ({mu})",
        "Leg weight": f"Leg weight ({fo})",
        "Leg inertia Fz": f"Leg inertia Fz ({fu})",
        "Net Fz above trunnion": f"Net Fz above trunnion ({fu})",
    }
    return [labels.get(f, f) for f in _GEAR_REPORT_FIELDS]


def gear_report_rows(project: Project, units: Optional[DeliverableUnits] = None,
                     safety_factor: Optional[float] = None) -> List[dict]:
    """The gear load report: one row per case per leg (decision G-12).

    **A free body, not a load list.** Each row states the reaction where LANDLOAD
    computes it -- the tyre contact patch, in the ground-line frame the manual
    prints and a gear engineer reads -- together with the strut state, ground
    angle and stroke it was computed at, and then the *same* reaction where the
    airframe receives it: the gear reference point, in airplane axes, with the
    lever-arm couple that carried it there. Both ends of the leg, so the two G-12
    artifacts are provably one load seen from two sides.

    **All 33 cases**, against the assembled deck's 24. The 23.499 supplementary
    nose-wheel family has no airplane equilibrium to assemble, but it is a
    gear-design case and this report is where it was always aimed -- the two
    artifacts carry different case sets by design, and each says so.

    ``Leg inertia Fz`` is the leg's own weight at the case's vertical ground-line
    load factor and is what closes the free body; ``Net Fz above trunnion`` is the
    reaction less that. Both are blank when no leg weight is entered (G-12a),
    which shows the free body **open** rather than closing it against a guess.
    See :data:`sloads.gear_loads.UNSPRUNG_NOTE` for the limit on what the inertia
    term means -- it is not a gear design load.

    Per the load-output contract, every row states its ``SF`` (R6-C2), and the
    ``Wheel`` column says which wheel a ``main`` row describes: the starboard
    one of the pair, its port twin being the mirror (R6-C4).
    """
    from ..gear_loads import MAIN, gear_case_loads
    from ..safety_factors import table_for

    u = units or solver_units(UnitSystem.IMPERIAL)
    table = table_for(project)
    rows: List[dict] = []
    for case in gear_case_loads(project):
        sf = (safety_factor if safety_factor is not None
              else table.required_factor_for(case))
        for leg in case.legs:
            if not any(leg.airplane) and not any(leg.ground_line):
                continue          # this leg carries nothing in this case
            px, py, pz = to_grid(*leg.patch, u)
            nx, ny, nz = to_grid(*leg.node, u)
            gv, gd, gs = to_force(leg.ground_line[0], leg.ground_line[1],
                                  leg.ground_line[2], u)
            fx, fy, fz = to_force(leg.airplane[0], leg.airplane[1],
                                  leg.airplane[2], u)
            mx, my, mz = to_moment(leg.couple[0], leg.couple[1],
                                   leg.couple[2], u)
            net = leg.net_of_inertia
            inertia = ("" if leg.inertia_fz is None else
                       fmt(to_force(0.0, 0.0, leg.inertia_fz, u)[2]))
            rows.append({
                "ID": case.case_ref.case_id if case.case_ref else "",
                "Case": str(case.case),
                "Condition": case.description,
                "FAR": case.far_reference,
                "Loading": case.cg_name,
                "Design weight": fmt(case.weight_lb * u.force.factor),
                "Leg": leg.leg,
                # A main row states the starboard wheel of the pair (its patch
                # is at +tread/2); the port twin is the mirror. Said in the
                # file rather than only in a code comment (R6-C4).
                "Wheel": "starboard" if leg.leg == MAIN else "centreline",
                "Carrier": leg.carrier.value if leg.carrier is not None else "",
                "Strut state": leg.strut_state,
                "Ground angle (deg)": f"{leg.ground_angle_deg:.3f}",
                "Stroke": fmt(leg.stroke_in * u.length.factor),
                "Stroke (%)": f"{leg.stroke_fraction * 100:.1f}",
                "Patch X": fmt(px), "Patch Y": fmt(py), "Patch Z": fmt(pz),
                "Ground-line V": fmt(gv), "Ground-line D": fmt(gd),
                "Ground-line S": fmt(gs),
                "Datum Fx": fmt(fx), "Datum Fy": fmt(fy), "Datum Fz": fmt(fz),
                "Ref point X": fmt(nx), "Ref point Y": fmt(ny),
                "Ref point Z": fmt(nz),
                "Transfer Mx": fmt(mx), "Transfer My": fmt(my),
                "Transfer Mz": fmt(mz),
                "Leg weight": ("" if leg.leg_weight_lb is None else
                               fmt(leg.leg_weight_lb * u.force.factor)),
                "Leg inertia Fz": inertia,
                "Net Fz above trunnion": ("" if net is None else
                                          fmt(to_force(0.0, 0.0, net[2], u)[2])),
                "SF": sf_str(sf),
            })
    return rows


def gear_report_csv(project: Project, header_comment: str = "",
                    system: UnitSystem = UnitSystem.IMPERIAL) -> str:
    """The gear load report as CSV text -- the G-12 companion file.

    Travels in the Export bundle and the manifest, stamped like every other
    channel, so the boundary condition a gear analysis starts from is legible
    without the report beside it. Loads are **LIMIT**, per the standing
    load-output contract, with the factor the governing table gives the case
    stated and not applied (``LIMIT (14 CFR 23.471 -- ground loads are limit
    loads); SF 1.5 not applied``).
    """
    u = solver_units(system)
    rows = gear_report_rows(project, u)
    buf = _io.StringIO()
    # The header states this bundle's units (R6-C2); the rows keep the bare
    # keys so their programmatic vocabulary is system-independent.
    csv.writer(buf).writerow(_gear_report_headers(u))
    writer = csv.DictWriter(buf, fieldnames=_GEAR_REPORT_FIELDS)
    writer.writerows(rows)
    return header_comment + buf.getvalue()


def write_gear_report_csv(project: Project, path: str, header_comment: str = "",
                          system: UnitSystem = UnitSystem.IMPERIAL) -> None:
    # Rendered **before** the file is opened: this is the one export channel that
    # legitimately refuses (a project with no gear geometry produces no report),
    # and opening first would truncate an existing file -- or leave a new empty
    # one -- on the way to the error. The CLI's contract is that a failed export
    # leaves no partial artifact set.
    text = gear_report_csv(project, header_comment, system)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def write_case_index_csv(project: Project, path: str, extra: Sequence = (),
                         assembled: Sequence = ()) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(case_index_csv(project, extra=extra, assembled=assembled))
