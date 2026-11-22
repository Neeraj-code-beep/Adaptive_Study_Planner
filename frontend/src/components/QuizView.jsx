import React, { useState } from 'react';

export default function QuizView({ onNavigate }) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [showHint, setShowHint] = useState(false);

  const question = {
    id: 'Q-BST-04',
    topic: 'Binary Search Trees (BST)',
    subskill: 'Inorder Traversal & Time Complexity',
    difficulty: 'Intermediate',
    opportunityIndex: 4,
    prompt: 'What is the worst-case time complexity of searching for a key in an unbalanced Binary Search Tree with N nodes?',
    options: [
      { id: 'A', text: 'O(1) constant time access', correct: false },
      { id: 'B', text: 'O(log N) logarithmic depth', correct: false },
      { id: 'C', text: 'O(N) linear time due to skewness into a linked list', correct: true },
      { id: 'D', text: 'O(N log N) comparison sort bound', correct: false },
    ],
    hint: 'Pedagogical Hint: Consider a BST constructed by inserting sequentially sorted elements [1, 2, 3, 4, 5]. What structural shape does the tree degenerate into?',
    explanation: 'When a BST is completely skewed (every node has only one child), tree height H equals N. Searching for the deepest leaf requires traversing all N nodes, yielding O(N) worst-case time.'
  };

  const handleSelect = (id) => {
    if (!submitted) setSelectedOption(id);
  };

  const handleSubmit = () => {
    if (selectedOption) setSubmitted(true);
  };

  const isCorrect = selectedOption === 'C';

  return (
    <div className="view-page quiz-container">
      <div className="quiz-header-bar">
        <div className="quiz-meta-left">
          <span className="quiz-badge">{question.topic}</span>
          <span className="quiz-subbadge">Opportunity #{question.opportunityIndex}</span>
          <span className="quiz-diff-badge">{question.difficulty}</span>
        </div>
        <div className="quiz-timer">
          <span className="timer-icon">⏱️</span>
          <span className="timer-text">01:45</span>
        </div>
      </div>

      <div className="question-box">
        <h3 className="question-prompt">{question.prompt}</h3>
        <span className="question-skill-tag">Subskill: {question.subskill}</span>

        <div className="options-list">
          {question.options.map((opt) => {
            let itemClass = 'option-card';
            if (selectedOption === opt.id) itemClass += ' selected';
            if (submitted) {
              if (opt.correct) itemClass += ' correct-opt';
              else if (selectedOption === opt.id) itemClass += ' incorrect-opt';
            }

            return (
              <div
                key={opt.id}
                className={itemClass}
                onClick={() => handleSelect(opt.id)}
              >
                <span className="option-id">{opt.id}</span>
                <span className="option-text">{opt.text}</span>
              </div>
            );
          })}
        </div>

        {showHint && (
          <div className="hint-callout">
            <strong>💡 Hint:</strong> {question.hint}
          </div>
        )}

        {submitted && (
          <div className={`result-feedback ${isCorrect ? 'result-success' : 'result-failure'}`}>
            <div className="feedback-header">
              {isCorrect ? '✅ Response Correct!' : '❌ Response Incorrect'}
            </div>
            <p className="feedback-explanation">{question.explanation}</p>
            <div className="bkt-impact-alert">
              <strong>BKT Inference Update:</strong> Observation $y_t = {isCorrect ? '1' : '0'}$. Posterior knowledge mastery updated from $P(L_3) = 0.58 \to P(L_4) = {isCorrect ? '0.71' : '0.44'}$.
            </div>
          </div>
        )}

        <div className="quiz-actions">
          {!submitted ? (
            <>
              <button className="btn btn-outline" onClick={() => setShowHint(!showHint)}>
                {showHint ? 'Hide Hint' : 'Request Pedagogical Hint'}
              </button>
              <button
                className="btn btn-primary"
                disabled={!selectedOption}
                onClick={handleSubmit}
              >
                Submit Response
              </button>
            </>
          ) : (
            <>
              <button className="btn btn-outline" onClick={() => onNavigate('dashboard')}>
                Return to Dashboard
              </button>
              <button className="btn btn-success" onClick={() => onNavigate('mastery')}>
                View Updated BKT Analytics &rarr;
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
