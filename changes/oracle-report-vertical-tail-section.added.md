- **The oracle report states the vertical tail's loads (note 44 §17, tier L, 2026-09-07).**
  Section 6, *Vertical Tail and Rudder Loads*, in five subsections mirroring section 5 —
  the surface and its loads reference axis, the four design conditions of 14 CFR
  23.441(a)(1)/(2)/(3) and 23.443(b) with the method that selected them, the critical
  loads with the rudder load on every one of them, the chordwise pressure distribution,
  and the spanwise loads at the root — plus **Appendix E**, the vertical tail's
  applied-load deck (`Case | GID | X | Y | Z | Fy | SF`) in airplane axes from the same
  mapper the exported deck uses. One builder produces sections 5 and 6 with the surface
  as a parameter, so the two are the same analysis read twice rather than two copies
  kept in step. Every load is LIMIT and states the 14 CFR 23.303 factor it has not been
  multiplied by.

- **The report withholds the vertical tail's spanwise loads on a non-conventional tail
  (note 44 OR-133/OR-134/OR-133a, tier L, 2026-09-07).** sloads models the empennage as
  a conventional tail; on a T-tail, cruciform or V-tail the fin is additionally the
  horizontal tail's supporting structure in the sense of 23.427(a), and that path is not
  modelled. Section 6.5 and Appendix E render the stated state under **"Not supported"**
  and no table; 6.2's condition register and 6.3's summary state that the set is short a
  condition and **name it**; 6.1's loads-reference-axis stations still print, because
  they are geometry, with the reason in the table's own note. Section 5, 6.3's totals,
  6.4 and Appendix D are unaffected, gated by diff. **The withholding is the report's
  only** — the calc, the decks, the CLI and the GUI are untouched, so the balanced
  deck's lateral cases still assemble on all three shipped T-tails.
