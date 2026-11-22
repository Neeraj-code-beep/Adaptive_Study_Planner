# Data Pipeline Architecture & Design

## 1. System Overview

The **Adaptive Study Planner** incorporates a dual-pipeline data architecture to decouple academic benchmark experimentation from live student application workflows:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   PIPELINE A: BENCHMARK EVALUATION                     │
│      (Offline Research, Parameter Estimation, and Model Validation)    │
│                                                                        │
│  [ Raw ASSISTments Data ] ──► [ Preprocessing & Cleaning ]             │
│                                           │                            │
│                                           ▼                            │
│                              [ Student-Wise K-Fold Split ]             │
│                                           │                            │
│                                           ▼                            │
│                              [ BKT Parameter Fitting (EM) ]            │
│                                           │                            │
│                                           ▼                            │
│                              [ Performance Evaluation (AUC/RMSE) ]     │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE B: APPLICATION RUNTIME                     │
│               (Real-Time Student Assessment & Adaptive Planning)       │
│                                                                        │
│   [ Student Quiz Response ]                                            │
│               │                                                        │
│               ▼                                                        │
│   [ Express.js API Gateway ] ──► [ PostgreSQL / Prisma Log ]           │
│               │                                                        │
│               ▼ HTTP (REST)                                            │
│   [ FastAPI ML Service ]                                               │
│         ├── 1. Fetch Student History                                   │
│         ├── 2. BKT Bayesian Update (Posteriors & Forecasts)            │
│         ├── 3. Prerequisite DAG Traversal                              │
│         └── 4. Recommend Next Optimal Topic / Revision                 │
│               │                                                        │
│               ▼ JSON Response                                          │
│   [ React + Vite Client Dashboard & Visualization ]                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline A: Benchmark Training & Evaluation Flow

1. **Ingestion:** Raw CSV files stored under `ml-service/data/raw/` (e.g., `as.csv`).
2. **Filtering:**
   - Drop records lacking concept/skill tags (`skill_name` is null).
   - Filter invalid response codes (retain binary responses: $0$ or $1$).
   - Prune users with fewer than $5$ interactions to ensure sequence stability.
3. **Chronological Sorting:** Sort every student's history strictly by `order_id` or timestamp.
4. **Student-Level Splitting:** Partition distinct `user_id` groups into 5 folds ($80\%$ train, $20\%$ test) to prevent temporal data leakage.
5. **Model Parameter Fitting:** Run Expectation-Maximization (Baum-Welch algorithm) to compute optimal parameters ($P(L_0), P(T), P(G), P(S)$) per skill.
6. **Artifact Persistence:** Store fitted parameter matrices under `ml-service/models/artifacts/` (excluded from git).

---

## 3. Pipeline B: Application Runtime Flow

1. **Event Ingestion:** Student submits an answer for a Data Structures quiz question on the frontend.
2. **Persistence:** Backend Express API validates input, stores interaction record in PostgreSQL via Prisma, and dispatches a JSON payload to the ML service.
3. **Knowledge Tracing Update:**
   - FastAPI ML service retrieves the student's current mastery state for the question's topic.
   - Computes Bayesian posterior using the topic's BKT parameters.
   - Updates latent mastery score $P(L_{t+1}) \in [0.0, 1.0]$.
4. **Adaptive Recommendation Engine:**
   - Evaluates all active topics against mastery thresholds ($\tau_{\text{mastery}} = 0.80$).
   - Traverses the Data Structures Prerequisite Directed Acyclic Graph (DAG).
   - If an advanced topic is unmastered but its prerequisites are weak, the engine prioritizes foundational remediation.
   - Outputs an ordered study itinerary with pedagogical justifications.
5. **Delivery:** Frontend receives structured recommendations and renders dynamic progress indicators and topic cards.

---

## 4. Logical Interaction Schemas

### Interaction Event Payload (Backend to ML Service):
```json
{
  "student_id": "usr_94821",
  "subject_id": "sub_dsa_01",
  "topic_id": "dsa_linked_lists",
  "question_id": "q_ll_rev_04",
  "correct": 1,
  "attempt_number": 1,
  "timestamp": "2026-11-22T04:15:30Z"
}
```

### Knowledge Tracing State Response (ML Service to Backend):
```json
{
  "student_id": "usr_94821",
  "topic_id": "dsa_linked_lists",
  "prior_mastery": 0.45,
  "posterior_mastery": 0.68,
  "forecast_mastery": 0.73,
  "predicted_next_correct": 0.77,
  "mastery_status": "in_progress",
  "opportunity_count": 5
}
```

### Adaptive Recommendation Response (ML Service to Backend):
```json
{
  "student_id": "usr_94821",
  "recommended_topic_id": "dsa_stacks",
  "recommended_action": "study_next",
  "reason": "Prerequisite topic 'Singly Linked Lists' mastered (score: 0.73). Ready to progress to Stacks.",
  "prerequisite_status": {
    "dsa_arrays": "mastered",
    "dsa_linked_lists": "mastered"
  },
  "review_queue": []
}
```
