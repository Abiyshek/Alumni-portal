import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Brain, BarChart3, Calendar, Heart, LogOut, Bell, Send, Zap, GraduationCap } from 'lucide-react';
import './PageStyle.css';
import { alumniAPI } from '../services/api';

function Insights({ user, onLogout }) {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);

  const suggestedQuestions = [
    'Which alumni segment donates the most?',
    'What factors correlate with higher donation amounts?',
    'Who are the most engaged alumni?',
    'What is the best time to reach out to alumni?',
    'How can we improve donation rates?',
  ];

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setError('');
    setLoading(true);

    try {
      const response = await alumniAPI.getInsights(question);
      const data = response.data;
      
      setConversationHistory((prev) => [
        ...prev,
        { type: 'question', text: question },
        { type: 'answer', text: data.answer, confidence: data.confidence || 0.85 },
      ]);
      setInsights({
        text: data.answer,
        confidence: data.confidence || 0.85,
        recommendations: data.recommendations || [],
      });
      setQuestion('');
    } catch (err) {
      setError('Error: ' + (err.response?.data?.error || err.message || 'Failed to get insights'));
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (q) => {
    setQuestion(q);
  };

  return (
    <div className="page-wrapper">
      {/* NAV BAR */}
      <div className="page-navbar">
        <div className="navbar-brand">
          <GraduationCap size={28} />
          <div className="brand-text">
            <div className="brand-main">Alumni</div>
            <div className="brand-sub">ML</div>
          </div>
        </div>

        <div className="navbar-menu">
          <Link to="/dashboard" className="nav-link">
            <BarChart3 size={18} /> Dashboard
          </Link>
          <Link to="/record-engagement" className="nav-link">
            <Calendar size={18} /> Record Engagement
          </Link>
          <Link to="/record-donation" className="nav-link">
            <Heart size={18} /> Record Donation
          </Link>
          <Link to="/forecast" className="nav-link">
            <Zap size={18} /> Forecast
          </Link>
          <Link to="/insights" className="nav-link active">
            <Brain size={18} /> AI Insights
          </Link>
        </div>

        <div className="navbar-right">
          <button className="nav-icon">
            <Bell size={20} />
          </button>
          <div className="user-info">
            <div className="user-avatar">{user?.name?.charAt(0) || 'U'}</div>
            <span>{user?.name || 'User'}</span>
          </div>
          <button className="nav-logout" onClick={() => {
            if (onLogout) onLogout();
            navigate('/login', { replace: true });
          }}>
            <LogOut size={18} /> Logout
          </button>
        </div>
      </div>

      {/* PAGE CONTENT */}
      <div className="page-content">
        <div className="page-header">
          <h1>AI Insights</h1>
          <p>Ask GenAI questions about your alumni data</p>
        </div>

        {error && (
          <div className="alert alert-error">
            ✗ {error}
          </div>
        )}

        {/* Question Input */}
        <div className="form-container">
          <form onSubmit={handleAskQuestion}>
            <div className="form-group">
              <label>Ask a Question</label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about alumni donations, engagement, or predictions..."
                rows="3"
              />
            </div>
            <button type="submit" className="btn-submit" disabled={loading || !question.trim()}>
              <Send size={18} /> {loading ? 'Analyzing...' : 'Get Insights'}
            </button>
          </form>

          {/* Suggested Questions */}
          <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #eee' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>💡</span> Suggested Questions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  className="btn-secondary"
                  onClick={() => handleSuggestedQuestion(q)}
                  style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '13px' }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Conversation History */}
        {conversationHistory.length > 0 && (
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem', fontSize: '16px', fontWeight: '600' }}>Conversation History</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {conversationHistory.map((msg, idx) => (
                <div key={idx} style={{ padding: '1rem', backgroundColor: msg.type === 'question' ? '#f8f9fa' : '#e8f4fd', borderRadius: '6px', borderLeft: `4px solid ${msg.type === 'question' ? '#ccc' : '#4da6ff'}` }}>
                  <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span>{msg.type === 'question' ? '👤' : '🤖'}</span>
                    <span>{msg.type === 'question' ? 'You' : 'AI Assistant'}</span>
                    {msg.confidence && (
                      <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#666' }}>
                        Confidence: {(msg.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '14px', lineHeight: '1.6', color: '#333' }}>{msg.text}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Current Insight */}
        {insights && (
          <div className="card">
            <h3 style={{ marginBottom: '1rem', fontSize: '16px', fontWeight: '600' }}>Latest Insight</h3>
            <div style={{ padding: '1rem', backgroundColor: '#f0f7ff', borderRadius: '6px', borderLeft: '4px solid #4da6ff', marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '14px', lineHeight: '1.6', marginBottom: '1rem', color: '#333' }}>{insights.text}</div>
              <div style={{ display: 'flex', gap: '1rem', fontSize: '12px', color: '#666' }}>
                <span>Confidence: {(insights.confidence * 100).toFixed(0)}%</span>
                <span>Generated: {new Date().toLocaleTimeString()}</span>
              </div>
            </div>

            {insights.recommendations && insights.recommendations.length > 0 && (
              <div>
                <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '1rem' }}>Recommended Actions</h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {insights.recommendations.map((rec, idx) => (
                    <li key={idx} style={{ padding: '0.75rem', paddingLeft: '2rem', backgroundColor: '#f8f9fa', marginBottom: '0.5rem', borderRadius: '4px', fontSize: '13px', position: 'relative' }}>
                      <span style={{ position: 'absolute', left: '0.75rem', fontWeight: '600', color: '#4da6ff' }}>✓</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Insights;
