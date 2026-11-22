# Machine Learning Evaluation Strategy & Metrics

## 1. Two Distinct Evaluation Paradigms

A critical conceptual foundation of this project is recognizing that **Knowledge Tracing** and **Adaptive Recommendation** represent two fundamentally different tasks requiring distinct evaluation metrics:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   TASK 1: KNOWLEDGE TRACING EVALUATION                 │
│      Goal: Predict whether student u will answer question t correctly. │
│      Output: Continuous probability p_t = P(C_t = 1) ∈ [0, 1]          │
│      Metrics: ROC-AUC, Log Loss, RMSE, Accuracy                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Feeds estimated mastery states
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               TASK 2: ADAPTIVE RECOMMENDATION EVALUATION               │
│      Goal: Select optimal next topic to study or revise.               │
│      Output: Ranked topic list or single target topic                  │
│      Metrics: Prerequisite Compliance, Precision@K, NDCG@K             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Knowledge Tracing Performance Metrics

For each interaction $t$, the model outputs a predicted probability $\hat{y}_t = P(C_t = 1) \in [0, 1]$, and we observe the ground-truth binary outcome $y_t \in \{0, 1\}$.

### A. Area Under the ROC Curve (ROC-AUC) — Primary Metric
- **Definition:** The probability that a randomly chosen correct response ($y=1$) is assigned a higher predicted probability $\hat{y}$ than a randomly chosen incorrect response ($y=0$):
  $$\text{AUC} = P(\hat{y}_i > \hat{y}_j \mid y_i = 1, y_j = 0)$$
- **Why AUC is Essential for KT:**
  1. **Threshold-Independent:** Evaluates the model's ranking ability across all decision thresholds rather than relying on an arbitrary $0.50$ cutoff.
  2. **Class Imbalance Robust:** In educational benchmarks, correct answers often outnumber incorrect answers (e.g., $68\%$ vs $32\%$ in ASSISTments). Accuracy can be misleadingly high (e.g., $68\%$ by always predicting 1), whereas AUC baseline for random guessing is strictly $0.50$.
  3. **Universal Literature Standard:** All published BKT and DKT papers report AUC, enabling direct benchmark comparison. Typical literature values range from $0.67 - 0.75$ for BKT and $0.72 - 0.82$ for DKT/AKT.

---

### B. Log Loss (Binary Cross-Entropy) — Calibration Metric
- **Definition:** Measures the divergence between predicted probabilities and actual outcomes:
  $$\text{Log Loss} = - \frac{1}{N} \sum_{i=1}^N \Big[ y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i) \Big]$$
- **Why Log Loss is Essential for KT:**
  - Penalizes **overconfident errors**. If a model predicts $\hat{y} = 0.95$ (student is almost certain to get it right) but the student slips and scores $0$, Log Loss severely penalizes the model.
  - Ensures probability outputs are well-calibrated, which is critical because our recommendation engine relies on actual probability values (e.g., thresholding at $P(L_t) \ge 0.75$).

---

### C. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}$$
Commonly reported in ITS literature (e.g., pyBKT benchmarks). Provides an interpretable average error in probability points.

---

### D. Classification Metrics (Accuracy, Precision, Recall, F1)
Evaluated after binarizing predictions using threshold $\tau = 0.50$:
$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}, \quad F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 3. Adaptive Recommendation Evaluation Metrics

Recommending a study topic is a **decision-support task**, not a binary classification task. It cannot be evaluated solely on whether the student gets questions right.

### A. Prerequisite Compliance Rate (PCR) — Primary Pedagogical Metric
- **Definition:** The proportion of recommended topics whose prerequisite concepts were already mastered ($P(L) \ge \tau$) prior to recommendation:
  $$\text{PCR} = \frac{\sum_{r \in \text{Recs}} \mathbb{I}\Big(\forall p \in \text{Prereqs}(r), \, P(L_p) \ge \tau\Big)}{|\text{Recs}|}$$
- A valid adaptive system must maintain $\text{PCR} \approx 1.0$ (never recommending advanced topics when foundational prerequisites are weak).

---

### B. Deficit Remediation Efficiency (DRE)
Measures the average number of practice interactions required for a student with an identified deficit ($P(L) < 0.50$) to attain mastery ($P(L) \ge 0.80$) under adaptive sequencing versus random or linear sequencing.

---

### C. Ranking Metrics (NDCG@K, Precision@K)
When generating a multi-item study itinerary of length $K$:
- **Precision@K:** Fraction of top-$K$ recommended topics that address genuine learning needs (unmastered topics whose prerequisites are met).
- **NDCG@K (Normalized Discounted Cumulative Gain):** Rewards placing the most urgent learning needs (immediate prerequisite gaps) at the top of the recommendation list:
  $$\text{DCG}@K = \sum_{i=1}^K \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}, \quad \text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$

---

## 4. Key Takeaway: Separation of Concerns

| Evaluation Dimension | Knowledge Tracing (BKT) | Adaptive Recommendation Engine |
| :--- | :--- | :--- |
| **Fundamental Question** | *How accurately do we estimate what the student knows?* | *How effectively do we guide what the student should study next?* |
| **Primary Evaluation Metric** | **ROC-AUC & Log Loss** | **Prerequisite Compliance (PCR) & Remediation Efficiency** |
| **Ground Truth Source** | Historical question-response binary logs | Pedagogical prerequisite DAG & mastery transition gains |
| **Failure Mode** | Inaccurate probability estimation (high RMSE) | Premature recommendation of advanced concepts or circular study plans |
