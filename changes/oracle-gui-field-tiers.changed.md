- **The oracle GUI renders every input field, in two marked tiers (#266, design note 57 D-57.2, tier M, 2026-09-13).**
  Until now a page of that front-end showed only `field_registry.oracle_input_paths()`, and the **83** sloads-only
  fields it dropped — thrust, the Part-25 speeds and Mach-margin basis, fuselage moment and lateral body aero, the
  fuselage 3-D stations, control-surface span and actuator geometry, the LRA beam mesh, and the rest — were enterable
  in no form at all. The charter said *the original suite's inputs and nothing this replication added*; the code said it
  by filtering a page definition, so a concept field's only way in was hand-edited JSON. Every registry path now
  renders. A field the original programs never asked for carries **✦** on its label and *"sloads extension, not an
  input of the original suite"* before its basis in its help, and the page says once what the mark means — so what the
  suite asked for is still legible at a glance, and leaving the marked fields unfilled asks exactly what the original
  programs asked.
- **The tier is marked on the field, not on a section, and the basis states a reason rather than a citation.**
  `field_registry.tier_of` is the one classifier (`SUITE` / `EXTENSION` / `JSON_ONLY`) and the mark is applied in
  `form._field_label` and `form._help` alone, so every shape a field renders in — scalar, tuple, curve, enum set and
  the grid columns a `data_editor` hides inside a canvas — inherits it. A section per page cannot work: a record holds
  fields of both tiers, and a second section over that record re-emits its row counter, its seed and its remove control
  under the same Streamlit key. The 63 extension rows' `basis` strings were rewritten in place — they cited the
  decision that added the field and said nothing about why sloads asks for it, which is the question this GUI's reader
  has just been handed. The `DATA_DICTIONARY.md` and the illustrated guide read the same strings and improve with them.
- **What no widget can address is declared with a reason, not dropped (note 57 gate 3).**
  Twenty fields sit on three records whose path crosses a `[]` hop — an engine's rotor set, a CG case's loading and its
  ballast — so addressing one means naming *which row*, which `form.record_at` cannot: it returns `None`, and
  `rows_at` returns a list detached from the project that would take an edit and drop it. `field_registry.JSON_ONLY_RECORDS`
  names all three with that reason; they are entered on the Project JSON Editor page (D-57.3, which is why that row was
  sequenced first). The guard re-derives the classification from the renderer's own addressing and fails both ways, so
  a record declared JSON-only that a widget could in fact take fails as loudly as the omission it replaced.
