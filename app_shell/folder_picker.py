"""Choosing the folder a page writes into -- one control, for every page that writes.

The Report page built this first and kept it private. The Beam Model page
writes the solver deck to a folder the user chooses too (note 67 D-67.7), and a
second page with its own picker is the #239 class: two dialogs, two fallback
browsers, two TCC warnings, free to drift. So the control lives here and each
page calls it with **its own** session-state key -- choosing where a deck goes
never moves where reports go.

**The OS dialog is the control; the in-app browser is the fallback.** The
oracle GUI runs locally, so the machine serving the page is the machine the user
is sitting at (OR-22) and the operating system's own folder chooser is
reachable through :mod:`sloads.export.directory_dialog`. It is what the user
already knows how to drive, and it can reach anywhere on the disk in one gesture
rather than one directory per click.

The click-through browser stays for the machine that has no dialog, and for the
case where the dialog cannot be raised. It is not dead code: a folder chooser
that silently does nothing would leave no way to set the location at all, and a
page that calls this exists to write somewhere.

This module holds only the current path as a string. Every question about what
that string *means* -- does it exist, what is inside it, may we write it -- is
answered in :mod:`sloads.export`, because a GUI module may not import ``os``
(gate G1).
"""

from __future__ import annotations

from typing import Sequence, Tuple

import streamlit as st

from app_shell.widget_keys import widget_key
from sloads.export import directory_dialog as dialog
from sloads.export import report_package as pkg


def folder_picker(state_key: str, *, key_prefix: str, label: str, prompt: str,
                  anchors: Sequence[Tuple[str, str]]) -> str:
    """Draw the folder chooser and return the folder currently chosen.

    ``state_key`` is the session-state key holding the path; it is the caller's,
    so two pages keep two folders. ``key_prefix`` names the widgets
    (``<prefix>_pick_btn`` and so on). ``label`` heads the path shown,
    ``prompt`` is the OS dialog's title, and ``anchors`` are the ``(label,
    path)`` starting points of the fallback browser, nearest first -- the first
    is where the folder starts when the page has never chosen one.
    """
    if state_key not in st.session_state:
        st.session_state[state_key] = pkg.browse_start(anchors[0][1])
    here = st.session_state[state_key]

    shown, chooser = st.columns([3, 1])
    shown.markdown(f"**{label}**  \n`{here}`")
    if chooser.button("📂 Choose folder…", key=widget_key(f"{key_prefix}_pick_btn"),
                      width="stretch", disabled=not dialog.native_picker_available()):
        picked = dialog.choose_directory(here, prompt=prompt)
        if picked:
            st.session_state[state_key] = picked
            st.rerun()
        # No message on ``None``: Cancel is a normal answer, and saying
        # "no folder chosen" to someone who deliberately pressed Cancel is noise.

    with st.expander("Or browse to it here", expanded=False):
        labels = [anchor for anchor, _path in anchors]
        jump = st.selectbox("Start from", labels, key=widget_key(f"{key_prefix}_anchor"))
        if st.button("Go", key=widget_key(f"{key_prefix}_anchor_btn"), width="stretch"):
            st.session_state[state_key] = pkg.browse_start(dict(anchors)[jump])
            st.rerun()

        up, into = st.columns([1, 2])
        with up:
            if st.button("⬆ Up one level", key=widget_key(f"{key_prefix}_up_btn"),
                         width="stretch", disabled=pkg.is_root(here)):
                st.session_state[state_key] = pkg.parent_of(here)
                st.rerun()
        subdirs = pkg.list_subdirs(here)
        with into:
            chosen = st.selectbox("Folders here", subdirs or ["(no subfolders)"],
                                  key=widget_key(f"{key_prefix}_subdir"),
                                  disabled=not subdirs, label_visibility="collapsed")
            if st.button("Open folder ▶", key=widget_key(f"{key_prefix}_down_btn"),
                         width="stretch", disabled=not subdirs):
                st.session_state[state_key] = pkg.child_of(here, chosen)
                st.rerun()

        made = st.text_input("New folder here", key=widget_key(f"{key_prefix}_mkdir"),
                             placeholder="e.g. Programme-X")
        if st.button("Create and use", key=widget_key(f"{key_prefix}_mkdir_btn"),
                     width="stretch", disabled=not made.strip()):
            # A folder name, not a path -- ``create_subdir`` refuses a separator
            # rather than normalising one, so this control cannot walk out of
            # the folder it is displayed in.
            try:
                st.session_state[state_key] = pkg.create_subdir(here, made)
            except (ValueError, OSError) as exc:
                st.error(str(exc))
            else:
                st.rerun()

    if not pkg.is_writable(here):
        # Choosing a folder is not being granted it: macOS keeps ~/Desktop and
        # friends behind TCC, and the OS dialog hands back a path this process
        # may still not be allowed to write. Said here, before the write, rather
        # than as a failure after the user has filled the whole page in.
        st.warning(
            f"`{here}` cannot be written to by this app. On macOS, Desktop, "
            "Documents and Downloads need permission granted to the terminal "
            "running sloads (System Settings ▸ Privacy & Security ▸ Files and "
            "Folders, or Full Disk Access). Choose another folder, or grant it "
            "and reopen this page.")
    return st.session_state[state_key]


__all__ = ["folder_picker"]
