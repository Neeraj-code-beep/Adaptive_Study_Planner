# Foundational Research Papers and Technical References

This document records the seminal research literature foundational to Bayesian Knowledge Tracing, Deep Knowledge Tracing, and modern attentive educational modeling.

---

## 1. Bayesian Knowledge Tracing Foundation

### Paper 1: Student Modeling in an Intelligent Tutoring System
- **Authors:** Albert T. Corbett, John R. Anderson
- **Year:** 1994
- **Publication Venue:** *User Modeling and User-Adapted Interaction (UMUAI)*, Vol. 4, Issue 4, pp. 253–278
- **Publisher:** Springer
- **Official DOI:** [10.1007/BF01099821](https://doi.org/10.1007/BF01099821)
- **Main Contribution:** Introduced Bayesian Knowledge Tracing (BKT) formulated as a two-state Hidden Markov Model (HMM) tracking student mastery of cognitive skills through four distinct parameters: prior knowledge $P(L_0)$, learning transition $P(T)$, guess probability $P(G)$, and slip probability $P(S)$. Demonstrated empirical effectiveness in the ACT Programming Tutor (LISP and Geometry).
- **Direct Relevance to Our Project:** Provides the mathematical foundation and parameter equations for our baseline Knowledge Tracing engine in Phase 4.

---

## 2. Deep Knowledge Tracing (DKT)

### Paper 2: Deep Knowledge Tracing
- **Authors:** Chris Piech, Jonathan Bassen, Jonathan Huang, Surya Ganguli, Mert Sahami, Leonidas J. Guibas, Jascha Sohl-Dickstein
- **Year:** 2015
- **Publication Venue:** *Advances in Neural Information Processing Systems 28 (NIPS 2015)*, pp. 505–513
- **Official arXiv Link:** [arXiv:1506.05908](https://arxiv.org/abs/1506.05908)
- **Main Contribution:** First application of deep recurrent neural networks (RNN and LSTM) to Knowledge Tracing. Formulated student interaction logs as sequences of one-hot encoded question-correctness tuples $(q_t, c_t)$ to predict student performance on future problems across all skills simultaneously without requiring expert-crafted concept prerequisite maps. Reported a ~25% AUC improvement over standard BKT on ASSISTments.
- **Direct Relevance to Our Project:** Serves as the primary advanced comparative architecture for our research roadmap once the BKT baseline is validated.

---

## 3. Self-Attentive Knowledge Tracing (SAKT)

### Paper 3: A Self-Attentive Model for Knowledge Tracing
- **Authors:** Shalini Pandey, George Karypis
- **Year:** 2019
- **Publication Venue:** *12th International Conference on Educational Data Mining (EDM 2019)*
- **Official arXiv Link:** [arXiv:1907.06837](https://arxiv.org/abs/1907.06837)
- **Main Contribution:** Replaced recurrent neural networks with Transformer self-attention mechanisms for Knowledge Tracing. SAKT models the direct relevance of past student interactions to a current question using multi-head attention, mitigating RNN gradient vanishing across long interaction histories while improving computational training efficiency.
- **Direct Relevance to Our Project:** Highlights the importance of attention mechanisms over student history for capturing non-Markovian learning dependencies.

---

## 4. Context-Aware Attentive Knowledge Tracing (AKT)

### Paper 4: Context-Aware Attentive Knowledge Tracing
- **Authors:** Aritra Ghosh, Neil Heffernan, Andrew S. Lan
- **Year:** 2020
- **Publication Venue:** *Proceedings of the AAAI Conference on Human Computation and Crowdsourcing (HCOMP / AAAI 2020)*
- **Official arXiv Link:** [arXiv:2007.12324](https://arxiv.org/abs/2007.12324)
- **Main Contribution:** Extended attention models by introducing monotonic exponential decay attention and context-aware embeddings combining question content difficulty and concept identifiers. Outperformed both DKT and SAKT on ASSISTments benchmarks while maintaining interpretable attention heatmaps.
- **Direct Relevance to Our Project:** Informs how question difficulty embeddings can enrich concept-level mastery estimates.

---

## 5. Knowledge Tracing Surveys

### Paper 5: Knowledge Tracing: A Survey
- **Authors:** Ghodai Abdelrahman, Qing Wang, Bernardo Nunes
- **Year:** 2023
- **Publication Venue:** *ACM Computing Surveys (CSUR)*, Vol. 55, Issue 11, Article 224, pp. 1–37
- **Publisher:** Association for Computing Machinery (ACM)
- **Official DOI:** [10.1145/3569576](https://doi.org/10.1145/3569576) | [arXiv:2201.06953](https://arxiv.org/abs/2201.06953)
- **Main Contribution:** Comprehensive taxonomy of Knowledge Tracing models, classifying approaches into probabilistic models (BKT, PFA), deep sequential models (DKT, DKVMN), and attention-based models (SAKT, AKT). Synthesizes standardized datasets, open-source benchmarking toolkits (pyBKT, pyKT), evaluation metrics (AUC, RMSE), and open research challenges.
- **Direct Relevance to Our Project:** Guides our evaluation methodology, data preprocessing rigor, and recommendation design.
