import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Heart, BarChart3, Calendar, LogOut, Bell, Brain, Zap, GraduationCap } from 'lucide-react';
import './PageStyle.css';
import { alumniAPI } from '../services/api';

function RecordDonation({ user, onLogout }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    alumniId: '',
    amount: '',
    fundType: 'general',
    donationDate: new Date().toISOString().split('T')[0],
    paymentMethod: 'card',
    notes: '',
    // New donor fields
    donorName: '',
    donorEmail: '',
    donorPhone: '',
    donorCompany: '',
    donorPosition: '',
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [useNewDonor, setUseNewDonor] = useState(false);
  const [alumni, setAlumni] = useState([]);

  React.useEffect(() => {
    const fetchAlumni = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/alumni', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` },
        });
        if (response.ok) {
          setAlumni(await response.json());
        }
      } catch (err) {
        console.error('Error fetching alumni:', err);
      }
    };
    fetchAlumni();
  }, []);

  const fundTypes = [
    { value: 'general', label: 'General Fund' },
    { value: 'scholarship', label: 'Scholarship Fund' },
    { value: 'infrastructure', label: 'Infrastructure' },
    { value: 'research', label: 'Research' },
  ];

  const paymentMethods = [
    { value: 'card', label: 'Credit/Debit Card' },
    { value: 'bank', label: 'Bank Transfer' },
    { value: 'check', label: 'Check' },
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

    // Get alumni ID - either selected or generate for new donor
    let alumni_id = formData.alumniId;
    let donationPayload = {
      fund_type: formData.fundType,
      date: formData.donationDate,
      payment_method: formData.paymentMethod,
    };

    if (useNewDonor) {
      // New donor - create ID and include donor details
      if (!formData.donorName || !formData.amount || !formData.donorEmail) {
        setError('Please fill all required fields for new donor');
        setLoading(false);
        return;
      }
      alumni_id = `NEW-${Date.now()}`;
      donationPayload = {
        ...donationPayload,
        alumni_id,
        amount: parseFloat(formData.amount),
        donor_name: formData.donorName,
        donor_email: formData.donorEmail,
        donor_phone: formData.donorPhone,
        donor_company: formData.donorCompany,
        donor_position: formData.donorPosition,
      };
    } else {
      // Existing alumni - verify required fields
      if (!formData.alumniId || !formData.amount) {
        setError('Please select alumni and enter amount');
        setLoading(false);
        return;
      }
      donationPayload = {
        ...donationPayload,
        alumni_id: formData.alumniId,
        amount: parseFloat(formData.amount),
      };
    }

    try {
      await alumniAPI.recordDonation(donationPayload);
      setSubmitted(true);
      setFormData({
        alumniId: '',
        amount: '',
        fundType: 'general',
        donationDate: new Date().toISOString().split('T')[0],
        paymentMethod: 'card',
        notes: '',
        donorName: '',
        donorEmail: '',
        donorPhone: '',
        donorCompany: '',
        donorPosition: '',
      });
      setUseNewDonor(false);
      setTimeout(() => setSubmitted(false), 3000);
    } catch (err) {
      setError('Error: ' + (err.response?.data?.error || err.message || 'Failed to record donation'));
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
          <Link to="/record-donation" className="nav-link active">
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
          <h1>Record Donation</h1>
          <p>Track and manage alumni donations</p>
        </div>

        <div className="form-container">
          {submitted && (
            <div className="alert alert-success">
              ✓ Donation recorded successfully!
            </div>
          )}
          {error && (
            <div className="alert alert-error">
              ✗ {error}
            </div>
          )}

          {/* Toggle between existing and new donor */}
          <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem' }}>
            <button
              type="button"
              onClick={() => setUseNewDonor(false)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: !useNewDonor ? '#007bff' : '#e9ecef',
                color: !useNewDonor ? 'white' : '#666',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: useNewDonor ? 'normal' : 'bold'
              }}
            >
              Existing Alumni
            </button>
            <button
              type="button"
              onClick={() => setUseNewDonor(true)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: useNewDonor ? '#28a745' : '#e9ecef',
                color: useNewDonor ? 'white' : '#666',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: useNewDonor ? 'bold' : 'normal'
              }}
            >
              New Donor
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            {!useNewDonor ? (
              <div className="form-group">
                <label>Select Alumni *</label>
                <select
                  name="alumniId"
                  value={formData.alumniId}
                  onChange={handleChange}
                  required
                >
                  <option value="">-- Choose an alumni --</option>
                  {alumni.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.department})
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label>Donor Name *</label>
                    <input
                      type="text"
                      name="donorName"
                      value={formData.donorName}
                      onChange={handleChange}
                      placeholder="Full name"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Email Address *</label>
                    <input
                      type="email"
                      name="donorEmail"
                      value={formData.donorEmail}
                      onChange={handleChange}
                      placeholder="email@example.com"
                      required
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Phone</label>
                    <input
                      type="tel"
                      name="donorPhone"
                      value={formData.donorPhone}
                      onChange={handleChange}
                      placeholder="(123) 456-7890"
                    />
                  </div>
                  <div className="form-group">
                    <label>Company</label>
                    <input
                      type="text"
                      name="donorCompany"
                      value={formData.donorCompany}
                      onChange={handleChange}
                      placeholder="Company name"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Position</label>
                  <input
                    type="text"
                    name="donorPosition"
                    value={formData.donorPosition}
                    onChange={handleChange}
                    placeholder="Job title"
                  />
                </div>
              </>
            )}

            <div className="form-group">
              <div className="form-group">
                <label>Amount ($) *</label>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  placeholder="0.00"
                  step="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label>Fund Type</label>
                <select name="fundType" value={formData.fundType} onChange={handleChange}>
                  {fundTypes.map(ft => (
                    <option key={ft.value} value={ft.value}>{ft.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Donation Date</label>
                <input
                  type="date"
                  name="donationDate"
                  value={formData.donationDate}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Payment Method</label>
                <select name="paymentMethod" value={formData.paymentMethod} onChange={handleChange}>
                  {paymentMethods.map(pm => (
                    <option key={pm.value} value={pm.value}>{pm.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                placeholder="Add any notes about this donation"
                rows="4"
              />
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Recording...' : 'Record Donation'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default RecordDonation;
