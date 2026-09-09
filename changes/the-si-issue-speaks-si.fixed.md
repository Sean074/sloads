- **The SI issue carried Imperial residue a reader could not tell from carve-outs (#232, 2026-09-08 review R8, tier S, 2026-09-08).**
  The conversion owner was missing three rows — `ft^2`, `lb/ft^2` and `ft/s`
  passed through `convert_results` unconverted — so areas, wing loading,
  dynamic pressure and the sink rate wore Imperial labels beside converted
  neighbours; they now convert (`m²`, `kN/m²`, `m/s` — kN/m², not the
  design-pressure load label kPa, because the unit string is what
  `is_load_unit` discriminates on and wing loading must not grow a factor
  column). Table 7's second inertia channel, whose "(lb-in^2)" is baked into
  the frozen module's labels, printed four kg·m² values as lb-in^2; the SI
  issue prints one channel and its intro says why. §4.1's mass account quoted
  the calc's Imperial diagnostic ("5990.0 lb of items" beside a kg table) —
  `MassCheck` now carries its named parts and the report restates the account
  through the units owner; the carry-through stations go through the length
  channel. The OEI input table's IZZ converts, "per inch of span" is per unit
  span, and the limitations statement is built for the issue's own system, so
  an SI report no longer advertises `lbs-ULT` markers none of its files
  carry. Guard: a document-wide sweep of both examples' SI builds bans every
  Imperial token outside the stated carve-outs (altitude in ft beside KEAS,
  and 23.473(d) quoted in its own units), with the carve-outs stripped before
  the scan so they cannot shelter a residue.
