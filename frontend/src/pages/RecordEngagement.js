import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Calendar, BarChart3, Heart, LogOut, Bell, Brain, Zap, GraduationCap } from 'lucide-react';
import './PageStyle.css';
import { alumniAPI } from '../services/api';

function RecordEngagement({ user, onLogout }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    alumniId: '',
    eventType: 'attendance',
    eventDescription: '',
    eventDate: new Date().toISOString().split('T')[0],
    attendees: '1',
    comments: '',
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const eventTypes = [
    { value: 'attendance', label: 'Event Attendance' },
    { value: 'newsletter', label: 'Newsletter Subscription' },
    { value: 'login', label: 'Portal Login' },
    { value: 'feedback', label: 'Feedback Submission' },
    { value: 'volunteer', label: 'Volunteer Activity' },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!formData.alumniId || !formData.eventType) {
      setError('Please fill all required fields');
      setLoading(false);
      return;
    }

    try {
      await alumniAPI.recordEngagement({
        alumni_id: formData.alumniId,
        event_type: formData.eventType,
        description: formData.eventDescription,
        date: formData.eventDate,
      });
      setSubmitted(true);
      setFormData({
        alumniId: '',
        eventType: 'attendance',
        eventDescription: '',
        eventDate: new Date().toISOString().split('T')[0],
        attendees: '1',
        comments: '',
      });
      setTimeout(() => setSubmitted(false), 3000);
    } catch (err) {
      setError('Error: ' + (err.response?.data?.error || err.message || 'Failed to record engagement'));
    } finally {
      setLoading(false);
    }
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
          <Link to="/record-engagement" className="nav-link active">
            <Calendar size={18} /> Record Engagement
          </Link>
          <Link to="/record-donation" className="nav-link">
            <Heart size={18} /> Record Donation
          </Link>
          <Link to="/forecast" className="nav-link">
            <Zap size={18} /> Forecast
          </Link>
          <Link to="/insights" className="nav-link">
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
          <h1>Record Engagement</h1>
          <p>Track and log alumni engagement activities</p>
        </div>

        <div className="form-container">
          {submitted && (
            <div className="alert alert-success">
              ✓ Engagement recorded successfully!
            </div>
          )}
          {error && (
            <div className="alert alert-error">
              ✗ {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Alumni ID *</label>
              <input
                type="text"
                name="alumniId"
                value={formData.alumniId}
                onChange={handleChange}
                placeholder="Enter alumni ID"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Event Type *</label>
                <select name="eventType" value={formData.eventType} onChange={handleChange} required>
                  {eventTypes.map(et => (
                    <option key={et.value} value={et.value}>{et.label}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Event Date</label>
                <input
                  type="date"
                  name="eventDate"
                  value={formData.eventDate}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Number of Attendees</label>
                <input
                  type="number"
                  name="attendees"
                  value={formData.attendees}
                  onChange={handleChange}
                  min="1"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Event Description</label>
              <textarea
                name="eventDescription"
                value={formData.eventDescription}
                onChange={handleChange}
                placeholder="Describe the engagement activity..."
                rows="4"
              />
            </div>

            <div className="form-group">
              <label>Comments</label>
              <textarea
                name="comments"
                value={formData.comments}
                onChange={handleChange}
                placeholder="Add any additional comments..."
                rows="3"
              />
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Recording...' : 'Record Engagement'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default RecordEngagement;
