# Data Preprocessing Strategy & Cleaning Plan

## 1. Objective and Preprocessing Principles

Knowledge Tracing requires strict preprocessing rigor because student interaction data is **longitudinally ordered** and **hierarchically grouped by learner**.

The preprocessing pipeline transforms raw event logs into a clean, reproducible interaction sequence table:
$$\mathcal{D} = \big\{ (u_i, q_{i,t}, k_{i,t}, c_{i,t}, t) \mid u_i \in \mathcal{U}, \, q \in \mathcal{Q}, \, k \in \mathcal{K}, \, c \in \{0, 1\} \big\}$$

---

## 2. Preprocessing & Data Cleaning Rules

### Rule 1: Missing Skill Labels
- **Observation:** In ASSISTments 2009–2010 (`as.csv`), 78,690 rows (14.97%) have a null `skill_name` and 66,326 rows (12.62%) have a null `skill_id`.
- **Action:** For BKT, skills operate as isolated Markov chains. Records lacking a skill identifier cannot update any skill model and are **dropped** from BKT training. For future DKT models predicting at the question level, question-only records may be retained.

### Rule 2: Handling Multiple Skills per Question
- **Observation:** Certain questions map to multiple Knowledge Components simultaneously. In the raw dataset, such records are duplicated per skill.
- **Action:** For standard BKT, each row updates the respective skill model independently. In advanced modeling or evaluation, multi-skill questions are treated either by averaging mastery across mapped skills or assigning primary skill tags.

### Rule 3: Deduplication and Repeated Attempts
- **Observation:** When a student fails an item, they may submit multiple consecutive attempts on the same question (`attempt_count > 1`).
- **Action:** Knowledge Tracing models the **first-response correctness** (`correct` column: $1$ if correct on the very first attempt without hint requests, $0$ otherwise). Subsequent repeated attempts on the same item within the same session are ignored for mastery updates to avoid bias from immediate trial-and-error.

### Rule 4: Filtering Sparse Learners and Rare Skills
- **Sparse Learners:** Students with fewer than $5$ interactions are pruned. A sequence of 1–3 responses does not provide sufficient statistical signal to evaluate learning transitions.
- **Rare Skills:** Skills with fewer than $30$ total interactions across all students are excluded from benchmark evaluation, as parameter fitting via Expectation-Maximization fails to converge stably on sparse sample sizes.

### Rule 5: Interaction Sequence Ordering
- **Action:** Rows for each student must be strictly sorted chronologically by `order_id` (or interaction timestamp). BKT and recurrent neural networks are inherently order-sensitive; disordered rows corrupt transition estimates.

---

## 3. Data Splitting: Addressing Data Leakage in Knowledge Tracing

> [!CAUTION]
> **Catastrophic Flaw in Random Row Splitting:**  
> In standard machine learning (e.g., image classification), rows are independent and identically distributed (i.i.d.), making random row-level train/test splitting standard practice.  
> **In Knowledge Tracing, random row splitting causes severe data leakage:** if interaction $t=5$ for student $A$ is in the training set and interaction $t=4$ is in the test set, the model uses future knowledge to predict the past, producing artificially inflated metrics (AUC > 0.95) that fail completely in production.

### Rigorous Evaluation Splitting Strategies

| Splitting Strategy | How It Works | Pedagogical Meaning Tested | Recommended Use |
| :--- | :--- | :--- | :--- |
| **Student-Wise K-Fold Split** | Partition the student population $\mathcal{U}$ into $K$ disjoint subsets. Fold $k$ contains all interactions of unseen students for testing; remaining $K-1$ folds are used for training. | Tests how well the model generalizes to **completely new students** joining the platform. | **Primary Strategy for BKT Parameter Estimation** |
| **Chronological (Time-Based) Split** | For each student, train on their first $70\%$ of interactions ($t \le T_{\text{split}}$) and test on the remaining $30\%$ ($t > T_{\text{split}}$). | Tests forward-in-time forecasting for existing students as they progress. | **Secondary Strategy for Longitudinal Validation** |
| **Random Row Split** | Randomly shuffle all interaction rows across all students. | Invalid: severe data leakage across temporal sequences. | **STRICTLY PROHIBITED** |

---

## 4. Expected Output Schema (Clean Processed Dataset)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `student_id` | String / Integer | Unique anonymized student identifier (`user_id`). |
| `order_id` | Integer | Chronological sequence index of the interaction. |
| `skill_id` | Integer | Unique identifier of the Knowledge Component. |
| `skill_name` | String | Standardized name of the topic or skill. |
| `problem_id` | Integer | Unique identifier of the attempted question. |
| `correct` | Integer (0 or 1) | Binary target: 1 = correct first attempt, 0 = incorrect/hint. |
| `opportunity` | Integer | Practice trial number for this student on this specific skill. |

---

## 5. Implementation Audit & Evolution from Phase 3 Assumptions to Phase 4 Policies

| Policy Area | Initial Phase 3 Assumption | Actual Phase 4 Observed Data | Final Implemented Policy | Status / Reason |
| :--- | :--- | :--- | :--- | :--- |
| **First-Attempt Filtering** | Filter strictly for `attempt_count == 1`. | `correct` is already the first-response indicator. `attempt_count` measures cumulative attempts across the tutoring session. Filtering for `== 1` discarded 89,583 valid failures ($C_t = 0$), falsely skewing accuracy from 69.5% to 85.5%. | **Retain all interactions where `correct` ∈ {0, 1} (Dataset A).** Keep `filter_first_attempt` as a configurable option in `PreprocessingConfig`. | **Implemented (Dataset A Default; Dataset B Optional).** Prevents catastrophic survival bias. |
| **Missing Skill Tags** | Filter out records lacking skill tags. | 66,326 rows lack both ID and name; 12,364 rows have orphan IDs that never appear in the paired dictionary. | **Exclude all 78,690 rows lacking verified skill names.** | **Implemented.** Prevents ungrounded, nameless Knowledge Components in BKT. |
| **Duplicate Elimination** | Deduplicate identical interaction rows. | 121,207 rows are duplicate records sharing the same `(order_id, skill_id)` key with differing `opportunity` counters due to SQL assignment joins. | **Deduplicate on composite event key `(order_id, skill_id)`.** | **Implemented.** Prevents multiple counts of the exact same question trial. |
| **Sparse Learner Pruning** | Prune learners with $< 5$ interactions. | Learners with 1–4 attempts provide insufficient longitudinal evidence for Markov state transitions. | **Filter learners with $< 5$ interactions iteratively.** | **Implemented (Configurable threshold).** |
| **Rare Skill Pruning** | Prune skills with $< 30$ observations. | Baum-Welch Expectation-Maximization parameter fitting fails to converge stably on sparse sample sizes. | **Filter skills with $< 30$ total observations iteratively.** | **Implemented (Configurable threshold).** |
| **Evaluation Protocols** | Proposed student-wise cross-validation. | Identified need for two distinct research evaluations: generalizability to new students vs future prediction for existing students. | **Generate two distinct splits: Protocol A (Unseen Students: 70/15/15) and Protocol B (Known Students: 80/20 chronological).** | **Implemented with zero leakage verification.** |
