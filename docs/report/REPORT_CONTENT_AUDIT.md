# Academic Mini-Project Report Content Audit

**Project:** Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning  
**Academic Level:** 3rd Year, 5th Semester, B.Tech Computer Science and Engineering  
**Institution:** Khwaja Moinuddin Chishti Language University, Lucknow  
**Department:** Computer Science and Engineering, Faculty of Engineering and Technology  
**Document Audited:** `docs/report/PROJECT_REPORT_DRAFT.md` (and companion `.docx`, `.pdf`)  
**Audit Date:** November 23, 2026 (Updated post-diagram integration & academic details verification)  
**Auditor:** Senior Academic Reviewer & Lead Software Engineer  

---

## 1. Chapter-by-Chapter Implementation Status Audit

| Chapter / Section | Content Description | Grounding Status | Implementation Reference |
|---|---|---|---|
| **Cover Page & Certificate** | Academic credentials, guide name, department | **Verified & Completed** | Student: Neeraj Mishra, Roll No: 2408272089, Enroll No: B-0956, Guide: Mr. Tasleem Jamal Khan. |
| **Acknowledgement** | Formal gratitude to guide, HOD, faculty, family | **Verified & Completed** | Acknowledges Mr. Tasleem Jamal Khan, Dept. CSE, and KMCLU faculty. |
| **Abstract** | Concise summary of problem, BKT, dataset, evaluation, architecture | **Verified Empirical** | Grounded in verified benchmark results and monorepo design. |
| **Chapter 1: Introduction** | 1.1 Background, 1.2 Problem Statement, 1.3 Objectives, 1.4 Scope | **Verified Theoretical** | Aligned with Phase 1–6 project goals. |
| **Chapter 2: Existing System & Limitations** | 2.1 Existing Systems, 2.2 Traditional Planning Flaws, 2.3 Need for Adaptive Learning, 2.4 Proposed Solution | **Verified Literature** | Contrasts LMS percentage gradebooks with cognitive tracing. |
| **Chapter 3: Literature Review & Tech Stack** | 3.1 KT, 3.2 BKT, 3.3 DKT, 3.4 ASSISTments, 3.5 Technology Stack | **Verified Literature** | Accurately distinguishes implemented stack from future tools. |
| **Chapter 4: System Architecture & Methodology** | 4.1 Overall Architecture (Figure 4.1), 4.2 Preprocessing (Figure 4.2), 4.3 Data Audit, 4.4 BKT Model (Figure 4.3, 4.4), 4.5 Formulas, 4.6 EM, 4.7 Protocols | **Verified Implementation** | Fully implemented in `ml-service/app/knowledge_tracing/bkt/`. All 4 architectural/mathematical diagrams embedded. |
| | 4.8 Database Architecture (Figure 4.5) | **Verified Implementation** | Implemented in `backend/prisma/schema.prisma` (11 normalized models). Vector ER diagram embedded. |
| | 4.9 Adaptive Recommendation Methodology (Figure 4.6) | **PROPOSED METHODOLOGY** | Prerequisite gating logic formalized; recommendation algorithm execution clearly labeled as proposed (Phase 8). |
| **Chapter 5: Implementation & Project Structure** | 5.1 Environment, 5.2 Monorepo Layout, 5.3 Frontend, 5.4 Backend, 5.5 ML Service, 5.6 BKT Code, 5.7 Prisma Code | **Verified Implementation** | Matches exact repository layout across all 3 services. |
| | 5.8 Current Status | **Verified Reality** | Accurately identifies completed vs upcoming phases. |
| **Chapter 6: Results & Evaluation** | 6.1 Dataset Stats, 6.2 Preprocessing, 6.3 BKT Results, 6.4 Baselines, 6.5 Calibration (ECE), 6.6 Evaluation Workflow (Figure 6.1) | **Verified Empirical** | Exact figures from `protocol_a_results.json` and `protocol_b_results.json`. Workflow diagram embedded. |
| | 6.7 Application Interface & Screenshots | **Pending Future Phase** | Application screenshots kept as clean pending placeholders awaiting Phase 7/8 frontend development. |
| | 6.8 Scientific Limitations | **Verified Rigor** | Explicitly documents the math-to-DSA transfer limitation and unexecuted migrations. |
| **Chapter 7: Conclusion & Future Scope** | 7.1 Conclusion, 7.2 Current Limitations, 7.3 Future Scope | **Verified Reality** | Roadmap strictly defined without premature completion claims. |
| **References & Links** | 13 academic & documentation citations, project links | **Verified Authentic** | Genuine published literature, official documentation; GitHub URL kept as placeholder `[GITHUB URL TO BE PROVIDED]`. |

---

## 2. Student & Academic Identity Information (Verified)

All academic credentials have been verified and injected consistently into Markdown, DOCX, and PDF:

1. **Student Official Name:** Neeraj Mishra
2. **University Roll Number:** 2408272089
3. **University Enrollment Number:** B-0956
4. **Course & Branch:** Bachelor of Technology (B.Tech) in Computer Science and Engineering
5. **Year & Semester:** Third Year / Fifth Semester
6. **Project Supervisor:** Mr. Tasleem Jamal Khan, Assistant Professor, Department of Computer Science and Engineering
7. **Department & Institution:** Department of Computer Science and Engineering, Faculty of Engineering and Technology, Khwaja Moinuddin Chishti Language University, Lucknow
8. **Submission Period:** November, 2026

---

## 3. Technical Vector Diagrams Audit

All 7 technical diagrams were authored from the ground up as scalable vector graphics (SVG) and rendered to high-resolution 300-DPI raster images (PNG) stored in `docs/report/assets/diagrams/`:

| Figure # | File Basename | Dimensions (PNG) | Content & Engineering Accuracy |
|---|---|---|---|
| **Figure 4.1** | `figure_4_1_overall_architecture` | 3959 × 2167 px | Decoupled multi-tier monorepo: React + Vite (port 5173), Express API gateway (port 5000), Prisma ORM, PostgreSQL (port 5432), and FastAPI ML service (port 8000) with REST/JSON and CORS contracts. |
| **Figure 4.2** | `figure_4_2_data_preprocessing_pipeline` | 3959 × 2000 px | 7-stage data preparation: 525,534 raw ASSISTments records $\to$ filtering missing skills $\to$ first attempts $\to$ deduplication (-121,207 rows) $\to$ chronologic sort $\to$ 324,449 clean interactions $\to$ 80/10/10 student-stratified split. |
| **Figure 4.3** | `figure_4_3_bkt_workflow` | 3834 × 1917 px | Dynamic BKT update loop: prior $P(L_t)$, expected performance $P(C_t=1)$ with slip $S$ and guess $G$, observation $y_t$, Bayes posterior $P(L_t \mid y_t)$, and learning transition $P(L_{t+1})$ with rate $T$. |
| **Figure 4.4** | `figure_4_4_bkt_hidden_markov_model` | 3834 × 1834 px | Discrete Two-State HMM: Unmastered ($L=0$) and Mastered ($L=1$) latent states, emission probabilities ($1-G, G, S, 1-S$), learning transition $T$, and zero-forgetting constraint ($1.0$). |
| **Figure 4.5** | `figure_4_5_database_er_diagram` | 4167 × 2667 px | Complete schema of all 11 normalized Prisma models (`User`, `StudentProfile`, `Subject`, `Topic`, `TopicPrerequisite`, `Question`, `QuestionOption`, `StudentInteraction`, `StudentTopicMastery`, `MasteryHistory`, `StudyRecommendation`) with PK/FK links and unique constraints. |
| **Figure 4.6** | `figure_4_6_adaptive_recommendation_workflow` | 3959 × 2042 px | Cognitive study planning decision engine: student interactions $\to$ BKT inference $\to$ mastery gating ($\tau \ge 0.85$) $\to$ Prerequisite DAG traversal. Clear visual distinction between *Implemented* components and *Proposed* recommendation engine. |
| **Figure 6.1** | `figure_6_1_model_evaluation_workflow` | 3959 × 2042 px | 4-stage empirical evaluation: zero-leakage student partitioning, EM parameter fitting, baseline benchmarking, and 10-decile calibration reliability analysis (ECE = 0.006872 / 0.69%). |

---

## 4. Document Length & Formatting Verification

- **Final PDF Length:** Exactly **19 formatted pages** (`docs/report/PROJECT_REPORT_DRAFT.pdf`).
- **Target Comparison:** Meets the target of approximately 20 meaningful pages without filler, blank pages, or artificial padding.
- **Section Breakdown:**
  - Page 1: Cover Page (Title, Degree, Student & Guide Details, University Emblem)
  - Page 2: College Certificate (Formal KMCLU Certificate layout with blank signature placeholders)
  - Page 3: Acknowledgement (Gratitude to Guide, HOD, and Faculty)
  - Page 4: Abstract (Comprehensive academic summary)
  - Pages 5–6: Table of Contents & List of Figures
  - Pages 7–18: Chapters 1 to 7 (Complete technical content and embedded figures)
  - Page 19: References & Project Verification Links
- **DOCX Companion:** Fully editable Microsoft Word document generated (`docs/report/PROJECT_REPORT_DRAFT.docx`, 2.76 MB).

---

## 5. Verification of Scientific & Academic Integrity Rules

1. **No Conflation with Internship:** The report is strictly an academic B.Tech CSE Mini-Project report on Adaptive Study Planning with zero company, corporate, or internship references.
2. **Implementation vs. Proposal Transparency:**
   - BKT training, EM fitting, ASSISTments preprocessing, API contracts, and Prisma schema definitions are documented as **Fully Implemented**.
   - Adaptive recommendation engine execution and study planner scheduling are explicitly labeled as **Proposed Methodology (Phase 8)**.
3. **Database Migration Honesty:** The report explicitly notes that Prisma models are defined and verified in schema, but local database migrations remain pending until local PostgreSQL service startup.
4. **Screenshots & Code Repositories:**
   - UI screenshots are preserved as pending placeholders awaiting Phase 7/8 frontend development.
   - GitHub URL is kept as `[GITHUB URL TO BE PROVIDED]`.
