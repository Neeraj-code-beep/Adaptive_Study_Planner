"""
Custom exception hierarchy for Bayesian Knowledge Tracing.

All BKT-specific exceptions inherit from BKTError so callers can
catch the entire family with a single ``except BKTError`` clause.
"""


class BKTError(Exception):
    """Base exception for all BKT-related errors."""


class InvalidParameterError(BKTError):
    """Raised when a BKT parameter value violates domain constraints.

    Examples
    --------
    - A probability outside [0, 1].
    - ``p_guess + p_slip >= 1`` (model is non-identifiable).
    - ``p_guess >= 0.5`` or ``p_slip >= 0.5`` when strict bounds are enforced.
    """


class InsufficientDataError(BKTError):
    """Raised when a skill has too few observations for reliable fitting.

    Typical triggers
    ----------------
    - Fewer than a configurable minimum number of student–skill sequences.
    - All observations for a skill share the same correctness value
      (no signal to separate guess / slip / learn).
    """


class ConvergenceError(BKTError):
    """Raised when the EM algorithm fails to converge within the
    allowed number of iterations.

    Attributes
    ----------
    iterations : int | None
        Number of iterations completed before the error was raised.
    delta : float | None
        Last observed change in log-likelihood (or parameter norm).
    """

    def __init__(
        self,
        message: str = "EM algorithm did not converge",
        *,
        iterations: int | None = None,
        delta: float | None = None,
    ) -> None:
        parts = [message]
        if iterations is not None:
            parts.append(f"iterations={iterations}")
        if delta is not None:
            parts.append(f"delta={delta:.6e}")
        super().__init__(" | ".join(parts))
        self.iterations = iterations
        self.delta = delta


class NumericalInstabilityError(BKTError):
    """Raised when a NaN or Inf is detected during BKT computation.

    This typically signals an underflow / overflow in the forward–backward
    algorithm and should be caught early to avoid silent corruption.
    """
