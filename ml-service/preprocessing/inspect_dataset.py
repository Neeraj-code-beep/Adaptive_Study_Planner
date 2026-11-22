"""
Dataset Inspection Script for ASSISTments Benchmark Dataset
File: ml-service/preprocessing/inspect_dataset.py

Purpose:
Inspect the raw ASSISTments benchmark dataset (ml-service/data/raw/as.csv)
without modifying the original file. Computes summary statistics including:
- Total row and column counts
- Available column names and sample rows
- Missing value counts per column
- Unique count of students, questions, and skills
- Correctness distribution (0 vs 1)
"""

import os
import csv
from collections import Counter

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "raw", "as.csv"
)

SOURCE_URL = "https://raw.githubusercontent.com/CAHLR/pyBKT-examples/master/data/as.csv"
ORIGINAL_NAME = "as.csv (ASSISTments 2009-2010 Skill Builder Dataset)"

def inspect_dataset(file_path=DATASET_PATH, sample_limit=3):
    if not os.path.exists(file_path):
        print(f"Error: Dataset file not found at: {file_path}")
        print(f"Expected source: {SOURCE_URL}")
        return None

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print("=" * 70)
    print("EDUCATIONAL DATASET AUDIT & INSPECTION REPORT")
    print("=" * 70)
    print(f"Dataset File:     {file_path}")
    print(f"Original Name:    {ORIGINAL_NAME}")
    print(f"Source URL:       {SOURCE_URL}")
    print(f"File Size:        {file_size_mb:.2f} MB")
    print("=" * 70)

    # Use ISO-8859-1 encoding to safely handle text characters in ASSISTments
    with open(file_path, mode="r", encoding="ISO-8859-1") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Error: Empty dataset file.")
            return None

        total_columns = len(header)
        col_indices = {col: i for i, col in enumerate(header)}

        missing_counts = [0] * total_columns
        samples = []
        total_rows = 0

        unique_students = set()
        unique_problems = set()
        unique_skills = set()
        correctness_dist = Counter()

        user_idx = col_indices.get("user_id")
        problem_idx = col_indices.get("problem_id")
        skill_idx = col_indices.get("skill_name")
        correct_idx = col_indices.get("correct")

        for row in reader:
            if not row:
                continue
            total_rows += 1

            if len(samples) < sample_limit:
                samples.append(row)

            # Check missing values per field
            for i in range(total_columns):
                val = row[i].strip() if i < len(row) else ""
                if val == "" or val.lower() == "nan" or val.lower() == "null":
                    missing_counts[i] += 1

            if user_idx is not None and user_idx < len(row) and row[user_idx].strip():
                unique_students.add(row[user_idx].strip())

            if problem_idx is not None and problem_idx < len(row) and row[problem_idx].strip():
                unique_problems.add(row[problem_idx].strip())

            if skill_idx is not None and skill_idx < len(row):
                skill_val = row[skill_idx].strip()
                if skill_val and skill_val.lower() not in ("nan", "null"):
                    unique_skills.add(skill_val)

            if correct_idx is not None and correct_idx < len(row):
                c_val = row[correct_idx].strip()
                if c_val:
                    correctness_dist[c_val] += 1

    print(f"\n1. DATASET DIMENSIONS")
    print(f"   - Total Rows:    {total_rows:,}")
    print(f"   - Total Columns: {total_columns}")

    print(f"\n2. COLUMN LIST & MISSING VALUE AUDIT")
    print(f"   {'#':<4} {'Column Name':<28} {'Missing Count':<16} {'Missing %':<10}")
    print(f"   {'-'*4} {'-'*28} {'-'*16} {'-'*10}")
    for i, col in enumerate(header):
        m_count = missing_counts[i]
        m_pct = (m_count / total_rows * 100) if total_rows > 0 else 0
        print(f"   {i+1:<4} {col:<28} {m_count:<16,} {m_pct:<10.2f}%")

    print(f"\n3. CORE ENTITY CARDINALITY")
    print(f"   - Unique Students (user_id):       {len(unique_students):,}")
    print(f"   - Unique Problems (problem_id):   {len(unique_problems):,}")
    print(f"   - Unique Skills (skill_name):     {len(unique_skills):,}")

    print(f"\n4. TARGET VARIABLE DISTRIBUTION (correct)")
    for label, count in sorted(correctness_dist.items()):
        pct = (count / total_rows * 100) if total_rows > 0 else 0
        desc = "Correct (1)" if label == "1" else ("Incorrect / Scaffolding (0)" if label == "0" else f"Other ({label})")
        print(f"   - {desc:<30}: {count:>10,} ({pct:.2f}%)")

    print(f"\n5. SAMPLE ROWS PREVIEW (Top {sample_limit} rows)")
    for r_idx, sample in enumerate(samples, 1):
        print(f"\n   --- Sample Row {r_idx} ---")
        preview_fields = ["order_id", "user_id", "problem_id", "skill_name", "correct", "attempt_count", "opportunity"]
        for fld in preview_fields:
            if fld in col_indices:
                idx = col_indices[fld]
                val = sample[idx] if idx < len(sample) else "N/A"
                print(f"       {fld:<18}: {val}")

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE - DATASET UNMODIFIED")
    print("=" * 70)

    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "unique_students": len(unique_students),
        "unique_problems": len(unique_problems),
        "unique_skills": len(unique_skills),
        "correctness_dist": dict(correctness_dist),
    }

if __name__ == "__main__":
    inspect_dataset()
