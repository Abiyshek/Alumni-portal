import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BarChart3, Calendar, Heart, LogOut, Bell, Brain, Zap, GraduationCap } from 'lucide-react';
import './PageStyle.css';

function Campaigns({ user, onLogout }) {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch campaigns from backend
    const fetchCampaigns = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const response = await fetch('http://localhost:5000/api/campaigns', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setCampaigns(data);
        } else {
          console.error('Failed to fetch campaigns:', response.status);
        }
      } catch (err) {
        console.error('Error fetching campaigns:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCampaigns();
  }, []);

  const handleCreateCampaign = () => {
    alert('Campaign creation coming soon!');
  };

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
          <h1>Fundraising Campaigns</h1>
          <p>Manage and track alumni fundraising initiatives</p>
        </div>

        <div className="form-container">
          <button className="btn-submit" onClick={handleCreateCampaign}>
            + Create New Campaign
          </button>
        </div>

        {loading ? (
          <p style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>Loading campaigns...</p>
        ) : campaigns.length === 0 ? (
          <p style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>No campaigns found</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="card">
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '1rem' }}>{campaign.name}</h3>
                
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '13px' }}>
                    <span>Progress</span>
                    <span style={{ fontWeight: '600' }}>
                      ${(campaign.raised / 1000).toFixed(0)}K / ${(campaign.goal / 1000).toFixed(0)}K
                    </span>
                  </div>
                  <div style={{ backgroundColor: '#e0e0e0', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                    <div style={{ backgroundColor: '#4da6ff', height: '100%', width: `${Math.min((campaign.raised / campaign.goal) * 100, 100)}%`, transition: 'width 0.3s' }} />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#4da6ff' }}>{campaign.donors}</div>
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '0.25rem' }}>Donors</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontSize: '13px', fontWeight: '600', color: campaign.status === 'Active' ? '#27ae60' : '#ff9800' }}>
                      {campaign.status}
                    </div>
                  </div>
                </div>

                <button className="btn-primary" style={{ width: '100%' }}>
                  View Details
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Campaigns;
