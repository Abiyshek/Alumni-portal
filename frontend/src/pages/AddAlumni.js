import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, BarChart3, Calendar, Heart, LogOut, Bell, Brain, Zap, GraduationCap } from 'lucide-react';
import './PageStyle.css';
import { alumniAPI } from '../services/api';

function AddAlumni({ user, onLogout }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    graduation_year: new Date().getFullYear(),
    department: '',
    phone: '',
    position: '',
    company: '',
    linkedin_url: '',
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const departments = [
    { value: 'computer_science', label: 'Computer Science' },
    { value: 'engineering', label: 'Engineering' },
    { value: 'business', label: 'Business' },
    { value: 'medicine', label: 'Medicine' },
    { value: 'law', label: 'Law' },
    { value: 'arts', label: 'Arts & Sciences' },
    { value: 'other', label: 'Other' },
  ];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'graduation_year' ? parseInt(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!formData.name || !formData.email) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    try {
      const response = await alumniAPI.addAlumni(formData);
      const alumni = response.data.alumni;
      
      setSuccessMessage(`Alumni "${alumni.name}" has been added successfully! (ID: ${alumni.alumni_id})`);
      setSubmitted(true);
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        graduation_year: currentYear,
        department: '',
        phone: '',
        position: '',
        company: '',
        linkedin_url: '',
      });

      // Redirect after 2 seconds with state to trigger refresh
      setTimeout(() => {
        navigate('/alumni-profiles', { state: { refresh: true } });
      }, 2000);
    } catch (err) {
      if (err.response?.status === 409) {
        setError('An alumni with this email already exists');
      } else {
        setError('Error: ' + (err.response?.data?.error || err.message || 'Failed to add alumni'));
      }
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
          <Link to="/alumni-profiles" className="nav-link">
            <UserPlus size={18} /> Alumni
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
          <h1>Add New Alumni</h1>
          <p>Register a new alumnus/alumna in the system</p>
        </div>

        {error && (
          <div className="alert alert-error">
            ✗ {error}
          </div>
        )}

        {submitted && successMessage && (
          <div className="alert alert-success">
            ✓ {successMessage}
          </div>
        )}

        {/* Form */}
        <div className="form-container">
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              {/* Name */}
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  id="name"
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., John Doe"
                  required
                />
              </div>

              {/* Email */}
              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="e.g., john@example.com"
                  required
                />
              </div>

              {/* Graduation Year */}
              <div className="form-group">
                <label htmlFor="graduation_year">Graduation Year</label>
                <select
                  id="graduation_year"
                  name="graduation_year"
                  value={formData.graduation_year}
                  onChange={handleChange}
                >
                  <option value="">Select year</option>
                  {years.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>

              {/* Department */}
              <div className="form-group">
                <label htmlFor="department">Department</label>
                <select
                  id="department"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                >
                  <option value="">Select department</option>
                  {departments.map((dept) => (
                    <option key={dept.value} value={dept.value}>
                      {dept.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Phone */}
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="e.g., +1-555-0123"
                />
              </div>

              {/* Position */}
              <div className="form-group">
                <label htmlFor="position">Current Position</label>
                <input
                  id="position"
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleChange}
                  placeholder="e.g., Software Engineer"
                />
              </div>

              {/* Company */}
              <div className="form-group">
                <label htmlFor="company">Current Company</label>
                <input
                  id="company"
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  placeholder="e.g., Tech Corp"
                />
              </div>

              {/* LinkedIn URL */}
              <div className="form-group">
                <label htmlFor="linkedin_url">LinkedIn Profile URL</label>
                <input
                  id="linkedin_url"
                  type="url"
                  name="linkedin_url"
                  value={formData.linkedin_url}
                  onChange={handleChange}
                  placeholder="https://linkedin.com/in/..."
                />
              </div>
            </div>

            <button type="submit" className="btn-submit" disabled={loading || !formData.name || !formData.email}>
              <UserPlus size={18} /> {loading ? 'Adding Alumni...' : 'Add Alumni'}
            </button>
          </form>

          {/* Info Box */}
          <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: '#f0f7ff', borderRadius: '8px', borderLeft: '4px solid #4da6ff' }}>
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '14px', fontWeight: '600', color: '#333' }}>ℹ️ Required Fields</h3>
            <p style={{ margin: 0, fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
              Only <strong>Full Name</strong> and <strong>Email Address</strong> are required. Other fields can be added later by updating the alumni profile.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddAlumni;
