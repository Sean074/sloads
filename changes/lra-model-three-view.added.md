- **The LRA beam model gets a three-view renderer (`scripts/plot_lra_model.py`, tier S, 2026-09-10).**
  A display-only analyst tool over the public exporter API: project JSON in, one
  4-panel PNG out (isometric + plan + side + front) of the step-12 skeleton --
  CBAR chains by section family, RBE2 ties, BM-5 tagged nodes, the SPC support
  -- with the planform/body outlines overlaid from the same geometry owners the
  exporter reads (`--no-outlines` to omit; wing/h-tail edges are draped at the
  beam chain's waterline, a stated picture convention). The exporter's refusal
  contract is kept verbatim: an `LraRefusal` prints its named datum and exits 2,
  never defaulting it. matplotlib joins the `dev` extra; smoke-tested on the
  conventional, T-tail and twin example projects (`tests/test_plot_lra_model.py`).
