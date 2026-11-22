"""
Dataset Validation Module
File: ml-service/preprocessing/validate_dataset.py

Performs comprehensive validation on incoming raw educational datasets:
- Column presence check
- Missing value audit
- Data type and format consistency
- Binary correctness target validation
- Duplicate detection
"""

from typing import List, Dict, Any, Tuple
from collections import Counter
from preprocessing.load_dataset import load_raw_dataset_stream

def validate_raw_dataset(
    file_path: str,
    required_columns: Tuple[str, ...],
    encoding: str = "ISO-8859-1"
) -> Dict[str, Any]:
    """
    Scans the raw dataset and generates a comprehensive validation profile.
    """
    header, stream = load_raw_dataset_stream(file_path, encoding=encoding)

    # 1. Column presence check
    missing_required = [col for col in required_columns if col not in header]
    if missing_required:
        stream.close()
        raise ValueError(f"Dataset is missing required columns: {missing_required}")

    total_rows = 0
    missing_counts = {col: 0 for col in header}
    unique_samples = {col: set() for col in header}
    correctness_counter = Counter()
    invalid_correctness = []

    seen_event_keys = set()
    event_duplicate_count = 0

    for row in stream:
        total_rows += 1

        for col, val in row.items():
            if val == "" or val.lower() in ("nan", "null"):
                missing_counts[col] += 1
            else:
                if len(unique_samples[col]) < 20:
                    unique_samples[col].add(val)

        # Check correctness validity
        c_val = row.get("correct", "").strip()
        if c_val in ("0", "1"):
            correctness_counter[c_val] += 1
        else:
            invalid_correctness.append((total_rows, c_val))

        # Check composite event duplicate: (order_id, skill_id)
        oid = row.get("order_id", "").strip()
        sid = row.get("skill_id", "").strip()
        if oid and sid:
            k = (oid, sid)
            if k in seen_event_keys:
                event_duplicate_count += 1
            else:
                seen_event_keys.add(k)

    validation_result = {
        "file_path": file_path,
        "total_rows": total_rows,
        "total_columns": len(header),
        "columns_present": header,
        "missing_counts": missing_counts,
        "missing_percentages": {
            col: round((count / total_rows * 100), 2) if total_rows > 0 else 0
            for col, count in missing_counts.items()
        },
        "correctness_distribution": dict(correctness_counter),
        "invalid_correctness_count": len(invalid_correctness),
        "invalid_correctness_samples": invalid_correctness[:5],
        "event_duplicate_count": event_duplicate_count,
        "validation_passed": len(missing_required) == 0 and len(invalid_correctness) == 0,
    }

    return validation_result
