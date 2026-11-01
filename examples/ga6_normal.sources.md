# `ga6_normal` — sources

The Appendix A GA-6 single of Ref 1 (McMaster's manual, `FAR23Loads_Code.pdf`):
every input is the manual's own, so the fixture is the oracle lock and carries
no grade column. The one input the manual never prints is below.

## Landing load factor (note 72 Q2, 2026-11-01)

`landing.airplane_load_factor` is **3.167**: the rounded design N McMaster's
LANDLOAD runs at (p230 reproduces at NLG 2.5 and at no other value, note 40
LF-9). It is kept although it sits below the fixture's own corrected energy
estimate, N = 3.764: p236's printed 3.0951 is the *gear* factor, and
N = NLG + L (14 CFR 23.473(e); approved deviation #401,
`docs/20_theory/02_approved_corrections.md`). The entered-below-computed
caution therefore fires on this fixture by design. Do not raise the N to
silence it: that would move p230–p233 off the oracle for no delivered benefit.
