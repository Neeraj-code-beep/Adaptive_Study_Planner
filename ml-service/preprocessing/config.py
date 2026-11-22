"""
Configuration Settings for Preprocessing Pipeline
File: ml-service/preprocessing/config.py

Provides centralized, configurable parameters for data ingestion, cleaning,
filtering, splitting, and reporting. All paths are resolved relative to the
repository root for portability across environments.
"""

import os
from dataclasses import dataclass, field
from typing import Tuple, Optional

# Base directory paths
PREPROCESSING_DIR = os.path.dirname(os.path.abspath(__file__))
ML_SERVICE_DIR = os.path.dirname(PREPROCESSING_DIR)
PROJECT_ROOT = os.path.dirname(ML_SERVICE_DIR)

DEFAULT_RAW_DATA_PATH = os.path.join(ML_SERVICE_DIR, "data", "raw", "as.csv")
DEFAULT_PROCESSED_DIR = os.path.join(ML_SERVICE_DIR, "data", "processed")
DEFAULT_SPLITS_DIR = os.path.join(ML_SERVICE_DIR, "data", "splits")
DEFAULT_REPORTS_DIR = os.path.join(ML_SERVICE_DIR, "data", "reports")

@dataclass
class PreprocessingConfig:
    """Configuration container for the preprocessing and splitting pipeline."""

    raw_data_path: str = DEFAULT_RAW_DATA_PATH
    processed_dir: str = DEFAULT_PROCESSED_DIR
    splits_dir: str = DEFAULT_SPLITS_DIR
    reports_dir: str = DEFAULT_REPORTS_DIR

    # Encoding of the raw ASSISTments CSV
    file_encoding: str = "ISO-8859-1"

    # Reproducibility seed
    random_seed: int = 42

    # Filtering Decisions:
    # filter_first_attempt = False preserves all valid skill interactions where
    # 'correct' measures first-attempt performance. Setting to True evaluates
    # Dataset B (attempt_count == 1 only) to compare survival bias.
    filter_first_attempt: bool = False

    # Minimum interaction thresholds
    min_student_interactions: int = 5
    min_skill_interactions: int = 30

    # Protocol A: Unseen-student split ratios (train, validation, test)
    unseen_student_ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15)

    # Protocol B: Known-student chronological history ratio
    known_student_history_ratio: float = 0.80

    # Required raw columns
    required_columns: Tuple[str, ...] = (
        "order_id",
        "user_id",
        "problem_id",
        "correct",
        "skill_id",
        "skill_name",
    )

    def get_processed_filepath(self, filename: str = "assistments_cleaned.csv") -> str:
        os.makedirs(self.processed_dir, exist_ok=True)
        return os.path.join(self.processed_dir, filename)

    def get_unseen_split_dir(self) -> str:
        path = os.path.join(self.splits_dir, "unseen_students")
        os.makedirs(path, exist_ok=True)
        return path

    def get_known_split_dir(self) -> str:
        path = os.path.join(self.splits_dir, "known_students_future")
        os.makedirs(path, exist_ok=True)
        return path

    def get_reports_dir(self) -> str:
        os.makedirs(self.reports_dir, exist_ok=True)
        return self.reports_dir
