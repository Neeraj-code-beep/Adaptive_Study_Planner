# Academic Mini-Project Report Content Audit

**Project:** Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning  
**Academic Level:** 3rd Year, B.Tech Computer Science and Engineering  
**Institution:** Khwaja Moinuddin Chishti Language University, Lucknow  
**Document Audited:** `docs/report/PROJECT_REPORT_DRAFT.md` (and companion `.docx`, `.pdf`)  
**Date:** November 2026  
**Auditor:** Senior Academic Reviewer & Lead Software Engineer  

---

## 1. Chapter-by-Chapter Implementation Status Audit

| Chapter / Section | Content Description | Grounding Status | Implementation Reference |
|---|---|---|---|
| **Cover Page & Certificate** | Academic credentials, guide name, department | **Verified Format** (Awaiting student details) | Formatted according to KMCLU reference standard. |
| **Acknowledgement** | Formal gratitude to guide, HOD, faculty, family | **Verified Format** | Acknowledges Mr. Tasleem Jamal Khan and Dept. CSE. |
| **Abstract** | Concise summary of problem, BKT, dataset, evaluation, architecture | **Verified Empirical** | Grounded in verified benchmark results and monorepo design. |
| **Chapter 1: Introduction** | 1.1 Background, 1.2 Problem Statement, 1.3 Objectives, 1.4 Scope | **Verified Theoretical** | Aligned with Phase 1–6 project goals. |
| **Chapter 2: Existing System & Limitations** | 2.1 Existing Systems, 2.2 Traditional Planning Flaws, 2.3 Need for Adaptive Learning, 2.4 Proposed Solution | **Verified Literature** | Contrasts LMS percentage gradebooks with cognitive tracing. |
| **Chapter 3: Literature Review & Tech Stack** | 3.1 KT, 3.2 BKT, 3.3 DKT, 3.4 ASSISTments, 3.5 Technology Stack | **Verified Literature** | Accurately distinguishes implemented stack from future tools. |
| **Chapter 4: System Architecture & Methodology** | 4.1 Overall Architecture, 4.2 Preprocessing, 4.3 Data Audit, 4.4 BKT Model, 4.5 Formulas, 4.6 EM, 4.7 Protocols | **Verified Implementation** | Fully implemented in `ml-service/app/knowledge_tracing/bkt/`. |
| | 4.8 Database Architecture | **Verified Implementation** | Implemented in `backend/prisma/schema.prisma` (11 models). |
| | 4.9 Adaptive Recommendation Methodology | **PROPOSED METHODOLOGY** | Prerequisite gating logic formalized; recommendation algorithm execution slated for Phase 8. |
| **Chapter 5: Implementation & Project Structure** | 5.1 Environment, 5.2 Monorepo Layout, 5.3 Frontend, 5.4 Backend, 5.5 ML Service, 5.6 BKT Code, 5.7 Prisma Code | **Verified Implementation** | Matches exact repository layout across all 3 services. |
| | 5.8 Current Status | **Verified Reality** | Accurately identifies completed vs upcoming phases. |
| **Chapter 6: Results & Evaluation** | 6.1 Dataset Stats, 6.2 Preprocessing, 6.3 BKT Results, 6.4 Baselines, 6.5 Calibration (ECE) | **Verified Empirical** | Exact figures from `protocol_a_results.json` and `protocol_b_results.json`. |
| | 6.6 Application Interface & Screenshots | **PLACEHOLDERS ONLY** | No synthetic screenshots fabricated; clean figure placeholders reserved for post-frontend phases. |
| | 6.7 Scientific Limitations | **Verified Rigor** | Explicitly documents the math-to-DSA transfer limitation and unexecuted migrations. |
| **Chapter 7: Conclusion & Future Scope** | 7.1 Conclusion, 7.2 Current Limitations, 7.3 Future Scope | **Verified Reality** | Roadmap strictly defined without premature completion claims. |
| **References & Links** | 13 academic & documentation citations, project links | **Verified Authentic** | Genuine published literature and official documentation. |

---

## 2. Missing Student & Academic Identity Information

The following items are designated with explicit placeholders to be confirmed by the student before final submission:

1. **Student Official Name:** Currently labeled as `[CONFIRM OFFICIAL NAME]`. *(Note: Neeraj Mishra is the Project Owner in the repository context; official university exam record name must be confirmed).*
2. **University Roll Number:** Currently labeled as `[ENTER ROLL NUMBER]`.
3. **University Enrollment Number:** Currently labeled as `[ENTER ENROLLMENT NUMBER]`.
4. **Official Submission Date:** Currently labeled as `[ENTER SUBMISSION DATE]` (Month: November 2026).

---

## 3. Visual Interface & Screenshot Audit

Per strict project instructions:
- **No fabricated or synthetic screenshots** of application interfaces were generated.
- The report includes three clearly numbered and labeled technical placeholders:
  - `Figure 6.2: [PLACEHOLDER - Student Diagnostic Study Dashboard]`
  - `Figure 6.3: [PLACEHOLDER - Interactive Topic Prerequisite DAG View]`
  - `Figure 6.4: [PLACEHOLDER - Adaptive Quiz Practice Interface]`
- Terminal test execution logs and ASCII reliability diagrams are included as genuine technical verifications.

---

## 4. Repository Links & External URLs

- **GitHub Repository:** Placed as `[GITHUB URL TO BE PROVIDED]`. Live deployment or private URLs were intentionally excluded until public repository publication.
- **Dataset Links:** Official Worcester Polytechnic Institute (WPI) repository link provided.
- **Research References:** Real DOI links and academic paper citations provided for all 13 bibliography entries.

---

## 5. Verification of Empirical Claims

All empirical metrics cited in the report were cross-checked against actual JSON report artifacts:
- Raw Records: 525,534 — **Verified** (`ml-service/data/raw/as.csv`).
- Cleaned Interactions: 324,449 across 3,676 students and 104 skills — **Verified** (`assistments_cleaned.csv`).
- Cleaned Correctness Rate: **65.88%** (213,748 / 324,449) — **Verified**.
- Protocol A BKT Performance: **ROC-AUC = 0.7135**, **Log Loss = 0.5697**, **Brier Score = 0.1928**, **Accuracy = 71.32%**, **ECE = 0.006872 (0.69%)** — **Verified** (`protocol_a_results.json`).
- Protocol B BKT Performance: **ROC-AUC = 0.7319**, **Log Loss = 0.5669**, **Brier Score = 0.1915**, **Accuracy = 71.86%**, **ECE = 0.012916 (1.29%)** — **Verified** (`protocol_b_results.json`).
- Baseline Correction: Smoothed Majority Log Loss = **0.6406** vs Hard Majority = **11.7210** — **Verified**.

---
*Audit certified by Lead Reviewer.*
