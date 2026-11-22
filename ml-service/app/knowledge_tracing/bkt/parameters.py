"""
Parameter containers and validation utilities for Bayesian Knowledge Tracing.

Uses only Python stdlib + dataclasses.  No pandas / sklearn / torch.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

from .exceptions import InvalidParameterError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parameter bounds
# ---------------------------------------------------------------------------

@dataclass
class ParameterBounds:
    """Min / max bounds for each BKT parameter.

    Defaults keep all probabilities in (0, 1) with guess and slip
    capped at 0.5 to maintain identifiability.
    """

    p_init_min: float = 0.001
    p_init_max: float = 0.999
    p_learn_min: float = 0.001
    p_learn_max: float = 0.999
    p_guess_min: float = 0.001
    p_guess_max: float = 0.5
    p_slip_min: float = 0.001
    p_slip_max: float = 0.5

    # Aliases for naming compatibility
    @property
    def min_p_init(self) -> float: return self.p_init_min
    @property
    def max_p_init(self) -> float: return self.p_init_max
    @property
    def min_p_learn(self) -> float: return self.p_learn_min
    @property
    def max_p_learn(self) -> float: return self.p_learn_max
    @property
    def min_p_guess(self) -> float: return self.p_guess_min
    @property
    def max_p_guess(self) -> float: return self.p_guess_max
    @property
    def min_p_slip(self) -> float: return self.p_slip_min
    @property
    def max_p_slip(self) -> float: return self.p_slip_max

    # -- helpers -------------------------------------------------------------

    def clamp(self, value: float, lo: float, hi: float) -> float:
        """Clamp *value* into [lo, hi]."""
        return max(lo, min(hi, value))

    def to_dict(self) -> Dict[str, float]:
        return {
            "p_init_min": self.p_init_min,
            "p_init_max": self.p_init_max,
            "p_learn_min": self.p_learn_min,
            "p_learn_max": self.p_learn_max,
            "p_guess_min": self.p_guess_min,
            "p_guess_max": self.p_guess_max,
            "p_slip_min": self.p_slip_min,
            "p_slip_max": self.p_slip_max,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ParameterBounds":
        return cls(**{k: float(v) for k, v in d.items()})


# ---------------------------------------------------------------------------
# Single-skill BKT parameters
# ---------------------------------------------------------------------------

@dataclass
class BKTParameters:
    """Four canonical BKT parameters for one knowledge component.

    Attributes
    ----------
    p_init : float
        P(L₀) — probability the student already knows the skill before
        the first opportunity.
    p_learn : float
        P(T) — probability of transitioning from unlearned to learned
        on each opportunity.
    p_guess : float
        P(G) — probability of a correct response despite not knowing
        the skill.
    p_slip : float
        P(S) — probability of an incorrect response despite knowing
        the skill.
    """

    p_init: float = 0.2
    p_learn: float = 0.1
    p_guess: float = 0.25
    p_slip: float = 0.1

    def __post_init__(self) -> None:
        self.validate(strict=False)

    @classmethod
    def default_prior(cls) -> "BKTParameters":
        """Standard literature baseline prior for educational datasets."""
        return cls(p_init=0.20, p_learn=0.10, p_guess=0.20, p_slip=0.10)

    # -- validation ----------------------------------------------------------

    def validate(self, *, strict: bool = True) -> None:
        """Check parameter constraints; raise InvalidParameterError on
        violation.

        Parameters
        ----------
        strict : bool
            When *True* (default), additionally enforce
            ``p_guess < 0.5`` and ``p_slip < 0.5`` for identifiability.
        """
        for name in ("p_init", "p_learn", "p_guess", "p_slip"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)):
                raise InvalidParameterError(
                    f"{name} must be numeric, got {type(value).__name__}"
                )
            if math.isnan(value) or math.isinf(value):
                raise InvalidParameterError(
                    f"{name} is {value} (NaN/Inf not allowed)"
                )
            if not (0.0 <= value <= 1.0):
                raise InvalidParameterError(
                    f"{name}={value:.6f} is outside [0, 1]"
                )

        if self.p_guess + self.p_slip >= 1.0:
            raise InvalidParameterError(
                f"p_guess + p_slip = {self.p_guess + self.p_slip:.6f} >= 1 "
                "(model non-identifiable)"
            )

        if strict:
            if self.p_guess >= 0.5:
                raise InvalidParameterError(
                    f"p_guess={self.p_guess:.6f} >= 0.5 (strict mode)"
                )
            if self.p_slip >= 0.5:
                raise InvalidParameterError(
                    f"p_slip={self.p_slip:.6f} >= 0.5 (strict mode)"
                )

    # -- clamping ------------------------------------------------------------

    def clamp_to_bounds(
        self, bounds: Optional[ParameterBounds] = None
    ) -> "BKTParameters":
        """Return a *new* BKTParameters with values clamped to *bounds*.

        Any clamping that actually changes a value is logged at WARNING
        level so silent parameter coercion is visible in experiment logs.
        """
        if bounds is None:
            bounds = ParameterBounds()

        mapping = {
            "p_init": (bounds.p_init_min, bounds.p_init_max),
            "p_learn": (bounds.p_learn_min, bounds.p_learn_max),
            "p_guess": (bounds.p_guess_min, bounds.p_guess_max),
            "p_slip": (bounds.p_slip_min, bounds.p_slip_max),
        }

        clamped_values: Dict[str, float] = {}
        for name, (lo, hi) in mapping.items():
            original = getattr(self, name)
            clamped = bounds.clamp(original, lo, hi)
            if clamped != original:
                logger.warning(
                    "Clamped %s: %.6f -> %.6f  (bounds [%.4f, %.4f])",
                    name,
                    original,
                    clamped,
                    lo,
                    hi,
                )
            clamped_values[name] = clamped

        return BKTParameters(**clamped_values)

    # -- serialization -------------------------------------------------------

    def to_dict(self) -> Dict[str, float]:
        return {
            "p_init": self.p_init,
            "p_learn": self.p_learn,
            "p_guess": self.p_guess,
            "p_slip": self.p_slip,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BKTParameters":
        return cls(
            p_init=float(d["p_init"]),
            p_learn=float(d["p_learn"]),
            p_guess=float(d["p_guess"]),
            p_slip=float(d["p_slip"]),
        )

    # -- display -------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"BKTParameters(p_init={self.p_init:.4f}, "
            f"p_learn={self.p_learn:.4f}, "
            f"p_guess={self.p_guess:.4f}, "
            f"p_slip={self.p_slip:.4f})"
        )


def clamp_parameters_to_bounds(
    params: BKTParameters, bounds: Optional[ParameterBounds] = None
) -> Tuple[BKTParameters, list[str]]:
    """Clamps parameters to bounds and returns (clamped_params, warnings_list)."""
    if bounds is None:
        bounds = ParameterBounds()

    warnings = []
    p_init = bounds.clamp(params.p_init, bounds.p_init_min, bounds.p_init_max)
    if p_init != params.p_init:
        warnings.append(f"Clamped p_init: {params.p_init:.6f} -> {p_init:.6f}")

    p_learn = bounds.clamp(params.p_learn, bounds.p_learn_min, bounds.p_learn_max)
    if p_learn != params.p_learn:
        warnings.append(f"Clamped p_learn: {params.p_learn:.6f} -> {p_learn:.6f}")

    p_guess = bounds.clamp(params.p_guess, bounds.p_guess_min, bounds.p_guess_max)
    if p_guess != params.p_guess:
        warnings.append(f"Clamped p_guess: {params.p_guess:.6f} -> {p_guess:.6f}")

    p_slip = bounds.clamp(params.p_slip, bounds.p_slip_min, bounds.p_slip_max)
    if p_slip != params.p_slip:
        warnings.append(f"Clamped p_slip: {params.p_slip:.6f} -> {p_slip:.6f}")

    # Enforce p_guess + p_slip < 1.0
    if p_guess + p_slip >= 0.999:
        p_guess = min(p_guess, 0.490)
        p_slip = min(p_slip, 0.490)
        warnings.append(f"Adjusted guess/slip for identifiability: G={p_guess}, S={p_slip}")

    clamped = BKTParameters(p_init=p_init, p_learn=p_learn, p_guess=p_guess, p_slip=p_slip)
    return clamped, warnings


# ---------------------------------------------------------------------------
# Multi-skill parameter store
# ---------------------------------------------------------------------------

@dataclass
class SkillParameters:
    """Registry mapping *skill_id* → :class:`BKTParameters`.

    Skills that have been independently fitted are tracked in
    ``fitted_skills``; skills that fall back to the global prior are
    tracked in ``fallback_skills``.

    Attributes
    ----------
    fallback_params : BKTParameters
        Global prior used for any skill_id not in the fitted set.
    _skill_map : dict[int, BKTParameters]
        Independently fitted parameters keyed by skill_id.
    fitted_skills : set[int]
        Skill IDs with independent parameter estimates.
    fallback_skills : set[int]
        Skill IDs that have been queried but lack independent fits
        (served by *fallback_params*).
    """

    fallback_params: BKTParameters = field(default_factory=BKTParameters)
    _skill_map: Dict[int, BKTParameters] = field(default_factory=dict)
    fitted_skills: Set[int] = field(default_factory=set)
    fallback_skills: Set[int] = field(default_factory=set)

    # -- access --------------------------------------------------------------

    def set_params(self, skill_id: int | str, params: BKTParameters) -> None:
        """Register independently fitted parameters for *skill_id*."""
        sid = int(skill_id) if str(skill_id).isdigit() else str(skill_id)
        self._skill_map[sid] = params
        self.fitted_skills.add(sid)
        self.fallback_skills.discard(sid)

    def get_params(self, skill_id: int | str) -> BKTParameters:
        """Return skill-specific params if available, else fallback.

        Side-effect: records *skill_id* in either ``fitted_skills`` or
        ``fallback_skills`` for bookkeeping.
        """
        sid = int(skill_id) if str(skill_id).isdigit() else str(skill_id)
        if sid in self._skill_map:
            return self._skill_map[sid]

        # First time seeing this skill with no fit — record as fallback
        if sid not in self.fallback_skills:
            logger.debug(
                "skill_id=%s has no fitted params; using fallback", sid
            )
            self.fallback_skills.add(sid)
        return self.fallback_params

    def has_fitted(self, skill_id: int | str) -> bool:
        """Return True if *skill_id* has independently fitted params."""
        sid = int(skill_id) if str(skill_id).isdigit() else str(skill_id)
        return sid in self._skill_map

    @property
    def num_fitted(self) -> int:
        return len(self.fitted_skills)

    @property
    def num_fallback(self) -> int:
        return len(self.fallback_skills)

    # -- serialization -------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fallback_params": self.fallback_params.to_dict(),
            "skill_map": {
                str(sid): params.to_dict()
                for sid, params in self._skill_map.items()
            },
            "fitted_skills": sorted(self.fitted_skills),
            "fallback_skills": sorted(self.fallback_skills),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SkillParameters":
        fallback = BKTParameters.from_dict(d["fallback_params"])
        skill_map = {
            int(sid): BKTParameters.from_dict(pdict)
            for sid, pdict in d.get("skill_map", {}).items()
        }
        fitted = set(d.get("fitted_skills", []))
        fallback_set = set(d.get("fallback_skills", []))
        obj = cls(
            fallback_params=fallback,
            _skill_map=skill_map,
            fitted_skills=fitted,
            fallback_skills=fallback_set,
        )
        return obj

    # -- display -------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"SkillParameters(fitted={self.num_fitted}, "
            f"fallback={self.num_fallback}, "
            f"fallback_params={self.fallback_params!r})"
        )
