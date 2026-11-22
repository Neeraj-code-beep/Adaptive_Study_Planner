"""
Student Sequence Builder Module
File: ml-service/preprocessing/sequence_builder.py

Groups cleaned student interactions and sorts each student's attempt history
strictly chronologically by order_id. Assigns a deterministic 1-based
interaction_index to ensure reproducibility across model runs.
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict

def build_student_sequences(
    records: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Sorts interactions chronologically per student and assigns a deterministic
    interaction_index. Handles ties using a stable compound sort key:
    (order_id, skill_id, question_id).

    Returns (sequenced_records, sequence_stats).
    """
    student_groups = defaultdict(list)
    for rec in records:
        student_groups[rec["student_id"]].append(rec)

    sequenced_records = []
    sequence_lengths = []
    tie_count = 0

    # Sort students deterministically by student_id
    for student_id in sorted(student_groups.keys()):
        group = student_groups[student_id]

        # Compound sort key:
        # 1. order_id (primary temporal order)
        # 2. skill_id (secondary tie-breaker)
        # 3. question_id (tertiary tie-breaker)
        group.sort(key=lambda r: (r["order_id"], str(r["skill_id"]), str(r["question_id"])))

        # Assign 1-based deterministic interaction_index
        last_order = None
        for idx, rec in enumerate(group, start=1):
            if last_order is not None and rec["order_id"] == last_order:
                tie_count += 1
            last_order = rec["order_id"]

            rec_copy = dict(rec)
            rec_copy["interaction_index"] = idx
            sequenced_records.append(rec_copy)

        sequence_lengths.append(len(group))

    sequence_stats = {
        "total_students": len(student_groups),
        "total_interactions": len(sequenced_records),
        "min_sequence_length": min(sequence_lengths) if sequence_lengths else 0,
        "max_sequence_length": max(sequence_lengths) if sequence_lengths else 0,
        "avg_sequence_length": round(sum(sequence_lengths) / len(sequence_lengths), 2) if sequence_lengths else 0,
        "median_sequence_length": sorted(sequence_lengths)[len(sequence_lengths) // 2] if sequence_lengths else 0,
        "tied_order_id_events": tie_count,
    }

    return sequenced_records, sequence_stats
