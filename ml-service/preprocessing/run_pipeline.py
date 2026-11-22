"""
End-to-End Preprocessing Pipeline CLI Runner
File: ml-service/preprocessing/run_pipeline.py

Executes the complete reproducible data pipeline:
Validation -> Cleaning -> Sequencing -> Evaluation Splitting -> Profile Reporting
"""

import sys
import os
import argparse
import time

# Ensure ml-service root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_SERVICE_DIR = os.path.dirname(SCRIPT_DIR)
if ML_SERVICE_DIR not in sys.path:
    sys.path.insert(0, ML_SERVICE_DIR)

from preprocessing.config import PreprocessingConfig
from preprocessing.validate_dataset import validate_raw_dataset
from preprocessing.clean_dataset import clean_and_normalize_records
from preprocessing.sequence_builder import build_student_sequences
from preprocessing.split_dataset import (
    create_unseen_student_splits,
    create_known_student_future_splits,
    export_records_to_csv,
)
from preprocessing.generate_dataset_report import generate_reports

def run_pipeline(config: PreprocessingConfig = None) -> dict:
    if config is None:
        config = PreprocessingConfig()

    start_time = time.time()
    print("=" * 75)
    print("STARTING DATA PREPROCESSING PIPELINE (ASSISTMENTS BENCHMARK)")
    print("=" * 75)
    print(f"Raw Input:             {config.raw_data_path}")
    print(f"Processed Output Dir:  {config.processed_dir}")
    print(f"Splits Output Dir:     {config.splits_dir}")
    print(f"Reports Output Dir:    {config.reports_dir}")
    print(f"First Attempt Filter:  {config.filter_first_attempt}")
    print(f"Min Student Attempts:  {config.min_student_interactions}")
    print(f"Min Skill Attempts:    {config.min_skill_interactions}")
    print(f"Random Seed:           {config.random_seed}")
    print("-" * 75)

    # 1. Validation Stage
    print("\n[Stage 1/5] Validating Raw Dataset...")
    raw_val = validate_raw_dataset(
        file_path=config.raw_data_path,
        required_columns=config.required_columns,
        encoding=config.file_encoding,
    )
    print(f"  ✓ Total Raw Rows:       {raw_val['total_rows']:,}")
    print(f"  ✓ Missing Skills:       {raw_val['missing_counts'].get('skill_name', 0):,} ({raw_val['missing_percentages'].get('skill_name', 0)}%)")
    print(f"  ✓ Correctness Valid:    {raw_val['invalid_correctness_count'] == 0}")

    # 2. Cleaning Stage
    print("\n[Stage 2/5] Cleaning and Normalizing Records...")
    cleaned_records, t_metrics = clean_and_normalize_records(config)
    print(f"  ✓ Dropped Missing Skill:{t_metrics['dropped_missing_skill']:,}")
    print(f"  ✓ Dropped Duplicates:   {t_metrics['dropped_event_duplicates']:,}")
    print(f"  ✓ Retained Clean Rows:  {t_metrics['final_cleaned_rows']:,} ({t_metrics['retained_percentage']}%)")

    # 3. Sequencing Stage
    print("\n[Stage 3/5] Building Chronological Student Sequences...")
    sequenced_records, seq_stats = build_student_sequences(cleaned_records)
    print(f"  ✓ Unique Students:      {seq_stats['total_students']:,}")
    print(f"  ✓ Average Seq Length:   {seq_stats['avg_sequence_length']}")
    print(f"  ✓ Median Seq Length:    {seq_stats['median_sequence_length']}")

    # Export canonical cleaned dataset
    clean_csv_path = config.get_processed_filepath("assistments_cleaned.csv")
    export_records_to_csv(sequenced_records, clean_csv_path)
    print(f"  ✓ Saved Cleaned CSV:    {clean_csv_path}")

    # 4. Evaluation Splitting Stage
    print("\n[Stage 4/5] Generating Evaluation Splits...")
    print("  Generating Protocol A (Unseen-Student Generalization)...")
    unseen_meta = create_unseen_student_splits(sequenced_records, config)
    print(f"    Train: {unseen_meta['student_counts']['train']:,} students ({unseen_meta['interaction_counts']['train']:,} rows)")
    print(f"    Val:   {unseen_meta['student_counts']['validation']:,} students ({unseen_meta['interaction_counts']['validation']:,} rows)")
    print(f"    Test:  {unseen_meta['student_counts']['test']:,} students ({unseen_meta['interaction_counts']['test']:,} rows)")

    print("  Generating Protocol B (Known-Student Future Prediction)...")
    known_meta = create_known_student_future_splits(sequenced_records, config)
    print(f"    History Rows:     {known_meta['history_interactions']:,}")
    print(f"    Future Test Rows: {known_meta['future_test_interactions']:,}")

    # 5. Reporting Stage
    print("\n[Stage 5/5] Generating Statistical Profiles and Reports...")
    reports = generate_reports(
        raw_validation=raw_val,
        cleaned_records=sequenced_records,
        transformation_metrics=t_metrics,
        sequence_stats=seq_stats,
        unseen_metadata=unseen_meta,
        known_metadata=known_meta,
        config=config,
    )
    for r_name, r_path in reports.items():
        print(f"  ✓ Generated: {os.path.basename(r_path)}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s")
    print("=" * 75)

    return {
        "validation": raw_val,
        "metrics": t_metrics,
        "sequence_stats": seq_stats,
        "unseen_meta": unseen_meta,
        "known_meta": known_meta,
        "reports": reports,
        "elapsed_seconds": elapsed,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ASSISTments Preprocessing Pipeline")
    parser.add_argument("--input", type=str, default=None, help="Path to raw CSV dataset")
    parser.add_argument("--output-dir", type=str, default=None, help="Path to processed output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splitting")
    parser.add_argument("--filter-first-attempt", action="store_true", help="Filter strictly for attempt_count == 1")
    parser.add_argument("--min-student-interactions", type=int, default=5, help="Minimum interactions per student")
    parser.add_argument("--min-skill-interactions", type=int, default=30, help="Minimum interactions per skill")

    args = parser.parse_args()

    cfg = PreprocessingConfig()
    if args.input:
        cfg.raw_data_path = args.input
    if args.output_dir:
        cfg.processed_dir = args.output_dir
    cfg.random_seed = args.seed
    cfg.filter_first_attempt = args.filter_first_attempt
    cfg.min_student_interactions = args.min_student_interactions
    cfg.min_skill_interactions = args.min_skill_interactions

    run_pipeline(cfg)
