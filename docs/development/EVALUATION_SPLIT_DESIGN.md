# Evaluation Split Design & Leakage Prevention Protocol

## 1. Overview of Evaluation Protocols

In Knowledge Tracing, evaluating predictive performance requires addressing two distinct pedagogical questions. To support both research claims, the preprocessing pipeline generates two independent, leakage-free evaluation splits:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               PROTOCOL A: UNSEEN-STUDENT GENERALIZATION                │
│  Research Question: Can the model accurately predict performance for   │
│                     new students not seen during parameter fitting?    │
│  Splitting Unit:    Disjoint Student IDs (70% Train, 15% Val, 15% Test)│
│  Files:             train.csv, validation.csv, test.csv                │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│             PROTOCOL B: KNOWN-STUDENT FUTURE PREDICTION                │
│  Research Question: Given a student's prior practice trials, can the   │
│                     model predict their future responses?              │
│  Splitting Unit:    Temporal Sequence (80% History, 20% Future Test)   │
│  Files:             history.csv, future_test.csv                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Protocol A: Unseen-Student Generalization

### Partitioning Methodology:
1. Distinct students $\mathcal{U} = \{u_1, u_2, \dots, u_{3676}\}$ are deterministically shuffled using random seed `42`.
2. Students are partitioned into disjoint sets:
   - **Training Set (70%):** 2,573 students (**227,011 interactions**)
   - **Validation Set (15%):** 551 students (**45,297 interactions**)
   - **Test Set (15%):** 552 students (**52,141 interactions**)
3. **Strict Isolation Guarantee:**
   $$\mathcal{U}_{\text{train}} \cap \mathcal{U}_{\text{val}} = \emptyset, \quad \mathcal{U}_{\text{train}} \cap \mathcal{U}_{\text{test}} = \emptyset, \quad \mathcal{U}_{\text{val}} \cap \mathcal{U}_{\text{test}} = \emptyset$$

### Target Class Distribution Across Splits:
- **Cleaned Dataset Total:** 213,748 correct (65.88%), 110,701 incorrect (34.12%)
- **Train:** 149,856 correct (66.01%), 77,155 incorrect (33.99%)
- **Validation:** 29,445 correct (65.00%), 15,852 incorrect (35.00%)
- **Test:** 34,447 correct (66.07%), 17,694 incorrect (33.93%)
*(Note: Corrected in Phase 5 audit; previous 69.53% report was based on uncleaned raw distribution).*

### How Future BKT Models Consume Protocol A:
1. Fit global parameters $\theta_k = (P(L_0), P(T), P(G), P(S))$ on `train.csv` using Expectation-Maximization (Baum-Welch).
2. Tune hyperparameters (e.g., convergence tolerance, bounded priors) using `validation.csv`.
3. Evaluate final predictive accuracy, AUC-ROC, and Log Loss on `test.csv`.

---

## 3. Protocol B: Known-Student Future Prediction

### Partitioning Methodology:
1. For each student $u$, their chronological interaction sequence $S_u = \langle (q_1, c_1), (q_2, c_2), \dots, (q_T, c_T) \rangle$ is sorted by `order_id`.
2. For eligible students with $T \ge 5$ interactions, the sequence is divided at index $t_{\text{split}} = \lfloor 0.80 \times T \rfloor$:
   - **History Segment ($t \le t_{\text{split}}$):** **258,128 interactions**
   - **Future Evaluation Segment ($t > t_{\text{split}}$):** **66,321 interactions**
3. **Temporal Leakage Prevention:**
   $$\forall u \in \mathcal{U}, \quad \max_{r \in \text{History}_u} (\text{order\_id}) \le \min_{r \in \text{Future}_u} (\text{order\_id})$$
   No future observation is ever included in the student's historical conditioning context.

### How Future BKT Models Consume Protocol B:
1. Global parameters $\theta_k$ are applied across each student's history segment.
2. The student's latent mastery $P(L_{t_{\text{split}}})$ is updated sequentially through all trials in `history.csv`.
3. The model forecasts probabilities $\hat{y}_t = P(C_t = 1)$ for the unobserved interactions in `future_test.csv` without updating parameters on the test set.

---

## 4. Why Random Row Splitting is Invalid for Knowledge Tracing

In standard supervised learning (e.g., image classification), data instances are assumed independent and identically distributed ($i.i.d.$). Random train/test row splitting is standard.

In Knowledge Tracing:
- Observations from the same student are **temporally and cognitively coupled**.
- Randomly shuffling rows places attempt $t=5$ in the training set and attempt $t=4$ in the test set.
- A model would use future mastery to predict past responses, causing catastrophic data leakage and falsely high AUC scores ($>0.95$) that collapse when deployed on real students.
- Protocols A and B strictly prevent this failure mode.
