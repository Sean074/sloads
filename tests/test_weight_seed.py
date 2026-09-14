"""The weight data base's seed button, and what a seeded row still owes (#269).

Design note 57 **D-57.7**: the seed is built fresh in the surviving GUI *with*
#78's hardening in its first version, because porting the known defect into its
new home to fix it later is the anti-pattern ``CLAUDE.md`` rule 4 names. Two
halves, and this file is the gate on both:

1. **Merge, refuse or replace is answered before the click.** The answer is
   *merge*: :data:`~sloads.modules.weight_estimate.SEED_CONTRACT`. It is the
   only one of the three that is also idempotent -- seeding a second time after
   positioning half the rows adds the other half and disturbs nothing -- and it
   makes the destructive path unreachable rather than captioned. The button used
   to replace ``weight.items`` wholesale and say so *after the fact*.
2. **A seeded row is loudly incomplete until positioned and tagged.** WTESTIMA
   supplies weights and nothing else, so the row arrives at station 0 untagged;
   ``mass_distribution.infer_component`` then lumps it on the fuselage beam at
   zero moment arm, which moves the CG and the body shear while looking like
   data. :func:`~sloads.mass_distribution.unplaced_warning` says so, in one
   place, for as long as it is true.
"""

import ast
import os
from dataclasses import replace

import pytest

from sloads import io, mass_distribution as md
from sloads.field_registry import TABLE_SEEDS
from sloads.models import MassComponent, MassItem, MassItemKind, Project
from sloads.modules.weight_estimate import SEED_CONTRACT, seed_plan, seeded_items

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXAMPLE = os.path.join(_ROOT, "examples", "ga6_normal.project.json")


def _project() -> Project:
    return io.load_project(_EXAMPLE)


# --------------------------------------------------------------------------- #
# The click is stated before it happens
# --------------------------------------------------------------------------- #
def test_the_plan_names_what_it_adds_and_what_it_keeps_before_the_click():
    """The caption is built from the plan, not written under the button by hand."""
    project = _project()
    plan = seed_plan(project)
    assert plan.offers and plan.add
    caption = plan.caption()
    assert str(len(plan.add)) in caption
    assert str(len(plan.kept)) in caption
    # The contract itself is carried, so "what happens to my rows" is answered
    # by the one sentence that owns the answer.
    assert SEED_CONTRACT in caption


def test_seeding_adds_and_never_replaces_an_entered_row():
    """#78's destructive half: an entered row keeps its weight, station and tag."""
    project = _project()
    before = {it.name: (it.weight_lb, it.x, it.component) for it in project.weight.items}
    after = seeded_items(project)
    for item in after:
        if item.name in before:
            assert (item.weight_lb, item.x, item.component) == before[item.name]
    # Nothing is dropped, and the entered rows keep their order at the head.
    assert [it.name for it in after[:len(before)]] == list(before)
    assert len(after) == len(before) + len(seed_plan(project).add)


def test_seeding_twice_adds_nothing_the_second_time():
    """Merge is idempotent; replace and refuse are not, which is why it was chosen."""
    project = _project()
    project.weight.items.extend(seed_plan(project).add)
    again = seed_plan(project)
    assert not again.offers
    assert again.reason


def test_a_row_already_entered_is_matched_on_its_name_not_its_spelling():
    project = _project()
    offered = seed_plan(project).add
    assert offered, "the fixture must have something left to seed"
    project.weight.items.append(replace(offered[0], name=f"  {offered[0].name.upper()} "))
    assert offered[0].name not in [it.name for it in seed_plan(project).add]


def test_a_project_with_no_mission_inputs_is_told_why_rather_than_crashing():
    project = _project()
    project.weight.estimation = None
    plan = seed_plan(project)
    assert not plan.offers
    assert plan.reason
    assert not plan.caption().startswith("Adds")


# --------------------------------------------------------------------------- #
# A seeded row is loudly incomplete until it is placed
# --------------------------------------------------------------------------- #
def test_a_seeded_row_is_named_as_unplaced_until_it_is_positioned_and_tagged():
    project = _project()
    assert md.unplaced_warning(project) == "", "the fixture's own rows are placed"

    seeded = seed_plan(project).add
    project.weight.items.extend(seeded)
    owed = md.unplaced_items(project)
    assert owed, "a seeded row carries a weight and nothing else"
    assert set(owed) <= {it.name for it in seeded}

    # Positioned *and* tagged clears it; either one alone does not.
    project.weight.items = [
        replace(it, x=100.0) if it.name in owed else it for it in project.weight.items]
    assert md.unplaced_items(project) == ()

    project.weight.items = [
        replace(it, x=0.0, component=MassComponent.FUSELAGE) if it.name in owed else it
        for it in project.weight.items]
    assert md.unplaced_items(project) == ()


def test_a_blank_row_is_not_reported_as_misplaced_weight():
    """A zero-weight row is a blank in progress; the row counter's warning owns it."""
    project = _project()
    project.weight.items.append(MassItem(name="", weight_lb=0.0, kind=MassItemKind.EMPTY))
    assert md.unplaced_items(project) == ()


def test_the_warning_says_what_the_unplaced_rows_cost():
    project = _project()
    project.weight.items.extend(seed_plan(project).add)
    text = md.unplaced_warning(project)
    assert "fuselage beam" in text and "station" in text


# --------------------------------------------------------------------------- #
# One owner for the button's behaviour
# --------------------------------------------------------------------------- #
def test_the_table_seed_registry_names_a_real_list_prefix():
    """``TABLE_SEEDS`` is ``RECORD_SEEDS``' analogue and is keyed the same way."""
    assert TABLE_SEEDS
    for prefix, seed in TABLE_SEEDS.items():
        assert prefix.endswith("[]")
        plan = seed(_project())
        assert hasattr(plan, "caption") and hasattr(plan, "offers")


def test_the_estimate_to_item_expansion_has_exactly_one_caller():
    """The merge, the matching and the sentence are the calc's; a page only renders.

    A GUI that expanded the estimate into rows itself would be the second owner
    this step exists to avoid -- and the one #270 would have to delete twice. The
    one caller is :func:`~sloads.modules.weight_estimate.seed_plan`, which is
    what both front-ends ask.
    """
    callers = []
    for base, _dirs, names in os.walk(_ROOT):
        if any(part in base for part in (".venv", ".git", "__pycache__", "reference")):
            continue
        for name in names:
            if not name.endswith(".py") or name == os.path.basename(__file__):
                continue
            path = os.path.join(base, name)
            tree = ast.parse(open(path, encoding="utf-8").read())
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == "estimate_to_mass_items"):
                    callers.append(os.path.relpath(path, _ROOT))
    assert callers == ["sloads/modules/weight_estimate.py"], callers


# --------------------------------------------------------------------------- #
# The page renders the offer, and the warning that follows it
# --------------------------------------------------------------------------- #
def _page(project=None):
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_string(
        "from oracle_app.form import render_step\nrender_step('weight_mass')\n",
        default_timeout=120)
    at.session_state["project"] = project if project is not None else _project()
    at.run()
    return at


def test_the_oracle_page_offers_the_seed_and_says_what_it_does_first():
    at = _page()
    assert not at.exception, [e.message for e in at.exception]
    labels = [b.label for b in at.button]
    assert any("Seed" in label and "from the estimate" in label for label in labels), labels
    assert any(SEED_CONTRACT in c.value for c in at.caption)


def test_seeding_moves_the_row_counter_and_offers_no_delete():
    """The seed adds rows and the page does not then offer to remove them.

    The 0.8.4 closure review: the click extended the list in the button body,
    which cannot move the retained row counter, so the next render warned that
    the count disagreed with the table and rendered *Delete the last N row(s)*
    for exactly the N rows just seeded -- the seed contract's *never deletes*
    undone by the page's own next sentence. The seed now runs as the button's
    ``on_click`` and moves the counter, the way row deletion always has.
    """
    at = _page()
    project = at.session_state["project"]
    before = len(project.weight.items)
    added = len(seed_plan(project).add)
    assert added, "the fixture must have something left to seed"
    next(b for b in at.button if "Seed" in b.label and "from the estimate" in b.label
         ).click().run()
    assert not at.exception, [e.message for e in at.exception]
    items = at.session_state["project"].weight.items
    assert len(items) == before + added
    counter = next(w for w in at.number_input if w.label.endswith("rows"))
    assert counter.value == len(items), (counter.label, counter.value, len(items))
    assert not [b.label for b in at.button if "Delete the last" in b.label]
    assert not [w.value for w in at.warning if "row count says" in w.value]


def test_the_oracle_page_warns_loudly_about_rows_that_were_never_placed():
    """A warning, not a caption -- and it is on the page before anything is clicked."""
    project = _project()
    project.weight.items.extend(seed_plan(project).add)
    at = _page(project)
    assert not at.exception, [e.message for e in at.exception]
    expected = md.unplaced_warning(project)
    assert any(w.value == expected for w in at.warning), [w.value for w in at.warning]


if __name__ == "__main__":  # zero-dependency self-runner
    import sys

    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
