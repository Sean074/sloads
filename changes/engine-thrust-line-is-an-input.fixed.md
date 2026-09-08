- **A counter-clockwise engine's sudden-stoppage torque is no longer a
  pound-foot short.** `ENGLOADS.BAS` prints `INT(-TORQSUDSTOP)` and BASIC's
  `INT` **floors** rather than truncating toward zero, so applying the rotation
  direction inside the flooring made `floor(-6824.6) = -6825` for one sense and
  `floor(+6824.6) = +6824` for the other — a difference in the rounding
  presented as a difference in the load. The oracle's own floored value is the
  clockwise one, and the opposite sense now publishes its exact negative. Caught
  by **G-53.1** on its first run; the printed Appendix B figure is untouched.
