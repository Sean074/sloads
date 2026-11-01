"""The `changes/` fragment contract and the release-cut builder (design notes 26, 61; #359).

Closure writes one typed fragment, not an edit to `CHANGELOG.md`; the release
cut assembles them into the release's subsections. History fragments retired on
2026-11-01 (#359): the changelog bullet, the design note and `git log` are the
record. What can rot: a fragment the builder cannot place (bad name, wrong
shape) and would be discovered only at release time -- a failure here.
"""

from __future__ import annotations

import importlib.util
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CHANGES = os.path.join(_ROOT, "changes")
_RECORD = os.path.join(_ROOT, "docs", "90_record")
_CHANGELOG = os.path.join(_RECORD, "CHANGELOG.md")
_SCRIPT = os.path.join(_ROOT, "scripts", "build_changelog.py")


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
        assert "\n## [Unreleased]\n" in fh.read()


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


@pytest.mark.parametrize("name", ["x.history.md", "x.history-added.md"])
def test_a_history_fragment_is_refused(bc, name):
    """Retired 2026-11-01 (#359): the record is the changelog bullet, the design
    note and git log. A history fragment is a naming error, found at write
    time by this guard and by solo_close.sh, not at the release cut."""
    with pytest.raises(bc.FragmentError, match="history"):
        bc.validate_fragment(name, "- **a** — b\n")


def test_parse_groups_fragments_by_type(bc):
    out = bc.parse_fragments({"a.fixed.md": "- **f**\n", "b.changed.md": "- **c**\n", "c.fixed.md": "- **g**\n"})
    assert set(out) == {"fixed", "changed"}
    assert out["fixed"] == ["- **f**\n", "- **g**\n"]


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


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-n", "0", "-q"]))
