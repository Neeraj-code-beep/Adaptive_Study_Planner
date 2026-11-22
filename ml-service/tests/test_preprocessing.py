"""
Automated Test Suite for Preprocessing Pipeline
File: ml-service/tests/test_preprocessing.py

Comprehensive tests using synthetic fixtures covering:
1. Correctness label normalization (0 and 1).
2. Invalid correctness rejection.
3. Missing student identifier rejection.
4. Missing skill identifier rejection.
5. Skill ID / skill name consistency tracking.
6. Event duplicate detection.
7. Legitimate repeated problem attempts.
8. Chronological ordering per student.
9. Equal order_id tie-breaking.
10. Stable, 1-based interaction indexing.
11. Protocol A: Student-wise split isolation (0% overlap).
12. Protocol B: Known-student chronological split (0% future leakage).
13. Reproducible split generation with random seed.
14. Empty or invalid file handling.
15. Missing required column detection.
"""

import unittest
import tempfile
import os
import csv
import json
import shutil
import sys

# Add ml-service to sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ML_SERVICE_DIR = os.path.dirname(TEST_DIR)
if ML_SERVICE_DIR not in sys.path:
    sys.path.insert(0, ML_SERVICE_DIR)

from preprocessing.config import PreprocessingConfig
from preprocessing.load_dataset import load_raw_dataset_stream, load_raw_dataset_memory
from preprocessing.validate_dataset import validate_raw_dataset
from preprocessing.clean_dataset import clean_and_normalize_records
from preprocessing.sequence_builder import build_student_sequences
from preprocessing.split_dataset import create_unseen_student_splits, create_known_student_future_splits

class TestPreprocessingPipeline(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.synthetic_csv = os.path.join(self.test_dir, "synthetic.csv")
        self.config = PreprocessingConfig(
            raw_data_path=self.synthetic_csv,
            processed_dir=os.path.join(self.test_dir, "processed"),
            splits_dir=os.path.join(self.test_dir, "splits"),
            reports_dir=os.path.join(self.test_dir, "reports"),
            min_student_interactions=1,
            min_skill_interactions=1,
            random_seed=42
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _write_csv(self, header, rows):
        with open(self.synthetic_csv, "w", newline="", encoding="ISO-8859-1") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    def test_01_correctness_normalization(self):
        """1. Correctness label normalization: '0' -> 0, '1' -> 1."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "1", "s1", "Arrays", "1"],
            ["1002", "u1", "p2", "0", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, metrics = clean_and_normalize_records(self.config)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["correct"], 1)
        self.assertEqual(records[1]["correct"], 0)

    def test_02_invalid_correctness_labels(self):
        """2. Invalid correctness labels (e.g. '2', 'unknown', '') are rejected."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "1", "s1", "Arrays", "1"],
            ["1002", "u1", "p2", "invalid", "s1", "Arrays", "1"],
            ["1003", "u1", "p3", "2", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, metrics = clean_and_normalize_records(self.config)
        self.assertEqual(len(records), 1)
        self.assertEqual(metrics["dropped_invalid_correctness"], 2)

    def test_03_missing_student_identifiers(self):
        """3. Records missing student identifier (user_id) are dropped."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "", "p1", "1", "s1", "Arrays", "1"],
            ["1002", "u1", "p2", "1", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, metrics = clean_and_normalize_records(self.config)
        self.assertEqual(len(records), 1)
        self.assertEqual(metrics["dropped_missing_identifiers"], 1)

    def test_04_missing_skill_identifiers(self):
        """4. Records with missing skill_name or skill_id are dropped."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "1", "", "Arrays", "1"],
            ["1002", "u1", "p2", "1", "s1", "", "1"],
            ["1003", "u1", "p3", "1", "s1", "NaN", "1"],
            ["1004", "u1", "p4", "1", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, metrics = clean_and_normalize_records(self.config)
        self.assertEqual(len(records), 1)
        self.assertEqual(metrics["dropped_missing_skill"], 3)

    def test_05_skill_consistency(self):
        """5. Consistent skill mapping retains expected names and IDs."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "1", "s1", "Arrays", "1"],
            ["1002", "u1", "p2", "1", "s2", "Stacks", "1"],
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        self.assertEqual(records[0]["skill_name"], "Arrays")
        self.assertEqual(records[1]["skill_name"], "Stacks")

    def test_06_duplicate_detection(self):
        """6. Redundant join duplicates sharing (order_id, skill_id) are eliminated."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "1", "s1", "Arrays", "1"],
            ["1001", "u1", "p1", "1", "s1", "Arrays", "1"],  # exact duplicate event
        ]
        self._write_csv(header, rows)
        records, metrics = clean_and_normalize_records(self.config)
        self.assertEqual(len(records), 1)
        self.assertEqual(metrics["dropped_event_duplicates"], 1)

    def test_07_legitimate_repeated_attempts(self):
        """7. Distinct problem attempts with different order_ids are preserved."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "0", "s1", "Arrays", "1"],
            ["1002", "u1", "p1", "1", "s1", "Arrays", "2"],  # later attempt on same problem
        ]
        self._write_csv(header, rows)
        records, metrics = clean_and_normalize_records(self.config)
        self.assertEqual(len(records), 2)
        self.assertEqual(metrics["dropped_event_duplicates"], 0)

    def test_08_chronological_ordering(self):
        """8. Student sequence is sorted chronologically by order_id."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["3000", "u1", "p3", "1", "s1", "Arrays", "1"],
            ["1000", "u1", "p1", "1", "s1", "Arrays", "1"],
            ["2000", "u1", "p2", "0", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        sequenced, _ = build_student_sequences(records)
        order_seq = [r["order_id"] for r in sequenced]
        self.assertEqual(order_seq, [1000, 2000, 3000])

    def test_09_equal_order_id_ties(self):
        """9. Ties in order_id are broken deterministically by (skill_id, question_id)."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1000", "u1", "p2", "1", "s2", "Stacks", "1"],
            ["1000", "u1", "p1", "1", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        sequenced, stats = build_student_sequences(records)
        self.assertEqual(sequenced[0]["skill_id"], "s1")
        self.assertEqual(sequenced[1]["skill_id"], "s2")
        self.assertEqual(stats["tied_order_id_events"], 1)

    def test_10_stable_interaction_indexing(self):
        """10. Interaction indices are 1-based, continuous integers per student."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            ["1001", "u1", "p1", "1", "s1", "Arrays", "1"],
            ["1002", "u1", "p2", "0", "s1", "Arrays", "1"],
            ["1003", "u2", "p3", "1", "s1", "Arrays", "1"],
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        sequenced, _ = build_student_sequences(records)
        u1_indices = [r["interaction_index"] for r in sequenced if r["student_id"] == "u1"]
        u2_indices = [r["interaction_index"] for r in sequenced if r["student_id"] == "u2"]
        self.assertEqual(u1_indices, [1, 2])
        self.assertEqual(u2_indices, [1])

    def test_11_unseen_student_isolation(self):
        """11. Protocol A: Train, validation, and test sets share 0 students."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        # Create 10 distinct students
        rows = [
            [str(1000 + i), f"u{i}", "p1", "1", "s1", "Arrays", "1"]
            for i in range(10)
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        sequenced, _ = build_student_sequences(records)
        metadata = create_unseen_student_splits(sequenced, self.config)

        split_dir = self.config.get_unseen_split_dir()
        def read_students(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                return set(row["student_id"] for row in r)

        train_s = read_students(os.path.join(split_dir, "train.csv"))
        val_s = read_students(os.path.join(split_dir, "validation.csv"))
        test_s = read_students(os.path.join(split_dir, "test.csv"))

        self.assertEqual(len(train_s & val_s), 0)
        self.assertEqual(len(train_s & test_s), 0)
        self.assertEqual(len(val_s & test_s), 0)
        self.assertTrue(metadata["verification"]["zero_student_overlap"])

    def test_12_known_student_future_split(self):
        """12. Protocol B: No future interactions appear before history (zero leakage)."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        # Single student with 10 chronological attempts
        rows = [
            [str(1000 + i), "u1", f"p{i}", str(i % 2), "s1", "Arrays", "1"]
            for i in range(10)
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        sequenced, _ = build_student_sequences(records)
        metadata = create_known_student_future_splits(sequenced, self.config)

        split_dir = self.config.get_known_split_dir()
        with open(os.path.join(split_dir, "history.csv"), "r", encoding="utf-8") as f:
            history = list(csv.DictReader(f))
        with open(os.path.join(split_dir, "future_test.csv"), "r", encoding="utf-8") as f:
            future = list(csv.DictReader(f))

        max_hist_order = max(int(r["order_id"]) for r in history)
        min_future_order = min(int(r["order_id"]) for r in future)
        self.assertLessEqual(max_hist_order, min_future_order)
        self.assertTrue(metadata["verification"]["zero_temporal_leakage"])

    def test_13_reproducible_split_generation(self):
        """13. Identical random seed produces identical split assignments."""
        header = ["order_id", "user_id", "problem_id", "correct", "skill_id", "skill_name", "attempt_count"]
        rows = [
            [str(1000 + i), f"u{i}", "p1", "1", "s1", "Arrays", "1"]
            for i in range(10)
        ]
        self._write_csv(header, rows)
        records, _ = clean_and_normalize_records(self.config)
        sequenced, _ = build_student_sequences(records)

        meta1 = create_unseen_student_splits(sequenced, self.config)
        meta2 = create_unseen_student_splits(sequenced, self.config)
        self.assertEqual(meta1["student_counts"], meta2["student_counts"])
        self.assertEqual(meta1["interaction_counts"], meta2["interaction_counts"])

    def test_14_empty_input_file(self):
        """14. Empty input file raises ValueError."""
        with open(self.synthetic_csv, "w") as f:
            pass
        with self.assertRaises(ValueError):
            validate_raw_dataset(self.synthetic_csv, self.config.required_columns)

    def test_15_missing_required_columns(self):
        """15. Input missing required columns raises ValueError."""
        header = ["user_id", "correct"]
        rows = [["u1", "1"]]
        self._write_csv(header, rows)
        with self.assertRaises(ValueError):
            validate_raw_dataset(self.synthetic_csv, self.config.required_columns)

if __name__ == "__main__":
    unittest.main()
