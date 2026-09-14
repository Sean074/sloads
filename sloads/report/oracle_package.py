"""The **issue package**: every file of one report issue, planned but not written.

Design note 44, OR-22 … OR-35. A report issue is a *package*, not a file -- the
document, the data behind every table and plot, the definition it was built from,
and a manifest -- in one directory that can be archived, signed, and reopened
years later.

```
LR-0142_RevB/
  report.tex          the document
  report.json         the spec the page edits (never written by the build)
  build.json          the as-built stamp: fingerprint, timestamp, generator
  project.json        the airplane definition it was built from
  MANIFEST.txt        a SUMMARY_REPORT.md 4.7 manifest of everything above
  data/<step_key>.csv one file per table or plot the document draws
  report.pdf          present only after a local compile
```

**Pure, like the rest of** :mod:`sloads.report`: this module returns the package's
*contents*; :mod:`sloads.export.report_package` writes them. The split is what
lets the determinism gate (G-OR-16) compare two builds without a filesystem.

``data/`` is filled by :mod:`sloads.report.package_data` (#245), which is where
the question "what does a package carry?" is answered; this module places what
that one decides and names it in the manifest. Since #245 it is the **only**
tabular channel either front end offers: the per-module download buttons and
the sidebar's results zip retired into it.

**Nothing here reads the clock.** The build timestamp arrives as an argument. A
builder that stamped ``now()`` would make byte-identical rebuilds impossible to
assert, and the gate would be quietly meaningless rather than loudly failing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import List, Optional, Sequence

from ..models import Project
from ..models.report import REPORT_SCHEMA_VERSION, ReportSpec
from ..units import UnitSystem
from . import package_data as _package_data
from .oracle_content import OracleDocument, build_oracle_document, section_ref
from .oracle_latex import render_oracle_document

PACKAGE_TEX = "report.tex"
PACKAGE_SPEC = "report.json"
PACKAGE_BUILD = "build.json"
PACKAGE_PROJECT = "project.json"
PACKAGE_MANIFEST = "MANIFEST.txt"
#: Re-exported from its owner (#245) so a caller assembling or reading a package
#: has one import for the package's shape. The directory's *contents* are
#: :mod:`sloads.report.package_data`'s to decide, and this module only places
#: them.
DATA_DIR = _package_data.DATA_DIR

#: What the manifest prints in place of its own hash.
#:
#: The manifest lists **itself**: a manifest that names every file except the one
#: the reader is holding was exactly review CR-C-1's defect, and
#: ``SUMMARY_REPORT.md`` §4.7 requires the list be exhaustive. Its own hash
#: cannot be inside it, so the row says so rather than being silently omitted.
SELF_HASH = "(this file)"


@dataclass(frozen=True)
class PackageMember:
    """One file of the package, plus the manifest facts §4.7 requires of it.

    ``units``, ``conventions`` and ``summarised_in`` are carried on the member
    rather than assembled in the manifest writer, so a file cannot be added to
    the package without stating them -- §4.7's "SHALL NOT be listed without its
    torsion axis and load basis" made structural instead of remembered.
    """

    name: str
    content: str
    contents: str
    units: str = "--"
    conventions: str = "--"
    summarised_in: str = "--"

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


def _units_sentence(system: UnitSystem) -> str:
    """§4.7's required opening: the package's unit system, stated once.

    A per-file units column that disagrees with this statement is a conformance
    failure, not a footnote -- so the statement comes first and the columns are
    read against it.
    """
    name = "SI" if system is UnitSystem.SI else "Imperial"
    return (
        f"Every file in this package is written in {name} units. All delivered "
        "loads are LIMIT: each load case states the safety factor prescribed "
        "for it and the basis of that factor, and sloads applies it nowhere. "
        "The -ULT marker appears only on a load the regulation prescribes "
        "already ultimate. Quantities that are not loads take no factor. "
        "Airspeed is KEAS and altitude is ft in both unit systems (aviation "
        "standard, never converted)."
    )


def manifest_text(members: Sequence[PackageMember], *, system: UnitSystem,
                  report_number: str, revision: str, built: str) -> str:
    """The package's ``MANIFEST.txt``, in `SUMMARY_REPORT.md` §4.7's shape.

    One block per file rather than a five-column table: §4.7's columns carry
    prose (*what it contains*, *its conventions*), and a fixed-width table of
    prose cells is unreadable at eighty columns -- which is the width a manifest
    is actually read at. The five facts are all present and labelled, which is
    what the rule requires; the layout is not what it legislates.
    """
    lines = [
        "sloads --- oracle technical report, issue package manifest",
        "=" * 72,
        f"Report:   {report_number or 'not assigned'}"
        + (f"  Rev {revision}" if revision else ""),
        f"Built:    {built}",
        "",
        "Units",
        "-----",
    ]
    lines += ["  " + line for line in _wrap(_units_sentence(system), 70)]
    lines += ["", "Files", "-----",
              "  Every file this package contains is listed below, and this list",
              "  names nothing the package does not contain.", ""]
    for member in members:
        digest = SELF_HASH if member.name == PACKAGE_MANIFEST else member.sha256
        lines.append(f"  {member.name}")
        lines.append(f"    sha256        {digest}")
        for label, value in (("contents", member.contents),
                             ("units", member.units),
                             ("conventions", member.conventions),
                             ("summarised in", member.summarised_in)):
            wrapped = _wrap(value, 56)
            lines.append(f"    {label:<13} {wrapped[0] if wrapped else '--'}")
            lines += [" " * 18 + cont for cont in wrapped[1:]]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _wrap(text: str, width: int) -> List[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def build_stamp(*, fingerprint: str, fingerprint_version: int, built: str,
                tool_version: str) -> str:
    """``build.json`` -- what this build was, as opposed to what the user typed.

    Kept out of ``report.json`` (OR-30) so the builder never writes the file the
    user edits. That is not tidiness: it is what lets G-OR-16 compare two builds
    byte for byte without maintaining a list of stamped fields to ignore, for
    every field the spec will ever grow.
    """
    return json.dumps({
        "generator": "sloads oracle technical report",
        "tool_version": tool_version,
        "built": built,
        "fingerprint": fingerprint,
        "fingerprint_version": fingerprint_version,
        "report_schema_version": REPORT_SCHEMA_VERSION,
    }, indent=2, sort_keys=True) + "\n"


def package_members(
    project: Project,
    spec: ReportSpec,
    *,
    built: str,
    tool_version: str = "",
    document: Optional[OracleDocument] = None,
    fingerprint: str = "",
    fingerprint_version: int = 0,
) -> List[PackageMember]:
    """Every file of the issue package, in write order.

    ``built`` is the caller's timestamp -- see the module docstring. ``document``
    may be passed by a caller that already built it (the page renders a preflight
    from the same object) so the document is never built twice and the preflight
    can never describe a different document than the one written.
    """
    from .. import io as io_
    from .fingerprint import anchors as anchor_rows

    # The anchors are computed here rather than asked of the caller: OR-21 makes
    # them the *human* half of provenance, and a caller that forgot them would
    # ship a fingerprint with nothing a reader can check it against -- which is
    # the half that actually gets used.
    doc = document if document is not None else build_oracle_document(
        project, spec, anchors=anchor_rows(project, tool_version=tool_version),
        fingerprint=fingerprint, fingerprint_version=fingerprint_version)

    intro = section_ref(doc.plan, "") if doc.plan else "section 1"

    # The data behind the document, decided before anything is rendered (#245).
    #
    # From ``doc`` and not from ``project``: the document was built from the
    # oracle projection and from one run of the modules, and both travel on it,
    # so a data file cannot come out of a different analysis from the page that
    # summarises it.
    data = _package_data.data_files(doc)
    # The document then lists what travels with it -- the reader's half of
    # G-OR-17, the manifest being the archivist's. Re-walking the document for
    # data files after this would find nothing new: a front-matter table is not
    # an appendix table and draws no figure.
    if doc.sections:
        doc = replace(doc, sections=[replace(
            doc.sections[0],
            subsections=list(doc.sections[0].subsections)
            + [_package_data.data_reference_section(data)])]
            + list(doc.sections[1:]))

    members = [
        PackageMember(
            name=PACKAGE_TEX,
            content=render_oracle_document(doc),
            contents="The report itself, as LaTeX source. Compile it from "
                     "inside this directory so its relative references resolve.",
            units="as stated in this manifest's Units section",
            conventions="axes, signs and safety factors per "
                        "docs/10_standard/CONVENTIONS.md",
            summarised_in="the whole document",
        ),
        PackageMember(
            name=PACKAGE_SPEC,
            content=io_.report_spec_to_json(spec),
            contents="The report specification this issue was built from: "
                     "identity, abstract, signatures, marking and section "
                     "selection. Edited by the report page; never written by a "
                     "build.",
            summarised_in="the title page",
        ),
        PackageMember(
            name=PACKAGE_BUILD,
            content=build_stamp(fingerprint=doc.fingerprint,
                                fingerprint_version=doc.fingerprint_version,
                                built=built, tool_version=tool_version),
            contents="The as-built stamp: what produced this package, when, and "
                     "the fingerprint of the analysis inputs it read.",
            summarised_in=f"{intro}, analysis basis",
        ),
        PackageMember(
            name=PACKAGE_PROJECT,
            content=io_.project_to_json(project),
            contents="The airplane definition this issue was built from, so the "
                     "package can be rebuilt without hunting for the project "
                     "file and the fingerprint has its subject present.",
            units="canonical Imperial (a stored project is never converted)",
            conventions="per docs/10_standard/CONVENTIONS.md",
            summarised_in=intro,
        ),
    ]
    # Placed after the four control files and before the manifest, which is the
    # order a package is read in: what it *is*, then what it carries, then the
    # list of both.
    members += [
        PackageMember(
            name=member.name, content=member.content, contents=member.contents,
            units=member.units,
            conventions="axes, signs and safety factors per the methods "
                        "statement in this file's own header",
            summarised_in=member.summarised_in)
        for member in data
    ]
    manifest = PackageMember(
        name=PACKAGE_MANIFEST,
        content="",
        contents="This file: every artifact the package carries, with its "
                 "hash, units, conventions and the section that summarises it.",
        summarised_in="itself",
    )
    listed = members + [manifest]
    rendered = manifest_text(listed, system=doc.system,
                             report_number=spec.report_number,
                             revision=spec.revision, built=built)
    return members + [PackageMember(
        name=manifest.name, content=rendered, contents=manifest.contents,
        units=manifest.units, conventions=manifest.conventions,
        summarised_in=manifest.summarised_in)]


def manifest_names(members: Sequence[PackageMember]) -> List[str]:
    """The file names the manifest claims, for the both-directions check."""
    return [m.name for m in members]


__all__ = [
    "DATA_DIR",
    "PACKAGE_BUILD",
    "PACKAGE_MANIFEST",
    "PACKAGE_PROJECT",
    "PACKAGE_SPEC",
    "PACKAGE_TEX",
    "SELF_HASH",
    "PackageMember",
    "build_stamp",
    "manifest_names",
    "manifest_text",
    "package_members",
]
