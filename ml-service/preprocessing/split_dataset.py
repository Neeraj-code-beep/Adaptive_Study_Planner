"""
Evaluation Split Generator Module
File: ml-service/preprocessing/split_dataset.py

Implements two distinct evaluation protocols:
1. Protocol A: Unseen-student generalization (disjoint student partitioning).
2. Protocol B: Known-student future prediction (longitudinal chronological sequence split).

Saves partition CSVs and structured metadata verifying zero data leakage.
"""

import os
import csv
import json
import random
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from preprocessing.config import PreprocessingConfig

def export_records_to_csv(records: List[Dict[str, Any]], filepath: str) -> None:
    """Writes a list of dictionary records to a CSV file."""
    if not records:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

def create_unseen_student_splits(
    records: List[Dict[str, Any]],
    config: PreprocessingConfig
) -> Dict[str, Any]:
    """
    Protocol A: Partitions distinct student IDs into train, validation, and test splits.
    Guarantees 0% student overlap between any two splits.
    """
    rng = random.Random(config.random_seed)

    # Group records by student
    student_records = defaultdict(list)
    for rec in records:
        student_records[rec["student_id"]].append(rec)

    all_students = sorted(student_records.keys())
    rng.shuffle(all_students)

    n_students = len(all_students)
    train_ratio, val_ratio, test_ratio = config.unseen_student_ratios
    train_end = int(n_students * train_ratio)
    val_end = train_end + int(n_students * val_ratio)

    train_students = set(all_students[:train_end])
    val_students = set(all_students[train_end:val_end])
    test_students = set(all_students[val_end:])

    # Strict isolation assertions
    assert len(train_students & val_students) == 0, "Data leakage: train and val overlap!"
    assert len(train_students & test_students) == 0, "Data leakage: train and test overlap!"
    assert len(val_students & test_students) == 0, "Data leakage: val and test overlap!"

    train_records = [r for r in records if r["student_id"] in train_students]
    val_records = [r for r in records if r["student_id"] in val_students]
    test_records = [r for r in records if r["student_id"] in test_students]

    # Check skill representation across splits
    all_skills = set(r["skill_id"] for r in records)
    train_skills = set(r["skill_id"] for r in train_records)
    val_skills = set(r["skill_id"] for r in val_records)
    test_skills = set(r["skill_id"] for r in test_records)

    split_dir = config.get_unseen_split_dir()
    train_file = os.path.join(split_dir, "train.csv")
    val_file = os.path.join(split_dir, "validation.csv")
    test_file = os.path.join(split_dir, "test.csv")

    export_records_to_csv(train_records, train_file)
    export_records_to_csv(val_records, val_file)
    export_records_to_csv(test_records, test_file)

    train_correct = Counter(r["correct"] for r in train_records)
    val_correct = Counter(r["correct"] for r in val_records)
    test_correct = Counter(r["correct"] for r in test_records)

    metadata = {
        "protocol": "Protocol A: Unseen-Student Generalization",
        "description": "Evaluates model ability to generalize to completely new students. No student appears across multiple splits.",
        "random_seed": config.random_seed,
        "configured_ratios": config.unseen_student_ratios,
        "total_students": n_students,
        "total_interactions": len(records),
        "student_counts": {
            "train": len(train_students),
            "validation": len(val_students),
            "test": len(test_students),
        },
        "interaction_counts": {
            "train": len(train_records),
            "validation": len(val_records),
            "test": len(test_records),
        },
        "correctness_distribution": {
            "train": dict(train_correct),
            "validation": dict(val_correct),
            "test": dict(test_correct),
        },
        "skill_coverage": {
            "total_skills": len(all_skills),
            "train_skills": len(train_skills),
            "val_skills": len(val_skills),
            "test_skills": len(test_skills),
            "skills_missing_from_test": len(all_skills - test_skills),
        },
        "verification": {
            "zero_student_overlap": True,
            "all_interactions_accounted": len(train_records) + len(val_records) + len(test_records) == len(records),
        },
        "files": {
            "train": train_file,
            "validation": val_file,
            "test": test_file,
        }
    }

    metadata_path = os.path.join(split_dir, "split_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata

def create_known_student_future_splits(
    records: List[Dict[str, Any]],
    config: PreprocessingConfig
) -> Dict[str, Any]:
    """
    Protocol B: Splits each eligible student's sequence chronologically into
    earlier practice history (e.g., 80%) and later evaluation future (20%).
    Guarantees zero forward-in-time leakage.
    """
    # Group records by student
    student_records = defaultdict(list)
    for rec in records:
        student_records[rec["student_id"]].append(rec)

    history_records = []
    future_test_records = []
    eligible_students = 0
    ineligible_students = 0
    temporal_leakage_detected = False

    for student_id in sorted(student_records.keys()):
        seq = student_records[student_id]
        # Must be strictly ordered
        seq.sort(key=lambda r: (r["order_id"], str(r["skill_id"]), str(r["question_id"])))

        # Eligible if student has enough interactions to form both history and future
        if len(seq) >= config.min_student_interactions:
            eligible_students += 1
            split_idx = int(len(seq) * config.known_student_history_ratio)
            # Ensure at least 1 future record
            split_idx = min(split_idx, len(seq) - 1)

            h_part = seq[:split_idx]
            f_part = seq[split_idx:]

            # Verify no temporal violation
            if h_part and f_part:
                if max(r["order_id"] for r in h_part) > min(r["order_id"] for r in f_part):
                    temporal_leakage_detected = True

            history_records.extend(h_part)
            future_test_records.extend(f_part)
        else:
            ineligible_students += 1
            # If ineligible, entire sequence remains in history
            history_records.extend(seq)

    assert not temporal_leakage_detected, "Temporal leakage detected in chronological split!"

    split_dir = config.get_known_split_dir()
    history_file = os.path.join(split_dir, "history.csv")
    future_file = os.path.join(split_dir, "future_test.csv")

    export_records_to_csv(history_records, history_file)
    export_records_to_csv(future_test_records, future_file)

    history_correct = Counter(r["correct"] for r in history_records)
    future_correct = Counter(r["correct"] for r in future_test_records)

    metadata = {
        "protocol": "Protocol B: Known-Student Future Prediction",
        "description": "Evaluates model ability to forecast future responses of known students given their past practice history.",
        "history_ratio": config.known_student_history_ratio,
        "eligible_students": eligible_students,
        "ineligible_students": ineligible_students,
        "total_interactions": len(records),
        "history_interactions": len(history_records),
        "future_test_interactions": len(future_test_records),
        "correctness_distribution": {
            "history": dict(history_correct),
            "future_test": dict(future_correct),
        },
        "verification": {
            "zero_temporal_leakage": True,
            "all_interactions_accounted": len(history_records) + len(future_test_records) == len(records),
        },
        "files": {
            "history": history_file,
            "future_test": future_file,
        }
    }

    metadata_path = os.path.join(split_dir, "split_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata
