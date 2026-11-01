import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { BarChart3, Calendar, Heart, LogOut, Bell, Brain, Zap, GraduationCap, Users } from 'lucide-react';
import './PageStyle.css';
import { alumniAPI } from '../services/api';

function AlumniProfiles({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [alumni, setAlumni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchAlumni = async () => {
    try {
      const response = await alumniAPI.getAllAlumni();
      setAlumni(response.data || []);
      console.log(`Loaded ${(response.data || []).length} alumni from backend`);
    } catch (err) {
      console.error('Error fetching alumni:', err);
      setAlumni([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch alumni list - runs on mount and when returning from AddAlumni
    fetchAlumni();
  }, [location]);

  const filteredAlumni = alumni.filter(a => 
    (a.name && a.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (a.company && a.company.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="page-wrapper">
      {/* NAV BAR */}
      <div className="page-navbar">
        <Link to="/dashboard" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="navbar-brand">
            <GraduationCap size={28} />
            <div className="brand-text">
              <div className="brand-main">Alumni</div>
              <div className="brand-sub">ML</div>
            </div>
          </div>
        </Link>

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
          <h1>Alumni Profiles</h1>
          <p>Browse and manage alumni records</p>
        </div>

        <div className="form-container">
          <div className="form-group">
            <label>Search Alumni</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name or company..."
            />
          </div>
          <button 
            className="btn-submit" 
            onClick={() => navigate('/add-alumni')}
            style={{ marginTop: '0.5rem' }}
          >
            + Add New Alumni
          </button>
        </div>

        {loading ? (
          <p style={{ textAlign: 'center', padding: '2rem' }}>Loading alumni...</p>
        ) : (
          <div className="card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Graduation Year</th>
                  <th>Engagement Score</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredAlumni.map((al) => (
                  <tr key={al.id}>
                    <td style={{ fontWeight: '600' }}>{al.name || 'Unknown'}</td>
                    <td>{al.company || 'N/A'}</td>
                    <td>{al.role || 'N/A'}</td>
                    <td>{al.gradYear || 'N/A'}</td>
                    <td>
                      <span style={{ backgroundColor: al.engagementScore > 0.85 ? '#d4edda' : al.engagementScore > 0.75 ? '#fff3cd' : '#f8d7da', color: al.engagementScore > 0.85 ? '#155724' : al.engagementScore > 0.75 ? '#856404' : '#721c24', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '12px', fontWeight: '500' }}>
                        {(al.engagementScore * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td>
                      <button 
                        className="btn-primary" 
                        style={{ padding: '0.4rem 0.8rem', fontSize: '12px' }}
                        onClick={() => navigate(`/alumni/${al.id}`)}
                      >
                        View Profile
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default AlumniProfiles;
