# Public Educational Datasets Investigation & Comparison

## 1. Overview of Evaluated Benchmarks

To ground our Knowledge Tracing research in empirical data, four prominent public educational datasets were investigated:
1. **ASSISTments 2009–2010 (Skill Builder Dataset)**
2. **ASSISTments 2017**
3. **EdNet (EdNet-KT1)**
4. **KDD Cup 2010 (Bridge to Algebra / Algebra I 2005–2006)**

---

## 2. Comprehensive Comparison Matrix

| Attribute | ASSISTments 2009–2010 (Skill Builder) | ASSISTments 2017 | EdNet (EdNet-KT1) | KDD Cup 2010 (Algebra I) |
| :--- | :--- | :--- | :--- | :--- |
| **Release Year** | 2010 (Corrected 2012) | 2017 | 2020 | 2010 |
| **Origin / Platform** | WPI ASSISTments (Middle School Math) | WPI ASSISTments (Math Learning) | Riiid Santa (TOEIC Prep App) | CMU LearnLab / Cognitive Tutor |
| **Primary Interaction Format** | Flat CSV (Problem attempt logs) | Flat CSV (Longitudinal response logs) | Partitioned CSVs by student | Tab-delimited transaction logs |
| **Interaction Records** | **525,534** (raw rows) | ~942,816 interactions | **131,441,538** interactions | ~8,918,054 step records |
| **Student Count** | **4,217** unique students | ~1,709 students | ~784,309 users | ~3,310 students |
| **Skill / Concept Count** | **110** discrete skills | ~102 skills | ~1,892 question skills | ~112 knowledge components |
| **Unique Questions** | **26,688** problems | ~3,162 questions | ~13,169 questions | ~173,113 problem steps |
| **Target Variable** | `correct` (1: first-attempt correct, 0: incorrect/hint) | `correct` (binary) | `user_answer` vs `correct_answer` | `Correct First Attempt` (0/1) |
| **Timestamp / Ordering** | Chronological `order_id` & `ms_first_response` | Explicit timestamps | Unix timestamps (`timestamp` ms) | Precise timestamps |
| **BKT Suitability** | **Highest (Gold Standard)** | Moderate | High (with extensive preprocessing) | High |
| **DKT Suitability** | High (standard DKT benchmark) | High | Highest (large sequence scale) | High |
| **File Size** | **~79.35 MB** (Single CSV) | ~110 MB | **~13 GB** (Multi-file directory) | ~1.5 GB |
| **Licensing / Access** | Open for academic research (CC BY-NC 4.0) | Open for academic research | Open research license (MIT / CC) | Open research archive (PSLC DataShop) |

---

## 3. Recommended Primary Benchmark: ASSISTments 2009–2010 (`as.csv`)

### Justification:
1. **Universally Established Baseline:** ASSISTments 2009–2010 is the universally accepted standard benchmark in Knowledge Tracing literature (used by Corbett & Anderson, Piech et al. 2015 for DKT, pyBKT, pyKT, and SAKT). Literature results are readily available for direct validation.
2. **Pedagogical Alignment:** Interaction sequences represent mastery-based problem sets ("Skill Builders"), where students practice a concept until achieving consecutive correct answers, mirroring our project's goal.
3. **Manageable Footprint:** At ~79.35 MB, the dataset can be processed in memory and analyzed rapidly without requiring distributed cluster infrastructure, making it ideal for our development environment.
4. **Clean Skill Component Tagging:** Features clean textual skill tags (`skill_name`) and unique numeric identifiers (`skill_id`).

---

## 4. Actual Dataset Inspection Results (`ml-service/data/raw/as.csv`)

The benchmark dataset file was downloaded and inspected using our reproducible script ([inspect_dataset.py](file:///N:/adaptive-study-planner/ml-service/preprocessing/inspect_dataset.py)).

### Provenance:
- **Local Location:** `N:\adaptive-study-planner\ml-service\data\raw\as.csv`
- **File Size:** **79.35 MB** (83,201,940 bytes)
- **Source URL:** `https://raw.githubusercontent.com/CAHLR/pyBKT-examples/master/data/as.csv`
- **Integrity Status:** Preserved in pristine, read-only state.

### Empirical Statistics:
- **Total Rows:** **525,534** interaction records
- **Total Columns:** **30** attributes
- **Unique Students (`user_id`):** **4,217**
- **Unique Problems (`problem_id`):** **26,688**
- **Unique Skills (`skill_name`):** **110**
- **Target Correctness Distribution (`correct`):**
  - Correct ($C_t = 1$): **357,085** records (**67.95%**)
  - Incorrect / Scaffolding ($C_t = 0$): **168,449** records (**32.05%**)

### Critical Observations for Preprocessing:
1. **Missing Skill Tags:**
   - 78,690 rows (14.97%) have a missing or null `skill_name`.
   - 66,326 rows (12.62%) have a missing `skill_id`.
   - *Implication:* Standard BKT models each skill independently; rows without an assigned skill cannot update any skill Markov chain and must be filtered out, leaving **446,844 valid skill-tagged interactions**.
2. **Interaction Ordering:**
   - Every row contains a non-null `order_id` (0 missing values), providing a deterministic chronological ordering for each student's attempt sequence.
3. **Opportunity Counter:**
   - The dataset includes an `opportunity` column tracking cumulative practice trials for each student on a given skill.
