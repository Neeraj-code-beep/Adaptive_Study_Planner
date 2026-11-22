# Bayesian Knowledge Tracing (BKT): Mathematical Formulation and Implementation Details

**Project:** Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning  
**Domain:** Educational Data Mining (EDM) / Artificial Intelligence in Education (AIED)  
**Author:** Neeraj Mishra (3rd Year, B.Tech CSE)  
**Implementation File Location:** `ml-service/app/knowledge_tracing/bkt/`  
**Audit Verification:** Audited and verified in Phase 5.1 (`docs/development/PHASE_5_1_AUDIT_REPORT.md`)  

---

## 1. Theoretical Foundation

Bayesian Knowledge Tracing (BKT), pioneered by Albert T. Corbett and John R. Anderson in 1994, models student cognitive mastery as a two-state Hidden Markov Model (HMM) per distinct knowledge component (skill).

For each knowledge component $k$, the student's latent cognitive state at opportunity step $t \in \{1, 2, \dots, T\}$ is modeled as a binary random variable:
- $q_t = 0$: **Unlearned State** (the student has not yet acquired the concept)
- $q_t = 1$: **Learned / Mastered State** (the student possesses the concept)

At each practice opportunity, the student produces an observable binary response:
$$y_t \in \{0, 1\}$$
where $y_t = 1$ denotes a correct response on the first attempt without tutoring assistance, and $y_t = 0$ denotes an incorrect response or an unassisted failure (including bottom-hint requests).

---

## 2. The Four Standard BKT Parameters

Every knowledge component $k$ is parameterized by a vector $\theta_k = (P(L_0), P(T), P(G), P(S))$:

| Parameter | Notation | Pedagogical Meaning | Bounded Domain |
|---|---|---|---|
| **Initial Knowledge (Prior)** | $P(L_0)$ | Prior probability that a student already mastered the skill before the first system trial | $[0.001, 0.999]$ |
| **Learning Transition** | $P(T)$ | Probability that a student in the unlearned state transitions to the learned state as a result of practicing | $[0.001, 0.999]$ |
| **Guess Rate** | $P(G)$ | Probability that a student in the unlearned state answers correctly (guessing or test strategy) | $[0.001, 0.500]$ |
| **Slip Rate** | $P(S)$ | Probability that a student in the learned state answers incorrectly (carelessness, typo, lapse) | $[0.001, 0.500]$ |

### Model Identifiability Condition:
In educational psychometrics, if $P(G) + P(S) \ge 1.0$, the relationship between latent mastery and observable correctness inverts (a student who knows the concept would be *less* likely to answer correctly than one who does not). To guarantee mathematical identifiability:
$$P(G) + P(S) < 1.0, \quad P(G) \le 0.50, \quad P(S) \le 0.50$$

---

## 3. Sequential Online Update Equations

The sequential update cycle operates in strict chronological order at each trial $t$:

```text
[ Current Latent Belief: P(L_t) ]
               │
               ▼
   [ 1. Prior Prediction ] ───────► P(C_t = 1) = P(L_t)(1 - S) + (1 - P(L_t))G
               │
               ▼
    [ Observe Response y_t ]
               │
               ▼
   [ 2. Evidence Update ] ────────► Compute Posterior P(L_t | y_t) via Bayes' Theorem
               │
               ▼
   [ 3. Learning Forecast ] ──────► P(L_{t+1}) = P(L_t | y_t) + (1 - P(L_t | y_t)) * T
               │
               ▼
[ Update Latent Belief for t+1 ]
```

### 3.1 Prior Prediction (Emission Step)
Before the student answers the item at opportunity $t$:
$$P(C_t = 1) = P(L_t)(1 - P(S)) + (1 - P(L_t))P(G)$$

### 3.2 Evidence Update (Bayes' Posterior)
Upon observing the actual outcome $y_t \in \{0, 1\}$:
- **Case $y_t = 1$ (Correct Response):**
  $$P(L_t \mid y_t = 1) = \frac{P(L_t)(1 - P(S))}{P(C_t = 1)}$$
- **Case $y_t = 0$ (Incorrect Response):**
  $$P(L_t \mid y_t = 0) = \frac{P(L_t)P(S)}{1 - P(C_t = 1)}$$

### 3.3 Learning Transition Step
Before the next trial $t+1$, the student may learn the concept:
$$P(L_{t+1}) = P(L_t \mid y_t) + (1 - P(L_t \mid y_t)) P(T)$$

---

## 4. Parameter Estimation: Baum-Welch Expectation-Maximization

The parameters $\theta_k = (P(L_0), P(T), P(G), P(S))$ are estimated per skill across multiple independent student sequences $Y = \{Y^{(1)}, Y^{(2)}, \dots, Y^{(K)}\}$.

### 4.1 HMM Matrix Representation
- **Transition Matrix $A$ ($2 \times 2$):**
  $$A = \begin{bmatrix} 1 - P(T) & P(T) \\ 0 & 1 \end{bmatrix}$$
  *Note:* State 1 (Learned) is absorbing (the classic Corbett & Anderson formulation assumes no forgetting).
- **Emission Matrix $B$ ($2 \times 2$):**
  $$B = \begin{bmatrix} 1 - P(G) & P(G) \\ P(S) & 1 - P(S) \end{bmatrix}$$
  Row 0 corresponds to the unlearned state; Row 1 to the learned state.
- **Initial Prior Distribution $\pi$ ($1 \times 2$):**
  $$\pi = [1 - P(L_0), \, P(L_0)]$$

### 4.2 Scaled Forward-Backward Algorithm
To prevent floating-point underflow on long sequences ($T_k > 100$), the forward and backward passes use local scaling coefficients $c_t$:

- **Forward Scaling:**
  $$\alpha_1(i) = \pi_i B_i(y_1), \quad c_1 = \frac{1}{\sum_{i} \alpha_1(i)}, \quad \hat{\alpha}_1(i) = c_1 \alpha_1(i)$$
  For $t = 2, \dots, T$:
  $$\alpha_t(j) = \left[ \sum_i \hat{\alpha}_{t-1}(i) A_{ij} \right] B_j(y_t), \quad c_t = \frac{1}{\sum_j \alpha_t(j)}, \quad \hat{\alpha}_t(j) = c_t \alpha_t(j)$$

- **Sequence Log-Likelihood:**
  $$\log P(Y) = - \sum_{t=1}^T \log(c_t)$$

- **Backward Scaling:**
  $$\hat{\beta}_T(i) = c_T$$
  For $t = T-1, \dots, 1$:
  $$\hat{\beta}_t(i) = c_t \sum_j A_{ij} B_j(y_{t+1}) \hat{\beta}_{t+1}(j)$$

### 4.3 E-Step: Sufficient Statistics
For each sequence $k$:
- **Posterior State Probability $\gamma_t(i)$:**
  $$\gamma_t(i) = P(q_t = i \mid Y) = \frac{\hat{\alpha}_t(i) \hat{\beta}_t(i)}{\sum_j \hat{\alpha}_t(j) \hat{\beta}_t(j)}$$
- **Posterior Transition Probability $\xi_t(i, j)$:**
  $$\xi_t(i, j) = P(q_t = i, q_{t+1} = j \mid Y) = \frac{\hat{\alpha}_t(i) A_{ij} B_j(y_{t+1}) \hat{\beta}_{t+1}(j)}{\sum_{m} \sum_{n} \hat{\alpha}_t(m) A_{mn} B_n(y_{t+1}) \hat{\beta}_{t+1}(n)}$$

### 4.4 M-Step: Closed-Form Updates Across All Sequences
Accumulating expected counts across all $K$ student sequences:
1. **Initial Mastery:**
   $$\hat{P}(L_0) = \frac{\sum_{k=1}^K \gamma_1^{(k)}(1)}{K}$$
2. **Learning Transition:**
   $$\hat{P}(T) = \frac{\sum_{k=1}^K \sum_{t=1}^{T_k - 1} \xi_t^{(k)}(0, 1)}{\sum_{k=1}^K \sum_{t=1}^{T_k - 1} \gamma_t^{(k)}(0)}$$
3. **Guess Probability:**
   $$\hat{P}(G) = \frac{\sum_{k=1}^K \sum_{t: y_t = 1} \gamma_t^{(k)}(0)}{\sum_{k=1}^K \sum_{t=1}^{T_k} \gamma_t^{(k)}(0)}$$
4. **Slip Probability:**
   $$\hat{P}(S) = \frac{\sum_{k=1}^K \sum_{t: y_t = 0} \gamma_t^{(k)}(1)}{\sum_{k=1}^K \sum_{t=1}^{T_k} \gamma_t^{(k)}(1)}$$

### 4.5 Projected M-Step & Identifiability Invariant Enforcement
In `em.py`, bounds clamping is applied **during each iteration at the M-step** (Projected EM algorithm):
- Each parameter is projected onto $[\theta_{\min}, \theta_{\max}]$.
- If $P(G) + P(S) \ge 0.999$, parameters are symmetrically rescaled so $P(G) + P(S) \le 0.99$, guaranteeing that the emission distribution maintains cognitive consistency:
  $$P(C = 1 \mid \text{Learned}) > P(C = 1 \mid \text{Unlearned})$$

---

## 5. Sparse Skill Policy and Fallback Prior

In real educational benchmarks, skill interaction frequency exhibits a heavy-tailed power-law distribution. Rare skills with insufficient trials ($< 5$ sequences or $< 50$ total attempts) cannot reliably support independent 4-parameter estimation without severe over-fitting or boundary degeneracy.

**Policy Implementation:**
1. A global pooled fallback parameter set $\theta_{\text{fallback}}$ is estimated via EM across all training interactions.
2. Skills meeting the minimum criteria ($N_{\text{sequences}} \ge 5$, $N_{\text{obs}} \ge 50$) receive independent fits.
3. Sparse skills are assigned $\theta_{\text{fallback}}$ and explicitly tagged in model metadata with `status: "fallback"`.

---

## 6. Assumptions and Inherent Limitations

| Dimension | BKT Modeling Assumption | Pedagogical Reality & Limitation |
|---|---|---|
| **Cognitive State** | Discrete binary mastery ($L \in \{0, 1\}$). | Ignores partial knowledge, misconceptions, and procedural fluency. |
| **Skill Transfer** | Skills are strictly independent Markov chains. | Ignores prerequisite dependencies (e.g., *Arrays* accelerating *Linked Lists*). |
| **Item Difficulty** | All questions within a skill share identical $G$ and $S$. | Easy items and complex multi-step problems are treated identically. |
| **Forgetting** | Transition from mastered to unmastered is zero ($P(F) = 0$). | Forgetting occurs over long intervals without spaced repetition. |
| **Response Latency** | Time-to-first-response ($ms$) is ignored. | Fast correct answers indicate automaticity; slow correct answers indicate deduction. |
