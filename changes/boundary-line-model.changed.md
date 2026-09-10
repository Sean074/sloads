- **The boundary-line model: entered lines derive the tail scalars (#25 step 2,
  note 54 D-54.1/D-54.8, tier L, schema v65, 2026-09-10).** The tail group's
  geometry is now entered as its **five boundary lines** — tail LE, tail TE and
  control LE (the `geometry.surfaces` polylines), the control's new
  `hinge_line` (v65), and the control's TE, which **is the parent's** along the
  interior of its span and therefore derives instead of being entered a second
  time (`tail_geometry.derived_control_trailing_edge`; an entered copy is held
  on the parent's line by `validate_control_trailing_edge`, hard on the tail
  groups — the wing controls join at the #260/D-54.6 fixture wave, whose
  estimated aileron polylines sit up to 9.4 in off their wing TE today). Every
  `[D]`-marked scalar of the two tail blocks (`HTAIL_BOUNDARY_DERIVED` /
  `VTAIL_BOUNDARY_DERIVED`, the #25 step 1 seam) **blank-derives** from the
  lines through `tail_geometry.boundary_derived_scalars`, consumed by
  `select.effective_tail_inputs`/`effective_vtail_inputs` and by
  `resolve_tail_planform` (note 36 OV-1: typed overrides, blank derives); the
  hinge halves SEFWDHL/SEAFTHL and SRFWDHL/SRAFTHL derive from the hinge
  line's area split (`control_hinge_areas`). A typed scalar stays
  authoritative — every Appendix A pin is untouched, `ga6_normal`'s
  elevator/rudder TEs are removed from the fixture because the derivation
  reproduces the printed tables byte-for-byte, and the Imperial digests did
  not move. Appendix A's printed h-tail/elevator/rudder figures are now
  **±0.1 % predictions** of the model (page-cited gate in
  `tests/test_tail_geometry.py`), and `validate_tail_planform` compares
  entered scalars only, retiring field-by-field as they stop being typed.
  `LayoutInput.htail_dihedral_deg` (D-54.8) is **declared, not modelled**: no
  load reads it (guarded) until note 51's dihedral guard and method spend it.
  The two tail input blocks are physically regrouped into the seam order with
  this bump — the regrouping step 1 deferred to the change that earned the
  version hop; the 64→65 migration is an identity.
