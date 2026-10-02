"""The oracle GUI's **Beam Model** page -- the deliverable, drawn and written.

Design note 67. The LRA free-free beam model is the primary deliverable, and
until this page the GUI had no route to it: the deck was written by the CLI
alone and drawn by a script. It is not an analysis step (D-67.1) -- it runs no
``.BAS`` program and fills no slice a computation reads -- so it is declared in
:data:`sloads.workflow.NON_STEP_PAGES` and never handed to ``register_pages``.

Four blocks, top to bottom (D-67.2): the members' loads reference axes,
read-only, with the way to Geometry where they are entered; the mesh counts,
which only the beam reads; the model drawn; and the write.

**It owns none of what it shows.** The axes table is
:func:`sloads.export.lra_model.reference_axis_rows`; the counts are the
registry's ``lra_mesh`` rows through :func:`oracle_app.form.render_page_inputs`;
the drawing is the catalogue's ``lra_beam_model`` family, the same figures the
oracle report prints in Appendix G; the files are
:mod:`sloads.export.deliverables`' -- the render and write the CLI's ``lra`` and
``oew`` targets call -- under :func:`sloads.report.bundle_stamps`' stamp, into
the folder :func:`app_shell.folder_picker.folder_picker` chose. A model the
exporter refuses is said verbatim and nothing is drawn or written on a guess.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app_shell.components import active_project, active_system, workflow_page_link
from app_shell.folder_picker import folder_picker
from app_shell.project_state import saved_path
from app_shell.widget_keys import widget_key
from oracle_app.figures import render_input_figures
from oracle_app.form import render_page_inputs
from sloads import field_registry as fr
from sloads import workflow as wf
from sloads.export import deliverables
from sloads.export.lra_model import LraRefusal, build_lra_model, reference_axis_rows
from sloads.export.report_package import build_timestamp
from sloads.report import bundle_stamps

#: The page's key and label, owned in ``workflow.NON_STEP_PAGES``.
PAGE_KEY = "beam_model"
PAGE_TITLE = wf.non_step_page(PAGE_KEY).title

#: The field every surface's loads reference axis is entered in.
AXIS_FIELD = "geometry.surfaces[].ref_axis_pct"

#: Session-state key of the folder the deck is written to. The page's own, so
#: choosing where a deck goes never moves where reports go (note 67 D-67.7).
_ROOT = "beam_model_root"


def _axes_block(project, system) -> None:
    st.subheader("Loads reference axes")
    st.caption(
        "The axis each member's beam runs on. A surface's axis is a chord "
        "fraction entered on Geometry, because the torsion computed there is "
        "stated about it as well; it is shown here beside the beam it places.")
    st.dataframe(pd.DataFrame(reference_axis_rows(project, system)),
                 hide_index=True, width="stretch")
    # Where the axis is entered is the registry's answer, not a key typed here
    # (gate G2): the link follows the field if it is ever re-paged.
    workflow_page_link(fr.entry(AXIS_FIELD).page, label="Enter the axes")


def _write_block(project, system) -> None:
    st.subheader("Write the deck")
    st.caption(
        "Writes the LRA beam model deck and, beside it, the operating empty "
        "weight's CONM2 mass set -- no payload and no fuel -- in "
        f"{system.value} solver units, each stamped with its methods and "
        "limitations. The same files the CLI writes with "
        "`--export-target lra` and `--export-target oew`.")
    folder = folder_picker(
        _ROOT, key_prefix="beam_model", label="Writing the deck to",
        prompt="Choose the folder to write the beam model deck into",
        anchors=deliverables.folder_anchors(saved_path()))
    prefix = deliverables.page_prefix(folder, saved_path())
    paths = [deliverables.deliverable_path(prefix, artifact)
             for artifact in deliverables.BEAM_PAGE_ARTIFACTS]
    st.markdown("Files:  \n" + "  \n".join(f"`{p}`" for p in paths))
    replacing = deliverables.existing(paths)
    confirmed = True
    if replacing:
        # One named confirmation, never a silent overwrite (D-67.8).
        st.warning(f"{len(replacing)} of these files already exist.")
        confirmed = st.checkbox(f"Replace the {len(replacing)} existing file(s)",
                                key=widget_key("beam_model_replace"))
    if not st.button("Write the deck and the OEW mass set",
                     key=widget_key("beam_model_write"), disabled=not confirmed):
        return
    _csv, stamp = bundle_stamps(project, system, build_timestamp())
    try:
        rendered, absences = deliverables.render_page_set(
            project, prefix, system=system, header_comment=stamp)
    except ValueError as exc:
        # An ``LraRefusal`` is one; the other is a deck with no balanced case
        # to carry. Either way nothing is written, and the reason is the
        # exporter's own (note 67 gate 4).
        st.error(str(exc))
        return
    try:
        written = deliverables.write_set(rendered)
    except OSError as exc:
        st.error(f"Nothing could be written to `{folder}`: {exc}")
        return
    st.success("Wrote " + ", ".join(f"`{p}`" for p in written))
    for absence in absences:
        st.warning(absence)


def render_beam_model_page() -> None:
    """The page. Nothing is computed here that the calc package does not own."""
    project = active_project()
    system = active_system()
    st.title(PAGE_TITLE)
    st.caption(
        "The loads reference axis beam model of the full-span, free-free "
        "airplane -- the solver deck sloads delivers. Every applied load is "
        "stated at one of its grids.")
    _axes_block(project, system)
    st.divider()
    render_page_inputs(project, PAGE_KEY, system)
    try:
        build_lra_model(project)
    except LraRefusal as exc:
        # Verbatim, and nothing drawn or written on a guess (note 67 gate 4):
        # the datum the refusal names is the one to enter, usually above.
        st.error(str(exc))
        return
    render_input_figures(project, PAGE_KEY, system)
    st.divider()
    _write_block(project, system)


__all__ = ["PAGE_KEY", "PAGE_TITLE", "render_beam_model_page"]
