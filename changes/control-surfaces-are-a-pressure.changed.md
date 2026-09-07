- **A disagreement between two entered areas is stated, not resolved silently (note 44
  §19 OR-152, tier L, 2026-09-07).** The area a control surface's loads are run on and
  the area its entered outline encloses are two different inputs, and they disagree on
  three of the four examples: the aileron's drawn outline is 4 % under its analysis area
  on `baron_58`, 5 % over on `cessna_210` and **44 % under** on
  `concept_regional_jet`. The printed pressure is the module's, computed from the
  analysis area; past 2 % the section says so, in both directions, and leaves which one
  is the airplane to the configuration. A figure that had shaded the outline and divided
  the load by it would have printed a pressure 77 % high on the regional jet for a load
  nothing had changed.

- **A tab is drawn on its control surface, not on the fixed one (OR-149, OR-155).** A
  tab is cut into an elevator, a rudder or an aileron, so that is what the locator draws
  it on. No tab planform is entered anywhere in the schema, so the rectangle is the
  entered area at the entered station — chord `MACTAB`, span `STAB/MACTAB`, trailing
  edge on the host's — and the caption says so in as many words. A shape a reader could
  mistake for entered geometry is what this document must not draw silently.

- **The flap prints the set its pick came from (OR-156).** The critical flap load is the
  largest of four 23.345(a) conditions — `ga6_normal` prints 212 / 425 / 629 / 625 lb,
  and that the last two are within 1 % is content a reader is owed. Where no engine
  record carries take-off power and a propeller diameter the 23.457(b) slipstream case
  does not exist, and the section states that condition with its consequence rather than
  printing a quietly smaller number.
