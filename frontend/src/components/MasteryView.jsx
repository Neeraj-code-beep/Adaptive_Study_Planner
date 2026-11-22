import React from 'react';

export default function MasteryView({ onNavigate }) {
  const steps = [
    { stepIndex: 0, prior: 0.25, correct: null, posterior: 0.25, note: 'Prior Initialization P(L₀)' },
    { stepIndex: 1, prior: 0.25, correct: 1, posterior: 0.46, note: 'Correct (y₁ = 1) → Evidence update + transition' },
    { stepIndex: 2, prior: 0.46, correct: 1, posterior: 0.64, note: 'Correct (y₂ = 1) → Evidence update + transition' },
    { stepIndex: 3, prior: 0.64, correct: 0, posterior: 0.52, note: 'Incorrect (y₃ = 0) → Slip penalized' },
    { stepIndex: 4, prior: 0.52, correct: 1, posterior: 0.71, note: 'Correct (y₄ = 1) → Rapid recovery' },
    { stepIndex: 5, prior: 0.71, correct: 1, posterior: 0.84, note: 'Correct (y₅ = 1) → Approaching mastery' },
    { stepIndex: 6, prior: 0.84, correct: 1, posterior: 0.92, note: 'Correct (y₆ = 1) → Mastery Threshold Achieved (≥ 0.85)' },
  ];

  return (
    <div className="view-page">
      <div className="page-header">
        <div>
          <h2>Bayesian Knowledge Tracing &mdash; Mastery Trajectory</h2>
          <p className="page-lead">
            Latent state probability P(L_t) evolution for topic <em>Binary Search Trees</em> over sequential practice opportunities.
          </p>
        </div>
        <div className="header-actions">
          <button className="btn btn-outline" onClick={() => onNavigate('dashboard')}>
            &larr; Back to Dashboard
          </button>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-label">Prior Mastery P(L₀)</span>
          <div className="stat-value text-primary">0.250</div>
          <span className="stat-sub">EM estimated skill prior</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Learning Rate P(T)</span>
          <div className="stat-value text-success">0.148</div>
          <span className="stat-sub">Transition probability per step</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Guess Probability P(G)</span>
          <div className="stat-value text-info">0.182</div>
          <span className="stat-sub">Identifiability bounded (&le; 0.5)</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Slip Probability P(S)</span>
          <div className="stat-value text-warning">0.094</div>
          <span className="stat-sub">Identifiability bounded (&le; 0.5)</span>
        </div>
      </div>

      <div className="card-box">
        <div className="box-header">
          <h3>Sequential Latent Mastery Progression Table</h3>
          <span className="badge-tag">Empirical Trace</span>
        </div>

        <table className="bkt-table">
          <thead>
            <tr>
              <th>Opportunity (t)</th>
              <th>Prior P(L_t)</th>
              <th>Observed Response (y_t)</th>
              <th>Posterior P(L_t | y_t)</th>
              <th>Next Prior P(L_t+1)</th>
              <th>Status / Pedagogical Interpretation</th>
            </tr>
          </thead>
          <tbody>
            {steps.map((s) => (
              <tr key={s.stepIndex} className={s.posterior >= 0.85 ? 'row-mastered' : ''}>
                <td><strong>t = {s.stepIndex}</strong></td>
                <td>{s.prior.toFixed(3)}</td>
                <td>
                  {s.correct === null ? (
                    <span className="text-muted">&mdash;</span>
                  ) : s.correct === 1 ? (
                    <span className="badge-pill pill-success">✓ Correct (1)</span>
                  ) : (
                    <span className="badge-pill pill-danger">✗ Incorrect (0)</span>
                  )}
                </td>
                <td><strong>{s.posterior.toFixed(3)}</strong></td>
                <td>{(s.posterior + (1 - s.posterior) * 0.148).toFixed(3)}</td>
                <td>
                  <span className="trace-note">{s.note}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="bkt-summary-footer">
          <div className="rule-box">
            <h4>Pedagogical Gating Rule</h4>
            <p>
              When P(L_t) &ge; 0.85, the student is designated as having cognitively mastered the concept. Subsequent exercises will decrease in repetition frequency and trigger unlocking of child nodes in the prerequisite DAG (e.g., <em>Heap & Priority Queue</em>).
            </p>
          </div>
          <button className="btn btn-primary" onClick={() => onNavigate('recommendations')}>
            Inspect Next Study Recommendations &rarr;
          </button>
        </div>
      </div>
    </div>
  );
}
