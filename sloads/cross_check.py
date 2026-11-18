"""The override cross-check's one comparison and its one printing (#243).

A cross-check warning sets a typed value beside the owner it overrides or
copies. Before #243 each site compared at its own ``1e-9`` or ``1e-6`` and
printed at four significant figures or the unit's row, so a warning could fire
on rounding noise and print one number twice -- "This is 0.4356 but ... says
0.4356" -- which trains the reader to dismiss the warning that matters. The
form's override captions and ``validation``'s override checks call
:func:`cross_check_disagrees`; a check whose contract is exact equality prints
through :func:`shown_apart`. ``tests/test_cross_check.py`` refuses a bare
near-zero comparison feeding a warning in either.

The tolerance lives here, not in ``units``: every upper-case float there is a
conversion factor to the factor-literal gate.
"""

from __future__ import annotations

from typing import Callable

from .units import shown_apart  # the owner moved to units with #339; re-exported

__all__ = ["CROSS_CHECK_REL", "cross_check_disagrees", "shown_apart"]

#: The relative difference below which a typed override and its owner agree
#: for a cross-check warning: the oracle band (±0.1 %, Decision 3). A warning
#: on a 0.02 % aspect-ratio rounding carries the same weight as a real data
#: error, and trains the reader to dismiss both.
CROSS_CHECK_REL = 1e-3


def cross_check_disagrees(a: float, b: float,
                          shown: Callable[[float], str],
                          rel: float = CROSS_CHECK_REL) -> bool:
    """Whether an override cross-check warns that ``a`` and ``b`` disagree.

    The one owner of the comparison every override cross-check makes (#243):
    the two differ by more than ``rel`` of the larger -- :data:`CROSS_CHECK_REL`
    unless the field states its own band (``FieldEntry.band``, design note 69
    D-69.10) -- **and** ``shown`` -- the formatter the warning prints them with
    -- writes them differently, so a warning can never print one number twice.
    A check with a stated reason for its own band (the hinge-halves check)
    passes it here; a check whose contract is *exact* equality prints its
    values through :func:`shown_apart` instead.
    """
    scale = max(abs(a), abs(b))
    if scale == 0.0 or abs(a - b) <= rel * scale:
        return False
    return shown(a) != shown(b)
