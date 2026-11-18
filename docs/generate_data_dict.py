#!/usr/bin/env python3
"""Generate ``docs/10_standard/DATA_DICTIONARY.md`` from the dataclasses.

The ``project.json`` schema (``SCHEMA_VERSION`` is deep and climbing) has no
reference other than the ``sloads/models/`` package itself. This script introspects the
**input** slices of :class:`sloads.models.Project` and emits a markdown data
dictionary: for every field its type, default, a units hint, and -- at *slice*
granularity -- the page that owns it and the calc modules that consume it.

Design (see backlog M2-11, decided 2026-07-20):

* **Source of truth is the code.** Type and default come from
  :func:`dataclasses.fields` / :func:`typing.get_type_hints`; the *units* hint is
  parsed from each field's trailing ``# comment`` in the source (falling back to a
  guess from the field-name suffix, e.g. ``_lb`` -> ``lb``). Comments are prose,
  not a structured units field, so the "Units / notes" column reproduces the
  inline comment verbatim -- treat it as a hint, not a contract.
* **Owning page / consumers are slice-level, not field-level.** ``workflow.py``
  records ``produces``/``requires`` per *slice*, not per field, so a field
  inherits its root slice's page and consumer list. The owning page is the step
  that ``produces`` the slice (plus a small override table for the slices
  ``workflow.py`` does not attribute by ``produces``); consumers are the calc
  modules whose source reads ``.<slice>``.
* **Input slices only.** The result slices (``envelope``/``mass``/``loads``) are
  outputs, not ``project.json`` inputs, and are excluded.

Run it (writes the doc in place; no third-party deps):

    .venv/bin/python docs/generate_data_dict.py

Re-run after any ``models/`` change so the dictionary tracks the schema
(``tests/test_data_dictionary.py`` fails until it is).
"""

from __future__ import annotations

import dataclasses
import enum
import inspect
import re
import typing
from pathlib import Path

import sloads.field_registry as fr
import sloads.models as m
import sloads.workflow as w

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = REPO_ROOT / "sloads" / "modules"
OUT_PATH = REPO_ROOT / "docs" / "10_standard" / "DATA_DICTIONARY.md"

# --------------------------------------------------------------------------- #
# The Project *input* slices, in workflow order. (attr, human-readable role)
# Result slices (envelope/mass/loads) and pure metadata (schema_version) are out
# of scope -- this is a project.json *input* dictionary.
# --------------------------------------------------------------------------- #
INPUT_SLICES = [
    ("engines", "Engine-mount inputs (one per engine)"),
    ("engine_layout", "Engine layout constraint (enum)"),
    ("weight", "Weight database (WTESTIMA / WTONECG / WTENV)"),
    ("geometry", "Geometry single-source (WINGGEOM + fuselage + empennage)"),
    ("speeds", "Structural design speeds & load factors (STRSPEED)"),
    ("aero", "Spanwise airload inputs (AIRLOADS)"),
    ("aero_coeffs", "Airplane-less-tail aero coefficients (FLTLOADS input)"),
    ("flight_loads", "Flight envelope / balancing tail loads (FLTLOADS)"),
    ("wing_mass", "Wing-mass distribution & load cases (WINGINER)"),
    ("fuselage_mass", "Fuselage mass distribution (SELECT / Ch 15)"),
    ("tail_mass", "Empennage surface mass override — derived from the component-tagged weight.items by default (plan 09 T-3)"),
    ("select_input", "Critical-load selection inputs (SELECT)"),
    ("tail_loads", "Rational horizontal-tail inputs (via geometry.empennage)"),
    ("vtail_loads", "Rational vertical-tail inputs (via geometry.empennage)"),
    ("aileron_loads", "Aileron simplified loads (AILERON)"),
    ("flap_loads", "Flap simplified loads (FLAPLOAD)"),
    ("tab_loads", "Tab simplified loads (TABLOADS)"),
    ("one_engine_out", "One-engine-out v-tail loads (ONENGOUT)"),
    ("landing", "Landing loads (LANDLOAD / GEARLOAD)"),
    ("lra_mesh", "LRA beam mesh: node count per member (design note 56 D-56.4)"),
    ("include_far25", "Opt-in FAR 25 supplemental cases (flag)"),
]

# Owning page comes from `sloads.field_registry` (design note 32, OG-14): the
# registry declares an editing page **per field**, so this generator no longer
# keeps its own slice-level override table. The two disagreed by construction --
# the overrides were a guess at what workflow.py's `produces` could not
# attribute, while the registry states it and is drift-guarded.

# Field-name suffix -> units, used when the inline comment carries no units hint.
SUFFIX_UNITS = [
    ("_rad_s", "rad/s"),
    ("_sqft", "ft^2"),
    ("_deg", "deg"),
    ("_lb", "lb"),
    ("_in", "in"),
    ("_ft", "ft"),
    ("_kt", "KEAS"),
    ("_hp", "hp"),
    ("_s", "s"),
    ("_pct_mac", "% MAC"),
    ("_mac", "% MAC"),
]


def _resolve_hints(cls):
    """The resolved annotations, from the registry's one resolver (#409).

    ``sloads.models`` is a package: the names its annotations use live in each
    submodule, not in the package namespace this once passed as ``globalns``,
    so resolving `Project` raised and a silent fallback to the raw strings left
    every slice untyped and the dictionary with two tables. There is no
    fallback now -- an unresolvable annotation raises, here and in the GUI.
    """
    return fr._hints(cls)


def _inline_comments(cls):
    """Map field name -> trailing ``# comment`` text from the class source."""
    out = {}
    try:
        src = inspect.getsource(cls)
    except (OSError, TypeError):
        return out
    field_line = re.compile(r"^\s*([a-zA-Z_]\w*)\s*:\s*[^#]*?#\s*(.+?)\s*$")
    for line in src.splitlines():
        mo = field_line.match(line)
        if mo:
            name, comment = mo.group(1), mo.group(2)
            # First comment wins (the field's own line, not a continuation).
            out.setdefault(name, comment)
    return out


def _units_hint(name, comment):
    """A best-effort units string: the inline comment, else a suffix guess."""
    if comment:
        return comment
    for suffix, units in SUFFIX_UNITS:
        if name.endswith(suffix):
            return units
    return ""


def _type_str(s):
    """Shorten the repr of an annotation `_render_type` has no name for."""
    s = re.sub(r"\bsloads\.models\.", "", str(s))
    s = re.sub(r"\btyping\.", "", s)
    return s


def _render_type(ann):
    """Render a resolved annotation to a short string."""
    origin = typing.get_origin(ann)
    args = typing.get_args(ann)
    if origin is None:
        if hasattr(ann, "__name__"):
            return ann.__name__
        return _type_str(str(ann))
    if origin in (list, typing.List):
        return f"List[{_render_type(args[0])}]"
    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        inner = " | ".join(_render_type(a) for a in non_none)
        if type(None) in args:
            return f"Optional[{inner}]"
        return inner
    if origin in (tuple, typing.Tuple):
        return "Tuple[" + ", ".join(_render_type(a) for a in args) + "]"
    name = getattr(origin, "__name__", str(origin))
    return f"{name}[" + ", ".join(_render_type(a) for a in args) + "]"


def _nested_dataclasses(ann, acc):
    """Collect dataclass types referenced by an annotation into ``acc`` (a list)."""
    if dataclasses.is_dataclass(ann):
        if ann not in acc:
            acc.append(ann)
        return
    for a in typing.get_args(ann):
        _nested_dataclasses(a, acc)


def _default_str(f):
    if f.default is not dataclasses.MISSING:
        val = f.default
        if isinstance(val, enum.Enum):
            return f"{type(val).__name__}.{val.name}"
        return repr(val)
    if f.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
        try:
            sample = f.default_factory()
        except Exception:
            return "(factory)"
        if dataclasses.is_dataclass(sample):
            return f"{type(sample).__name__}() (factory)"
        return f"{sample!r} (factory)"
    return "**required**"


def _md_escape(text):
    return text.replace("|", "\\|").replace("\n", " ")


# --------------------------------------------------------------------------- #
# Slice -> owning page & consuming modules, from workflow.py + module sources.
# --------------------------------------------------------------------------- #
def _owning_page(slice_attr):
    """The page(s) that edit this slice, from the field registry (OG-14).

    A slice whose fields are edited on more than one page says so rather than
    picking one -- ``geometry`` is the case that used to be flattened, and
    hiding it is precisely the ownership question the registry exists to answer.
    """
    pages = {fr.BY_PATH[p].page for p in fr.paths_under(slice_attr)}
    if not pages:
        for step in w.STEPS:
            if step.produces == slice_attr:
                return step.title
        return "(unattributed)"
    # A page that is not a step -- the Beam Model page (note 67 D-67.3) -- is
    # named by its ``NON_STEP_PAGES`` row, the owner of its title.
    return " / ".join(sorted(
        w.BY_KEY[k].title if k in w.BY_KEY else w.non_step_page(k).title
        for k in pages))


def _consuming_modules(slice_attr):
    """Modules whose source reads ``.<slice_attr>`` (word-bounded).

    A module is one source file **or a package of them** (``balance/``, #191),
    and a read anywhere inside a package is a read by the module that package
    names -- the dictionary's unit is the module, not the file.
    """
    pat = re.compile(r"\.%s\b" % re.escape(slice_attr))
    hits = []
    for path in sorted(MODULES_DIR.iterdir()):
        if path.name == "__init__.py":
            continue
        if path.is_dir():
            sources = sorted(path.glob("*.py"))
        elif path.suffix == ".py":
            sources = [path]
        else:
            continue
        if any(pat.search(p.read_text(encoding="utf-8")) for p in sources):
            hits.append(path.stem)
    return hits


#: The two input slices that are `Project` *properties* over
#: ``geometry.empennage`` (step G6), not fields: typed here by hand.
PROXY_SLICES = {"tail_loads": m.TailLoadsInput, "vtail_loads": m.VTailLoadsInput}


def _slice_type(slice_attr):
    """The dataclass behind a Project input slice, or None for an enum/flag slice."""
    if slice_attr in PROXY_SLICES:
        return PROXY_SLICES[slice_attr]
    hints = _resolve_hints(m.Project)
    ann = hints.get(slice_attr)
    acc = []
    _nested_dataclasses(ann, acc)
    return acc[0] if acc else None


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def render_dataclass_table(cls, lines, seen):
    """Emit a field table for ``cls`` and queue any nested dataclasses."""
    hints = _resolve_hints(cls)
    comments = _inline_comments(cls)
    doc = inspect.getdoc(cls) or ""
    summary = doc.split("\n\n")[0].replace("\n", " ").strip() if doc else ""

    lines.append(f"### `{cls.__name__}`")
    lines.append("")
    if summary:
        lines.append(f"{_md_escape(summary)}")
        lines.append("")
    lines.append("| Field | Type | Units / notes | Default |")
    lines.append("| --- | --- | --- | --- |")

    queue = []
    for f in dataclasses.fields(cls):
        ann = hints[f.name]
        type_s = _render_type(ann)
        comment = comments.get(f.name, "")
        units = _units_hint(f.name, comment)
        lines.append(
            f"| `{f.name}` | `{_md_escape(type_s)}` | "
            f"{_md_escape(units)} | `{_md_escape(_default_str(f))}` |"
        )
        _nested_dataclasses(ann, queue)
    lines.append("")

    for nested in queue:
        if nested not in seen:
            seen.append(nested)


def build():
    lines = []
    lines.append("# `project.json` Input Data Dictionary")
    lines.append("")
    lines.append(
        "> **Generated file — do not edit by hand.** Produced by "
        "[`docs/generate_data_dict.py`](../generate_data_dict.py) from "
        "the `sloads/models/` dataclasses. Regenerate after any schema change: "
        "`.venv/bin/python docs/generate_data_dict.py`."
    )
    lines.append("")
    lines.append(f"Schema version: **{m.SCHEMA_VERSION}**.")
    lines.append("")
    lines.append(
        "This dictionary covers the **input** slices of `Project` "
        "(`sloads/models/project.py`) — the fields that make up a `project.json`. The "
        "result slices (`envelope`, `mass`, `loads`) are computed outputs and are "
        "out of scope."
    )
    lines.append("")
    lines.append("**Column meaning & caveats:**")
    lines.append("")
    lines.append(
        "- *Type* / *Default* are introspected from the dataclass "
        "(`typing.get_type_hints` / `dataclasses.fields`) — authoritative."
    )
    lines.append(
        "- *Units / notes* reproduces the field's inline `# comment` verbatim "
        "(falling back to a guess from the name suffix, e.g. `_lb`→lb). Comments "
        "are prose, not a structured units field — treat it as a hint."
    )
    lines.append(
        "- *Owning page* and *Consumed by* are **slice-level**, not per-field: "
        "`workflow.py` tracks data flow per slice, so every field inherits its "
        "root slice's page and consumer list. Owning page is the workflow step "
        "that `produces` the slice (with a small override table in the generator "
        "for slices workflow doesn't attribute); *Consumed by* lists the calc "
        "modules whose source reads `.<slice>`."
    )
    lines.append("")

    # ---- Top-level slice map ------------------------------------------------ #
    lines.append("## Project slice map")
    lines.append("")
    lines.append(
        "The top-level `Project` fields. `name`/`engineer`/`date` are free-text "
        "metadata; `schema_version` is set by `io.py`. The rest are the input "
        "slices detailed below."
    )
    lines.append("")
    lines.append("| Slice | Type | Owning page | Consumed by | Role |")
    lines.append("| --- | --- | --- | --- | --- |")
    project_hints = _resolve_hints(m.Project)
    for attr, role in INPUT_SLICES:
        cls = _slice_type(attr)
        if attr in PROXY_SLICES:
            type_s = cls.__name__          # a property, not a `Project` field
        else:
            ann = project_hints[attr]      # KeyError: INPUT_SLICES names a slice the schema lacks
            type_s = _render_type(ann)
            bare = [a for a in typing.get_args(ann) if a is not type(None)] or [ann]
            if isinstance(bare[0], type) and issubclass(bare[0], enum.Enum):
                type_s += " (enum)"
        consumers = _consuming_modules(attr)
        consumers_s = ", ".join(f"`{c}`" for c in consumers) if consumers else "—"
        lines.append(
            f"| `{attr}` | `{type_s}` | {_owning_page(attr)} | "
            f"{consumers_s} | {_md_escape(role)} |"
        )
    lines.append("")

    # ---- Per-dataclass field tables ---------------------------------------- #
    lines.append("## Field tables")
    lines.append("")
    lines.append(
        "One table per input dataclass, in slice order (nested types follow the "
        "slice that first references them). A field typed as another dataclass is "
        "detailed in that dataclass's own table."
    )
    lines.append("")

    rendered = []          # dataclasses already emitted
    seen = []              # discovery queue (nested types to emit)
    for attr, _role in INPUT_SLICES:
        cls = _slice_type(attr)
        if cls is None or cls in rendered:
            continue
        rendered.append(cls)
        render_dataclass_table(cls, lines, seen)
        # Emit newly-discovered nested dataclasses right after their referrer.
        i = 0
        while i < len(seen):
            nested = seen[i]
            i += 1
            if nested not in rendered:
                rendered.append(nested)
                render_dataclass_table(nested, lines, seen)

    # ---- Enums appendix ----------------------------------------------------- #
    lines.append("## Enumerations")
    lines.append("")
    enum_types = [
        obj
        for _name, obj in sorted(vars(m).items())
        if isinstance(obj, type) and issubclass(obj, enum.Enum) and obj is not enum.Enum
    ]
    for et in enum_types:
        # Only the enum's *own* docstring -- getdoc() would inherit str/Enum's.
        # Python <= 3.10's EnumMeta also stamps the placeholder "An enumeration."
        # into a docstring-less enum's own __dict__; drop it so the output is
        # identical on every interpreter in the CI matrix.
        doc = et.__dict__.get("__doc__") or ""
        if doc.strip() == "An enumeration.":
            doc = ""
        summary = doc.split("\n\n")[0].replace("\n", " ").strip()
        members = ", ".join(f"`{e.name}` = `{e.value!r}`" for e in et)
        lines.append(f"- **`{et.__name__}`** — {members}."
                     + (f" {_md_escape(summary)}" if summary else ""))
    lines.append("")

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# The oracle GUI user guide (docs/60_guide/) — design note 34, issue #96.
#
# UG-3: every chapter's field table is *generated* from `sloads.field_registry`
# (path, quantity, units, type, origin), written to `_generated/<step_key>.md`
# and linked from the chapter — prose never restates a units string, a default,
# or a field count. UG-7: the chapter set and its order are
# `sloads.workflow.oracle_steps()`, so adding a `.BAS`-backed step scaffolds a
# chapter here with no hand edit (note 32's G2 property, inherited).
# Gates G-UG-1…G-UG-6: `tests/test_guide.py`.
# --------------------------------------------------------------------------- #
GUIDE_DIR = REPO_ROOT / "docs" / "60_guide"
GEN_DIR = GUIDE_DIR / "_generated"

GENERATED_BANNER = (
    "<!-- Generated by docs/generate_data_dict.py — DO NOT EDIT.\n"
    "     Regenerate: .venv/bin/python docs/generate_data_dict.py -->"
)

#: The eight chapter section headings, in order (note 34 §3). Guard G-UG-6
#: asserts every chapter carries exactly these as its `##` sequence, so chapter
#: fourteen stays as complete as chapter one.
CHAPTER_HEADINGS = (
    "What this page is for",
    "Before this page",
    "The inputs",
    "Screenshots",
    "Worked example — single (`ga6_normal`)",
    "Worked example — twin (`baron_58`)",
    "Results on this page",
    "Common mistakes",
)


def guide_chapters():
    """``[("01", step), …]`` — chapter number and workflow step, UG-7 order."""
    return [(f"{i:02d}", step) for i, step in enumerate(w.oracle_steps(), start=1)]


def _page_entries(step_key):
    """This page's registry rows, in registry declaration order."""
    return [e for e in fr.REGISTRY if e.page == step_key]


def _entry_units(path):
    """The units hint for a registry path, from the owning dataclass source."""
    located = fr._locate(path)
    if located is None:
        return ""
    cls, field = located
    comment = _inline_comments(cls).get(field.name, "")
    return _units_hint(field.name, comment)


def _entry_type(path):
    ann = fr.field_type(path)
    if ann is None:
        raise KeyError(f"registry path {path!r} does not locate a field")
    return _render_type(ann)


def _entry_default(path):
    located = fr._locate(path)
    if located is None:
        return ""
    _cls, field = located
    return _default_str(field)


def _origin_cell(e):
    label = e.origin.value
    if e.supplied:
        label += " (supplied)"
    return label


def _provenance_cell(e):
    parts = [e.basis]
    if e.quantity:
        parts.append(f"quantity: *{e.quantity}*")
    if e.derived_from:
        kind = "override" if e.governs else "display-only copy"
        parts.append(f"{kind} of `{e.derived_from}`")
    return _md_escape("; ".join(p for p in parts if p))


def _guide_field_table(step):
    """The generated field-table file for one oracle page."""
    lines = [GENERATED_BANNER, ""]
    lines.append(f"### Input fields — {step.title} (`{step.key}`)")
    lines.append("")
    entries = _page_entries(step.key)
    if not entries:
        lines.append(
            "This page enters no input fields of its own — every quantity it "
            "uses is entered on an earlier page (see the chapter's *Before "
            "this page* section)."
        )
        lines.append("")
        return "\n".join(lines) + "\n"
    lines.append(
        "Generated from `sloads/field_registry.py` — the registry of record "
        "for where each input field is edited and where it came from. "
        "*Origin* `original` means a named `.BAS` program asked for the field; "
        "`sloads` marks capability this replication added (`supplied` = the "
        "oracle input set needs it anyway). Types, units and defaults are "
        "introspected from `sloads/models.py`."
    )
    lines.append("")
    lines.append("| Field | Type | Units / notes | Default | Origin | Provenance |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for e in entries:
        lines.append(
            f"| `{e.path}` | `{_md_escape(_entry_type(e.path))}` | "
            f"{_md_escape(_entry_units(e.path))} | "
            f"`{_md_escape(_entry_default(e.path))}` | {_origin_cell(e)} | "
            f"{_provenance_cell(e)} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def _guide_chapter_list():
    """The generated chapter index (UG-7 — no hand-maintained chapter list)."""
    lines = [GENERATED_BANNER, ""]
    lines.append("### The chapters, in workflow order")
    lines.append("")
    lines.append("| # | Chapter | Page key | Original program(s) |")
    lines.append("| --- | --- | --- | --- |")
    for nn, step in guide_chapters():
        bas = f"`{step.bas}`" if step.bas else "— (modern page)"
        lines.append(
            f"| {int(nn)} | [{step.title}](../{nn}_{step.key}.md) | "
            f"`{step.key}` | {bas} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Worked-example figures (#428). Every number a worked example quotes is read
# here, from a run of the bundled example, and written to
# `_generated/worked_<example>.md`; the appendices link that table and quote no
# figure of their own. G-UG-2 keeps the table current, and
# `tests/test_guide.py` holds each `book` figure to the manual's printed value.
# --------------------------------------------------------------------------- #
class WorkedFigure(typing.NamedTuple):
    """One quoted figure: where it is read, and (for the oracle airplane) the
    value the manual prints.

    ``title`` and ``key`` are the exact :class:`ConditionResult` title and
    :class:`LoadValue` key, so a renamed condition fails the generator rather
    than blanking a cell. ``tol`` is the absolute band the guard allows against
    ``book``; 0 means the printed resolution plus 0.1 % (Decision 3).
    """

    page: str
    quantity: str
    module: str
    title: str
    key: str
    decimals: int
    book: typing.Optional[float] = None
    cite: str = ""
    tol: float = 0.0


#: The single (`ga6_normal`): Appendix A's airplane, so most rows carry the
#: printed figure. Each `cite` is the page the module's own oracle test cites.
_NZ_TOL = 0.01  # converged to ±0.005, printed to 2 dp (tests/test_flight_envelope.py _nz_tol)
GA6_FIGURES = (
    WorkedFigure("weight_mass", "Maximum take-off weight (WTESTIMA)", "weight_estimate",
                 "Estimated weight summary", "max_take_off_weight", 0, 3468.0, "Appendix A p134"),
    WorkedFigure("weight_mass", "Empty weight (WTESTIMA)", "weight_estimate",
                 "Estimated weight summary", "empty_weight", 0, 2150.0, "Appendix A p134"),
    WorkedFigure("structural_speeds", "Limit positive load factor n₊", "structural_speeds",
                 "Limit maneuver load factors", "limit_positive_load_factor", 2, 3.8, "Appendix A p179"),
    WorkedFigure("structural_speeds", "Limit negative load factor n₋", "structural_speeds",
                 "Limit maneuver load factors", "limit_negative_load_factor", 2, -1.52, "Appendix A p179"),
    WorkedFigure("structural_speeds", "Maneuver speed VA", "structural_speeds",
                 "Structural design speeds", "maneuver_speed_va", 1, 121.3, "Appendix A p179"),
    WorkedFigure("structural_speeds", "Cruise speed VC (chosen)", "structural_speeds",
                 "Structural design speeds", "cruise_speed_vc", 1, 170.0, "Appendix A p179"),
    WorkedFigure("structural_speeds", "Dive speed VD (1.25 × VC)", "structural_speeds",
                 "Structural design speeds", "dive_speed_vd", 1, 212.5, "Appendix A p179"),
    WorkedFigure("flight_envelope", "MAN A corner, CG1: load factor", "flight_envelope",
                 "CRUISE CG1 @ 0 ft, case 3: MAN A", "load_factor_nz", 2, 3.80,
                 "Appendix A p180", _NZ_TOL),
    WorkedFigure("flight_envelope", "MAN A corner, CG1: angle of attack", "flight_envelope",
                 "CRUISE CG1 @ 0 ft, case 3: MAN A", "angle_of_attack", 2, 12.75,
                 "Appendix A p180", 0.05),
    WorkedFigure("flight_envelope", "GUST +C corner, CG1: load factor", "flight_envelope",
                 "CRUISE CG1 @ 0 ft, case 10: GUST +C", "load_factor_nz", 2, 3.96,
                 "Appendix A p180", _NZ_TOL),
    WorkedFigure("flight_envelope", "SELECT's critical PHAA case: load factor", "select",
                 "Critical wing load PHAA (case 22)", "load_factor_nz", 2),
    WorkedFigure("engine_mount", "Take-off mean engine torque", "engine",
                 "Limit takeoff torque (factor x mean) with 75% limit maneuver vertical load factor",
                 "mean_takeoff_torque", 2, 554.39, "Appendix A, ENGLOADS"),
    WorkedFigure("landing_loads", "Landing sink rate V", "landing",
                 "Landing load factor (LGFACTOR)", "sink_rate", 4, 9.0048, "Appendix A p236"),
    WorkedFigure("landing_loads", "Gear factor NLG (the book's printed energy ratio N; #401)",
                 "landing", "Landing load factor (LGFACTOR)", "landing_gear_factor_nlg", 4,
                 3.0951, "Appendix A p236"),
    WorkedFigure("landing_loads", "Governing airplane load factor N (entered)", "landing",
                 "Landing load factor (LGFACTOR)", "governing_airplane_load_factor_n", 3),
)

#: The concept twin (`atr42_100`): no printed oracle exists, so no `book`
#: column -- its check is the closure block below the table.
ATR42_FIGURES = (
    WorkedFigure("weight_mass", "Aft-gross weight (MTOW)", "weight_onecg",
                 "Mass properties -- aft gross", "weight", 0),
    WorkedFigure("weight_mass", "Aft-gross CG station", "weight_onecg",
                 "Mass properties -- aft gross", "xbar_fus_station", 1),
    WorkedFigure("weight_mass", "Aft-gross pitch inertia IYY", "weight_onecg",
                 "Mass properties -- aft gross", "iyy", 0),
    WorkedFigure("structural_speeds", "Limit positive load factor n₊ (entered, category C)",
                 "structural_speeds", "Limit maneuver load factors",
                 "limit_positive_load_factor", 2),
    WorkedFigure("structural_speeds", "Limit negative load factor n₋", "structural_speeds",
                 "Limit maneuver load factors", "limit_negative_load_factor", 2),
    WorkedFigure("structural_speeds", "Maneuver speed VA", "structural_speeds",
                 "Structural design speeds", "maneuver_speed_va", 1),
    WorkedFigure("structural_speeds", "Cruise speed VC (chosen)", "structural_speeds",
                 "Structural design speeds", "cruise_speed_vc", 1),
    WorkedFigure("structural_speeds", "Dive speed VD (chosen)", "structural_speeds",
                 "Structural design speeds", "dive_speed_vd", 1),
    WorkedFigure("flight_envelope", "SELECT's critical PMAA case: load factor", "select",
                 "Critical wing load PMAA (case 270)", "load_factor_nz", 3),
    WorkedFigure("one_engine_out", "Engine failure at VD: side force on the fin", "one_engine_out",
                 "One engine out — VD (limit) (engine 1)", "fy_side", 0),
    WorkedFigure("one_engine_out", "Engine failure at VC (prescribed ultimate): side force",
                 "one_engine_out", "One engine out — VC (ultimate) (engine 1)", "fy_side", 0),
)

WORKED_EXAMPLES = {"ga6_normal": GA6_FIGURES, "atr42_100": ATR42_FIGURES}


def _load_example(name):
    from sloads.io import load_project
    return load_project(REPO_ROOT / "examples" / f"{name}.project.json")


def worked_figures(name):
    """``[(figure, condition, value)]`` for one bundled example, in table order.

    Raises ``KeyError`` naming the figure when its condition or key is gone, so
    a renamed result fails here, not as an empty cell.
    """
    from sloads.registry import get
    project = _load_example(name)
    results = {}
    out = []
    for fig in WORKED_EXAMPLES[name]:
        if fig.module not in results:
            results[fig.module] = get(fig.module)(project).conditions
        cond = next((c for c in results[fig.module] if c.title == fig.title), None)
        if cond is None:
            raise KeyError(f"{name}: no {fig.module} condition titled {fig.title!r}")
        value = next((v for v in cond.values if v.key == fig.key), None)
        if value is None:
            raise KeyError(f"{name}: {fig.title!r} has no value keyed {fig.key!r}")
        out.append((fig, cond, value))
    return out


def figure_tolerance(fig):
    """The guard's band against ``fig.book``: ``tol``, else print resolution + 0.1 %."""
    if fig.tol:
        return fig.tol
    return 0.5 * 10 ** -fig.decimals + 1e-3 * abs(fig.book or 0.0)


def _sf_cell(sf):
    if sf is None:
        return "N/A"
    return "1.0 (already ultimate)" if sf == 1.0 else f"{sf:g}"


def _page_link(step_key):
    for nn, step in guide_chapters():
        if step.key == step_key:
            return f"[{step.title}](../{nn}_{step.key}.md)"
    raise KeyError(step_key)


def _closure_lines(name):
    """The balanced-case and deck closure statement for a concept example."""
    from sloads.export.balanced_deck import balanced_deck
    from sloads.export.equilibrium import closes, deck_resultants
    from sloads.modules.balance import build_balanced_cases

    project = _load_example(name)
    built = build_balanced_cases(project)
    cases = list(built[0] if isinstance(built, tuple) else built)
    # A ground case is reacted at the gear, not by a distributed inertia set, so
    # the -nz*W identity is a flight-case statement (the G-OR-72 rule).
    flight = [c for c in cases if not any(lv.source.startswith("gear") for lv in c.loads)]
    inertia = [(c, sum(lv.fz for lv in c.loads if "inertia" in lv.source)) for c in flight]
    ratios = [-i / (c.nz * c.weight_lb) for c, i in inertia if i]
    relief = max(flight, key=lambda c: abs(c.delta_n))
    res = deck_resultants(balanced_deck(project, cases=cases))
    closed = sum(
        all(closes(f, 0.0, scale=r.force_scale) for f in (r.fx, r.fy, r.fz))
        and all(closes(mm, 0.0, scale=r.moment_scale) for mm in (r.mx, r.my, r.mz))
        for r in res.values()
    )
    return [
        "### Closure (the check that stands in for an oracle)",
        "",
        "| Check | Result |",
        "| --- | --- |",
        f"| Balanced cases assembled | {len(cases)} ({len(flight)} flight, "
        f"{len(cases) - len(flight)} ground) |",
        f"| Flight cases: inertia resultant ÷ (−n<sub>z</sub>·W) | "
        f"{min(ratios):.4f} to {max(ratios):.4f} (LIMIT: no factor applied) |",
        f"| Largest closure relief Δn on a flight case | {relief.delta_n:+.3f} "
        f"({relief.label}, {relief.cg}) |",
        f"| LRA deck subcases whose six resultants close to zero | "
        f"{closed} of {len(res)} |",
        "",
        "Δn is the rigid-body load-factor increment the closure applied: how much of "
        "the balance was assumed rather than computed. The deck check re-reads the "
        "written `FORCE`/`MOMENT` cards (`sloads.export.equilibrium`).",
        "",
    ]


def _worked_table(name):
    """``_generated/worked_<name>.md``: the figures, read from a run of the example."""
    rows = worked_figures(name)
    has_book = any(fig.book is not None for fig, _c, _v in rows)
    lines = [GENERATED_BANNER, ""]
    lines.append(f"### Figures from a run of `examples/{name}.project.json`")
    lines.append("")
    lines.append(
        "Every value is LIMIT as delivered; the SF column is the factor the case "
        "states and nothing applies."
    )
    lines.append("")
    head = "| Page | Quantity | sloads | Units | SF |"
    rule = "| --- | --- | --- | --- | --- |"
    if has_book:
        head += " Book | Printed |"
        rule += " --- | --- |"
    lines += [head, rule]
    for fig, cond, value in rows:
        cell = f"{value.value:,.{fig.decimals}f}"
        row = (f"| {_page_link(fig.page)} | {fig.quantity} | {cell} | "
               f"{value.units or '—'} | {_sf_cell(cond.safety_factor)} |")
        if has_book:
            book = "—" if fig.book is None else f"{fig.book:,.{fig.decimals}f}"
            row += f" {book} | {fig.cite or '—'} |"
        lines.append(row)
    lines.append("")
    if not has_book:
        lines += _closure_lines(name)
    return "\n".join(lines) + "\n"


def build_guide_tables():
    """Every file under ``_generated/``: ``{filename: content}``."""
    out = {"chapters.md": _guide_chapter_list()}
    for _nn, step in guide_chapters():
        out[f"{step.key}.md"] = _guide_field_table(step)
    for name in WORKED_EXAMPLES:
        out[f"worked_{name}.md"] = _worked_table(name)
    return out


def _chapter_stub(nn, step):
    """A template-conformant placeholder chapter (filled by #96's later stages)."""
    bas = f"`{step.bas}`" if step.bas else "none — a modern page the workflow needs"
    body = [
        f"# {int(nn)}. {step.title}",
        "",
        "> **Placeholder chapter** — scaffolded by `docs/generate_data_dict.py`; "
        "the prose lands with the chapter stages of issue #96 (design note 34).",
        "",
        f"*Original program(s):* {bas}.",
        "",
    ]
    for heading in CHAPTER_HEADINGS:
        body.append(f"## {heading}")
        body.append("")
        if heading == "The inputs":
            body.append(
                "The field table for this page is generated from "
                f"`sloads/field_registry.py`: [`_generated/{step.key}.md`]"
                f"(_generated/{step.key}.md)."
            )
            body.append("")
        body.append("*Not yet written.*")
        body.append("")
    return "\n".join(body)


def scaffold_chapters():
    """Create any missing chapter file as a stub; never touch an existing one."""
    created = []
    for nn, step in guide_chapters():
        path = GUIDE_DIR / f"{nn}_{step.key}.md"
        if not path.exists():
            path.write_text(_chapter_stub(nn, step), encoding="utf-8")
            created.append(path)
    return created


def write_guide():
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    tables = build_guide_tables()
    for name, content in tables.items():
        (GEN_DIR / name).write_text(content, encoding="utf-8")
    for stale in GEN_DIR.glob("*.md"):
        if stale.name not in tables:
            stale.unlink()
            print(f"Removed stale {stale.relative_to(REPO_ROOT)}")
    print(f"Wrote {len(tables)} files under {GEN_DIR.relative_to(REPO_ROOT)}/")
    for path in scaffold_chapters():
        print(f"Scaffolded {path.relative_to(REPO_ROOT)}")


def main():
    OUT_PATH.write_text(build(), encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    write_guide()


if __name__ == "__main__":
    main()
