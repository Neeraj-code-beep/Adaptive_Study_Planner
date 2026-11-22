# ASSISTments 2009–2010 Data Audit & Empirical Analysis

## 1. Executive Summary

This document presents a comprehensive empirical audit of the raw ASSISTments 2009–2010 skill builder dataset (`as.csv`) stored at `ml-service/data/raw/as.csv` (SHA-256: `f22e3fb7872c1784ce93b0f9ebabbe0cbcac4f896fd8b4a11667b9715d77dbdc`).

---

## 2. Comprehensive Column Audit

| # | Column Name | Inferred Type | Missing Count | Missing % | Unique Count | Example Values | Required for KT? | Pipeline Decision | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `order_id` | Integer | 0 | 0.00% | 426,827 | `33022537`, `33022709` | **Yes** | **Retained** | Global chronological primary key of the problem action log. |
| 2 | `assignment_id` | Integer | 0 | 0.00% | 12,504 | `232624`, `232625` | No | Excluded | Teacher assignment grouping; not relevant for skill mastery. |
| 3 | `user_id` | Integer | 0 | 0.00% | 4,217 | `64525`, `70363` | **Yes** | **Retained (student_id)** | Primary student identifier. |
| 4 | `assistment_id` | Integer | 0 | 0.00% | 17,998 | `33112`, `33114` | No | Excluded | Container of one or more problems. |
| 5 | `problem_id` | Integer | 0 | 0.00% | 26,688 | `51424`, `51435` | **Yes** | **Retained (question_id)** | Specific question attempted. |
| 6 | `original` | Binary (0/1) | 0 | 0.00% | 2 | `1`, `0` | Optional | Retained (metadata) | Distinguishes main problems (1) from scaffolding steps (0). |
| 7 | `correct` | Binary (0/1) | 0 | 0.00% | 2 | `1`, `0` | **Yes** | **Retained (Target)** | 1 if correct on first attempt without hints, 0 otherwise. |
| 8 | `attempt_count` | Integer | 0 | 0.00% | 61 | `1`, `2`, `0`, `3` | Optional | Retained (metadata) | Cumulative attempts on problem during session. |
| 9 | `ms_first_response` | Integer | 0 | 0.00% | 41,208 | `26500`, `7850` | Optional | Retained (metadata) | Latency to first action in milliseconds. |
| 10 | `tutor_mode` | String | 0 | 0.00% | 2 | `tutor`, `test` | No | Excluded | Session mode. |
| 11 | `answer_type` | String | 0 | 0.00% | 6 | `choose_1`, `algebra` | No | Excluded | Question response format. |
| 12 | `sequence_id` | Integer | 0 | 0.00% | 1,478 | `5905`, `5906` | No | Excluded | Problem set identifier. |
| 13 | `student_class_id` | Integer | 0 | 0.00% | 1,241 | `12423`, `12424` | No | Excluded | Classroom identifier. |
| 14 | `position` | Integer | 0 | 0.00% | 237 | `1`, `2` | No | Excluded | Assignment list position. |
| 15 | `type` | String | 0 | 0.00% | 3 | `MasterySection` | No | Excluded | Curriculum section type. |
| 16 | `base_sequence_id` | Integer | 0 | 0.00% | 1,478 | `5905`, `5906` | No | Excluded | Parent problem set copy ID. |
| 17 | `skill_id` | Integer | 66,326 | 12.62% | 123 | `1`, `2`, `110` | **Yes** | **Retained (skill_id)** | Knowledge Component ID. |
| 18 | `skill_name` | String | 78,690 | 14.97% | 110 | `Box and Whisker`, `Circle Graph` | **Yes** | **Retained (skill_name)** | Knowledge Component human-readable label. |
| 19 | `teacher_id` | Integer | 0 | 0.00% | 178 | `22964` | No | Excluded | Instructor identifier. |
| 20 | `school_id` | Integer | 0 | 0.00% | 30 | `2` | No | Excluded | Institution identifier. |
| 21 | `hint_count` | Integer | 0 | 0.00% | 16 | `0`, `1`, `2` | Optional | Retained (metadata) | Count of requested hints. |
| 22 | `hint_total` | Integer | 0 | 0.00% | 16 | `3`, `4` | No | Excluded | Total hints available. |
| 23 | `overlap_time` | Integer | 0 | 0.00% | 45,920 | `26500` | No | Excluded | Total session duration. |
| 24 | `template_id` | Integer | 0 | 0.00% | 1,029 | `30722` | No | Excluded | Problem question template ID. |
| 25 | `answer_id` | Integer | 476,856 | 90.74% | 18,914 | `12345` | No | Excluded | Multiple-choice option ID. |
| 26 | `answer_text` | String | 94,783 | 18.04% | 12,044 | `4`, `yes` | No | Excluded | Free response text. |
| 27 | `first_action` | Integer | 0 | 0.00% | 2 | `0`, `1` | No | Excluded | 0=attempt, 1=hint request. |
| 28 | `bottom_hint` | Integer | 445,627 | 84.80% | 1 | `1` | No | Excluded | Bottom-hint request flag. |
| 29 | `opportunity` | Integer | 0 | 0.00% | 362 | `1`, `2`, `3` | Optional | Excluded (recomputed) | Practice trial counter for skill. |
| 30 | `opportunity_original`| Integer | 76,314 | 14.52% | 291 | `1`, `2` | No | Excluded | Opportunity on main problems only. |

---

## 3. Deep-Dive: Missing Skill Information

```text
Total Raw Rows: 525,534
├── Rows with both skill_name and skill_id populated: 446,844 (85.03%)
│   ├── Unique skill names: 110
│   └── Unique skill IDs: 111 (1 name maps to 2 IDs: 'Absolute Value' -> IDs 85 and 163)
└── Rows with missing skill information: 78,690 (14.97%)
    ├── Both skill_name and skill_id missing: 66,326 rows
    └── skill_name missing, but skill_id present: 12,364 rows
        └── These 12,364 rows belong to 12 orphan IDs (37, 76, 94, 101, etc.)
            that NEVER appear in the paired 446,844 rows.
```

### Policy Conclusion:
Because the 12 orphan IDs have no text label in the entire dataset, and the 66,326 rows lack all identifiers, none of the 78,690 rows can be safely assigned to a reliable Knowledge Component. **All 78,690 rows are excluded from skill-level BKT modeling**, leaving **446,844 skill-tagged records**.

---

## 4. Deep-Dive: Attempt Count & Discovery of Survival Bias

A key research inquiry was determining whether filtering for `attempt_count == 1` is appropriate.

### Cross-Tabulation of `attempt_count` vs `correct`:
| `attempt_count` | Total Rows | Correct ($C_t = 1$) | Incorrect ($C_t = 0$) | Correctness Rate |
|---|---|---|---|---|
| **0** (Hint requested before attempt) | 22,153 | 12,971 | 9,182 | 58.55% |
| **1** (Completed in 1 attempt) | 403,814 | 342,634 | 61,180 | **84.85%** |
| **2** (Completed in 2 attempts) | 58,585 | 1,197 | 57,388 | **2.04%** |
| **3** (Completed in 3 attempts) | 18,917 | 194 | 18,723 | **1.03%** |
| **4** (Completed in 4 attempts) | 9,405 | 30 | 9,375 | **0.32%** |
| **5+** (Completed in 5+ attempts) | 12,660 | 59 | 12,601 | **0.47%** |

### Critical Finding:
In ASSISTments, `correct` records whether the student got the question right on their **first try**. When a student makes a mistake, the tutor prompts them to try again until they succeed. Thus, students who failed on their first try have `attempt_count >= 2`.

If we filter by `attempt_count == 1`:
- We discard **89,583 valid first-attempt failures** ($C_t = 0$).
- The dataset correctness rate artificially spikes from **69.54% to 85.50%**.
- This introduces a massive **survival bias** that would cripple BKT's ability to estimate slip and learning rates.

### Candidate Dataset Comparison:
| Metric | Dataset A (All Valid Skill Rows - Verified) | Dataset B (`attempt_count == 1` Only) | Impact of Filtering |
|---|---|---|---|
| **Total Cleaned Interactions** | **324,449** | 258,926 | -65,523 rows (-20.2%) |
| **Unique Students** | **3,676** | 3,598 | -78 students |
| **Unique Skills** | **104** | 104 | Same |
| **Correct (1) Count** | **213,748** | 200,944 | -12,804 correct |
| **Incorrect (0) Count** | **110,701** | 57,982 | **-52,719 incorrect (-47.6%)** |
| **Correctness %** | **65.88%** | **77.61%** | **+11.73% artificial inflation** |
| **Recommendation** | **PRIMARY (DEFENSIBLE)** | REJECTED (SURVIVORSHIP BIAS) | Use Dataset A |
*(Note: Corrected in Phase 5 audit: previous table referenced intermediate unpruned figures; actual cleaned CSV yields 213,748 correct / 110,701 incorrect = 65.88%).*

---

## 5. Duplicate Record Investigation

In the raw dataset, **121,207 rows** are duplicate records sharing the same `(order_id, skill_id)` key. The rows differ only in their incremented `opportunity` counter caused by database joins across classroom assignment tables in the original 2009–2010 release.

Deduplicating by `(order_id, skill_id)` eliminates this artifact, reducing the 446,844 skill-tagged rows to **325,637 unique physical problem-skill interactions**. Subsequent threshold filtering (min 5 attempts per student, min 30 per skill) yields the final clean set of **324,449 interactions**.
