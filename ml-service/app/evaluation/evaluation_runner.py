"""
BKT Evaluation Runner
File: ml-service/app/evaluation/evaluation_runner.py

Executes end-to-end evaluation for:
- Protocol A: Unseen-Student Generalization
- Protocol B: Known-Student Future Prediction (Leakage-Safe Cohort Design)

Evaluates BKT against three non-KT baselines:
1. Majority Class
2. Global Correctness Rate
3. Per-Skill Correctness Rate
"""

import os
import sys
import csv
import json
import random
import time
from collections import defaultdict
from typing import List, Dict, Any, Tuple

# Ensure ml-service root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
ML_SERVICE_DIR = os.path.dirname(APP_DIR)
if ML_SERVICE_DIR not in sys.path:
    sys.path.insert(0, ML_SERVICE_DIR)

from app.knowledge_tracing.bkt.parameters import BKTParameters, ParameterBounds, SkillParameters
from app.knowledge_tracing.bkt.em import fit_all_skills
from app.knowledge_tracing.bkt.inference import (
    predict_student_all_skills,
    initialize_student_from_history,
)
from app.knowledge_tracing.bkt.serialization import save_model_artifact, save_evaluation_report
from app.evaluation.probability_metrics import compute_all_metrics
from app.evaluation.baselines import fit_baselines


def load_csv_records(filepath: str) -> List[Dict[str, Any]]:
    """Loads CSV into list of dicts with properly cast fields."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "student_id": row["student_id"],
                "question_id": row.get("question_id", ""),
                "skill_id": row["skill_id"],
                "skill_name": row.get("skill_name", ""),
                "correct": int(row["correct"]),
                "order_id": int(row["order_id"]) if row.get("order_id", "").isdigit() else row.get("order_id", ""),
                "interaction_index": int(row["interaction_index"]) if row.get("interaction_index", "").isdigit() else 1,
            })
    return records


def group_by_student(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Groups records by student_id and sorts chronologically."""
    groups = defaultdict(list)
    for r in records:
        groups[r["student_id"]].append(r)
    for sid in groups:
        groups[sid].sort(key=lambda x: (x["order_id"], str(x["skill_id"]), str(x.get("question_id", ""))))
    return dict(groups)


def extract_skill_sequences(records: List[Dict[str, Any]]) -> Dict[str, List[List[int]]]:
    """
    Extracts per-skill lists of independent student observation sequences.
    
    Structure:
        {skill_id: [[s1_obs1, s1_obs2, ...], [s2_obs1, s2_obs2, ...], ...]}
        
    CRITICAL: Sequences from different students are NEVER concatenated.
    """
    student_skill = defaultdict(list)
    for r in records:
        student_skill[(r["student_id"], str(r["skill_id"]))].append(r)

    skill_sequences = defaultdict(list)
    for (sid, skid), recs in student_skill.items():
        recs.sort(key=lambda x: x["order_id"])
        seq = [r["correct"] for r in recs]
        if seq:
            skill_sequences[skid].append(seq)

    return dict(skill_sequences)


def run_protocol_a(
    splits_dir: str,
    output_dir: str,
    models_dir: str,
    random_seed: int = 42,
    max_em_iterations: int = 100,
    convergence_tol: float = 1e-4,
    n_restarts: int = 3,
) -> Dict[str, Any]:
    """
    Protocol A: Unseen-Student Generalization.
    
    1. Fits BKT parameters on training students only.
    2. Uses validation students for diagnostics/tuning.
    3. Evaluates held-out test students sequentially (online).
    """
    print("\n" + "=" * 75)
    print("RUNNING PROTOCOL A: UNSEEN-STUDENT GENERALIZATION")
    print("=" * 75)

    train_path = os.path.join(splits_dir, "unseen_students", "train.csv")
    val_path = os.path.join(splits_dir, "unseen_students", "validation.csv")
    test_path = os.path.join(splits_dir, "unseen_students", "test.csv")

    train_records = load_csv_records(train_path)
    val_records = load_csv_records(val_path)
    test_records = load_csv_records(test_path)

    print(f"Loaded Train: {len(train_records):,} interactions")
    print(f"Loaded Validation: {len(val_records):,} interactions")
    print(f"Loaded Test: {len(test_records):,} interactions")

    # Extract sequences for EM fitting (TRAINING DATA ONLY)
    print("\nExtracting per-skill student sequences from training data...")
    train_skill_seqs = extract_skill_sequences(train_records)
    print(f"Found {len(train_skill_seqs)} skills with training sequences.")

    # Fit BKT parameters
    print(f"\nFitting BKT parameters via EM (max_iter={max_em_iterations}, restarts={n_restarts})...")
    start_t = time.time()
    fit_result = fit_all_skills(
        skill_sequences=train_skill_seqs,
        min_sequences=5,
        min_total_observations=50,
        max_iterations=max_em_iterations,
        convergence_tol=convergence_tol,
        n_restarts=n_restarts,
        random_seed=random_seed,
    )
    fit_duration = time.time() - start_t
    print(f"EM fitting complete in {fit_duration:.2f}s.")
    print(f"  Fitted skills: {fit_result['fitted_count']}")
    print(f"  Fallback skills: {fit_result['fallback_count']}")

    skill_params: SkillParameters = fit_result["skill_params"]

    # Save model artifact
    model_artifact_path = os.path.join(models_dir, "bkt_protocol_a.json")
    save_model_artifact(
        skill_params=skill_params,
        fit_results=fit_result,
        config={
            "max_iterations": max_em_iterations,
            "convergence_tol": convergence_tol,
            "n_restarts": n_restarts,
            "random_seed": random_seed,
            "fit_duration_seconds": round(fit_duration, 2),
        },
        output_path=model_artifact_path,
        protocol_name="Protocol A: Unseen-Student Generalization",
    )
    print(f"Saved BKT Protocol A model artifact: {model_artifact_path}")

    # Fit baselines on training data only
    print("\nFitting baselines on training data...")
    baselines = fit_baselines(train_records)

    eval_results = {}

    for split_name, split_records in [("validation", val_records), ("test", test_records)]:
        print(f"\nEvaluating on {split_name} ({len(split_records):,} records)...")

        # BKT sequential online prediction
        student_groups = group_by_student(split_records)
        bkt_preds = []
        actuals = []

        for sid, seq in student_groups.items():
            step_results = predict_student_all_skills(seq, skill_params)
            for r in step_results:
                bkt_preds.append(r["prediction"])
                actuals.append(r["actual"])

        # Compute BKT metrics
        bkt_metrics = compute_all_metrics(actuals, bkt_preds)

        # Baseline predictions on same records
        maj_preds = baselines["majority_class"].predict(len(split_records))
        maj_metrics = compute_all_metrics(actuals, maj_preds)

        maj_hard_preds = baselines["majority_class_hard"].predict(len(split_records))
        maj_hard_metrics = compute_all_metrics(actuals, maj_hard_preds)

        glob_preds = baselines["global_correctness_rate"].predict(len(split_records))
        glob_metrics = compute_all_metrics(actuals, glob_preds)

        skill_preds = baselines["per_skill_rate"].predict_sequence(split_records)
        skill_metrics = compute_all_metrics(actuals, skill_preds)

        eval_results[split_name] = {
            "bkt": bkt_metrics,
            "majority_class": maj_metrics,
            "majority_class_hard": maj_hard_metrics,
            "global_correctness_rate": glob_metrics,
            "per_skill_rate": skill_metrics,
        }

        print(f"  --- {split_name.upper()} RESULTS ---")
        print(f"  BKT:              AUC={bkt_metrics['roc_auc']}, ECE={bkt_metrics['ece']}, LogLoss={bkt_metrics['log_loss']}, Brier={bkt_metrics['brier_score']}, Acc={bkt_metrics['accuracy']}")
        print(f"  Per-Skill Rate:   AUC={skill_metrics['roc_auc']}, ECE={skill_metrics['ece']}, LogLoss={skill_metrics['log_loss']}, Brier={skill_metrics['brier_score']}, Acc={skill_metrics['accuracy']}")
        print(f"  Global Rate:      AUC={glob_metrics['roc_auc']}, ECE={glob_metrics['ece']}, LogLoss={glob_metrics['log_loss']}, Brier={glob_metrics['brier_score']}, Acc={glob_metrics['accuracy']}")
        print(f"  Majority (Smoothed): AUC={maj_metrics['roc_auc']}, ECE={maj_metrics['ece']}, LogLoss={maj_metrics['log_loss']}, Brier={maj_metrics['brier_score']}, Acc={maj_metrics['accuracy']}")
        print(f"  Majority (Hard):     AUC={maj_hard_metrics['roc_auc']}, ECE={maj_hard_metrics['ece']}, LogLoss={maj_hard_metrics['log_loss']}, Brier={maj_hard_metrics['brier_score']}, Acc={maj_hard_metrics['accuracy']}")

    # Save evaluation report
    report_path = os.path.join(output_dir, "protocol_a_results.json")
    save_evaluation_report(eval_results, report_path, "Protocol A: Unseen-Student Generalization", "BKT")
    print(f"\nSaved Protocol A evaluation report: {report_path}")

    return {
        "results": eval_results,
        "fit_summary": {
            "fitted_count": fit_result["fitted_count"],
            "fallback_count": fit_result["fallback_count"],
            "fit_duration_seconds": round(fit_duration, 2),
        },
    }


def run_protocol_b(
    cleaned_data_path: str,
    output_dir: str,
    models_dir: str,
    random_seed: int = 42,
    train_student_ratio: float = 0.70,
    history_ratio: float = 0.80,
    max_em_iterations: int = 100,
    convergence_tol: float = 1e-4,
    n_restarts: int = 3,
) -> Dict[str, Any]:
    """
    Protocol B: Known-Student Future Prediction (LEAKAGE-SAFE DESIGN).
    
    Leakage-Safe Cohort Partitioning:
    1. Students are partitioned into:
       - Parameter-Training Cohort (70%): Used ONLY to fit global BKT & baseline parameters.
       - Evaluation Cohort (30%): Disjoint students evaluated on future responses.
    2. For each student in the Evaluation Cohort:
       - Historical prefix (80%) is used ONLY to initialize student latent mastery.
       - Future suffix (20%) is predicted sequentially (predict before update).
    3. Guarantees:
       - Parameter-training students never have their future evaluated.
       - Evaluation students' data is never used to fit global parameters.
       - Future interactions are never seen during student state initialization.
    """
    print("\n" + "=" * 75)
    print("RUNNING PROTOCOL B: KNOWN-STUDENT FUTURE PREDICTION (LEAKAGE-SAFE)")
    print("=" * 75)

    all_records = load_csv_records(cleaned_data_path)
    print(f"Loaded full cleaned dataset: {len(all_records):,} interactions.")

    student_groups = group_by_student(all_records)
    all_students = sorted(student_groups.keys())
    print(f"Total unique students: {len(all_students):,}")

    # Partition students deterministically into disjoint cohorts
    rng = random.Random(random_seed)
    shuffled_students = list(all_students)
    rng.shuffle(shuffled_students)

    split_point = int(len(shuffled_students) * train_student_ratio)
    param_train_students = set(shuffled_students[:split_point])
    eval_cohort_students = set(shuffled_students[split_point:])

    # Strict isolation assertion
    assert len(param_train_students & eval_cohort_students) == 0, "Student cohort leakage detected!"

    print(f"Parameter-Training Cohort: {len(param_train_students):,} students")
    print(f"Evaluation Cohort:         {len(eval_cohort_students):,} students")

    # Collect parameter training records
    param_train_records = []
    for sid in param_train_students:
        param_train_records.extend(student_groups[sid])

    print(f"Parameter-Training records: {len(param_train_records):,} interactions")

    # Fit BKT on Parameter-Training Cohort only
    param_skill_seqs = extract_skill_sequences(param_train_records)
    print(f"\nFitting BKT on Parameter-Training Cohort ({len(param_skill_seqs)} skills)...")
    start_t = time.time()
    fit_result = fit_all_skills(
        skill_sequences=param_skill_seqs,
        min_sequences=5,
        min_total_observations=50,
        max_iterations=max_em_iterations,
        convergence_tol=convergence_tol,
        n_restarts=n_restarts,
        random_seed=random_seed,
    )
    fit_duration = time.time() - start_t
    print(f"EM fitting complete in {fit_duration:.2f}s.")
    print(f"  Fitted skills: {fit_result['fitted_count']}")
    print(f"  Fallback skills: {fit_result['fallback_count']}")

    skill_params: SkillParameters = fit_result["skill_params"]

    # Save Protocol B model artifact
    model_artifact_path = os.path.join(models_dir, "bkt_protocol_b.json")
    save_model_artifact(
        skill_params=skill_params,
        fit_results=fit_result,
        config={
            "max_iterations": max_em_iterations,
            "convergence_tol": convergence_tol,
            "n_restarts": n_restarts,
            "random_seed": random_seed,
            "train_student_ratio": train_student_ratio,
            "history_ratio": history_ratio,
            "fit_duration_seconds": round(fit_duration, 2),
        },
        output_path=model_artifact_path,
        protocol_name="Protocol B: Known-Student Future Prediction",
    )
    print(f"Saved BKT Protocol B model artifact: {model_artifact_path}")

    # Fit baselines on Parameter-Training Cohort records only
    baselines = fit_baselines(param_train_records)

    # Process Evaluation Cohort students
    print("\nProcessing Evaluation Cohort students (history initialization + future prediction)...")
    bkt_future_preds = []
    future_actuals = []
    future_records_list = []

    total_eval_history_records = 0
    total_eval_future_records = 0
    eligible_eval_students = 0

    for sid in sorted(eval_cohort_students):
        seq = student_groups[sid]
        if len(seq) < 2:
            continue

        split_idx = max(1, int(len(seq) * history_ratio))
        split_idx = min(split_idx, len(seq) - 1)  # Ensure at least 1 future record

        history_part = seq[:split_idx]
        future_part = seq[split_idx:]

        if not future_part:
            continue

        eligible_eval_students += 1
        total_eval_history_records += len(history_part)
        total_eval_future_records += len(future_part)
        future_records_list.extend(future_part)

        # 1. Initialize mastery from history
        student_mastery = initialize_student_from_history(history_part, skill_params)

        # 2. Predict future sequentially (predict before update)
        step_results = predict_student_all_skills(
            future_part, skill_params, initial_mastery=student_mastery
        )

        for r in step_results:
            bkt_future_preds.append(r["prediction"])
            future_actuals.append(r["actual"])

    print(f"Evaluation cohort statistics:")
    print(f"  Eligible students:       {eligible_eval_students:,}")
    print(f"  History interactions:    {total_eval_history_records:,}")
    print(f"  Future test evaluations: {total_eval_future_records:,}")

    # Compute metrics for BKT
    bkt_metrics = compute_all_metrics(future_actuals, bkt_future_preds)

    # Baseline predictions on identical future records
    maj_preds = baselines["majority_class"].predict(len(future_actuals))
    maj_metrics = compute_all_metrics(future_actuals, maj_preds)

    maj_hard_preds = baselines["majority_class_hard"].predict(len(future_actuals))
    maj_hard_metrics = compute_all_metrics(future_actuals, maj_hard_preds)

    glob_preds = baselines["global_correctness_rate"].predict(len(future_actuals))
    glob_metrics = compute_all_metrics(future_actuals, glob_preds)

    skill_preds = baselines["per_skill_rate"].predict_sequence(future_records_list)
    skill_metrics = compute_all_metrics(future_actuals, skill_preds)

    eval_results = {
        "future_test": {
            "bkt": bkt_metrics,
            "majority_class": maj_metrics,
            "majority_class_hard": maj_hard_metrics,
            "global_correctness_rate": glob_metrics,
            "per_skill_rate": skill_metrics,
        }
    }

    print("\n--- PROTOCOL B FUTURE TEST RESULTS ---")
    print(f"BKT:                 AUC={bkt_metrics['roc_auc']}, ECE={bkt_metrics['ece']}, LogLoss={bkt_metrics['log_loss']}, Brier={bkt_metrics['brier_score']}, Acc={bkt_metrics['accuracy']}")
    print(f"Per-Skill Rate:      AUC={skill_metrics['roc_auc']}, ECE={skill_metrics['ece']}, LogLoss={skill_metrics['log_loss']}, Brier={skill_metrics['brier_score']}, Acc={skill_metrics['accuracy']}")
    print(f"Global Rate:         AUC={glob_metrics['roc_auc']}, ECE={glob_metrics['ece']}, LogLoss={glob_metrics['log_loss']}, Brier={glob_metrics['brier_score']}, Acc={glob_metrics['accuracy']}")
    print(f"Majority (Smoothed): AUC={maj_metrics['roc_auc']}, ECE={maj_metrics['ece']}, LogLoss={maj_metrics['log_loss']}, Brier={maj_metrics['brier_score']}, Acc={maj_metrics['accuracy']}")
    print(f"Majority (Hard):     AUC={maj_hard_metrics['roc_auc']}, ECE={maj_hard_metrics['ece']}, LogLoss={maj_hard_metrics['log_loss']}, Brier={maj_hard_metrics['brier_score']}, Acc={maj_hard_metrics['accuracy']}")

    # Save cohort metadata
    cohort_metadata = {
        "protocol": "Protocol B: Known-Student Future Prediction (Leakage-Safe)",
        "random_seed": random_seed,
        "train_student_ratio": train_student_ratio,
        "history_ratio": history_ratio,
        "total_unique_students": len(all_students),
        "param_train_student_count": len(param_train_students),
        "eval_cohort_student_count": len(eval_cohort_students),
        "eligible_eval_students": eligible_eval_students,
        "param_train_interactions": len(param_train_records),
        "eval_history_interactions": total_eval_history_records,
        "eval_future_interactions": total_eval_future_records,
        "param_train_student_ids": sorted(list(param_train_students)),
        "eval_cohort_student_ids": sorted(list(eval_cohort_students)),
        "leakage_verification": {
            "zero_student_overlap": len(param_train_students & eval_cohort_students) == 0,
            "eval_history_isolated_from_fitting": True,
            "eval_future_isolated_from_initialization": True,
        },
    }

    cohort_path = os.path.join(output_dir, "protocol_b_cohort_metadata.json")
    with open(cohort_path, "w", encoding="utf-8") as f:
        json.dump(cohort_metadata, f, indent=2)
    print(f"\nSaved Protocol B cohort metadata: {cohort_path}")

    report_path = os.path.join(output_dir, "protocol_b_results.json")
    save_evaluation_report(eval_results, report_path, "Protocol B: Known-Student Future Prediction", "BKT")
    print(f"Saved Protocol B evaluation report: {report_path}")

    return {
        "results": eval_results,
        "cohort_metadata": cohort_metadata,
        "fit_summary": {
            "fitted_count": fit_result["fitted_count"],
            "fallback_count": fit_result["fallback_count"],
            "fit_duration_seconds": round(fit_duration, 2),
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BKT Evaluation Runner")
    parser.add_argument("--protocol", choices=["a", "b", "both"], default="both")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-iter", type=int, default=100)
    parser.add_argument("--restarts", type=int, default=3)
    parser.add_argument("--tol", type=float, default=1e-4)

    args = parser.parse_args()

    splits_d = os.path.join(ML_SERVICE_DIR, "data", "splits")
    cleaned_f = os.path.join(ML_SERVICE_DIR, "data", "processed", "assistments_cleaned.csv")
    models_d = os.path.join(ML_SERVICE_DIR, "models", "artifacts")
    reports_d = os.path.join(ML_SERVICE_DIR, "data", "reports", "bkt")

    os.makedirs(models_d, exist_ok=True)
    os.makedirs(reports_d, exist_ok=True)

    if args.protocol in ("a", "both"):
        run_protocol_a(
            splits_dir=splits_d,
            output_dir=reports_d,
            models_dir=models_d,
            random_seed=args.seed,
            max_em_iterations=args.max_iter,
            convergence_tol=args.tol,
            n_restarts=args.restarts,
        )

    if args.protocol in ("b", "both"):
        run_protocol_b(
            cleaned_data_path=cleaned_f,
            output_dir=reports_d,
            models_dir=models_d,
            random_seed=args.seed,
            max_em_iterations=args.max_iter,
            convergence_tol=args.tol,
            n_restarts=args.restarts,
        )
