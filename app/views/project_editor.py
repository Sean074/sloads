"""Streamlit page for reviewing/hand-editing the whole project as JSON.

One page of the multi-page app; run the suite with:  streamlit run app/Home.py

**The page body moved to** :mod:`app_shell.project_editor` (design note 57,
D-57.3): the oracle GUI carries the editor too, so it is owned once in the
shared shell and this file is the ``app/`` page that renders it. It stays a
file because ``app/``'s navigation is built as ``views/<step key>.py``
(``app/Home.py``) -- and it is deleted with the rest of the tree at D-57.1.
"""

from __future__ import annotations

from app_shell.project_editor import render_project_editor

render_project_editor()
