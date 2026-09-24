"""The `changes/` fragment contract and the release-cut builder (design notes 26, 28, 61).

Closure writes a fragment, not an edit to `CHANGELOG.md` or the history file;
the release cut assembles them (changelog subsections; history entries rolled
to the top of `00_completed_development.md`, MD-4). Design note 61 CV-2 made a
tier-M/L closure write **one** fragment: the history entry also *derives* its
changelog bullet, so the two files can no longer drift apart because there is
no second file. Three things can rot: a fragment the builder cannot place (bad
name, wrong shape, no derivable lead) and would be discovered only at release
time; a derived bullet that stops matching the entry it came from; and either
live record file growing back into the record the split retired. The first two
are failures here; the third is a warning — size is a release-roll trigger
(`RELEASE_PROCESS.md` §4, note 61 CV-5), not a defect in the change that
crossed it.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CHANGES = os.path.join(_ROOT, "changes")
_RECORD = os.path.join(_ROOT, "docs", "90_record")
_CHANGELOG = os.path.join(_RECORD, "CHANGELOG.md")
_HISTORY = os.path.join(_RECORD, "00_completed_development.md")
_SCRIPT = os.path.join(_ROOT, "scripts", "build_changelog.py")

#: A live record file rolls into an archive at the next release cut once it
#: passes this (design note 26 D-4 for the history; note 61 CV-5 extended the
#: same rule to the changelog). Warn, do not fail.
HISTORY_LINE_THRESHOLD = 1500


def _builder():
    spec = importlib.util.spec_from_file_location("build_changelog", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bc():
    return _builder()


# --- the fragments on disk -------------------------------------------------


def test_every_fragment_on_disk_is_valid(bc):
    files = bc.load_fragments(_CHANGES)
    bc.parse_fragments(files)  # raises FragmentError naming the file


def test_changes_dir_holds_only_fragments_and_the_readme():
    stray = [n for n in os.listdir(_CHANGES) if not n.startswith(".") and n != "README.md" and not n.endswith(".md")]
    assert stray == [], f"non-fragment files in changes/: {stray}"


def test_changelog_still_has_an_unreleased_heading():
    with open(_CHANGELOG, encoding="utf-8") as fh:
        assert bc_unreleased(fh.read())


def bc_unreleased(text: str) -> bool:
    return "\n## [Unreleased]\n" in text


# --- the builder's pure functions ---------------------------------------


@pytest.mark.parametrize(
    "name",
    ["Foo.added.md", "foo.md", "foo.bar.baz.md", "foo_bar.added.md", "foo.improved.md", "foo.added.txt"],
)
def test_bad_fragment_names_are_refused(bc, name):
    with pytest.raises(bc.FragmentError, match=name.split(".")[0]):
        bc.validate_fragment(name, "- ok\n")


def test_non_bullet_body_is_refused(bc):
    with pytest.raises(bc.FragmentError, match="bullet"):
        bc.validate_fragment("foo.fixed.md", "**Foo.** not a bullet\n")


def test_merge_leads_with_fragments_and_keeps_legacy_text(bc):
    legacy = "\n### Added\n\n- **Old added.** text\n\n### Fixed\n\n- **Old fixed.**\n"
    frags = {"fixed": ["- **New fixed.**\n"], "changed": ["- **New changed.**\n"]}
    out = bc.merge_section(legacy, frags)
    assert out.index("### Added") < out.index("### Changed") < out.index("### Fixed")
    assert out.index("**New fixed.**") < out.index("**Old fixed.**")
    assert "**Old added.**" in out and "**New changed.**" in out
    assert "### Breaking" not in out and "### Removed" not in out


def test_cut_release_touches_only_the_unreleased_block(bc):
    log = (
        "# Changelog\n\n---\n\n## [Unreleased]\n\n### Fixed\n\n- **legacy**\n\n"
        "## [0.5.0] — 2026-08-13\n\n### Added\n\n- old\n"
    )
    out = bc.cut_release(log, {"added": ["- **frag**\n"]}, "0.6.0", "2026-08-20")
    head, _, tail = out.partition("## [0.5.0]")
    assert tail == " — 2026-08-13\n\n### Added\n\n- old\n"
    assert head.count("## [Unreleased]") == 1
    assert "## [0.6.0] — 2026-08-20\n\n### Added\n\n- **frag**\n\n### Fixed\n\n- **legacy**\n" in head
    assert head.index("## [Unreleased]") < head.index("## [0.6.0]")


def test_cut_release_without_unreleased_heading_is_an_error(bc):
    with pytest.raises(ValueError, match="Unreleased"):
        bc.cut_release("# Changelog\n\n## [0.5.0] — d\n", {}, "0.6.0", "2026-08-20")


# --- history fragments (design note 28 MD-4) ---------------------------


def test_history_fragment_shapes():
    bc = _builder()
    assert bc.validate_fragment("x.history.md", "- **Tier M (tier M, 2026-08-20)** — one paragraph\n") == "history"
    assert bc.validate_fragment("x.history.md", "## Step 14 — full step\n\n**Objective.** …\n") == "history"
    assert bc.validate_fragment("x.history.md", "**Step 14 — full step**\n\n**Objective.** …\n") == "history"
    with pytest.raises(bc.FragmentError, match="history fragment"):
        bc.validate_fragment("x.history.md", "a plain paragraph\n")
    with pytest.raises(bc.FragmentError, match="tier-M bullet"):  # un-bulleted tier M (#299)
        bc.validate_fragment("x.history.md", "**Tier M (tier M, 2026-08-20).** one paragraph\n")
    with pytest.raises(bc.FragmentError, match="empty"):
        bc.validate_fragment("x.history.md", "\n")


def test_roll_history_inserts_after_the_header_rule_and_keeps_the_rest_byte_identical(bc):
    history = "# Completed Development\n\nheader prose\n\n---\n\n- **Old (tier M)** — t\n\n**Step X**\n\nbody\n"
    out = bc.roll_history(history, ["- **New A** — a\n", "**Step B**\n\n**Objective.** b\n"])
    head, _, tail = out.partition("---\n")
    assert head == "# Completed Development\n\nheader prose\n\n"
    assert tail == (
        "\n- **New A** — a\n\n**Step B**\n\n**Objective.** b\n\n"
        "- **Old (tier M)** — t\n\n**Step X**\n\nbody\n"
    )
    assert bc.roll_history(history, []) == history


def test_roll_history_without_a_rule_is_an_error(bc):
    with pytest.raises(ValueError, match="rule"):
        bc.roll_history("# H\n\nno rule here\n", ["- **x** — y\n"])


def test_parse_separates_history_from_changelog_types(bc):
    out = bc.parse_fragments({"a.fixed.md": "- **f**\n", "b.history.md": "- **h** — p\n"})
    # 'changed' is b's derived bullet: b wrote no changelog fragment of its own.
    assert set(out) == {"fixed", "history", "changed"}


# --- one telling: the derived changelog bullet (design note 61 CV-2) ------


def test_a_tier_m_history_entry_derives_its_changelog_bullet(bc):
    body = "- **Thing lands (#245, tier M, 2026-09-13)** — a long paragraph that\nwraps and keeps going.\n"
    out = bc.parse_fragments({"thing.history.md": body})
    assert out["history"] == [body.strip("\n") + "\n"]
    assert out["changed"] == ["- **Thing lands (#245, tier M, 2026-09-13)**\n"]


def test_a_tier_l_step_derives_its_changelog_bullet(bc):
    out = bc.parse_fragments({"x.history-added.md": "## Step 14 — the thing (note 61, tier L)\n\n**Objective.** …\n"})
    assert out["added"] == ["- **Step 14 — the thing (note 61, tier L)**\n"]


def test_a_hand_written_bullet_suppresses_the_derived_one(bc):
    """The escape hatch: when the consumer-facing bullet differs, write it."""
    out = bc.parse_fragments({
        "x.history.md": "- **Internal framing (#1, tier M, 2026-09-13)** — why\n",
        "x.changed.md": "- **What a user sees (#1).** the other wording\n",
    })
    assert out["changed"] == ["- **What a user sees (#1).** the other wording\n"]


def test_a_history_fragment_with_no_lead_phrase_is_refused(bc):
    with pytest.raises(bc.FragmentError, match="lead phrase"):
        bc.validate_fragment("x.history.md", "## \n")


def test_an_unknown_derived_subsection_is_refused(bc):
    with pytest.raises(bc.FragmentError, match="derived type"):
        bc.validate_fragment("x.history-sideways.md", "- **a** — b\n")


def test_derived_bullets_flatten_a_wrapped_lead(bc):
    out = bc.derive_bullet("x.history.md", "- **A lead that\n  wraps over lines (#9)** — body\n")
    assert out == "- **A lead that wraps over lines (#9)**\n"


# --- the changelog roll (design note 61 CV-5) -----------------------------


def _fake_changelog():
    return ("# Changelog\n\n## [Unreleased]\n\n"
            "## [0.3.0] — c\n\nc body\n\n## [0.2.0] — b\n\nb body\n\n## [0.1.0] — a\n\na body\n")


def test_roll_changelog_keeps_the_newest_blocks_and_freezes_the_rest(bc):
    live, archived = bc.roll_changelog(_fake_changelog(), keep=2)
    assert "## [0.3.0]" in live and "## [0.2.0]" in live
    assert "## [0.1.0]" not in live
    assert archived.startswith("## [0.1.0] — a\n")


def test_roll_changelog_is_byte_preserving(bc):
    text = _fake_changelog()
    live, archived = bc.roll_changelog(text, keep=2)
    assert live.rstrip("\n") + "\n\n" + archived == text


def test_roll_changelog_is_a_no_op_when_there_is_nothing_to_archive(bc):
    text = _fake_changelog()
    assert bc.roll_changelog(text, keep=9) == (text, "")


def test_a_rolled_archive_is_named_after_its_newest_release(bc):
    assert bc.archive_name("## [0.1.0] — a\n\nbody\n") == "CHANGELOG_to_0.1.0.md"
    assert "do not edit" in bc.archive_header("## [0.1.0] — a\n").lower()


# --- the live record files' size ------------------------------------------


@pytest.mark.parametrize("path", [_HISTORY, _CHANGELOG])
def test_live_record_size_is_within_the_roll_threshold_or_warns(path):
    with open(path, encoding="utf-8") as fh:
        n = sum(1 for _ in fh)
    if n > HISTORY_LINE_THRESHOLD:
        warnings.warn(
            f"{os.path.relpath(path, _ROOT)} is {n} lines (> {HISTORY_LINE_THRESHOLD}): "
            "roll the older release blocks into an archive at the next cut "
            "(RELEASE_PROCESS.md §4; `build_changelog.py --roll`)",
            stacklevel=1,
        )


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
