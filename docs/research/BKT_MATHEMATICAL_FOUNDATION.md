# Mathematical Foundation of Bayesian Knowledge Tracing (BKT)

## 1. Introduction to Bayesian Knowledge Tracing

**Bayesian Knowledge Tracing (BKT)**, introduced by Albert T. Corbett and John R. Anderson in 1994, is a Hidden Markov Model (HMM) formulation designed to model the acquisition of a cognitive skill over an ordered sequence of learning opportunities.

In BKT, each skill/Knowledge Component is modeled as an independent two-state Markov chain:
- **State 0 (Unmastered / Not Known):** The student has not yet learned the skill.
- **State 1 (Mastered / Known):** The student has acquired the skill.

At each practice opportunity $t$, the student produces an observable binary response:
$$C_t \in \{0, 1\}$$
where $C_t = 1$ denotes a correct response on the first attempt without assistance, and $C_t = 0$ denotes an incorrect response or hint request.

---

## 2. The Four Core BKT Parameters

Standard BKT is defined by exactly **four parameters** per skill:

| Parameter | Mathematical Notation | Real-World Pedagogical Meaning | Typical Range in Literature |
| :--- | :--- | :--- | :--- |
| **Initial Knowledge (Prior)** | $P(L_0)$ | The probability that a student already knows the skill prior to any practice on this platform (background preparation). | $0.05 - 0.40$ |
| **Learning Rate (Transition)** | $P(T)$ | The probability that a student who does not know the skill transitions from the unlearned state to the learned state as a result of a practice opportunity. | $0.05 - 0.30$ |
| **Guess Probability** | $P(G)$ | The probability that a student who **does not** know the skill answers a question correctly by guessing or elimination. | $0.10 - 0.30$ |
| **Slip Probability** | $P(S)$ | The probability that a student who **does** know the skill answers a question incorrectly due to a typographical error, misreading, or lapse in attention. | $0.05 - 0.20$ |

> [!NOTE]
> Standard BKT assumes **no forgetting**: once a skill is mastered, the transition probability from mastered back to unmastered is assumed to be zero ($P(F) = 0$).

---

## 3. Mathematical Update Equations

Updating a student's knowledge state proceeds in two distinct steps at each opportunity $t$:
1. **Evidence Update (Posterior Calculation):** Adjust mastery probability given the observed response $C_t$ using Bayes' theorem.
2. **Transition Forecast (Next State Prediction):** Account for the possibility of learning between practice opportunities.

### Step 1: Posterior Update Given Observed Evidence

Let $P(L_t)$ denote the prior probability that the student knows the skill at step $t$ (before observing response $C_t$).

#### Case A: The Student Answers Correctly ($C_t = 1$)
Applying Bayes' theorem:
$$P(L_t \mid C_t = 1) = \frac{P(C_t = 1 \mid L_t = 1) \cdot P(L_t)}{P(C_t = 1)}$$

Expanding the terms:
- Likelihood of correct answer given mastery: $P(C_t = 1 \mid L_t = 1) = 1 - P(S)$
- Likelihood of correct answer given non-mastery: $P(C_t = 1 \mid L_t = 0) = P(G)$
- Total probability of a correct answer:
  $$P(C_t = 1) = P(L_t)(1 - P(S)) + (1 - P(L_t))P(G)$$

Therefore:
$$P(L_t \mid C_t = 1) = \frac{P(L_t)(1 - P(S))}{P(L_t)(1 - P(S)) + (1 - P(L_t))P(G)}$$

#### Case B: The Student Answers Incorrectly ($C_t = 0$)
Applying Bayes' theorem:
$$P(L_t \mid C_t = 0) = \frac{P(C_t = 0 \mid L_t = 1) \cdot P(L_t)}{P(C_t = 0)}$$

Expanding the terms:
- Likelihood of incorrect answer given mastery: $P(C_t = 0 \mid L_t = 1) = P(S)$
- Likelihood of incorrect answer given non-mastery: $P(C_t = 0 \mid L_t = 0) = 1 - P(G)$
- Total probability of an incorrect answer:
  $$P(C_t = 0) = P(L_t)P(S) + (1 - P(L_t))(1 - P(G))$$

Therefore:
$$P(L_t \mid C_t = 0) = \frac{P(L_t)P(S)}{P(L_t)P(S) + (1 - P(L_t))(1 - P(G))}$$

---

### Step 2: Transition / Learning Forecast

After conditioning on the observation, the student undergoes a practice learning opportunity. The probability of knowing the skill at the *next* time step ($t+1$) accounts for the possibility that an unmastered student learned the concept during this trial:

$$P(L_{t+1}) = P(L_t \mid C_t) + \Big(1 - P(L_t \mid C_t)\Big) \cdot P(T)$$

---

### Step 3: Predicting Next-Step Observed Correctness

The expected probability that the student will answer the *next* question ($t+1$) correctly is:
$$P(C_{t+1} = 1) = P(L_{t+1})\cdot (1 - P(S)) + (1 - P(L_{t+1}))\cdot P(G)$$

---

## 4. Fundamental Conceptual Distinctions

It is essential to distinguish between three core probabilities in Knowledge Tracing:

1. **Probability of Knowing a Skill ($P(L_t)$):**  
   The latent, unobservable belief that the student possesses the underlying conceptual competency.
2. **Probability of Answering Correctly ($P(C_t = 1)$):**  
   The observable behavioral outcome. Always differs from $P(L_t)$ due to guessing $P(G)$ and slipping $P(S)$. Even if $P(L_t) = 1.0$, $P(C_t = 1) = 1 - P(S) < 1.0$.
3. **Probability of Learning a Skill ($P(T)$):**  
   The transition rate representing the likelihood of acquiring the concept during an instructional opportunity given that it was previously unmastered.

---

## 5. Step-by-Step Numerical Walkthrough

> [!IMPORTANT]
> The parameters below are **illustrative parameters** chosen to demonstrate the mathematical mechanics of BKT step-by-step. In actual application, parameters are estimated empirically from benchmark datasets (e.g., via Expectation-Maximization / Baum-Welch).

### Illustrative Parameter Setup:
- **Prior Mastery:** $P(L_0) = 0.20$ (20% initial chance of knowing the concept)
- **Learning Rate:** $P(T) = 0.15$ (15% chance of learning from an attempt)
- **Guess Rate:** $P(G) = 0.25$ (25% chance of guessing correctly on multiple-choice)
- **Slip Rate:** $P(S) = 0.10$ (10% chance of slipping despite knowing the concept)

---

### Opportunity 1: Student Answers Correctly ($C_1 = 1$)

#### Step 1.1: Calculate Prior Probability of Correct Response
$$P(C_1 = 1) = P(L_0)(1 - P(S)) + (1 - P(L_0))P(G)$$
$$P(C_1 = 1) = 0.20 \cdot (1 - 0.10) + (1 - 0.20) \cdot 0.25 = 0.20 \cdot 0.90 + 0.80 \cdot 0.25 = 0.18 + 0.20 = 0.38$$
*(The student had a 38% chance of answering correctly).*

#### Step 1.2: Compute Posterior Mastery Given Correct Response
$$P(L_1 \mid C_1 = 1) = \frac{P(L_0)(1 - P(S))}{P(C_1 = 1)} = \frac{0.18}{0.38} \approx 0.4737$$
*(Because the student answered correctly, our belief in their mastery increases from 20% to 47.37%).*

#### Step 1.3: Forecast Mastery for Next Opportunity ($t = 2$)
$$P(L_2) = P(L_1 \mid C_1 = 1) + (1 - P(L_1 \mid C_1 = 1)) \cdot P(T)$$
$$P(L_2) = 0.4737 + (1 - 0.4737) \cdot 0.15 = 0.4737 + 0.5263 \cdot 0.15 = 0.4737 + 0.0789 \approx 0.5526$$
*(Factoring in the learning opportunity, predicted mastery entering Opportunity 2 is **55.26%**).*

#### Step 1.4: Forecast Predicted Correctness on Next Question
$$P(C_2 = 1) = P(L_2)(1 - P(S)) + (1 - P(L_2))P(G)$$
$$P(C_2 = 1) = 0.5526 \cdot 0.90 + (1 - 0.5526) \cdot 0.25 = 0.4973 + 0.4474 \cdot 0.25 = 0.4973 + 0.1119 \approx 0.6092$$
*(Probability of answering the second question correctly rises to **60.92%**).*

---

### Opportunity 2: Student Answers Incorrectly ($C_2 = 0$)

Now, on the second question, the student answers **incorrectly** ($C_2 = 0$).

#### Step 2.1: Prior Probability of Incorrect Response
$$P(C_2 = 0) = 1 - P(C_2 = 1) = 1 - 0.6092 = 0.3908$$

#### Step 2.2: Compute Posterior Mastery Given Incorrect Response
$$P(L_2 \mid C_2 = 0) = \frac{P(L_2) \cdot P(S)}{P(C_2 = 0)} = \frac{0.5526 \cdot 0.10}{0.3908} = \frac{0.05526}{0.3908} \approx 0.1414$$
*(Notice the dramatic drop: because the student failed, our belief that they had mastered the concept drops from 55.26% to **14.14%**).*

#### Step 2.3: Forecast Mastery for Opportunity 3 ($t = 3$)
$$P(L_3) = P(L_2 \mid C_2 = 0) + (1 - P(L_2 \mid C_2 = 0)) \cdot P(T)$$
$$P(L_3) = 0.1414 + (1 - 0.1414) \cdot 0.15 = 0.1414 + 0.8586 \cdot 0.15 = 0.1414 + 0.1288 \approx 0.2702$$
*(Predicted mastery entering Opportunity 3 recovers slightly to **27.02%** due to the learning opportunity).*

---

## 6. Assumptions and Limitations of Standard BKT

| Assumption | Description | Real-World Limitation |
| :--- | :--- | :--- |
| **Binary Latent State** | Knowledge is strictly discrete: a student either fully knows or does not know a skill. | Ignores partial understanding, intermediate mental models, and degrees of fluency. |
| **Single-Skill Independence** | Skills are treated as isolated Markov chains with zero cross-skill transfer. | In computer science, mastering *Pointers* directly accelerates learning *Linked Lists*. BKT cannot model this transfer natively. |
| **Identical Item Difficulty** | All questions mapped to a skill share identical guess $P(G)$ and slip $P(S)$ rates. | A trivial array indexing question has different difficulty than an array dynamic reallocation question. |
| **No Forgetting** | Transition probability from learned to unlearned is zero ($P(F) = 0$). | In reality, students forget concepts over time if not periodically practiced. |

---

## 7. Why BKT is the Ideal Baseline for our B.Tech CSE Project

Despite its simplifications, BKT remains the gold standard baseline for educational data mining for four decisive reasons:

1. **Complete Interpretability:** Unlike deep neural networks, every BKT parameter has an intuitive educational meaning ($P(L_0), P(T), P(G), P(S)$). Instructors and students can understand exactly why a recommendation was made.
2. **Low Sample Complexity:** BKT can be fitted accurately with modest interaction counts per skill ($50-100$ responses), whereas DKT requires tens of thousands of continuous multi-skill sequences.
3. **Real-Time Edge Inference:** Calculating BKT updates requires only elementary floating-point arithmetic (sub-millisecond latency on a standard CPU), ensuring seamless integration into our Express/FastAPI architecture.
4. **Pedagogical Alignment:** BKT directly outputs an interpretable mastery probability $P(L_t) \in [0, 1]$, which translates into clean threshold-based recommendation rules ($P(L_t) < 0.70 \implies \text{Remediate}$).
