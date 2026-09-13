"""Aircraft Comparison — place the design against a reference fleet.

The Export-section input-assessment page: it answers "how does this airplane
compare to similar aircraft?" in one place, the concept-mode charter
(``CLAUDE.md``: "assesses a configuration against similar airplanes"). It carries
the quantitative placement (nearest-N similar aircraft, W/S & W/P percentile
band, outlier flags), a parameter table (subject + nearest-N), and six scatter
tabs: the two loading/weight scatters (W/S-vs-W/P, MTOW-vs-empty-weight) plus
four geometric scatters (wingspan / wing area / aspect ratio / seats vs. MTOW).

**Reduced to its framing at #268** (note 57 D-57.5), when this page ported to the
surviving GUI. Everything it used to own moved to an owner that outlives it: the
subject's priority chain and the reference-CSV read to :mod:`sloads.fleet`, the
six figures to :mod:`sloads.report.fleet_figures`, and the rendering to
:mod:`app_shell.fleet_view`, which ``oracle_app/fleet.py`` calls the same way.
Two pages, one implementation -- so the port cannot drift from the page it ported
from during the milestone in which both exist, and #270 deletes a file that owns
nothing.

Presentation only. The reference fleet is nominal published specs (Imperial) —
never a FAR input, so the ULT/limit rules and ``load_cases_to_rows`` are
untouched.

One page of the multipage app; run the suite with:  streamlit run app/Home.py
"""

from __future__ import annotations

import streamlit as st

from app_shell.components import stop_page
from app_shell.fleet_view import render_figures, render_fleet_table, render_readout
from sloads import Project, reference_fleet, subject_from_project
from sloads.report.fleet_figures import fleet_figures

st.title("Aircraft Comparison")
st.caption(
    "This airplane placed against a reference fleet by wing loading (W/S), power "
    "loading (W/P), weight and geometry. Reference figures are nominal published "
    "specs (Imperial) for comparison only — they never enter a FAR computation. "
    "Jets (no shaft power) carry no W/P."
)

project: Project = st.session_state.get("project", Project(name=""))

fleet = reference_fleet()
if not fleet:
    st.info("The bundled reference aircraft data could not be read.")
    stop_page()

subject = subject_from_project(project)
if subject is not None:
    render_readout(subject, fleet)
else:
    st.info(
        "Set the design weight (Structural Speeds, or the weight estimate / data base) "
        "to place this airplane against the fleet. The reference fleet is shown below."
    )

render_figures(fleet_figures(subject, fleet), key_prefix="app.fleet.figure")
render_fleet_table(fleet)
