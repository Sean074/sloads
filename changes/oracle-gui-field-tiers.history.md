- **The oracle GUI renders every input path in two marked field tiers (#266, design note 57 D-57.2, tier M, 2026-09-13)** —
  the second row of band B5 and the one the convergence depends on: `app/views/` cannot retire while 83 fields are
  enterable only there. The barrier was one line — `page_groups` filtering on `oracle_input_paths()` — and the charter
  it enforced (note 32 OG-1/OG-2, *"the original suite's inputs, and nothing this replication added"*) had no way to
  distinguish *not asked for by the original programs* from *unreachable*. Both tiers render now; `field_registry.tier_of`
  classifies every path `SUITE`/`EXTENSION`/`JSON_ONLY`, and the extension tier is marked on the widget rather than
  gathered into a section, because a record holds fields of both tiers and a second section over one record emits its
  row counter, its seed and its remove control a second time under the same Streamlit key — D-57.2's *"marked section
  per page"* amended to marking that travels with the field. Marking is applied in `form._field_label` and `form._help`
  alone, the two functions every widget passes through, so a grid column is marked in the only place a grid column can
  be. `oracle_input_paths()` keeps its name and its callers but stops claiming to bound what the GUI writes: what it
  bounds — and what gate G5 was always really testing — is the tier, *with only these fields populated every
  oracle-page module still runs and every Appendix A oracle still passes*. Twenty fields on three records whose path
  crosses a `[]` hop stay JSON-editor-only, declared in `JSON_ONLY_RECORDS` with the reason, and note 57 gate 3's
  registry-walking guard re-derives that classification from the renderer's own addressing so it cannot be used to hide
  anything. Gates 4 and 5 (note 60 §5) assert here: every extension widget marked and stating its basis, and G-OR-74's
  screen sweep reading the tree at all — which is #239, closed the day before for this row.
