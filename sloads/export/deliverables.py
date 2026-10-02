"""What a delivered file is called -- one name per artifact, for every route.

The CLI wrote its file names inline (``f"{prefix}.lra_model.bdf"``) and the
Beam Model page writes the same artifacts (note 67 D-67.8). Two routes spelling
one name is the #239 class: the day one of them changes, a deck written from the
GUI and the deck written headless stop being recognisably the same file. So the
names live here, and both routes ask.

The spellings are the shipped ones, unchanged -- a dot before the LRA and gear
names, an underscore before the mass names, because that is what users' scripts
already glob for. They are a contract, not a style.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from ..units import UnitSystem

if TYPE_CHECKING:
    from ..models import Project

#: Artifact key -> the suffix appended to the caller's prefix.
SUFFIXES: Dict[str, str] = {
    # The LRA beam model, the primary deliverable (note 24 R-1).
    "lra": ".lra_model.bdf",
    # The balanced cases' loads on a user-imported LRA model (note 56 D-56.5).
    "lra_import": ".lra_loads.bdf",
    # The landing gear interface load definition (decision G-12).
    "gear": ".gear_loads.csv",
    # The CONM2/MASSSET mass model and its GPWG check deck (plan 12 C-4).
    "mass": "_mass.bdf",
    "mass_check": "_mass_check.bdf",
    # The operating empty weight's CONM2 set: no payload, no fuel (note 67
    # D-67.9). New with the Beam Model page, so it takes the dotted form of the
    # deck it is written beside rather than the older mass names' underscore.
    "oew": ".oew_mass.bdf",
}


def deliverable_path(prefix: str, artifact: str) -> str:
    """The file ``artifact`` is written to under ``prefix``.

    ``prefix`` is a path stem -- a directory and a base name, as the CLI's
    ``--export-sbeam out`` takes it. Raises ``KeyError`` for an artifact this
    module does not name, so a route cannot invent a file name of its own.
    """
    return prefix + SUFFIXES[artifact]


#: What the Beam Model page writes, in order: the deck and, beside it, the
#: operating empty weight's mass set (note 67 D-67.9).
BEAM_PAGE_ARTIFACTS = ("lra", "oew")

#: The base name the page writes under when the project has never been saved,
#: so has no file name to borrow.
UNSAVED_STEM = "sloads"


def render(project: "Project", artifact: str, *,
           system: UnitSystem = UnitSystem.IMPERIAL,
           header_comment: str = "") -> str:
    """One artifact's text, stamped -- the writer both routes call.

    Rendered and returned rather than written, so a route that writes several
    files can render them all first: a refusal (``LraRefusal``, a
    ``ValueError``) then leaves no partial set on disk, which is the contract
    the retired ``lra_model.write_lra_model_bdf`` kept for one file (note 67
    gate 4).
    """
    if artifact == "lra":
        from .lra_model import lra_model_bdf

        return lra_model_bdf(project, header_comment=header_comment, system=system)
    if artifact == "oew":
        from .mass_cards import oew_fragment

        return oew_fragment(project, header_comment=header_comment, system=system)
    raise KeyError(f"no single-file renderer for artifact {artifact!r}")


def render_set(project: "Project", prefix: str, artifacts: Sequence[str], *,
               system: UnitSystem = UnitSystem.IMPERIAL,
               header_comment: str = "") -> Dict[str, str]:
    """``{path: text}`` for every artifact, all rendered before any is written."""
    return {deliverable_path(prefix, artifact):
            render(project, artifact, system=system, header_comment=header_comment)
            for artifact in artifacts}


def write_set(rendered: Dict[str, str]) -> List[str]:
    """Write a rendered set; return the paths written, in order."""
    for path, text in rendered.items():
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return list(rendered)


def page_prefix(folder: str, project_path: Optional[str]) -> str:
    """The prefix the Beam Model page writes under: the chosen folder, and the
    saved project file's own stem (``atr42_100`` for ``atr42_100.project.json``)
    -- or :data:`UNSAVED_STEM` for a project that has no file yet. The page may
    not build a path itself (gate G1), so it asks here."""
    stem = UNSAVED_STEM
    if project_path:
        from ..io import PROJECT_SUFFIX

        base = os.path.basename(project_path)
        stem = (base[:-len(PROJECT_SUFFIX)] if base.endswith(PROJECT_SUFFIX)
                else os.path.splitext(base)[0]) or UNSAVED_STEM
    return os.path.join(folder, stem)


def folder_anchors(project_path: Optional[str]) -> List[Tuple[str, str]]:
    """``(label, folder)`` starting points for choosing where a deck goes,
    nearest first: beside the project file, the app's projects folder, home.

    Not the Report page's anchors -- those start in the reports folder an issue
    package belongs in, which is not where a solver deck is looked for."""
    from ..io import default_projects_dir

    anchors = []
    if project_path:
        anchors.append(("Beside the project (default)",
                        os.path.dirname(os.path.abspath(project_path))))
    anchors += [("The app's projects folder", default_projects_dir()),
                ("Home folder", os.path.expanduser("~"))]
    seen, unique = set(), []
    for label, path in anchors:
        resolved = os.path.abspath(path)
        if resolved not in seen:
            seen.add(resolved)
            unique.append((label, resolved))
    return unique


def render_page_set(project: "Project", prefix: str, *,
                    system: UnitSystem = UnitSystem.IMPERIAL,
                    header_comment: str = "",
                    ) -> Tuple[Dict[str, str], List[str]]:
    """The Beam Model page's set: ``({path: text}, [absence sentences])``.

    The deck is the deliverable, so its refusal (``LraRefusal``) propagates and
    the page writes nothing. The OEW mass set is its companion: a project with
    no operating rows still gets its deck, and the set's absence is returned as
    a sentence rather than raised -- the CLI's ``mass`` target treats an
    unbuildable check deck the same way.
    """
    rendered = render_set(project, prefix, ("lra",), system=system,
                          header_comment=header_comment)
    absences: List[str] = []
    try:
        rendered.update(render_set(project, prefix, ("oew",), system=system,
                                   header_comment=header_comment))
    except ValueError as exc:
        absences.append(f"No operating empty weight mass set: {exc}.")
    return rendered, absences


def existing(paths: Sequence[str]) -> List[str]:
    """The paths among ``paths`` that a write would replace."""
    return [path for path in paths if os.path.exists(path)]


__all__ = [
    "BEAM_PAGE_ARTIFACTS",
    "SUFFIXES",
    "UNSAVED_STEM",
    "deliverable_path",
    "existing",
    "folder_anchors",
    "page_prefix",
    "render",
    "render_page_set",
    "render_set",
    "write_set",
]
