- **The Project JSON Editor moves to `app_shell/` and the oracle GUI carries it
  (#265, note 57 D-57.3, tier S, 2026-09-13).** The editor's page body is now
  `app_shell/project_editor.py`, owned once and rendered by both front-ends;
  `app/views/project_editor.py` is the two-line `app/` page that calls it, and
  `oracle_app/Oracle.py` registers the editor on `st.navigation` only — never in
  `register_pages`, which stays exactly `workflow.oracle_steps()` (gate G2), on
  the OR-16 pattern the Report page established. Title and URL path are read from
  `workflow.py` rather than typed again. First row of band B5: the editor is the
  escape hatch that makes every sloads-only field enterable in the surviving GUI
  before D-57.2 builds a widget for any of them, so no later port waits on the
  field tiers. Behaviour is unchanged — the same display-unit round trip, the
  same Apply-side safety-factor warning, the same session replacement — and the
  `st.session_state` scan in `tests/test_persistence.py` follows the page into
  the shell so its coverage did not lapse with the move.
