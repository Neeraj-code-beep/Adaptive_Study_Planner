# Application Screenshot Inventory & Interface Audit

**Project:** Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning  
**Workspace:** `N:\adaptive-study-planner`  
**Audit Date:** November 23, 2026  
**Inspection Environment:** Windows 10/11, Google Chrome Headless (1280×900 Viewport), React 18 / Vite v6.4.6, Express v4.21.2, FastAPI v0.165.0  

---

## 1. Executive Summary

All primary screens requested for the academic project report have been fully rendered and captured directly from the live application running on the Vite development server (`http://localhost:5173/`).

Every application screenshot represents the actual browser viewport rendered with high typography standards, responsive CSS layout, mathematical notation, and interactive states.

---

## 2. Inventory of Captured Screenshots

### 2.1 Screenshot 1: Application Landing & Architecture Topology
- **Filename:** `01-homepage.png`
- **File Path:** `docs/report/assets/screenshots/01-homepage.png`
- **Resolution & Size:** 1280 × 900 px, 101.8 KB, RGB
- **Application Route:** `http://localhost:5173/?tab=home`
- **Rendered Component:** `App.jsx` + `Navbar.jsx`
- **What it Demonstrates:**
  - Official project header: *"Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning"*.
  - Academic status badge: `Phase 2–6 Completed • Academic Prototype`.
  - Architecture overview cards for **Student Learning & Dashboard**, **Knowledge Tracing Engine**, and **Adaptive Recommendations**.
  - Live Service Topology bar with operational port mapping (`Frontend: 5173`, `Backend API: 5000`, `ML Service: 8000`).
  - Project footer crediting Neeraj Mishra (3rd Year B.Tech CSE, KMCLU Lucknow).
- **Implementation Status:** Fully functional navigation hub.

---

### 2.2 Screenshot 2: Student Cognitive Dashboard
- **Filename:** `02-student-dashboard.png`
- **File Path:** `docs/report/assets/screenshots/02-student-dashboard.png`
- **Resolution & Size:** 1280 × 900 px, 125.2 KB, RGB
- **Application Route:** `http://localhost:5173/?tab=dashboard`
- **Rendered Component:** `DashboardView.jsx`
- **What it Demonstrates:**
  - High-level metric summary:
    - **Latent Knowledge Mastery:** `74.2%` across 12 Data Structures concepts.
    - **Questions Evaluated:** `142` (Empirical accuracy: `71.3%`).
    - **Concepts Mastered:** `8 / 12` (Threshold $P(L_t) \ge 0.85$).
    - **BKT Calibration Error (ECE):** `0.69%`.
  - Color-coded progress bars for individual concepts (Arrays 94%, Stacks & Queues 89%, Linked Lists 84%, Binary Trees 64%, BST 58%, Graph BFS/DFS 42%, Dynamic Programming 18%).
  - Active remediation callout banner recommending Graph Traversal revision.
  - Recent interaction opportunity timeline with BKT posterior updates ($P(L_t) \to 0.64$, $P(L_t) \to 0.42$).
- **Implementation Status:** Fully rendered student performance view.

---

### 2.3 Screenshot 3: Curriculum Concept Prerequisite Graph (DAG)
- **Filename:** `03-topic-selection.png`
- **File Path:** `docs/report/assets/screenshots/03-topic-selection.png`
- **Resolution & Size:** 1280 × 900 px, 118.0 KB, RGB
- **Application Route:** `http://localhost:5173/?tab=topics`
- **Rendered Component:** `TopicsView.jsx`
- **What it Demonstrates:**
  - 4-Tier topological layout of 12 Data Structures & Algorithms concepts:
    - **Tier 1 (Foundations):** Arrays & Dynamic Sizing (Mastered at 94%).
    - **Tier 2 (Linear Structures):** Singly & Doubly Linked Lists (84%), Stacks & Queues (89%), Divide & Conquer Sorting (91%).
    - **Tier 3 (Hierarchical Trees & Hashing):** Binary Trees & Traversals (64%), BST (58%), Hash Tables (78%), Recursion (82%).
    - **Tier 4 & 5 (Graphs & Dynamic Programming):** Heaps (52%), Graph Representations (42%), Graph BFS/DFS (38%), Dynamic Programming (18% - Locked).
  - Explicit prerequisite dependency labels for every node.
  - Cognitive prerequisite gating enforcement (DP is marked *"Prerequisite Gated"* with practice locked until recursion mastery reaches 85%).
- **Implementation Status:** Fully rendered curriculum navigation interface.

---

### 2.4 Screenshot 4: Adaptive Quiz & Practice Interface
- **Filename:** `04-practice-interface.png`
- **File Path:** `docs/report/assets/screenshots/04-practice-interface.png`
- **Resolution & Size:** 1280 × 900 px, 63.9 KB, RGB
- **Application Route:** `http://localhost:5173/?tab=quiz`
- **Rendered Component:** `QuizView.jsx`
- **What it Demonstrates:**
  - Active assessment header: Topic (*Binary Search Trees*), Opportunity counter (*#4*), Difficulty (*Intermediate*), and active timer (*01:45*).
  - Pedagogical question prompt: Worst-case time complexity of searching in an unbalanced BST.
  - 4 multiple-choice options with distinct interactive hover/selection states.
  - "Request Pedagogical Hint" action explaining degenerate tree structures.
  - Post-submission BKT evidence update banner demonstrating posterior calculation $P(L_3) = 0.58 \to P(L_4) = 0.71$.
- **Implementation Status:** Fully interactive student practice component.

---

### 2.5 Screenshot 5: BKT Latent Mastery Progression Trajectory
- **Filename:** `05-mastery-visualization.png`
- **File Path:** `docs/report/assets/screenshots/05-mastery-visualization.png`
- **Resolution & Size:** 1280 × 900 px, 101.7 KB, RGB
- **Application Route:** `http://localhost:5173/?tab=mastery`
- **Rendered Component:** `MasteryView.jsx`
- **What it Demonstrates:**
  - Model parameter header: $P(L_0) = 0.250$, $P(T) = 0.148$, $P(G) = 0.182$, $P(S) = 0.094$.
  - 7-step tabular interaction trace across opportunities $t = 0 \dots 6$:
    - Shows prior $P(L_t)$, binary correctness response $y_t \in \{0, 1\}$, Bayesian posterior $P(L_t \mid y_t)$, and transition update $P(L_{t+1})$.
    - Highlights recovery dynamics after slip on $t=3$ ($0.64 \to 0.52 \to 0.71$).
    - Demonstrates achievement of mastery threshold ($P(L_t) \ge 0.85$) at opportunity $t=6$ ($0.920$).
  - Pedagogical gating rule explanation.
- **Implementation Status:** Complete analytical progression visualization.

---

### 2.6 Screenshot 6: Adaptive Study Recommendations Queue
- **Filename:** `06-recommendations.png`
- **File Path:** `docs/report/assets/screenshots/06-recommendations.png`
- **Resolution & Size:** 1280 × 900 px, 87.4 KB, RGB
- **Application Route:** `http://localhost:5173/?tab=recommendations`
- **Rendered Component:** `RecommendationsView.jsx`
- **What it Demonstrates:**
  - Priority-ranked personalized study feed:
    - **Rank 1 (Urgent Remediation - High Priority):** *Graph BFS & DFS Algorithms* (Current mastery: 38%). Prerequisites satisfied; targeted review needed.
    - **Rank 2 (Frontier Learning - Medium Priority):** *Heaps & Priority Queues* (Current mastery: 52%). Next sequential topic ready for introduction.
    - **Rank 3 (Prerequisite Gated - Locked):** *Dynamic Programming (1D Memoization)* (Current mastery: 18%). Locked until Recursion mastery reaches $\ge 85\%$.
  - Pedagogical rationale, estimated time investment, and direct action triggers.
- **Implementation Status:** Complete recommendation queue interface.

---

### 2.7 Additional Service Runtime Screenshots
- `02-ml-service-api-docs.png` (28.1 KB): FastAPI live Swagger UI interactive documentation on port 8000.
- `03-backend-health-endpoint.png` (10.3 KB): Express backend `/health` diagnostic probe on port 5000.

---

## 3. Summary of Files Generated

| Target Report Figure | Screenshot File | Dimensions | Status |
|---|---|---|---|
| Figure 6.2: System Architecture & Landing | `01-homepage.png` | 1280 × 900 | Captured & Verified |
| Figure 6.3: Student Diagnostic Dashboard | `02-student-dashboard.png` | 1280 × 900 | Captured & Verified |
| Figure 6.4: Prerequisite DAG View | `03-topic-selection.png` | 1280 × 900 | Captured & Verified |
| Figure 6.5: Adaptive Practice Interface | `04-practice-interface.png` | 1280 × 900 | Captured & Verified |
| Figure 6.6: BKT Mastery Progression Trace | `05-mastery-visualization.png` | 1280 × 900 | Captured & Verified |
| Figure 6.7: Personalized Study Queue | `06-recommendations.png` | 1280 × 900 | Captured & Verified |
