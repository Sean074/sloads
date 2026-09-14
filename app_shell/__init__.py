"""The app-layer shell — everything a sloads GUI needs that is *not* a page.

**One owner, no GUI is its parent** (design note 32, decision OG-4 / step OG-B).
The shell is project state and the unsaved-changes guard, the units toggle, the
project-file sidebar, the page scaffold, the unit-input boundary, the JSON
editor, the figure helpers and the LIMIT station tables. Before this package
these lived inside ``app/`` — two of them importable only as bare top-level
modules on Streamlit's implicit path, and the project-lifecycle helpers not
importable *at all*, because ``app/Home.py`` executed a whole Streamlit app at
import time. A second GUI could therefore only have copied them, which is the
dual path this project rejects in the calc layer (``CLAUDE.md`` rule 3),
relocated to the shell.

**There is one front-end now** (``oracle_app``, note 57 D-57.1 at #270), so the
boundary this package draws is no longer between two GUIs. It is kept, and is
load-bearing for two reasons: the guard in ``tests/test_app_shell.py`` asserts
the shell never imports a GUI package back, which is what keeps page decoration
out of the reusable half; and an entry point is a thin thing again — the
``sloads-oracle`` script builds a page set and hands it to the shell.

Layout:

* :mod:`app_shell.components` — page scaffold (:func:`~app_shell.components.page`,
  :func:`~app_shell.components.page_header`), the unit boundary
  (:func:`~app_shell.components.unit_number_input`,
  :func:`~app_shell.components.active_system`), workflow-derived page links and
  the FAR 23 applicability banner.
* :mod:`app_shell.project_state` — the project in ``st.session_state``, the
  saved-snapshot baseline and the dirty/discard/load guard.
* :mod:`app_shell.widget_keys` — widget identity across a project replacement:
  the *project generation* stamped into every key of a widget seeded from the
  project, so a load cannot leave stale widgets to overwrite it (#51).
* :mod:`app_shell.sidebar` — the global sidebar every page inherits: units
  toggle, project Open/Save/upload/download, About.
* :mod:`app_shell.project_editor` — the JSON editor page (note 57 D-57.3): the
  escape hatch for any field no form reaches, with its own validate-and-apply.
* :mod:`app_shell.plots` — the screen renderer of a report figure (note 60
  D-60.1): a peer of :mod:`sloads.report.plots_tex` over the same ``PlotData``,
  so the screen and the document cannot draw different pictures.
* :mod:`app_shell.fleet_view` — the comparison readout, figures and table (note
  57 D-57.5), handed ``FleetStats`` by :mod:`sloads.fleet` and ``Figure``
  objects by :mod:`sloads.report.fleet_figures`.
* :mod:`app_shell.limit_csv` — the analysis pages' LIMIT station tables (pure
  functions, no Streamlit).
* :mod:`app_shell.nav` — the register of *which page a step key is* in the
  running GUI, so a cross-page link resolves to a page object rather than to the
  front-end's directory layout (note 32, OG-F).

**What is *not* shell: navigation.** The entry point builds its own page set —
:func:`sloads.workflow.gui_pages`, the derived analysis steps plus the declared
non-step pages (note 57 D-57.1) — and the shell only holds the lookup: an entry
point hands :func:`app_shell.nav.register_pages` the page set it just built, and
a link asks for one back. ``st.set_page_config`` likewise stays in the entry
point, **exactly one call, and none anywhere else** (OG-10) — guarded in
``tests/test_app_shell.py``.

Nothing here computes a load, converts a deliverable or writes an export: the
shell is presentation over :mod:`sloads`, and the guard in
``tests/test_app_shell.py`` asserts it never imports a GUI package back.
"""

from __future__ import annotations
