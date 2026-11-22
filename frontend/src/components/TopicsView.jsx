import React from 'react';

export default function TopicsView({ onNavigate }) {
  const dagNodes = [
    { id: 'arrays', label: '1. Arrays & Vectors', level: 1, mastery: 94, status: 'Mastered', prereqs: [] },
    { id: 'linked_lists', label: '2. Singly & Doubly Linked Lists', level: 2, mastery: 84, status: 'Mastered', prereqs: ['Arrays'] },
    { id: 'stacks_queues', label: '3. Stacks & Queues', level: 2, mastery: 89, status: 'Mastered', prereqs: ['Arrays'] },
    { id: 'trees', label: '4. Binary Trees & Traversals', level: 3, mastery: 64, status: 'In Progress', prereqs: ['Linked Lists', 'Stacks & Queues'] },
    { id: 'bst', label: '5. Binary Search Trees (BST)', level: 3, mastery: 58, status: 'In Progress', prereqs: ['Binary Trees'] },
    { id: 'heap', label: '6. Heaps & Priority Queues', level: 4, mastery: 52, status: 'In Progress', prereqs: ['Binary Trees'] },
    { id: 'graphs', label: '7. Graph Representations (Adj List)', level: 4, mastery: 42, status: 'Needs Remediation', prereqs: ['Stacks & Queues', 'Binary Trees'] },
    { id: 'graph_traversal', label: '8. Graph BFS & DFS Algorithms', level: 4, mastery: 38, status: 'Needs Remediation', prereqs: ['Graph Representations'] },
    { id: 'hashing', label: '9. Hash Tables & Collision Handling', level: 3, mastery: 78, status: 'In Progress', prereqs: ['Arrays', 'Linked Lists'] },
    { id: 'sorting', label: '10. Divide & Conquer Sorting', level: 2, mastery: 91, status: 'Mastered', prereqs: ['Arrays'] },
    { id: 'recursion', label: '11. Recursion & Backtracking', level: 3, mastery: 82, status: 'In Progress', prereqs: ['Stacks & Queues'] },
    { id: 'dp', label: '12. Dynamic Programming (1D & 2D)', level: 5, mastery: 18, status: 'Prerequisite Gated', prereqs: ['Recursion', 'Divide & Conquer'] },
  ];

  return (
    <div className="view-page">
      <div className="page-header">
        <div>
          <h2>Curriculum Concept Prerequisite Graph (DAG)</h2>
          <p className="page-lead">
            Topological ordering of Data Structures concepts. Gating constraints enforce prerequisite mastery ($P(L_t) \ge 0.80$) before advanced nodes unlock.
          </p>
        </div>
        <div className="header-actions">
          <span className="badge-legend mastered">● Mastered (&ge;80%)</span>
          <span className="badge-legend progress">● In Progress (50-79%)</span>
          <span className="badge-legend remediation">● Needs Revision (&lt;50%)</span>
          <span className="badge-legend locked">● Gated / Locked</span>
        </div>
      </div>

      <div className="dag-container">
        <div className="dag-layers">
          <div className="dag-column">
            <span className="layer-title">Tier 1: Foundations</span>
            {dagNodes.filter(n => n.level === 1).map(node => (
              <div key={node.id} className="dag-card mastered">
                <div className="dag-card-header">
                  <h4>{node.label}</h4>
                  <span className="mastery-pill">{node.mastery}%</span>
                </div>
                <p className="dag-prereqs">Prerequisites: None (Root)</p>
                <div className="dag-card-footer">
                  <span className="status-label text-success">✓ Complete</span>
                  <button className="btn-sm" onClick={() => onNavigate('quiz')}>Practice</button>
                </div>
              </div>
            ))}
          </div>

          <div className="dag-column">
            <span className="layer-title">Tier 2: Linear Structures</span>
            {dagNodes.filter(n => n.level === 2).map(node => (
              <div key={node.id} className={`dag-card ${node.mastery >= 80 ? 'mastered' : 'progress'}`}>
                <div className="dag-card-header">
                  <h4>{node.label}</h4>
                  <span className="mastery-pill">{node.mastery}%</span>
                </div>
                <p className="dag-prereqs">Prereqs: {node.prereqs.join(', ')}</p>
                <div className="dag-card-footer">
                  <span className="status-label text-success">✓ Unlocked</span>
                  <button className="btn-sm" onClick={() => onNavigate('quiz')}>Review</button>
                </div>
              </div>
            ))}
          </div>

          <div className="dag-column">
            <span className="layer-title">Tier 3: Hierarchical Trees</span>
            {dagNodes.filter(n => n.level === 3).map(node => (
              <div key={node.id} className={`dag-card ${node.mastery >= 50 ? 'progress' : 'remediation'}`}>
                <div className="dag-card-header">
                  <h4>{node.label}</h4>
                  <span className="mastery-pill">{node.mastery}%</span>
                </div>
                <p className="dag-prereqs">Prereqs: {node.prereqs.join(', ')}</p>
                <div className="dag-card-footer">
                  <span className="status-label text-primary">In Progress</span>
                  <button className="btn-sm btn-primary-sm" onClick={() => onNavigate('quiz')}>Train</button>
                </div>
              </div>
            ))}
          </div>

          <div className="dag-column">
            <span className="layer-title">Tier 4 & 5: Graphs & DP</span>
            {dagNodes.filter(n => n.level >= 4).map(node => (
              <div key={node.id} className={`dag-card ${node.status === 'Prerequisite Gated' ? 'locked' : 'remediation'}`}>
                <div className="dag-card-header">
                  <h4>{node.label}</h4>
                  <span className="mastery-pill">{node.mastery}%</span>
                </div>
                <p className="dag-prereqs">Prereqs: {node.prereqs.join(', ')}</p>
                <div className="dag-card-footer">
                  <span className={`status-label ${node.status === 'Prerequisite Gated' ? 'text-muted' : 'text-warning'}`}>
                    {node.status}
                  </span>
                  <button
                    className={`btn-sm ${node.status === 'Prerequisite Gated' ? 'disabled' : 'btn-warning-sm'}`}
                    disabled={node.status === 'Prerequisite Gated'}
                    onClick={() => onNavigate('quiz')}
                  >
                    {node.status === 'Prerequisite Gated' ? '🔒 Locked' : 'Remediate'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
