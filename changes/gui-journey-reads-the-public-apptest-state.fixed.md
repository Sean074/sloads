- **The GUI journey carries its session through Streamlit's public tester API, and every reach past it is now declared (tier S, 2026-09-16).**
  `AppTest.session_state` was the internal `SafeSessionState` through Streamlit
  1.63, and one line of `tests/test_gui_journey.py` read its private
  `filtered_state` property to carry widget state from page to page. 1.64 wrapped
  that object in a documented tester-facing one and moved the real state to
  `_session_state`; the reach stopped resolving and the wrapper's `__getattr__`
  reported it as a missing *key* — `AttributeError: filtered_state not found in
  session_state` — which is an API change wearing a state defect's error message.
  It failed all five fixtures on CI while the local gate stayed green, because a
  developer's venv is pinned by whatever was current when it was made and CI
  installs the newest release every run. The walk now calls the public
  `to_dict()` where it exists and falls back to the private property below 1.64,
  so it holds across the whole supported range (`streamlit>=1.51`, no ceiling);
  the carried view — user state and keyed widgets, internal keys excluded — is
  identical either way, and the journey passes on 1.58.0 and 1.64.0 alike.
  This is the unbounded-ceiling policy doing exactly what `pyproject.toml` says
  it is for, so the finding is that the warning was worth less than it should
  have been: a reach into internals turns an upstream-API alarm into noise about
  a key. `tests/test_ci_conformance.py` — which already owns the unpinned-install
  policy this rests on — now scans `tests/` for private Streamlit spellings and
  requires each one to be declared with its reason, with a companion that fails
  when a declaration outlives the reach it excused.
