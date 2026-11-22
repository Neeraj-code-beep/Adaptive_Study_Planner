import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'home', label: 'Overview', icon: '🏠' },
    { id: 'dashboard', label: 'Student Dashboard', icon: '📊' },
    { id: 'topics', label: 'Curriculum DAG', icon: '🗺️' },
    { id: 'quiz', label: 'Adaptive Quiz', icon: '📝' },
    { id: 'mastery', label: 'BKT Analytics', icon: '🧠' },
    { id: 'recommendations', label: 'Study Planner', icon: '🎯' },
  ];

  return (
    <nav className="top-navbar">
      <div className="nav-container">
        <div className="nav-brand" onClick={() => setActiveTab('home')}>
          <span className="brand-logo">🎓</span>
          <div className="brand-text">
            <span className="brand-title">AdaptiveStudy</span>
            <span className="brand-sub">BKT Recommendation Engine</span>
          </div>
        </div>

        <div className="nav-links">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-button ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </div>

        <div className="nav-profile">
          <div className="avatar-circle">NM</div>
          <div className="profile-details">
            <span className="student-name">Neeraj Mishra</span>
            <span className="student-id">CSE • 3rd Year</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
