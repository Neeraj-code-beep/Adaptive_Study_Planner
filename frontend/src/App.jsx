import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import TopicsView from './components/TopicsView';
import QuizView from './components/QuizView';
import MasteryView from './components/MasteryView';
import RecommendationsView from './components/RecommendationsView';

function App() {
  // Read initial tab from URL query param if present (?tab=dashboard)
  const getInitialTab = () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const tab = params.get('tab');
      if (tab && ['home', 'dashboard', 'topics', 'quiz', 'mastery', 'recommendations'].includes(tab)) {
        return tab;
      }
    } catch (e) {}
    return 'home';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab);

  // Sync state with URL parameter for easy linking and automated capture
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    try {
      const url = new URL(window.location);
      url.searchParams.set('tab', tabId);
      window.history.pushState({}, '', url);
    } catch (e) {}
  };

  useEffect(() => {
    const onPopState = () => {
      setActiveTab(getInitialTab());
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  return (
    <div className="app-shell">
      <Navbar activeTab={activeTab} setActiveTab={handleTabChange} />

      <main className="main-viewport">
        {activeTab === 'home' && (
          <div className="app-container">
            <header className="app-header">
              <div className="project-badge">Phase 2–6 Completed &bull; Academic Prototype</div>
              <h1>Knowledge-Tracing-Based Adaptive Topic Recommendation for Personalized Study Planning</h1>
              <p className="app-subtitle">
                An adaptive learning system estimating student topic mastery via Bayesian Knowledge Tracing (BKT) and recommending optimal learning trajectories across concept prerequisite graphs.
              </p>
            </header>

            <div className="sections-grid">
              {/* Section 1: Student Learning */}
              <section className="info-card" onClick={() => handleTabChange('dashboard')}>
                <div className="card-header">
                  <span className="card-icon">📚</span>
                  <h2>Student Learning &amp; Dashboard</h2>
                </div>
                <p className="card-description">
                  Tracks individual student interactions, cognitive state progression, and empirical accuracy across 12 Data Structures concepts.
                </p>
                <div className="card-status">
                  <span className="status-indicator"></span>
                  <span className="status-text">Interactive dashboard ready &mdash; Click to view</span>
                </div>
              </section>

              {/* Section 2: Knowledge Tracing */}
              <section className="info-card" onClick={() => handleTabChange('mastery')}>
                <div className="card-header">
                  <span className="card-icon">🧠</span>
                  <h2>Knowledge Tracing Engine</h2>
                </div>
                <p className="card-description">
                  Probabilistic modeling utilizing BKT Baum-Welch EM parameters ($P(L_0), P(T), P(G), P(S)$) to compute latent mastery posteriors.
                </p>
                <div className="card-status">
                  <span className="status-indicator"></span>
                  <span className="status-text">FastAPI service calibrated (ECE: 0.69%) &mdash; Click to view</span>
                </div>
              </section>

              {/* Section 3: Adaptive Recommendations */}
              <section className="info-card" onClick={() => handleTabChange('recommendations')}>
                <div className="card-header">
                  <span className="card-icon">🎯</span>
                  <h2>Adaptive Recommendations</h2>
                </div>
                <p className="card-description">
                  Prerequisite-gated sequencing planner generating personalized next-topic study schedules and remediation queues.
                </p>
                <div className="card-status">
                  <span className="status-indicator"></span>
                  <span className="status-text">Topological DAG ordering active &mdash; Click to view</span>
                </div>
              </section>
            </div>

            <section className="service-status-bar">
              <h3>Service Topology &amp; Ports</h3>
              <div className="services-list">
                <div className="service-item">
                  <span className="service-name">Frontend (React / Vite)</span>
                  <span className="service-port">http://localhost:5173</span>
                </div>
                <div className="service-item">
                  <span className="service-name">Backend API (Express / Prisma)</span>
                  <span className="service-port">http://localhost:5000</span>
                </div>
                <div className="service-item">
                  <span className="service-name">ML Service (FastAPI / BKT)</span>
                  <span className="service-port">http://localhost:8000</span>
                </div>
              </div>
            </section>

            <footer className="app-footer">
              <p>Project Owner: Neeraj Mishra &bull; 3rd Year B.Tech Computer Science and Engineering &bull; KMCLU Lucknow</p>
            </footer>
          </div>
        )}

        {activeTab === 'dashboard' && <DashboardView onNavigate={handleTabChange} />}
        {activeTab === 'topics' && <TopicsView onNavigate={handleTabChange} />}
        {activeTab === 'quiz' && <QuizView onNavigate={handleTabChange} />}
        {activeTab === 'mastery' && <MasteryView onNavigate={handleTabChange} />}
        {activeTab === 'recommendations' && <RecommendationsView onNavigate={handleTabChange} />}
      </main>
    </div>
  );
}

export default App;
