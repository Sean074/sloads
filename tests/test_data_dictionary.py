"""Drift guard for the generated project.json data dictionary.

`docs/generate_data_dict.py` introspects `sloads.models` and writes
`docs/10_standard/DATA_DICTIONARY.md`. This test asserts the committed doc is
in sync with the current dataclasses (so a schema change that forgets to
regenerate fails CI) and that every input slice is documented.
"""

import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEN = os.path.join(_REPO, "docs", "generate_data_dict.py")
_DOC = os.path.join(_REPO, "docs", "10_standard", "DATA_DICTIONARY.md")


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_data_dict", _GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_committed_doc_matches_generator():
    gen = _load_generator()
    with open(_DOC, encoding="utf-8") as fh:
        committed = fh.read()
    assert committed == gen.build(), (
        "DATA_DICTIONARY.md is stale — regenerate it: "
        "`.venv/bin/python docs/generate_data_dict.py`"
    )


def test_every_input_slice_is_documented():
    gen = _load_generator()
    doc = gen.build()
    for attr, _role in gen.INPUT_SLICES:
        assert f"`{attr}`" in doc, f"slice {attr} missing from data dictionary"


def _input_dataclasses(gen):
    """Every dataclass reachable from the input slices, nested ones included."""
    import dataclasses

    import sloads.models as models

    todo = [cls for attr, _ in gen.INPUT_SLICES if (cls := gen._slice_type(attr))]
    seen = []
    while todo:
        cls = todo.pop()
        if cls in seen:
            continue
        seen.append(cls)
        for f in dataclasses.fields(cls):
            gen._nested_dataclasses(gen._resolve_hints(cls)[f.name], todo)
    assert models.Project not in seen
    return seen


def test_every_input_dataclass_has_a_complete_table():
    """#409 (review D-6). `models/` became a package and the generator's hint
    resolver started raising on `Project`; a swallowed exception turned that
    into two field tables and `?` types. Every dataclass an input slice
    reaches, nested ones included, has a table, and no cell is `?`."""
    gen = _load_generator()
    doc = gen.build()
    classes = _input_dataclasses(gen)
    assert len(classes) > 2, "the slice walk found almost nothing -- the resolver is broken again"
    for cls in classes:
        assert f"### `{cls.__name__}`" in doc, f"no field table for {cls.__name__}"
    assert "`?`" not in doc, "an unresolved type reached the dictionary"
    for name, table in gen.build_guide_tables().items():
        assert "`?`" not in table, f"an unresolved type reached the guide table {name}"


def test_an_unresolvable_annotation_raises_instead_of_degrading():
    """The fallback to raw strings is gone, in the generator and in the
    registry it shares the resolver with: a name `models/` does not define
    fails the build rather than printing `?` (#409)."""
    import dataclasses

    import pytest

    import sloads.field_registry as fr
    import sloads.models as models

    @dataclasses.dataclass
    class Broken:
        x: "NoSuchTypeAnywhere"  # noqa: F821  -- the point of the test

    gen = _load_generator()
    with pytest.raises(NameError):
        gen._resolve_hints(Broken)
    with pytest.raises(NameError):
        fr._hints(Broken)
    hints = gen._resolve_hints(models.Project)
    assert not [k for k, v in hints.items() if isinstance(v, str)], "Project has unresolved hints"


def test_schema_version_recorded():
    import sloads.models as models

    gen = _load_generator()
    assert f"Schema version: **{models.SCHEMA_VERSION}**" in gen.build()


def test_gui_design_schema_paragraph_points_at_the_owner():
    """GUI_design.md's schema paragraph names the owner, never the number.

    M4-16 guarded the *value* here (the line went stale three times: v31, v32,
    the v33 bump) — which kept the copy current but kept the copy. The 2026-08-16
    documentation-currency rule (`00_program_overview.md`) retires the copy: the
    paragraph points at `SCHEMA_VERSION` in `sloads/models/project.py`, and
    `tests/test_doc_currency.py` fails on any literal beside it. This asserts the
    pointer is present, so the paragraph cannot silently lose it either.
    """
    doc = os.path.join(_REPO, "docs", "10_standard", "GUI_design.md")
    with open(doc, encoding="utf-8") as fh:
        text = fh.read()
    assert "`SCHEMA_VERSION`, whose owner is `sloads/models/project.py`" in text, (
        "GUI_design.md's schema paragraph must point at the SCHEMA_VERSION owner (no literal value)."
    )


if __name__ == "__main__":
    test_committed_doc_matches_generator()
    test_every_input_slice_is_documented()
    test_every_input_dataclass_has_a_complete_table()
    test_an_unresolvable_annotation_raises_instead_of_degrading()
    test_schema_version_recorded()
    test_gui_design_schema_paragraph_points_at_the_owner()
    print("ok")
