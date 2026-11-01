import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Zap, BarChart3, Calendar, Heart, LogOut, Bell, Brain, GraduationCap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PageStyle.css';
import { alumniAPI } from '../services/api';

function Forecast({ user, onLogout }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    segment: 'mid_career',
    fundType: 'general',
    month: '6',
  });

  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const segments = [
    { value: 'recent_grads', label: 'Recent Graduates (0-3 years)' },
    { value: 'early_career', label: 'Early Career (3-7 years)' },
    { value: 'mid_career', label: 'Mid Career (7-15 years)' },
    { value: 'executives', label: 'Executives (15+ years)' },
  ];

  const fundTypes = [
    { value: 'general', label: 'General Fund' },
    { value: 'scholarship', label: 'Scholarship Fund' },
    { value: 'infrastructure', label: 'Infrastructure' },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGenerateForecast = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await alumniAPI.getForecast(formData);
      const data = response.data;
      const segmentName = segments.find(s => s.value === formData.segment)?.label;
      const fundName = fundTypes.find(f => f.value === formData.fundType)?.label;

      // Use REAL data from backend - NO FALLBACKS
      setForecast({
        segment: segmentName,
        fundType: fundName,
        predictedDonors: data.predictedDonors ?? 0,  // Real data with no fallback
        projectedAmount: data.projectedAmount ?? 0,  // Real data with no fallback
        confidence: (data.confidence ?? 0).toFixed(2),
        averageDonation: data.averageDonation ?? 0,
        trend: data.trend ?? [],  // Real trend from database
        recommendations: data.recommendations ?? [],  // Real recommendations based on actual data
      });
    } catch (err) {
      setError('Error: ' + (err.response?.data?.error || err.message || 'Failed to generate forecast'));
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
          <Link to="/record-engagement" className="nav-link">
            <Calendar size={18} /> Record Engagement
          </Link>
          <Link to="/record-donation" className="nav-link">
            <Heart size={18} /> Record Donation
          </Link>
          <Link to="/forecast" className="nav-link active">
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
          <h1>Donation Forecast</h1>
          <p>ML-powered predictions for alumni engagement</p>
        </div>

        {error && (
          <div className="alert alert-error">
            ✗ {error}
          </div>
        )}

        {/* Forecast Parameters Card */}
        <div className="form-container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div className="form-group">
              <label>Alumni Segment</label>
              <select name="segment" value={formData.segment} onChange={handleChange}>
                {segments.map(seg => (
                  <option key={seg.value} value={seg.value}>{seg.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Fund Type</label>
              <select name="fundType" value={formData.fundType} onChange={handleChange}>
                {fundTypes.map(fund => (
                  <option key={fund.value} value={fund.value}>{fund.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Forecast Period</label>
              <select name="month" value={formData.month} onChange={handleChange}>
                <option value="3">3 Months</option>
                <option value="6">6 Months</option>
                <option value="12">12 Months</option>
              </select>
            </div>
          </div>

          <button className="btn-submit" onClick={handleGenerateForecast} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Forecast'}
          </button>
        </div>

        {/* Forecast Results */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p>Generating forecast...</p>
          </div>
        )}

        {forecast && (
          <>
            {/* Key Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
              <div className="card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#666', marginBottom: '0.5rem' }}>Predicted Donors</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: '#4da6ff' }}>{forecast.predictedDonors}</div>
                </div>
              </div>
              <div className="card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#666', marginBottom: '0.5rem' }}>Projected Revenue</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: '#4da6ff' }}>${(forecast.projectedAmount / 1000).toFixed(0)}K</div>
                </div>
              </div>
              <div className="card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#666', marginBottom: '0.5rem' }}>Avg Donation</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: '#4da6ff' }}>${forecast.averageDonation}</div>
                </div>
              </div>
              <div className="card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#666', marginBottom: '0.5rem' }}>Confidence</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: '#4da6ff' }}>{(forecast.confidence * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>

            {/* Forecast Chart */}
            <div className="card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
              <h3 style={{ marginBottom: '1.5rem', fontSize: '16px', fontWeight: '600' }}>Projected Donation Trend</h3>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={forecast.trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" label={{ value: 'Donors', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Amount ($)', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="donors" fill="#3498db" name="Projected Donors" />
                  <Bar yAxisId="right" dataKey="amount" fill="#2ecc71" name="Projected Amount" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Recommendations */}
            <div className="card" style={{ marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1.5rem', fontSize: '16px', fontWeight: '600' }}>Recommendations</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {forecast.recommendations.map((rec, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '1rem', padding: '0.75rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                    <div style={{ minWidth: '28px', width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#4da6ff', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '600', fontSize: '13px' }}>{idx + 1}</div>
                    <div style={{ fontSize: '14px' }}>{rec}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Forecast;
