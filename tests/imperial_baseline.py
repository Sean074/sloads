"""The Imperial-output baseline: every deliverable channel, every example, digested.

M4-20 changed how every deliverable is written. Its central promise (decision
D-21) is that **Imperial output is unchanged** but for its new in-band unit
statement — a promise that is worth exactly as much as the test behind it.

This module builds the artifact set once, so the generator and the guard cannot
drift apart:

* :func:`artifacts` renders every channel for one example, in Imperial, with no
  header stamp (the stamp carries a tool version and would make the digest
  depend on the build rather than on the numbers).
* :func:`digests` reduces each to a SHA-256, and ``fixtures_imperial/digests.json``
  freezes them.

Digests rather than full copies: the six examples across ~10 channels each are
megabytes of near-identical CSV, and the question a guard has to answer is binary
("did any Imperial byte move?"). When one fails, regenerate locally and diff the
two renders — the frozen file tells you *that* it moved, and ``git diff`` on the
regenerated fixture tells you which channel.

Regenerate deliberately, never reflexively::

    .venv/bin/python tests/imperial_baseline.py     # rewrites the fixture

A regeneration is a claim that the change to Imperial output is intended. Say so
in the commit and in ``CHANGELOG.md``.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "fixtures_imperial", "digests.json")

#: Every shipped example — the GA single the oracle is locked to, the twins, and
#: the two concept-mode configurations that exceed the FAR 23 caps.
#: (``cessna_210`` and ``dhc8_dash8`` retired to unmaintained parking, #264;
#: ``baron_58`` added 2026-09-11 — it postdated this list and was never
#: pinned, so the closure-locked twin's delivered bytes went unguarded. The
#: tie to ``examples/`` is now structural:
#: ``test_deliverable_units.py::test_the_baseline_pins_every_bundled_example``
#: fails when a fixture is added or removed without a deliberate regeneration.)
EXAMPLES = (
    "atr42_100.project.json",
    "baron_58.project.json",
    "concept_heavy.project.json",
    "concept_regional_jet.project.json",
    "ga6_normal.project.json",
)


def _try(fn, *args, **kwargs):
    """Render a channel, or skip it — an example that lacks a slice has no artifact."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, ZeroDivisionError, KeyError, IndexError, TypeError):
        return None


def artifacts(example: str) -> Dict[str, str]:
    """``{channel: text}`` for one example, rendered in Imperial with no stamp."""
    from sloads import io, registry
    from sloads.report import applied as ap
    from sloads.export.balanced_deck import balanced_deck
    from sloads.modules.aileron import build_aileron
    from sloads.modules.balance import build_balanced_cases
    from sloads.modules.body_loads import build_body_loads
    from sloads.modules.flap import build_flap
    from sloads.modules.net_loads import build_net_loads, loads_ref_axis_results
    from sloads.modules.tab import build_tabs
    from sloads.modules.tail_span import build_tail_span
    from sloads.modules.taildist import build_tail_chordwise
    from sloads.report import LoadChannel, module_text_report
    from sloads.report import tables as rt

    project = io.load_project(os.path.join(_ROOT, "examples", example))
    out: Dict[str, str] = {}

    # Human channel: one load-case CSV and one text report per module, on the
    # LIMIT channel -- the baseline exists to represent what ``cli.py`` builds,
    # and since design note 48 (OR-76/OR-79) the CLI's per-module output is the
    # LIMIT channel. Rendering ULTIMATE here would freeze bytes no shipped
    # command produces.
    module_results = registry.run_all_modules(project)
    for mr in module_results:
        out[f"csv/{mr.module}"] = io.load_cases_csv(
            mr, channel=LoadChannel.LIMIT)
        out[f"txt/{mr.module}"] = module_text_report(
            mr.module, mr.conditions, channel=LoadChannel.LIMIT)

    # Solver channel: the component deliverables, exactly as the Export page
    # builds them (wing results transferred to the loads reference axis first).
    net = _try(build_net_loads, project)
    wing = loads_ref_axis_results(project, net.wing_net) if net is not None else None
    body = _try(build_body_loads, project)
    tail = _try(build_tail_chordwise, project)
    control = []
    for build in (build_aileron, build_flap, build_tabs):
        control += (_try(build, project) or [])

    # Note 56 D-56.2 deleted ten of the channels this baseline used to render
    # -- the wing span CSV, wing cards, wing stick deck, body span/fitting/cards,
    # tail chordwise and cards, and both control-surface files -- together with
    # the two spanwise tail decks below them. What replaces them is the applied
    # load set per component, which is the row set every one of those decks was
    # written from, so the *loads* under digest are unchanged even though the
    # channel names and the byte counts are not.
    if wing:
        text = _try(ap.applied_load_csv, wing)
        if text:
            out["sbeam/wing_applied"] = text
    if body:
        text = _try(ap.applied_load_csv, body, component="fuselage",
                    project=project)
        if text:
            out["sbeam/body_applied"] = text

    # Spanwise empennage (plan 09 T4). Per surface, because each has its own axis
    # map and its own GID band -- a shared channel would hide a swap between them.
    spans = _try(build_tail_span, project) or {}
    for component in ("htail", "vtail"):
        results = spans.get(component) or []
        if not results:
            continue
        text = _try(ap.applied_load_csv, results, component=component)
        if text:
            out[f"sbeam/{component}_applied"] = text

    # The assembled full-span deck -- the mission's aim-2 deliverable, and until
    # B8a-2 the one deliverable this baseline did **not** cover. Found while
    # changing the closure field: the 6-DOF rewrite moved every closure card in
    # every assembled deck and no digest noticed, because the per-component
    # channels above are all this file ever rendered. Plan 11 acceptance #5 ("if
    # a digest moves, something leaked") can only mean something if the digest
    # exists.
    deck = _try(balanced_deck, project)
    if deck:
        out["sbeam/balanced_deck"] = deck

    # The LRA beam model (step 12) -- the third deliverable. Absent on the two
    # fixtures with no fuselage data, where the exporter refuses by design
    # (LraRefusal is a ValueError, so _try records the refusal as absence).
    from sloads.export.lra_model import lra_model_bdf

    deck = _try(lra_model_bdf, project)
    if deck:
        out["sbeam/lra_model"] = deck

    # The CONM2 mass model -- the second deliverable, and until note 56 D-56.6
    # the one this baseline still did not cover. D-56.6 moved every CONM2 onto
    # its own GRID at the item's CG and deleted the deck's placeholder beam,
    # which rewrote the artifact end to end, and no digest channel moved --
    # because none existed. Exactly the hole the balanced deck's channel was
    # added to close, one artifact over. Both forms are rendered: the fragment
    # is what a recipient splices, the check deck is what a GPWG reads.
    from sloads.export.mass_cards import conm2_fragment, mass_check_deck

    for name, build in (("mass_model", conm2_fragment),
                        ("mass_check", mass_check_deck)):
        deck = _try(build, project)
        if deck:
            out[f"sbeam/{name}"] = deck

    # The index's assembled deck-number column is filled from the assembled
    # deck's own cases (design note 17), so the baseline builds them here too --
    # a column no channel renders is a column no digest can protect.
    balanced = _try(build_balanced_cases, project, []) or []
    # Deck-exported results first (see ``case_index_rows_from``): first-seen
    # defines a row's flight condition, and the row states the condition its
    # cards were computed at.
    index = _try(rt.case_index_csv_from,
                 wing or [], body or [], tail or [], control,
                 *(mr.conditions for mr in module_results),
                 assembled=balanced)
    if index:
        out["case_index"] = index
    # The gear load report (G-12) -- five of six fixtures produce one, and the
    # sixth has no gear geometry at all, so its absence here is the coverage
    # statement rather than a gap.
    gear = _try(rt.gear_report_csv, project)
    if gear:
        out["gear_report"] = gear
    return out


def digests() -> Dict[str, Dict[str, str]]:
    """``{example: {channel: sha256}}`` across every example."""
    return {
        example: {
            channel: hashlib.sha256(text.encode("utf-8")).hexdigest()
            for channel, text in sorted(artifacts(example).items())
        }
        for example in EXAMPLES
    }


def load_fixture() -> Dict[str, Dict[str, str]]:
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def write_fixture() -> None:
    os.makedirs(os.path.dirname(FIXTURE), exist_ok=True)
    with open(FIXTURE, "w", encoding="utf-8") as fh:
        json.dump(digests(), fh, indent=2, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":
    write_fixture()
    frozen = load_fixture()
    print(f"wrote {FIXTURE}")
    print(f"{len(frozen)} examples, "
          f"{sum(len(v) for v in frozen.values())} channels")
