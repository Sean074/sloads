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

from typing import Callable, List, Sequence

from .units import canonical, delivered_precision, format_value

__all__ = ["CROSS_CHECK_REL", "cross_check_disagrees", "shown_apart"]

#: The relative difference below which a typed override and its owner agree
#: for a cross-check warning: the oracle band (±0.1 %, Decision 3). A warning
#: on a 0.02 % aspect-ratio rounding carries the same weight as a real data
#: error, and trains the reader to dismiss both.
CROSS_CHECK_REL = 1e-3


def cross_check_disagrees(a: float, b: float,
                          shown: Callable[[float], str]) -> bool:
    """Whether an override cross-check warns that ``a`` and ``b`` disagree.

    The one owner of the comparison every override cross-check makes (#243):
    the two differ by more than :data:`CROSS_CHECK_REL` of the larger, **and**
    ``shown`` -- the formatter the warning prints them with -- writes them
    differently, so a warning can never print one number twice. A check with
    a stated reason for its own band (the wing-area and hinge-halves checks)
    keeps it; a check whose contract is *exact* equality prints its values
    through :func:`shown_apart` instead.
    """
    scale = max(abs(a), abs(b))
    if scale == 0.0 or abs(a - b) <= CROSS_CHECK_REL * scale:
        return False
    return shown(a) != shown(b)


def shown_apart(values: Sequence[float], units: str = "") -> List[str]:
    """``values`` printed at their row (:func:`format_value`), widened to the
    first common decimal count at which every two values that differ print
    differently (#243).

    For a check whose contract is exact equality -- a derived read of a single
    owner -- any difference is the defect, and a 0.4 lb drift printed at the
    pound row reads ``5000 lb ... 5000 lb``. Values that agree print at the
    row; one decimal count serves the whole sentence, so its numbers stay
    comparable.
    """
    exact = [canonical(float(v)) for v in values]

    def apart(texts: List[str]) -> bool:
        return all(texts[i] != texts[j]
                   for i in range(len(exact)) for j in range(i + 1, len(exact))
                   if exact[i] != exact[j])

    texts = [format_value(v, units) for v in values]
    if apart(texts):
        return texts
    first = (delivered_precision(units) or 0) + 1
    for decimals in range(first, first + 12):
        widened = [f"{v:.{decimals}f}" for v in exact]  # note 65 exempt: the owner
        if apart(widened):
            return widened
    return texts
