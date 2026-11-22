"""
Sequential BKT Inference Engine
File: ml-service/app/knowledge_tracing/bkt/inference.py

Implements sequential, online BKT inference over student interaction sequences:
1. Predict next response prior to observing it
2. Update latent mastery state after observation
3. Support per-student and per-skill state isolation
4. Handle history initialization for longitudinal prediction
"""

from typing import List, Dict, Any, Tuple, Optional
from app.knowledge_tracing.bkt.parameters import BKTParameters, SkillParameters
from app.knowledge_tracing.bkt.model import update_mastery, predict_correct_probability


def predict_student_skill_sequence(
    interactions: List[Dict[str, Any]],
    params: BKTParameters,
    initial_mastery: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Processes an ordered interaction sequence for a single student on a single skill.
    
    Ensures strict online sequencing:
    - Prediction is computed FIRST from current mastery.
    - Mastery is updated AFTER observing the outcome.
    
    Returns a list of step dicts:
        {
            "step": int,
            "prediction": float,
            "actual": int,
            "mastery_before": float,
            "mastery_after": float
        }
    """
    results = []
    current_mastery = params.p_init if initial_mastery is None else initial_mastery

    for step, rec in enumerate(interactions, start=1):
        actual = int(rec["correct"])
        pred, next_mastery = update_mastery(
            p_mastery=current_mastery,
            observed_correct=actual,
            p_guess=params.p_guess,
            p_slip=params.p_slip,
            p_learn=params.p_learn,
        )

        results.append({
            "step": step,
            "prediction": pred,
            "actual": actual,
            "mastery_before": current_mastery,
            "mastery_after": next_mastery,
        })
        current_mastery = next_mastery

    return results


def predict_student_all_skills(
    interactions: List[Dict[str, Any]],
    skill_params: SkillParameters,
    initial_mastery: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """
    Processes an ordered interaction sequence for a single student across MULTIPLE skills.
    Maintains independent mastery state for each skill.
    
    Args:
        interactions: List of dicts, each with 'skill_id' and 'correct'
        skill_params: Registry of per-skill BKT parameters
        initial_mastery: Optional mapping of skill_id -> starting mastery probability
        
    Returns:
        List of dicts with predictions, actuals, and skill_ids
    """
    # Track student's mastery independently per skill
    mastery_states: Dict[str, float] = {}
    if initial_mastery:
        mastery_states.update({str(k): float(v) for k, v in initial_mastery.items()})

    results = []

    for step, rec in enumerate(interactions, start=1):
        skill_id = str(rec["skill_id"])
        params = skill_params.get_params(skill_id)

        # Initialize skill state if not present
        if skill_id not in mastery_states:
            mastery_states[skill_id] = params.p_init

        current_mastery = mastery_states[skill_id]
        actual = int(rec["correct"])

        pred, next_mastery = update_mastery(
            p_mastery=current_mastery,
            observed_correct=actual,
            p_guess=params.p_guess,
            p_slip=params.p_slip,
            p_learn=params.p_learn,
        )

        results.append({
            "step": step,
            "skill_id": skill_id,
            "prediction": pred,
            "actual": actual,
            "mastery_before": current_mastery,
            "mastery_after": next_mastery,
        })

        # Update mastery state for this skill
        mastery_states[skill_id] = next_mastery

    return results


def initialize_student_from_history(
    history: List[Dict[str, Any]],
    skill_params: SkillParameters,
    initial_mastery: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Runs sequential BKT state updates through a student's historical interactions
    to compute their current latent mastery for each practiced skill.
    
    No predictions are recorded; only final mastery states are returned.
    
    Returns:
        Dict mapping skill_id -> mastery_probability at end of history
    """
    mastery_states: Dict[str, float] = {}
    if initial_mastery:
        mastery_states.update({str(k): float(v) for k, v in initial_mastery.items()})

    for rec in history:
        skill_id = str(rec["skill_id"])
        params = skill_params.get_params(skill_id)

        if skill_id not in mastery_states:
            mastery_states[skill_id] = params.p_init

        current_mastery = mastery_states[skill_id]
        actual = int(rec["correct"])

        _, next_mastery = update_mastery(
            p_mastery=current_mastery,
            observed_correct=actual,
            p_guess=params.p_guess,
            p_slip=params.p_slip,
            p_learn=params.p_learn,
        )
        mastery_states[skill_id] = next_mastery

    return mastery_states
