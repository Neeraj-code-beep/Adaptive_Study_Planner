# Preprocessing Pipeline Implementation Guide

## 1. Pipeline Architecture

The data preprocessing pipeline transforms the raw ASSISTments 2009–2010 skill builder dataset (`as.csv`) into clean, normalized, chronologically sequenced interactions and reproducible evaluation splits.

```text
[ Raw CSV: ml-service/data/raw/as.csv ]
                    │
                    ▼
       [ Stage 1: Validation ]
       validate_dataset.py
       - Column presence, null audit, type checks, binary target verification.
                    │
                    ▼
        [ Stage 2: Cleaning ]
        clean_dataset.py
        - Drop unassigned skills (78,690 rows).
        - Drop join duplicates sharing (order_id, skill_id) (121,207 rows).
        - Enforce binary correctness (0 or 1).
        - Apply student & skill threshold filters (min_student=5, min_skill=30).
                    │
                    ▼
       [ Stage 3: Sequencing ]
       sequence_builder.py
       - Group by student_id.
       - Compound sort: (order_id, skill_id, question_id).
       - Assign deterministic 1-based interaction_index.
       - Export: ml-service/data/processed/assistments_cleaned.csv
                    │
                    ▼
       [ Stage 4: Evaluation Splitting ]
       split_dataset.py
       ├── Protocol A: Unseen-Student Generalization (70% Train, 15% Val, 15% Test)
       └── Protocol B: Known-Student Future Prediction (80% History, 20% Future Test)
                    │
                    ▼
        [ Stage 5: Profiling & Reports ]
        generate_dataset_report.py
        - Export profiles & audit summaries to ml-service/data/reports/
```

---

## 2. Modules and Responsibilities

| Module | Location | Primary Responsibility |
| :--- | :--- | :--- |
| `config.py` | `ml-service/preprocessing/config.py` | Centralized configuration dataclass (`PreprocessingConfig`) for file paths, seeds, thresholds, and splitting ratios. |
| `load_dataset.py` | `ml-service/preprocessing/load_dataset.py` | Streaming and in-memory CSV loader with explicit `ISO-8859-1` encoding and safe file handle closure. |
| `validate_dataset.py` | `ml-service/preprocessing/validate_dataset.py` | Validates column schemas, missingness percentages, duplicate rates, and target values. |
| `clean_dataset.py` | `ml-service/preprocessing/clean_dataset.py` | Applies filtering rules, schema normalization, and composite event key deduplication. |
| `sequence_builder.py` | `ml-service/preprocessing/sequence_builder.py` | Groups interactions by learner, sorts chronologically, resolves ties, and assigns sequence indices. |
| `split_dataset.py` | `ml-service/preprocessing/split_dataset.py` | Generates leakage-free evaluation splits for Protocol A (unseen students) and Protocol B (future prediction). |
| `generate_dataset_report.py` | `ml-service/preprocessing/generate_dataset_report.py` | Generates structured JSON audit profiles and comparative metrics. |
| `run_pipeline.py` | `ml-service/preprocessing/run_pipeline.py` | CLI orchestrator tying all stages together with configurable arguments. |

---

## 3. Canonical Interaction Schema

Each processed interaction record follows a standardized canonical schema:

| Field Name | Type | Description | Source Field |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Unique anonymized learner identifier. | `user_id` |
| `question_id` | String | Unique problem identifier. | `problem_id` |
| `skill_id` | String | Numeric Knowledge Component identifier. | `skill_id` |
| `skill_name` | String | Standardized textual concept name. | `skill_name` |
| `correct` | Integer (0 or 1) | Binary first-response outcome (1 = correct, 0 = incorrect/hint). | `correct` |
| `order_id` | Integer | Original global chronological event log ID from ASSISTments. | `order_id` |
| `interaction_index` | Integer | Deterministic 1-based chronological index within the student's attempt history. | Generated |
| `attempt_count` | Integer | Total attempts made by the student to complete this item in the tutor. | `attempt_count` |
| `ms_first_response` | Integer | Milliseconds taken before student submitted first response. | `ms_first_response` |
| `hint_count` | Integer | Total hint requests submitted on this item. | `hint_count` |
| `original` | Integer (0 or 1) | 1 for original/main problem, 0 for scaffolding item. | `original` |

---

## 4. Key Preprocessing Decisions

### 4.1 Missing Skill Handling
- **Observed:** 78,690 raw rows lacked `skill_name` (66,326 lacked both ID and name; 12,364 had an orphan `skill_id` that never appeared in the paired dictionary).
- **Decision:** Exclude all 78,690 rows. BKT tracks independent skill Markov chains; interactions without verified skill names cannot update any knowledge component.

### 4.2 Deduplication of Assignment Joins
- **Observed:** 121,207 rows were redundant join duplicates sharing the same `(order_id, skill_id)`.
- **Decision:** Deduplicate using the composite event key `(order_id, skill_id)`. This prevents counting identical problem logs multiple times across class assignments.

### 4.3 Attempt Count & Survival Bias Policy
- **Observed:** `correct` is already the first-response indicator. The column `attempt_count` measures the *total attempts* made to solve the item.
- **Decision:** Do NOT filter for `attempt_count == 1`. Filtering for `attempt_count == 1` causes catastrophic survival bias, discarding 89,583 valid first-attempt failures and falsely inflating correctness from 69.5% to 85.6%.

---

## 5. Execution Commands

From project root:
```powershell
# Run using Python virtual environment
.\ml-service\.venv\Scripts\python.exe ml-service/preprocessing/run_pipeline.py

# Run with optional flags:
.\ml-service\.venv\Scripts\python.exe ml-service/preprocessing/run_pipeline.py --seed 42 --min-student-interactions 5 --min-skill-interactions 30
```

From `ml-service` directory:
```powershell
Set-Location "N:\adaptive-study-planner\ml-service"
.\.venv\Scripts\Activate.ps1
python preprocessing/run_pipeline.py
```

To run the automated test suite:
```powershell
.\ml-service\.venv\Scripts\python.exe -m unittest ml-service/tests/test_preprocessing.py
```
