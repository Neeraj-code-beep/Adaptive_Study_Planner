# Application Topic Structure & Prerequisite Graph (Data Structures)

## 1. Domain Scope & Pedagogical Rationale

The primary subject for our adaptive study planning application is **Data Structures and Algorithms (DSA)**, aligned with the 3rd-year B.Tech Computer Science and Engineering curriculum.

To support both **fine-grained knowledge estimation** and **prerequisite-guided recommendations**, the domain is organized into **12 foundational to intermediate topics** structured as a **Directed Acyclic Graph (DAG)**.

---

## 2. Topic Prerequisite Dependency Graph (DAG)

```text
                     ┌──────────────────┐
                     │ 1. Arrays & Dyn. │
                     │      Arrays      │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ 2. Pointers &    │
                     │  Memory Mgmt.    │
                     └────────┬─────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐
│ 3. Singly Linked      │           │ 11. Searching         │
│         Lists         │           │  (Linear & Binary)    │
└───────────┬───────────┘           └───────────┬───────────┘
            │                                   │
      ┌─────┴──────────────┐                    ▼
      ▼                    ▼           ┌───────────────────────┐
┌───────────┐        ┌───────────┐     │ 12. Sorting           │
│ 4. Doubly │        │ 5. Stacks │     │ (Merge, Quick, Heap)  │
│  & Circ.  │        └─────┬─────┘     └───────────────────────┘
│  Lists    │              │
└───────────┘        ┌─────┴─────────────┐
                     ▼                   ▼
              ┌─────────────┐     ┌─────────────┐
              │  6. Queues  │     │ 7. Binary   │
              │  & Deques   │     │ Trees &     │
              └─────────────┘     │ Traversals  │
                                  └──────┬──────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
         ┌─────────────────────┐                   ┌─────────────────────┐
         │ 8. Binary Search    │                   │ 9. Priority Queues  │
         │    Trees (BST)      │                   │    & Binary Heaps   │
         └──────────┬──────────┘                   └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ 10. Graph           │
         │ Representations     │
         │   (BFS / DFS)       │
         └─────────────────────┘
```

---

## 3. Detailed Topic Definitions

| # | Topic ID | Topic Name | Description | Prerequisites | Question Types |
|---|---|---|---|---|---|
| 1 | `dsa_arrays` | Arrays & Dynamic Arrays | Contiguous memory, indexing, insertions, deletions, amortized resizing, and time complexity. | *None (Foundational)* | Multiple-choice indexing, code tracing, amortized complexity analysis. |
| 2 | `dsa_pointers` | Pointers & Memory Management | Pointer arithmetic, memory addresses, dynamic allocation (`malloc`/`free`, `new`/`delete`), and memory leaks. | `dsa_arrays` | Pointer dereferencing output, memory allocation trace. |
| 3 | `dsa_singly_linked_lists` | Singly Linked Lists | Node representation, head pointer, traversal, inserting at head/tail, and node deletion. | `dsa_pointers` | Pointer manipulation tracing, bug identification, time complexity. |
| 4 | `dsa_doubly_linked_lists` | Doubly & Circular Linked Lists | Two-way node pointers (`next`, `prev`), circular links, sentinel nodes, and bidirectional traversal. | `dsa_singly_linked_lists` | Pointer reassignment sequence, circular loop detection. |
| 5 | `dsa_stacks` | Stacks & Applications | LIFO principle, push/pop operations, array and linked-list implementations, expression evaluation, matching parentheses. | `dsa_singly_linked_lists` | State of stack after operations, infix to postfix conversions. |
| 6 | `dsa_queues` | Queues & Deques | FIFO principle, enqueue/dequeue, circular queue array implementation, double-ended queues. | `dsa_stacks`, `dsa_arrays` | Circular queue front/rear index calculations, operation tracing. |
| 7 | `dsa_binary_trees` | Binary Trees & Traversals | Hierarchical node structures, height, depth, full/complete binary trees, preorder, inorder, postorder, and level-order traversals. | `dsa_stacks`, `dsa_queues` | Traversal sequence reconstruction, tree property calculation. |
| 8 | `dsa_binary_search_trees` | Binary Search Trees (BST) | BST invariant ($L < Node < R$), search, insertion, deletion (predecessor/successor replacement), and balance considerations. | `dsa_binary_trees` | Inorder sequence identification, node deletion pointer rearrangement. |
| 9 | `dsa_heaps` | Priority Queues & Heaps | Min/Max heap properties, array-based tree representation, heapify up/down, insertion, extract-min/max in $O(\log n)$. | `dsa_binary_trees`, `dsa_arrays` | Array representation to tree conversion, heapify step tracing. |
| 10 | `dsa_graphs` | Graph Representations | Vertices, edges, adjacency matrix vs adjacency list, Breadth-First Search (BFS), and Depth-First Search (DFS). | `dsa_queues`, `dsa_binary_trees` | Adjacency matrix construction, BFS/DFS visitation order. |
| 11 | `dsa_searching` | Searching Algorithms | Linear search ($O(n)$), binary search on sorted arrays ($O(\log n)$), loop invariants, and boundary conditions. | `dsa_arrays` | Binary search step trace, index comparison count. |
| 12 | `dsa_sorting` | Sorting Algorithms | Bubble/Selection/Insertion sort ($O(n^2)$), Merge Sort ($O(n \log n)$ divide-and-conquer), and Quick Sort partitioning. | `dsa_arrays`, `dsa_searching` | Pass-by-pass array trace, stability analysis, best/worst case complexity. |

---

## 4. Mapping Application Topics to Knowledge Tracing Components

In our knowledge tracing engine:
1. **Knowledge Component Representation:** Each of the 12 topics is assigned an independent BKT model instance with its own parameters:
   $$\theta_k = \Big( P(L_0^k), P(T^k), P(G^k), P(S^k) \Big)$$
2. **Student State Vector:** At any point in time, a student $u$ has a topic mastery vector:
   $$\mathbf{M}_u = \big[ P(L^1), P(L^2), \dots, P(L^{12}) \big] \in [0, 1]^{12}$$
3. **Prerequisite Gating Rule:**
   Before topic $k_j$ can be recommended for study:
   $$\forall p \in \text{Prerequisites}(k_j), \quad P(L^p) \ge \tau_{\text{mastery}} \quad (\text{e.g., } 0.75)$$
   If any prerequisite $p$ falls below the threshold, the system automatically intervenes and recommends remedial practice on prerequisite $p$.
