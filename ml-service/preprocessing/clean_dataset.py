"""
Dataset Cleaning & Transformation Module
File: ml-service/preprocessing/clean_dataset.py

Implements reproducible cleaning transformations:
1. Normalizes identifiers and schema.
2. Filters records lacking verified skill names/IDs.
3. Enforces binary target correctness (1 or 0).
4. Eliminates join duplicate records using composite event keys (order_id, skill_id).
5. Optionally applies first-attempt filtering (for dataset comparison).
6. Optionally prunes sparse students or rare skills based on configurable thresholds.
7. Generates detailed transformation counts and audit logs.
"""

from typing import List, Dict, Any, Tuple, Set
from collections import Counter, defaultdict
from preprocessing.config import PreprocessingConfig
from preprocessing.load_dataset import load_raw_dataset_stream

def clean_and_normalize_records(
    config: PreprocessingConfig
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes the cleaning pipeline on the raw dataset according to configuration.
    Returns (cleaned_records, transformation_metrics).
    """
    header, stream = load_raw_dataset_stream(
        config.raw_data_path,
        encoding=config.file_encoding
    )

    total_input_rows = 0
    dropped_missing_skill = 0
    dropped_invalid_correct = 0
    dropped_missing_identifiers = 0
    dropped_duplicates = 0
    dropped_non_first_attempt = 0

    seen_event_keys: Set[Tuple[str, str]] = set()
    cleaned_candidates = []

    for row in stream:
        total_input_rows += 1

        uid = row.get("user_id", "").strip()
        pid = row.get("problem_id", "").strip()
        oid = row.get("order_id", "").strip()
        sid = row.get("skill_id", "").strip()
        sname = row.get("skill_name", "").strip()
        corr_raw = row.get("correct", "").strip()
        att_raw = row.get("attempt_count", "").strip()

        # Check required identifiers
        if not uid or not pid or not oid:
            dropped_missing_identifiers += 1
            continue

        # Check skill presence
        if not sname or sname.lower() in ("nan", "null") or not sid or sid.lower() in ("nan", "null"):
            dropped_missing_skill += 1
            continue

        # Check correctness validity (must be 0 or 1)
        if corr_raw not in ("0", "1"):
            dropped_invalid_correct += 1
            continue
        corr = int(corr_raw)

        # Composite event key deduplication (order_id, skill_id)
        # Prevents multiply-logged assignment join duplicates
        event_key = (oid, sid)
        if event_key in seen_event_keys:
            dropped_duplicates += 1
            continue
        seen_event_keys.add(event_key)

        # Optional first-attempt filtering
        if config.filter_first_attempt and att_raw != "1":
            dropped_non_first_attempt += 1
            continue

        # Canonical record construction
        canonical_record = {
            "student_id": uid,
            "question_id": pid,
            "skill_id": sid,
            "skill_name": sname,
            "correct": corr,
            "order_id": int(oid) if oid.isdigit() else oid,
            "attempt_count": int(att_raw) if att_raw.isdigit() else 1,
            "ms_first_response": int(row.get("ms_first_response", "0")) if row.get("ms_first_response", "").isdigit() else 0,
            "hint_count": int(row.get("hint_count", "0")) if row.get("hint_count", "").isdigit() else 0,
            "original": int(row.get("original", "1")) if row.get("original", "").isdigit() else 1,
        }
        cleaned_candidates.append(canonical_record)

    # Optional threshold-based filtering (sparse students and rare skills)
    # Applied iteratively until stability
    final_records = cleaned_candidates
    dropped_sparse_students = 0
    dropped_rare_skills = 0

    if config.min_student_interactions > 1 or config.min_skill_interactions > 1:
        current_records = cleaned_candidates
        while True:
            student_counts = Counter(r["student_id"] for r in current_records)
            skill_counts = Counter(r["skill_id"] for r in current_records)

            valid_students = {s for s, c in student_counts.items() if c >= config.min_student_interactions}
            valid_skills = {k for k, c in skill_counts.items() if c >= config.min_skill_interactions}

            filtered = [
                r for r in current_records
                if r["student_id"] in valid_students and r["skill_id"] in valid_skills
            ]

            if len(filtered) == len(current_records):
                break
            current_records = filtered

        dropped_sparse_students = len(cleaned_candidates) - len(current_records)
        final_records = current_records

    transformation_metrics = {
        "raw_input_rows": total_input_rows,
        "dropped_missing_identifiers": dropped_missing_identifiers,
        "dropped_missing_skill": dropped_missing_skill,
        "dropped_invalid_correctness": dropped_invalid_correct,
        "dropped_event_duplicates": dropped_duplicates,
        "dropped_non_first_attempt": dropped_non_first_attempt,
        "dropped_threshold_filters": dropped_sparse_students,
        "final_cleaned_rows": len(final_records),
        "retained_percentage": round((len(final_records) / total_input_rows * 100), 2) if total_input_rows > 0 else 0,
        "filter_first_attempt_applied": config.filter_first_attempt,
        "min_student_interactions_applied": config.min_student_interactions,
        "min_skill_interactions_applied": config.min_skill_interactions,
    }

    return final_records, transformation_metrics
