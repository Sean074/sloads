- **SELECT's accelerated-roll pick is no longer decided inside the balance's tolerance: roll points whose wing lift ties to 0.5 % go to the larger net root bending (#320, tier S, 2026-09-29).**
  SELECT took the `AC ROLL` point with the largest `LZW`, and the points it
  chose between differ by less than FLTLOADS balances to (0.04–0.41 % on the
  fixtures against 0.5 %), so any change to the iteration could move the slot
  and every digest that reads it. Points within `select.LZW_TIE_REL` (the
  balance's `NZ_BALANCE_TOL`, as a fraction of the lift) of the largest are now
  one lift, and the tie goes to the point whose net root `Mxx` — the variant row
  the slot would deliver, through the new `wing_variants.Assessor`, the one row
  builder the table also uses — is the largest; a project without a wing model
  keeps the largest `LZW` and its `ACRL` note says so. `ga6_normal`,
  `atr42_100` and `concept_heavy` deliver the same case (the GA6's Appendix A
  pick stays at sea level, 400,817 against 400,315 lb-in). `concept_regional_jet`
  moves from V-n case 180 (20,000 ft) to 40 (sea level), root `Mxx`
  5,486,079 → 5,527,521 lb-in (+0.76 %); `baron_58`'s mzfw aft row moves from
  case 80 (sea level) to 180 (10,000 ft), +32 lb-in (+0.006 %). Imperial digest:
  12 regional-jet channels and 7 Baron channels. From #321: `Δcm = −0.01·δ` is
  `constants.AILERON_DCM_PER_DEG`, the CAM 3.222 schedule is one function
  (`aileron.cam_3222_deflection`) that AILERON and the steady roll call with
  their own speeds, and a project with no category or a wing with `Iwxx = 0`
  is refused by name, no longer given the normal rule or a zero roll
  acceleration.
