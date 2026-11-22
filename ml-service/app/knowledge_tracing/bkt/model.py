"""
BKT Core Mathematical Operations
File: ml-service/app/knowledge_tracing/bkt/model.py

Implements pure mathematical functions for Bayesian Knowledge Tracing:
1. Prior prediction of correctness: P(C_t = 1)
2. Posterior mastery update given correct response: P(L_t | C_t = 1)
3. Posterior mastery update given incorrect response: P(L_t | C_t = 0)
4. Learning transition update: P(L_{t+1})
5. Complete step update cycle: predict -> observe -> posterior -> transition
"""

import math
from typing import Tuple
from app.knowledge_tracing.bkt.exceptions import NumericalInstabilityError, InvalidParameterError

EPSILON = 1e-15
CLAMP_MIN = 1e-10
CLAMP_MAX = 1.0 - 1e-10


def _check_finite(val: float, name: str) -> None:
    """Ensures value is numeric and finite."""
    if math.isnan(val) or math.isinf(val):
        raise NumericalInstabilityError(f"{name} produced non-finite value: {val}")


def predict_correct_probability(p_mastery: float, p_guess: float, p_slip: float) -> float:
    """
    Computes the prior probability that the student answers the next question correctly.
    
    Formula:
        P(C = 1) = p_mastery * (1 - p_slip) + (1 - p_mastery) * p_guess
    """
    _check_finite(p_mastery, "p_mastery")
    _check_finite(p_guess, "p_guess")
    _check_finite(p_slip, "p_slip")

    p = max(0.0, min(1.0, p_mastery))
    g = max(0.0, min(1.0, p_guess))
    s = max(0.0, min(1.0, p_slip))

    p_corr = p * (1.0 - s) + (1.0 - p) * g
    _check_finite(p_corr, "p_correct")
    return max(CLAMP_MIN, min(CLAMP_MAX, p_corr))


def posterior_learned_given_correct(p_mastery: float, p_guess: float, p_slip: float) -> float:
    """
    Computes the posterior probability of mastery after observing a correct response (C = 1).
    
    Formula:
        P(L | C=1) = [p_mastery * (1 - p_slip)] / [p_mastery * (1 - p_slip) + (1 - p_mastery) * p_guess]
    """
    _check_finite(p_mastery, "p_mastery")
    p = max(0.0, min(1.0, p_mastery))
    g = max(0.0, min(1.0, p_guess))
    s = max(0.0, min(1.0, p_slip))

    numerator = p * (1.0 - s)
    denominator = numerator + (1.0 - p) * g

    if denominator <= EPSILON:
        return CLAMP_MIN

    post = numerator / denominator
    _check_finite(post, "posterior_learned_given_correct")
    return max(CLAMP_MIN, min(CLAMP_MAX, post))


def posterior_learned_given_incorrect(p_mastery: float, p_guess: float, p_slip: float) -> float:
    """
    Computes the posterior probability of mastery after observing an incorrect response (C = 0).
    
    Formula:
        P(L | C=0) = [p_mastery * p_slip] / [p_mastery * p_slip + (1 - p_mastery) * (1 - p_guess)]
    """
    _check_finite(p_mastery, "p_mastery")
    p = max(0.0, min(1.0, p_mastery))
    g = max(0.0, min(1.0, p_guess))
    s = max(0.0, min(1.0, p_slip))

    numerator = p * s
    denominator = numerator + (1.0 - p) * (1.0 - g)

    if denominator <= EPSILON:
        return CLAMP_MIN

    post = numerator / denominator
    _check_finite(post, "posterior_learned_given_incorrect")
    return max(CLAMP_MIN, min(CLAMP_MAX, post))


def apply_learning_transition(p_posterior: float, p_learn: float) -> float:
    """
    Applies the learning transition to compute mastery for the next opportunity.
    
    Formula:
        P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) * p_learn
    """
    _check_finite(p_posterior, "p_posterior")
    _check_finite(p_learn, "p_learn")

    post = max(0.0, min(1.0, p_posterior))
    t = max(0.0, min(1.0, p_learn))

    p_next = post + (1.0 - post) * t
    _check_finite(p_next, "apply_learning_transition")
    return max(CLAMP_MIN, min(CLAMP_MAX, p_next))


def update_mastery(
    p_mastery: float,
    observed_correct: int,
    p_guess: float,
    p_slip: float,
    p_learn: float,
) -> Tuple[float, float]:
    """
    Executes one complete sequential BKT step:
    1. Calculate prediction: P(Correct) based on current p_mastery (PRIOR to observation)
    2. Compute posterior belief given observed correctness: P(L | C)
    3. Apply learning transition: P(L_next) = P(L | C) + (1 - P(L | C)) * p_learn
    
    Returns:
        (prediction_before_update, new_mastery_after_transition)
    """
    if observed_correct not in (0, 1):
        raise InvalidParameterError(f"observed_correct must be 0 or 1, got {observed_correct}")

    # 1. Prediction before update
    pred = predict_correct_probability(p_mastery, p_guess, p_slip)

    # 2. Evidence update (posterior)
    if observed_correct == 1:
        posterior = posterior_learned_given_correct(p_mastery, p_guess, p_slip)
    else:
        posterior = posterior_learned_given_incorrect(p_mastery, p_guess, p_slip)

    # 3. Transition forecast (next trial)
    new_mastery = apply_learning_transition(posterior, p_learn)

    return pred, new_mastery
