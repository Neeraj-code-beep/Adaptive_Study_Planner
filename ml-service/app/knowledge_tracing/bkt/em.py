"""
Expectation-Maximization (Baum-Welch) for Bayesian Knowledge Tracing
File: ml-service/app/knowledge_tracing/bkt/em.py

Implements EM parameter estimation for the 2-state HMM formulation of standard BKT:
- State 0: Unlearned (L=0)
- State 1: Learned (L=1)
- Observations: 0 (Incorrect), 1 (Correct)
- No forgetting: transition from 1 to 0 is strictly 0.0

Uses scaled forward-backward algorithm to prevent floating-point underflow.
Supports multiple independent student sequences per skill.
"""

import math
import logging
import random
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from app.knowledge_tracing.bkt.parameters import (
    BKTParameters,
    ParameterBounds,
    SkillParameters,
    clamp_parameters_to_bounds,
)
from app.knowledge_tracing.bkt.exceptions import NumericalInstabilityError, InsufficientDataError

logger = logging.getLogger(__name__)

EPSILON = 1e-15


def _build_hmm_matrices(params: BKTParameters) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Constructs initial state vector (pi), transition matrix (A), and emission matrix (B).
    
    pi: [P(unlearned), P(learned)] = [1 - L0, L0]
    A: [[1 - T, T], [0, 1]]  (absorbing learned state)
    B: [[1 - G, G], [S, 1 - S]]  (rows: states, cols: obs 0 and 1)
    """
    pi = np.array([1.0 - params.p_init, params.p_init], dtype=np.float64)
    A = np.array([
        [1.0 - params.p_learn, params.p_learn],
        [0.0, 1.0]
    ], dtype=np.float64)
    B = np.array([
        [1.0 - params.p_guess, params.p_guess],
        [params.p_slip, 1.0 - params.p_slip]
    ], dtype=np.float64)
    return pi, A, B


def scaled_forward(
    observations: List[int], pi: np.ndarray, A: np.ndarray, B: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes scaled forward probabilities alpha_hat and scale factors c.
    
    alpha_hat[t, s] = P(y_1..t, q_t=s) normalized so sum_s alpha_hat[t, s] = 1.0
    c[t] = 1.0 / sum_s unscaled_alpha[t, s]
    
    Returns:
        (alpha_hat, c)
    """
    T = len(observations)
    alpha_hat = np.zeros((T, 2), dtype=np.float64)
    c = np.zeros(T, dtype=np.float64)

    # Step t=0
    y0 = observations[0]
    unscaled_alpha_0 = pi * B[:, y0]
    denom_0 = np.sum(unscaled_alpha_0)
    if denom_0 < EPSILON:
        denom_0 = EPSILON
    c[0] = 1.0 / denom_0
    alpha_hat[0] = unscaled_alpha_0 * c[0]

    # Induction t=1..T-1
    for t in range(1, T):
        yt = observations[t]
        unscaled_alpha_t = np.dot(alpha_hat[t - 1], A) * B[:, yt]
        denom_t = np.sum(unscaled_alpha_t)
        if denom_t < EPSILON:
            denom_t = EPSILON
        c[t] = 1.0 / denom_t
        alpha_hat[t] = unscaled_alpha_t * c[t]

    return alpha_hat, c


def scaled_backward(
    observations: List[int], A: np.ndarray, B: np.ndarray, c: np.ndarray
) -> np.ndarray:
    """
    Computes scaled backward probabilities beta_hat using scale factors from forward pass.
    
    beta_hat[T-1, :] = c[T-1]
    beta_hat[t, i] = c[t] * sum_j A[i,j] * B[j, y_{t+1}] * beta_hat[t+1, j]
    """
    T = len(observations)
    beta_hat = np.zeros((T, 2), dtype=np.float64)
    beta_hat[T - 1] = c[T - 1]

    for t in range(T - 2, -1, -1):
        y_next = observations[t + 1]
        beta_hat[t] = c[t] * np.dot(A, B[:, y_next] * beta_hat[t + 1])

    return beta_hat


def e_step_single_sequence(
    observations: List[int], pi: np.ndarray, A: np.ndarray, B: np.ndarray
) -> Dict[str, Any]:
    """
    Executes E-step for a single student sequence.
    
    Computes:
    - gamma[t, i]: posterior probability of being in state i at step t
    - xi[t, i, j]: posterior probability of transition i -> j at step t
    - log_likelihood: -sum(log(c))
    """
    T = len(observations)
    alpha_hat, c = scaled_forward(observations, pi, A, B)
    beta_hat = scaled_backward(observations, A, B, c)

    # gamma[t, i] = (alpha_hat[t, i] * beta_hat[t, i]) / sum_j (alpha_hat[t, j] * beta_hat[t, j])
    gamma = np.zeros((T, 2), dtype=np.float64)
    for t in range(T):
        prod = alpha_hat[t] * beta_hat[t]
        s = np.sum(prod)
        if s > EPSILON:
            gamma[t] = prod / s
        else:
            gamma[t] = np.array([0.5, 0.5])

    # xi[t, i, j] = P(q_t = i, q_{t+1} = j | Y)
    xi = np.zeros((T - 1, 2, 2), dtype=np.float64) if T > 1 else np.zeros((0, 2, 2))
    for t in range(T - 1):
        y_next = observations[t + 1]
        num = np.outer(alpha_hat[t], B[:, y_next] * beta_hat[t + 1]) * A
        denom = np.sum(num)
        if denom > EPSILON:
            xi[t] = num / denom
        else:
            xi[t] = A / np.sum(A)

    log_likelihood = -np.sum(np.log(c + EPSILON))

    return {
        "gamma": gamma,
        "xi": xi,
        "log_likelihood": float(log_likelihood),
    }


def m_step(
    all_gamma: List[np.ndarray],
    all_xi: List[np.ndarray],
    all_observations: List[List[int]],
    bounds: ParameterBounds,
) -> Tuple[BKTParameters, List[str]]:
    """
    Executes M-step across all student sequences for a skill.
    
    Updates:
    - p_init: average gamma_0(learned) across students
    - p_learn: sum xi(0, 1) / sum gamma(0) across t < T
    - p_guess: sum_{y=1} gamma(0) / sum gamma(0) across all t
    - p_slip: sum_{y=0} gamma(1) / sum gamma(1) across all t
    """
    K = len(all_observations)
    if K == 0:
        return BKTParameters.default_prior(), ["No sequences provided to M-step"]

    # 1. Update p_init = sum_k gamma_1(state=1) / K
    init_learned_sum = sum(float(g[0, 1]) for g in all_gamma)
    new_p_init = init_learned_sum / K

    # 2. Update p_learn = sum_{k, t<T} xi(0, 1) / sum_{k, t<T} gamma(0)
    trans_01_sum = 0.0
    gamma_0_trans_sum = 0.0
    for k in range(K):
        T_k = len(all_observations[k])
        if T_k > 1:
            trans_01_sum += float(np.sum(all_xi[k][:, 0, 1]))
            gamma_0_trans_sum += float(np.sum(all_gamma[k][:-1, 0]))

    if gamma_0_trans_sum > EPSILON:
        new_p_learn = trans_01_sum / gamma_0_trans_sum
    else:
        new_p_learn = bounds.min_p_learn

    # 3. Update p_guess = sum_{k, t: y=1} gamma(0) / sum_{k, t} gamma(0)
    # 4. Update p_slip = sum_{k, t: y=0} gamma(1) / sum_{k, t} gamma(1)
    gamma_0_obs1 = 0.0
    gamma_0_total = 0.0
    gamma_1_obs0 = 0.0
    gamma_1_total = 0.0

    for k in range(K):
        obs = all_observations[k]
        g = all_gamma[k]
        for t, yt in enumerate(obs):
            g0 = float(g[t, 0])
            g1 = float(g[t, 1])

            gamma_0_total += g0
            gamma_1_total += g1

            if yt == 1:
                gamma_0_obs1 += g0
            else:
                gamma_1_obs0 += g1

    new_p_guess = (gamma_0_obs1 / gamma_0_total) if gamma_0_total > EPSILON else bounds.min_p_guess
    new_p_slip = (gamma_1_obs0 / gamma_1_total) if gamma_1_total > EPSILON else bounds.min_p_slip

    raw_params = BKTParameters(
        p_init=new_p_init,
        p_learn=new_p_learn,
        p_guess=new_p_guess,
        p_slip=new_p_slip,
    )

    clamped_params, warnings = clamp_parameters_to_bounds(raw_params, bounds)
    return clamped_params, warnings


def fit_skill_em_single_restart(
    student_sequences: List[List[int]],
    initial_params: BKTParameters,
    bounds: ParameterBounds,
    max_iterations: int = 100,
    convergence_tol: float = 1e-4,
) -> Dict[str, Any]:
    """Runs EM until convergence or max_iterations for a single initialization."""
    current_params = initial_params
    prev_ll = -float("inf")
    ll_history = []
    converged = False
    all_warnings = []

    for it in range(1, max_iterations + 1):
        pi, A, B = _build_hmm_matrices(current_params)

        all_gamma = []
        all_xi = []
        total_ll = 0.0

        for seq in student_sequences:
            estep = e_step_single_sequence(seq, pi, A, B)
            all_gamma.append(estep["gamma"])
            all_xi.append(estep["xi"])
            total_ll += estep["log_likelihood"]

        ll_history.append(total_ll)

        # Check convergence
        delta_ll = total_ll - prev_ll
        if it > 1 and abs(delta_ll) < convergence_tol:
            converged = True
            break
        prev_ll = total_ll

        # M-step
        current_params, warnings = m_step(all_gamma, all_xi, student_sequences, bounds)
        all_warnings.extend(warnings)

    return {
        "params": current_params,
        "log_likelihood": prev_ll if converged else total_ll,
        "ll_history": ll_history,
        "iterations": it,
        "converged": converged,
        "warnings": all_warnings,
    }


def fit_skill_parameters(
    student_sequences: List[List[int]],
    bounds: Optional[ParameterBounds] = None,
    init_params: Optional[BKTParameters] = None,
    max_iterations: int = 100,
    convergence_tol: float = 1e-4,
    n_restarts: int = 3,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Fits BKT parameters for a single skill using EM with multiple restarts.
    Selects the best fit based strictly on training log-likelihood.
    """
    if bounds is None:
        bounds = ParameterBounds()

    if not student_sequences or sum(len(s) for s in student_sequences) == 0:
        raise InsufficientDataError("No observations provided for skill fitting.")

    rng = random.Random(random_seed)
    best_result = None
    best_ll = -float("inf")
    best_restart_idx = 0

    for r_idx in range(n_restarts):
        if r_idx == 0 and init_params is not None:
            restart_init = init_params
        else:
            # Deterministic random initialization within bounds
            restart_init = BKTParameters(
                p_init=rng.uniform(bounds.min_p_init + 0.05, 0.50),
                p_learn=rng.uniform(bounds.min_p_learn + 0.02, 0.30),
                p_guess=rng.uniform(bounds.min_p_guess + 0.05, 0.35),
                p_slip=rng.uniform(bounds.min_p_slip + 0.02, 0.20),
            )

        res = fit_skill_em_single_restart(
            student_sequences=student_sequences,
            initial_params=restart_init,
            bounds=bounds,
            max_iterations=max_iterations,
            convergence_tol=convergence_tol,
        )

        if res["log_likelihood"] > best_ll:
            best_ll = res["log_likelihood"]
            best_result = res
            best_restart_idx = r_idx

    best_result["best_restart"] = best_restart_idx
    best_result["n_restarts"] = n_restarts
    return best_result


def fit_all_skills(
    skill_sequences: Dict[str, List[List[int]]],
    min_sequences: int = 5,
    min_total_observations: int = 50,
    bounds: Optional[ParameterBounds] = None,
    max_iterations: int = 100,
    convergence_tol: float = 1e-4,
    n_restarts: int = 3,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Fits independent BKT parameters for all skills in skill_sequences.
    
    Skills that do not meet minimum observation thresholds receive fallback parameters
    fitted on the pooled observations of all training sequences.
    
    Returns:
        Dict with 'skill_params', 'per_skill_results', 'fitted_count', 'fallback_count'
    """
    if bounds is None:
        bounds = ParameterBounds()

    # 1. Fit pooled global fallback on all sequences
    logger.info("Fitting global pooled fallback parameters...")
    all_seqs_pooled = []
    for seqs in skill_sequences.values():
        all_seqs_pooled.extend(seqs)

    if all_seqs_pooled:
        fallback_fit = fit_skill_parameters(
            student_sequences=all_seqs_pooled[:500],  # Sample representative subset for speed
            bounds=bounds,
            init_params=BKTParameters.default_prior(),
            max_iterations=50,
            convergence_tol=convergence_tol,
            n_restarts=1,
            random_seed=random_seed,
        )
        global_fallback = fallback_fit["params"]
    else:
        global_fallback = BKTParameters.default_prior()

    skill_params = SkillParameters(fallback_params=global_fallback)
    per_skill_results = {}
    fitted_count = 0
    fallback_count = 0

    total_skills = len(skill_sequences)
    logger.info("Fitting BKT parameters across %d skills...", total_skills)

    for i, (skill_id, seqs) in enumerate(skill_sequences.items(), start=1):
        total_obs = sum(len(s) for s in seqs)
        n_seqs = len(seqs)

        if n_seqs >= min_sequences and total_obs >= min_total_observations:
            try:
                fit_res = fit_skill_parameters(
                    student_sequences=seqs,
                    bounds=bounds,
                    init_params=global_fallback,
                    max_iterations=max_iterations,
                    convergence_tol=convergence_tol,
                    n_restarts=n_restarts,
                    random_seed=random_seed + i,
                )
                skill_params.set_params(skill_id, fit_res["params"])
                per_skill_results[skill_id] = {
                    "status": "fitted",
                    "total_observations": total_obs,
                    "student_sequences": n_seqs,
                    "params": fit_res["params"].to_dict(),
                    "log_likelihood": fit_res["log_likelihood"],
                    "iterations": fit_res["iterations"],
                    "converged": fit_res["converged"],
                    "warnings": fit_res["warnings"][:5],  # Keep top warnings
                }
                fitted_count += 1
            except Exception as e:
                logger.warning("Fit failed for skill %s: %s; using fallback", skill_id, e)
                per_skill_results[skill_id] = {
                    "status": "fallback",
                    "reason": str(e),
                    "total_observations": total_obs,
                    "student_sequences": n_seqs,
                    "params": global_fallback.to_dict(),
                }
                skill_params.fallback_skills.add(str(skill_id))
                fallback_count += 1
        else:
            per_skill_results[skill_id] = {
                "status": "fallback",
                "reason": f"Below thresholds (n_seqs={n_seqs} < {min_sequences} or total_obs={total_obs} < {min_total_observations})",
                "total_observations": total_obs,
                "student_sequences": n_seqs,
                "params": global_fallback.to_dict(),
            }
            skill_params.fallback_skills.add(str(skill_id))
            fallback_count += 1

    return {
        "skill_params": skill_params,
        "per_skill_results": per_skill_results,
        "global_fallback": global_fallback.to_dict(),
        "fitted_count": fitted_count,
        "fallback_count": fallback_count,
        "total_skills": total_skills,
    }
