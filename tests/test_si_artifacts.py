"""An SI artifact states every number in SI (#338).

A number a calc builder formats into text never meets a unit system:
``units.convert_results`` converts values, never labels or notes. Before #338
the SI LRA deck said "side of body ASSUMED at BL 23.00 in" beside GRIDs in mm,
the SI mass deck captioned each MASSSET in lb and in, ``concept_heavy``'s SI
document placed its wing station "at FS 236.0 in", and Baron's SI WTENV table
put "station -105 in" in a label. The owner is ``units.UnitText`` (a sentence
whose quantities render in the channel written to) for the computed notes, and
a value of its own for a number a persisted record carries (D2).

* **SA-1, the rule** -- ``UnitText`` renders each quantity through the same
  conversion and precision a ``LoadValue`` goes through, keeps aviation units,
  and has no implicit text.
* **SA-2, the owner is structural** -- every provenance record a deck reads
  types its ``note`` as ``UnitText``.
* **SA-3, the gate** -- on every shipped fixture, the SI LRA deck's and the SI
  mass decks' ``$`` text, and (slow lane) the SI issue package, contain no
  Imperial-unit number. Case names and the project name are identifiers, the
  same in every system (D3), and are removed before the scan.
"""

import dataclasses
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from imperial_baseline import EXAMPLES

from sloads import io
from sloads.units import NO_TEXT, Quantity, UnitSystem, UnitText, format_value, unit_text

_EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

#: A number followed by an Imperial unit sloads converts in SI. ``kt`` and
#: altitude ``ft`` are aviation-standard in both systems and are not listed.
#: ``in`` before one of :data:`_PREPOSITION_OBJECTS` is the preposition
#: ("section 7 in full"), named rather than inferred: "-105 in is outside" is
#: a station, and a rule that let any word follow would pass it.
_PREPOSITION_OBJECTS = ("full", "the", "a", "an", "each", "every", "its", "this", "both")
_IMPERIAL_NUMBER = re.compile(
    r"\d(?:[\d,]*\d)?(?:\.\d+)?\s?"
    r"(?:lb-in|in-lb|ft-lb|lb/ft\^?2|lb/in\^?2|slug-ft\^?2|lb-in\^?2|lb\b|psf\b|psi\b|"
    r"in\b(?! (?:" + "|".join(_PREPOSITION_OBJECTS) + r")\b))")


def _project(example):
    return io.load_project(os.path.join(_EXAMPLES_DIR, example))


def _identifiers(project):
    """Every name an artifact may print verbatim: the project's, each weight/CG
    case's, and each assembled case's (a re-weighted ground case is named at
    its weight in lb, D3)."""
    from sloads.modules.balance import build_balanced_cases

    names = {project.name} if getattr(project, "name", "") else set()
    weight = project.weight
    names |= {c.name for c in (getattr(weight, "cg_cases", None) or [])}
    built = build_balanced_cases(project)
    cases = built[0] if isinstance(built, tuple) else built
    names |= {c.cg for c in cases}
    return sorted(names, key=len, reverse=True)


def _leaks(text, names):
    """Imperial-unit numbers in ``text`` once every identifier is removed.

    A deck wraps its ``$`` lines, so a name can break across two; the scan
    reads the comment text joined and whitespace-collapsed."""
    flat = " ".join(re.sub(r"^\$\s*", "", ln) for ln in text.splitlines())
    flat = re.sub(r"\s+", " ", flat)
    for name in names:
        flat = flat.replace(name, "<name>")
    return sorted({m.group(0) for m in _IMPERIAL_NUMBER.finditer(flat)})


def _comments(deck):
    return "\n".join(ln for ln in deck.splitlines() if ln.startswith("$"))


# --------------------------------------------------------------------------- #
# SA-1: the rule
# --------------------------------------------------------------------------- #
def test_a_unit_text_renders_each_quantity_in_the_system_written_to():
    t = unit_text("side of body ASSUMED at BL ", Quantity(23.0, "in"), ", gross ",
                  Quantity(3400.0, "lb", "mass"), ", load ", Quantity(1000.0, "lb"),
                  ", at ", Quantity(170.0, "kt(EAS)"), " and ", Quantity(4.5, "%"), " {x}")
    assert t.render(UnitSystem.IMPERIAL) == (
        f"side of body ASSUMED at BL {format_value(23.0, 'in')} in, gross "
        f"{format_value(3400.0, 'lb')} lb, load {format_value(1000.0, 'lb')} lb, at "
        f"{format_value(170.0, 'kt(EAS)')} kt(EAS) and {format_value(4.5, '%')} % {{x}}")
    si = t.render(UnitSystem.SI)
    assert f"BL {format_value(23.0 * 25.4, 'mm')} mm" in si
    assert f"gross {format_value(3400.0 * 0.45359237, 'kg')} kg" in si          # a weight -> kg
    assert f"load {format_value(1000.0 * 4.4482216152605, 'N')} N" in si        # a force -> N
    assert "170.0 kt(EAS)" in si and si.endswith("% {x}")                      # aviation unit kept; braces literal


def test_a_unit_text_has_no_implicit_text_and_joins_without_rendering():
    a = unit_text("at ", Quantity(10.0, "in"))
    b = unit_text("and ", Quantity(20.0, "in"))
    with pytest.raises(TypeError):
        str(a)
    with pytest.raises(TypeError):
        f"{a}"
    joined = UnitText.join("; ", [a, b]) + "."
    assert joined.render(UnitSystem.SI) == (
        f"at {format_value(254.0, 'mm')} mm; and {format_value(508.0, 'mm')} mm.")
    assert (" " + a).render(UnitSystem.IMPERIAL).startswith(" at ")
    assert not NO_TEXT and not unit_text() and a


# --------------------------------------------------------------------------- #
# SA-2: the owner is structural
# --------------------------------------------------------------------------- #
def test_every_provenance_note_a_deck_reads_is_a_unit_text():
    """The records whose notes reach the LRA deck (through the joint register
    or directly) type ``note`` as ``UnitText``; a ``str`` field here is the
    pre-#338 leak, back. ``BodyDragWaterline`` is the one ``str``: its notes
    state no quantity, and no deck reads it."""
    import typing

    from sloads.derived_geometry import FuselageCentreline, FuselageLra, SobStation
    from sloads.export.lra_model import LraModel
    from sloads.joints import Joint
    from sloads.modules.tail_span import HTailAttachment
    from sloads.tail_geometry import HTailWaterline, TailPlanform, VtailRoot

    for record in (SobStation, FuselageCentreline, FuselageLra, VtailRoot,
                   HTailWaterline, HTailAttachment, Joint):
        assert typing.get_type_hints(record)["note"] is UnitText, record.__name__
    assert typing.get_type_hints(TailPlanform)["notes"] == typing.List[UnitText]
    assert typing.get_type_hints(LraModel)["assumed_notes"] == typing.List[UnitText]


# --------------------------------------------------------------------------- #
# SA-3: the gate
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("example", EXAMPLES)
def test_no_si_solver_file_states_an_imperial_number(example):
    """The SI LRA deck and both SI mass decks, every ``$`` line."""
    from sloads.export.lra_model import LraRefusal, lra_model_bdf
    from sloads.export.mass_cards import conm2_fragment, mass_check_deck

    project = _project(example)
    names = _identifiers(project)
    decks = {"mass": conm2_fragment(project, system=UnitSystem.SI),
             "mass_check": mass_check_deck(project, system=UnitSystem.SI)}
    try:
        decks["lra"] = lra_model_bdf(project, system=UnitSystem.SI)
    except LraRefusal:
        assert example == "concept_heavy.project.json", example   # no side of body: refused by design
    leaks = {name: _leaks(_comments(deck), names) for name, deck in decks.items()}
    assert not any(leaks.values()), leaks


def test_the_si_lra_deck_states_its_case_names_are_identifiers():
    """D3: said once, above the case map, in SI only."""
    from sloads.export.lra_model import CASE_NAME_IDENTIFIER_NOTE, lra_model_bdf

    project = _project("atr42_100.project.json")
    words = CASE_NAME_IDENTIFIER_NOTE.split()[:6]
    si = re.sub(r"\s+", " ", _comments(lra_model_bdf(project, system=UnitSystem.SI)).replace("$", " "))
    imperial = re.sub(r"\s+", " ", _comments(lra_model_bdf(project)).replace("$", " "))
    assert " ".join(words) in si and " ".join(words) not in imperial


@pytest.mark.slow
@pytest.mark.parametrize("example", EXAMPLES)
def test_no_si_issue_package_states_an_imperial_number(example):
    """The SI document and every file of its ``data/``, less the gear report,
    which is the solver channel's companion (``deck_format.fmt``, D-65.8)."""
    from sloads.models.report import default_spec
    from sloads.report.oracle_content import build_oracle_document
    from sloads.report.oracle_latex import render_oracle_document
    from sloads.report.package_data import DATA_DIR, data_files

    project = _project(example)
    names = _identifiers(project)
    doc = build_oracle_document(project, dataclasses.replace(default_spec(), unit_system=UnitSystem.SI))
    channels = {f.name: f.content for f in data_files(doc) if f.name != f"{DATA_DIR}/gear_loads.csv"}
    channels["document"] = render_oracle_document(doc)
    leaks = {name: found for name, text in channels.items() if (found := _leaks(text, names))}
    assert not leaks, leaks


def test_the_wing_station_reaches_the_document_in_its_channel():
    """D2: ``concept_heavy``'s assumed wing station is persisted as a clause
    with no number in it, and section 8 states the station from ``x_wing``."""
    from sloads.joints import WING_STATION_CENTRELINE_REASON
    from sloads.modules.body_loads import build_body_loads

    results = build_body_loads(_project("concept_heavy.project.json"))
    assert results and all(r.wing_station_note == WING_STATION_CENTRELINE_REASON for r in results)
    assert not _leaks(WING_STATION_CENTRELINE_REASON, [])


if __name__ == "__main__":
    import traceback

    failed = 0
    tests = [
        test_a_unit_text_renders_each_quantity_in_the_system_written_to,
        test_a_unit_text_has_no_implicit_text_and_joins_without_rendering,
        test_every_provenance_note_a_deck_reads_is_a_unit_text,
        test_the_si_lra_deck_states_its_case_names_are_identifiers,
        test_the_wing_station_reaches_the_document_in_its_channel,
    ] + [lambda e=e: test_no_si_solver_file_states_an_imperial_number(e) for e in EXAMPLES] \
      + [lambda e=e: test_no_si_issue_package_states_an_imperial_number(e) for e in EXAMPLES]
    for t in tests:
        try:
            t()
            print(f"PASS {getattr(t, '__name__', t)}")
        except Exception:
            failed += 1
            print(f"FAIL {getattr(t, '__name__', t)}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
