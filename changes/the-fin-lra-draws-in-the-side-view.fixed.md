- **The three-view draws the fin's loads reference axis in the side view, not
  the top (tier S, 2026-09-08, found at the §3.5 pre-release walk).** The
  Configuration & Layout LRA overlay looped over every WINGGEOM surface and
  drew each into the Top view, treating the polyline's second coordinate as a
  butt line — but a vertical surface's second coordinate is a **waterline**
  (the GA6 fin root is `(240.912, 117.0)`), so the fin's and rudder's LRA
  rendered in the x-y plane, off past the wingtip. Worse latent on `baron_58`:
  its fin sets `symmetric=True`, which the loop would mirror about y=0,
  hanging a second fin below the airplane — the same trap the oracle report's
  planform figures already ruled on (the frame decides, never `symmetric`).
  The frame logic now has one owner, `configuration.lra_overlays` — vtail and
  rudder go to the Side view (X vs waterline), never mirrored; planform
  surfaces keep the Top view with the symmetric mirror — and the view consumes
  it. `sloads/modules/configuration.py` is frozen (note 44 OR-13): edited
  under an owner OR-15 admission granted 2026-09-08, scoped to one additive
  function and its import, recorded on the manifest hash in
  `tests/test_frozen_set.py`. Guarded
  (`test_configuration.py::test_lra_overlay_puts_a_waterline_span_surface_in_the_side_view`);
  proven both ways — forcing every surface into the Top frame fails the guard.
