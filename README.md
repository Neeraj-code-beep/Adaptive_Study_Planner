# Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning

## Academic Information
- **Project Owner:** Neeraj Mishra
- **Academic Level:** 3rd Year, B.Tech Computer Science and Engineering
- **Domain:** Artificial Intelligence in Education (AIED) / Educational Data Mining (EDM)

---

## 1. Project Overview
The **Adaptive Study Planner** is a specialized educational system designed to analyze student learning interactions, estimate topic-level knowledge acquisition through formal **Knowledge Tracing (KT)** models, and generate dynamic, personalized study schedules.

Unlike generic e-learning management systems or static quiz portals, this platform does not rely on simple percentage averages or generic generative chatbots for mastery estimation. Instead, it measures student latent knowledge states over continuous response sequences using mathematical and statistical models, and leverages topic prerequisite dependency structures to recommend the most optimal topic to study or revise next.

Initial subject focus: **Data Structures** (8–12 foundational to intermediate topics).

---

## 2. Technology Stack

### Frontend
- **Framework:** React with Vite (JavaScript / JSX)
- **Routing:** React Router
- **HTTP Client:** Axios
- **Data Visualization:** Recharts
- **Styling:** Modular CSS

### Backend
- **Runtime:** Node.js
- **Framework:** Express.js (ES Modules)
- **Database:** PostgreSQL
- **ORM:** Prisma ORM
- **Architecture:** Layered (Routes -> Middlewares -> Controllers -> Services -> Repositories -> Prisma)

### Machine Learning Service
- **Runtime:** Python 3.10+
- **API Framework:** FastAPI
- **Server:** Uvicorn
- **Data/Validation:** Pydantic, Pydantic-Settings (NumPy, Pandas, Scikit-learn, PyTorch to be added in algorithm implementation phase)
- **Role:** Dedicated ML service handling BKT estimation, prerequisite traversal, and recommendation algorithms.

---

## 3. Monorepo Architecture

```text
adaptive-study-planner/
├── frontend/          # React + Vite client application (Port 5173)
├── backend/           # Node.js + Express + Prisma REST API (Port 5000)
├── ml-service/        # Python + FastAPI Knowledge Tracing service (Port 8000)
├── docs/              # Research papers, system architecture, API specs & setup guides
├── .editorconfig      # Uniform coding conventions
├── .env.example       # Root environment guide
├── .gitignore         # Monorepo git exclusion rules
└── README.md          # Project documentation
```

---

## 4. Service Ports & Topology

| Service | Technology | Port | URL | Health Endpoint |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | React + Vite | `5173` | http://localhost:5173 | http://localhost:5173 |
| **Backend API** | Express.js | `5000` | http://localhost:5000 | http://localhost:5000/health |
| **ML Service** | FastAPI + Uvicorn | `8000` | http://localhost:8000 | http://localhost:8000/health |
| **ML API Docs** | Swagger UI | `8000` | http://localhost:8000/docs | http://localhost:8000/docs |

---

## 5. Prerequisites

Before running the applications, ensure you have installed:
- **Node.js:** v18.0.0 or higher (v22.x recommended)
- **npm:** v9.0.0 or higher
- **Python:** 3.10 or higher (Python 3.13 tested)
- **Git**

*Note: PostgreSQL is required for future database phases. It is not required to run the Phase 2 foundation services.*

---

## 6. Service Startup Instructions

### A. Frontend Application (Port 5173)
```bash
cd frontend
npm install
npm run dev
# Starts on http://localhost:5173
```
Production build:
```bash
npm run build
```

### B. Backend API Service (Port 5000)
```bash
cd backend
npm install
npm run dev
# Starts on http://localhost:5000
# Health check: http://localhost:5000/health
```

### C. Machine Learning Service (Port 8000)
```bash
cd ml-service
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# Starts on http://127.0.0.1:8000
# Health check: http://127.0.0.1:8000/health
# Interactive API documentation: http://127.0.0.1:8000/docs
```

For detailed step-by-step local setup commands and verification testing, refer to [LOCAL_SETUP.md](docs/development/LOCAL_SETUP.md).

---

## 7. Current Implementation Status

- **Phase 1: Project Scaffolding & Engineering Foundation (COMPLETED)**
  - Clean monorepo directory layout established.
  - Strict separation of concerns between Frontend, Backend, ML Service, and Documentation.
  - Package manifests, environment templates, and gitignore protections configured.
- **Phase 2: Application Foundation and Service Initialization (COMPLETED)**
  - Frontend configured on port 5173 with strict port binding; production build verified.
  - Express.js backend initialized on port 5000 with CORS and `/health` endpoint verified.
  - Python FastAPI ML service initialized on port 8000 with `/health` and `/docs` verified.
  - Minimal PostgreSQL Prisma schema datasource configured (no premature models or live DB dependency).
  - All three services tested with actual HTTP requests.
- **Phase 3: Knowledge Tracing Research, Dataset Discovery and Understanding (COMPLETED)**
  - Mathematical formulation and Hidden Markov Model updates for Bayesian Knowledge Tracing documented.
  - Benchmark educational datasets investigated; ASSISTments 2009–2010 (`as.csv`) secured and audited (525,534 records across 4,217 students and 110 skills).
  - Reproducible dataset inspection script created at `ml-service/preprocessing/inspect_dataset.py`.
  - Data preprocessing pipeline designed to prevent temporal data leakage (student-wise K-Fold cross validation).
  - Data Structures application curriculum structured as a 12-topic prerequisite Directed Acyclic Graph (DAG).
  - Research papers verified and evaluation strategies formalized (AUC-ROC, Log Loss for KT vs PCR, NDCG for recommendations).
- **Phase 4: Reproducible Data Preprocessing Pipeline and Evaluation Data Preparation (COMPLETED)**
  - End-to-end reproducible preprocessing pipeline implemented (8 Python modules, CLI runner).
  - Raw ASSISTments dataset (525,534 rows) cleaned to 324,449 interactions (61.74% retained) across 3,676 students and 104 skills.
  - Dropped 78,690 missing-skill rows and 121,207 join-duplicate rows with documented rationale.
  - `attempt_count` survival bias investigated; Dataset A (all valid rows) used by default with configurable first-attempt filter.
  - Two leakage-free evaluation protocols: Protocol A (unseen-student 70/15/15 split) and Protocol B (known-student 80/20 chronological split).
  - 15 automated unit tests passing; SHA-256 reproducibility verification confirmed across runs.
  - Comprehensive documentation: data audit, evaluation split design, preprocessing implementation guide.
- **Phase 5: Bayesian Knowledge Tracing (BKT) Implementation, Parameter Estimation & Evaluation (COMPLETED)**
  - Verified Phase 4 data audit: corrected cleaned correctness rate to 65.88% (213,748 / 324,449) and verified deduplication validity.
  - Implemented 4-parameter BKT ($P(L_0), P(T), P(G), P(S)$) with strict identifiability constraints ($P(G), P(S) < 0.50, G+S < 1$).
  - Developed scaled Baum-Welch (EM) parameter estimation to prevent underflow, fitting 99 skills independently with pooled fallback for 5 sparse skills.
  - Implemented online sequential inference engine (prediction before evidence update, Bayes posterior, learning transition).
  - Implemented 3 non-KT baseline models: Majority Class, Global Correctness Rate, and Per-Skill Correctness Rate.
  - Evaluated Protocol A (Unseen Students): BKT achieves **0.7135 ROC-AUC** and **0.5697 Log Loss** vs 0.6274 AUC for Per-Skill baseline.
  - Evaluated Protocol B (Known Students Future Prediction): BKT achieves **0.7319 ROC-AUC** and **0.5669 Log Loss** under a leakage-safe cohort design.
  - Serialized model artifacts and evaluation reports saved to JSON under `ml-service/models/artifacts/` and `ml-service/data/reports/bkt/`.
- **Phase 5.1: BKT Implementation Audit, Mathematical Verification & Experiment Validation (COMPLETED)**
  - Mathematical audit verified predict-before-observe order, monotonic Bayes evidence update, and independent student-skill states.
  - Baum-Welch EM audited: verified scaled forward-backward passes, non-decreasing log-likelihood ($\Delta\text{LL} \ge -10^{-7}$), and projected M-step bound enforcement.
  - Corrected Majority Class baseline using Laplace smoothing ($(N_{\text{pos}}+1)/(N_{\text{total}}+2)$), reducing Log Loss from 11.7210 to 0.6406 (exact marginal entropy).
  - Implemented Expected Calibration Error (ECE) and 10-bin Reliability Diagrams. BKT achieved an exceptional **ECE of 0.0069 (0.69%)**.
  - All 49 unit tests passed in 0.213s.
- **Phase 5.2: Final Reproducibility & Calibration Verification (COMPLETED)**
  - Verified 10-bin calibration tables, reliability curves, and EM convergence stats across 104 skills.
  - Cross-referenced boundary-constrained parameters ($P(G)=0.50$, $P(S)=0.50$, $P(L_0) \ge 0.90$) with empirical interaction patterns from 324,449 cleaned rows.
  - Confirmed 100% deterministic reproducibility across reruns (0.000000 delta).
- **Phase 6: Database Architecture, PostgreSQL Design & Prisma ORM Implementation (COMPLETED - CURRENT)**
  - Fully normalized relational database schema designed and implemented in `backend/prisma/schema.prisma` (11 models, 5 enums).
  - Core domains modeled: User & StudentProfile, Subject & Topic hierarchy, TopicPrerequisite DAG with cycle detection strategy, Question & Option bank, StudentInteraction time-series log, StudentTopicMastery, MasteryHistory snapshot audit, and StudyRecommendation.
  - Upgraded `@prisma/client` to version 6.19.3 matching CLI; generated compiled Prisma Client.
  - Implemented centralized Prisma singleton with connection diagnostics and graceful shutdown in `backend/src/config/prisma.js`.
  - Added non-blocking database status reporting to Express `/health` endpoint.
  - 7 automated backend tests implemented (Node test runner) with 100% pass rate.
  - Frontend production build and ML test suite verified intact.
- **Phase 7 (Upcoming):** Backend Integration, REST APIs & ML Service Bridge.
- **Phase 8 (Upcoming):** Adaptive Recommendation Engine & Prerequisite Gating.
- **Phase 9 (Upcoming):** Frontend UI, Dashboards & Visualization.
