"""
BKT Model and Evaluation Artifact Serialization
File: ml-service/app/knowledge_tracing/bkt/serialization.py

Provides JSON serialization and deserialization for:
1. Fitted BKT model parameters and metadata
2. Evaluation reports and baseline comparisons
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from app.knowledge_tracing.bkt.parameters import SkillParameters, BKTParameters


def save_model_artifact(
    skill_params: SkillParameters,
    fit_results: Dict[str, Any],
    config: Dict[str, Any],
    output_path: str,
    protocol_name: str,
    dataset_identifier: str = "assistments_2009_2010",
) -> str:
    """
    Serializes a fitted BKT model to structured JSON.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    artifact = {
        "model_type": "bayesian_knowledge_tracing",
        "model_version": "1.0.0",
        "protocol": protocol_name,
        "dataset": dataset_identifier,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "summary": {
            "total_skills": fit_results.get("total_skills", 0),
            "fitted_skills_count": fit_results.get("fitted_count", 0),
            "fallback_skills_count": fit_results.get("fallback_count", 0),
            "global_fallback_params": fit_results.get("global_fallback", {}),
        },
        "per_skill_parameters": skill_params.to_dict(),
        "per_skill_fit_details": fit_results.get("per_skill_results", {}),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    return output_path


def load_model_artifact(filepath: str) -> Tuple[SkillParameters, Dict[str, Any]]:
    """
    Loads a saved BKT model artifact from JSON.
    Returns (SkillParameters, metadata_dict).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        artifact = json.load(f)

    param_dict = artifact["per_skill_parameters"]
    skill_params = SkillParameters.from_dict(param_dict)
    return skill_params, artifact


def save_evaluation_report(
    results: Dict[str, Any],
    output_path: str,
    protocol_name: str,
    model_name: str = "BKT",
) -> str:
    """
    Saves evaluation metrics report to JSON.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report = {
        "protocol": protocol_name,
        "primary_model": model_name,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return output_path
