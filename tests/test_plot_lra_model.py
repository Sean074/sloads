"""The LRA three-view renderer (`scripts/plot_lra_model.py`), offline.

A display-only analyst tool over the public exporter API; what is asserted
here is the capability's claims, not pixels: it renders the example projects
whose LRA model builds (conventional ga6, T-tail atr42, twin baron), it keeps
the exporter's refusal contract verbatim (exit 2, the datum named, no output
file), and `--no-outlines` still produces a plot.

matplotlib is a dev extra; the whole module skips when it is absent, exactly
as the script itself degrades.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys

import pytest

pytest.importorskip("matplotlib")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPT = os.path.join(_ROOT, "scripts", "plot_lra_model.py")


@pytest.fixture(scope="module")
def plm():
    spec = importlib.util.spec_from_file_location("plot_lra_model", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["plot_lra_model"] = mod
    spec.loader.exec_module(mod)
    return mod


def _example(name: str) -> str:
    return os.path.join(_ROOT, "examples", f"{name}.project.json")


@pytest.mark.parametrize("name", ["ga6_normal", "atr42_100", "baron_58"])
def test_renders_example_project(plm, tmp_path, name):
    """Conventional, T-tail and twin layouts all render to a non-trivial PNG."""
    out = tmp_path / f"{name}.png"
    rc = plm.main([_example(name), "-o", str(out), "--dpi", "60"])
    assert rc == 0
    assert out.exists() and out.stat().st_size > 10_000, (
        f"{name}: expected a non-trivial PNG, got "
        f"{out.stat().st_size if out.exists() else 'no file'}")


def test_no_outlines_flag_still_renders(plm, tmp_path):
    out = tmp_path / "bare.png"
    rc = plm.main([_example("ga6_normal"), "-o", str(out), "--dpi", "60", "--no-outlines"])
    assert rc == 0 and out.exists()


def test_refusal_is_kept_verbatim(plm, tmp_path, capsys):
    """A missing LRA datum exits 2 with the exporter's own message and writes
    nothing -- the script must never default what build_lra_model refuses."""
    with open(_example("ga6_normal"), encoding="utf-8") as fh:
        doc = json.load(fh)
    for surf in doc["geometry"]["surfaces"]:
        if surf["name"] == "wing":
            surf["ref_axis_pct"] = None
    src = tmp_path / "no_axis.project.json"
    src.write_text(json.dumps(doc), encoding="utf-8")
    out = tmp_path / "refused.png"
    rc = plm.main([str(src), "-o", str(out), "--dpi", "60"])
    assert rc == 2
    assert "ref_axis_pct" in capsys.readouterr().err
    assert not out.exists()


def test_default_output_path_is_derived(plm, tmp_path):
    """No -o: the PNG lands beside the input, named <stem>_lra_views.png."""
    with open(_example("ga6_normal"), encoding="utf-8") as fh:
        doc = fh.read()
    src = tmp_path / "ga6_normal.project.json"
    src.write_text(doc, encoding="utf-8")
    rc = plm.main([str(src), "--dpi", "60"])
    assert rc == 0
    assert (tmp_path / "ga6_normal_lra_views.png").exists()


if __name__ == "__main__":  # zero-dependency self-runner
    sys.exit(pytest.main([__file__, "-p", "no:xdist", "-q"]))
