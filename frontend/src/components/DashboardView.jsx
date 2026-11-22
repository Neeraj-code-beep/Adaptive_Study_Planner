import React from 'react';

export default function DashboardView({ onNavigate }) {
  const topics = [
    { name: 'Arrays & Dynamic Sizing', mastery: 94, state: 'Mastered', color: '#10b981', attempts: 24 },
    { name: 'Stack & Queue Evaluation', mastery: 89, state: 'Mastered', color: '#10b981', attempts: 18 },
    { name: 'Linked List Pointers', mastery: 84, state: 'Mastered', color: '#10b981', attempts: 22 },
    { name: 'Binary Trees & Traversals', mastery: 64, state: 'In Progress', color: '#3b82f6', attempts: 31 },
    { name: 'Binary Search Trees (BST)', mastery: 58, state: 'In Progress', color: '#3b82f6', attempts: 19 },
    { name: 'Graph BFS & DFS Traversal', mastery: 42, state: 'Remediation', color: '#f59e0b', attempts: 16 },
    { name: 'Dynamic Programming Memoization', mastery: 18, state: 'Prerequisite Gated', color: '#94a3b8', attempts: 6 },
  ];

  return (
    <div className="view-page">
      <div className="page-header">
        <div>
          <h2>Student Cognitive Dashboard</h2>
          <p className="page-lead">Real-time Bayesian Knowledge Tracing across curriculum concept sequences.</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => onNavigate('quiz')}>
            Start Adaptive Quiz
          </button>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-label">Latent Knowledge Mastery</span>
          <div className="stat-value text-primary">74.2%</div>
          <span className="stat-sub">Across 12 Data Structures concepts</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Questions Evaluated</span>
          <div className="stat-value text-dark">142</div>
          <span className="stat-sub">Empirical accuracy: 71.3%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Concepts Mastered</span>
          <div className="stat-value text-success">8 / 12</div>
          <span className="stat-sub">Threshold $P(L_t) \ge 0.85$</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">BKT Calibration (ECE)</span>
          <div className="stat-value text-info">0.69%</div>
          <span className="stat-sub">Reliability decile error</span>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card-box">
          <div className="box-header">
            <h3>Concept Mastery Breakdown</h3>
            <span className="badge-tag">BKT Updated</span>
          </div>
          <div className="mastery-list">
            {topics.map((t, idx) => (
              <div key={idx} className="mastery-item">
                <div className="item-meta">
                  <span className="item-title">{t.name}</span>
                  <div className="item-numbers">
                    <span className="item-state" style={{ color: t.color }}>{t.state}</span>
                    <span className="item-pct">{t.mastery}%</span>
                  </div>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${t.mastery}%`, backgroundColor: t.color }}></div>
                </div>
                <span className="item-attempts">{t.attempts} interaction opportunities logged</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card-box">
          <div className="box-header">
            <h3>Diagnostic Recommendation</h3>
            <span className="badge-priority">Highest Priority</span>
          </div>
          <div className="recommendation-callout">
            <div className="callout-icon">🎯</div>
            <div className="callout-body">
              <h4>Remediation Suggested: Graph BFS & DFS Traversal</h4>
              <p>
                Prerequisites (Queue and Trees) are satisfied ($P(L) \ge 0.84$), but recent diagnostic correctness dropped to 42%. Slip probability estimated at $0.09$.
              </p>
              <div className="callout-meta">
                <span>Estimated Time: 15 mins</span> &bull; <span>6 Diagnostic Questions</span>
              </div>
              <button className="btn btn-warning" onClick={() => onNavigate('quiz')}>
                Launch Graph Remediation Session
              </button>
            </div>
          </div>

          <div className="recent-log-box">
            <h4>Recent Opportunity Log</h4>
            <ul className="log-timeline">
              <li className="log-entry">
                <span className="log-badge correct">Correct (+0.08)</span>
                <span className="log-topic">BST Inorder Successor &bull; $P(L_t) \to 0.64$</span>
                <span className="log-time">12 mins ago</span>
              </li>
              <li className="log-entry">
                <span className="log-badge incorrect">Incorrect (-0.12)</span>
                <span className="log-topic">Graph Adjacency List Traversal &bull; $P(L_t) \to 0.42$</span>
                <span className="log-time">28 mins ago</span>
              </li>
              <li className="log-entry">
                <span className="log-badge correct">Correct (+0.06)</span>
                <span className="log-topic">Linked List Cycle Detection &bull; $P(L_t) \to 0.84$</span>
                <span className="log-time">1 hour ago</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
