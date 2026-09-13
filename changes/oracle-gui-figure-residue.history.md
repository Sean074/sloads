- **The figure residue is ruled on rather than deleted (note 60 §9 amended
  2026-09-13, tier M, 2026-09-13)** — #267 ported sixteen of note 60 §1.1's
  twenty figures and #268 took the fleet comparison, leaving three that had no
  report producer. They were reported at #267's close instead of being allowed
  to disappear with `app/views/` at #270, and the owner ruled on all three in
  session. **Figure 6, item weight against fuselage station, ports here.** The
  reason it could not port at #267 was that `PlotData` had no way to express a
  cloud of named points; #268 added `Series.marker` and `Series.labels` for the
  fleet scatters, which made this figure a producer of about fifty lines —
  `content.item_station_plot_data`, one series per `MassItemKind` so that a
  heavy item at an extreme station can be read as the airplane or as a loading,
  named points on hover, and the oracle report's section 2.2 printing it beside
  the weight/CG envelope so it satisfies gate 10 like every other family. The
  shapes that tell the three kinds apart are stated in the existing
  `Series.style` channel as a pgfplots `mark=` token and honoured by both
  renderers, shape and not colour because §4.3 requires the printed figure to
  read in greyscale. **Figure 18, the wing + fuselage snapshot, retires
  superseded** by the two distributions #267 put on the pages that compute them.
  **Figure 19, imported against computed, is deferred with the capability it
  needs** — an inbound channel for an externally computed load distribution,
  filed in backlog band C — *additional analysis
  capability, design notes first* — and requiring a design note at AGREED first,
  because the hard part is the contract (columns, stations, units, and what a
  disagreement means) and not the overlay. The point of the row is that #270
  now deletes a page and not a capability nobody decided about.
