import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { TrendingUp, Users, Gift, Target, Download, Menu, LogOut, Bell, GraduationCap, BarChart3, Calendar, Heart, Zap, Brain, Lock } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import './Dashboard.css';

function Dashboard({ user, onLogout }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    setTimeout(() => {
      setStats({
        totalAlumni: 42850,
        activeEngagements: 12420,
        predictedDonors: 3150,
        confidence: 88,
        engagementTrend: [
          { month: 'JAN', engagement: 2400 },
          { month: 'FEB', engagement: 2810 },
          { month: 'MAR', engagement: 3200 },
          { month: 'APR', engagement: 3900 },
          { month: 'MAY', engagement: 3800 },
          { month: 'JUN', engagement: 4200 },
          { month: 'JUL', engagement: 4500 },
          { month: 'AUG', engagement: 4100 },
          { month: 'SEP', engagement: 4800 },
          { month: 'OCT', engagement: 4300 },
          { month: 'NOV', engagement: 5200 },
        ],
        donationsByRegion: [
          { region: 'CAN', probability: 0.45 },
          { region: 'USA', probability: 0.72 },
          { region: 'GBR', probability: 0.38 },
          { region: 'GER', probability: 0.35 },
          { region: 'FRA', probability: 0.32 },
          { region: 'JPN', probability: 0.25 },
          { region: 'AUS', probability: 0.55 },
          { region: 'SOP', probability: 0.42 },
          { region: 'IND', probability: 0.48 },
          { region: 'GLOBAL', probability: 0.85 },
          { region: 'NY', probability: 0.88 },
          { region: 'TX', probability: 0.60 },
          { region: 'CA', probability: 0.92 },
          { region: 'FL', probability: 0.58 },
          { region: 'WA', probability: 0.55 },
        ],
        highValueProspects: [
          {
            name: 'Eleanor D. Vance',
            company: 'B.S. Computer Science',
            gradYear: '12',
            engagementScore: 0.96,
            potential: '$250,000+',
          },
          {
            name: 'Dr. Marcus Sterling',
            company: 'MBA Finance',
            gradYear: '05',
            engagementScore: 0.88,
            potential: '$100,000+',
          },
          {
            name: 'Professor James Liu',
            company: 'PhD Engineering',
            gradYear: '08',
            engagementScore: 0.82,
            potential: '$75,000+',
          },
          {
            name: 'Catherine Wells',
            company: 'B.A. Business',
            gradYear: '10',
            engagementScore: 0.79,
            potential: '$50,000+',
          },
        ],
      });
      setLoading(false);
    }, 500);
  }, []);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-sidebar">
          <div className="sidebar-header">
            <div className="sidebar-logo">ALUMNI</div>
            <div className="sidebar-title">EXECUTIVE<br/>PORTAL</div>
          </div>
        </div>
        <div className="dashboard-main">
          <div className="loading-spinner">Loading Dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-wrapper">
      {/* TOP NAVIGATION BAR */}
      <div className="top-navbar">
        <Link to="/dashboard" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="navbar-brand">
            <div className="brand-icon">
              <GraduationCap size={28} />
            </div>
            <div className="brand-text">
              <div className="brand-main">Alumni</div>
              <div className="brand-sub">ML</div>
            </div>
          </div>
        </Link>

        <div className="navbar-menu">
          <Link to="/dashboard" className="nav-link active">
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
            <div className="user-avatar-small">{user?.name?.charAt(0) || 'U'}</div>
            <span className="user-name-nav">{user?.name || 'User'}</span>
          </div>
          <button className="nav-logout" onClick={() => {
            if (onLogout) onLogout();
            navigate('/login', { replace: true });
          }}>
            <LogOut size={18} /> Logout
          </button>
        </div>
      </div>

      {/* MAIN CONTAINER */}
      <div className="dashboard-container">
        {/* Professional Sidebar */}
        <div className={`dashboard-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <div className="sidebar-header">
            <div className="sidebar-logo">ALUMNI</div>
            <div className="sidebar-title">EXECUTIVE<br/>PORTAL</div>
          </div>
          <div className="sidebar-menu">
            <div className="sidebar-item active" onClick={() => navigate('/dashboard')}>
              <TrendingUp size={20} /> 
              {sidebarOpen && <span>Dashboard</span>}
            </div>
            <div className="sidebar-item" onClick={() => navigate('/alumni-profiles')}>
              <Users size={20} /> 
              {sidebarOpen && <span>Alumni Profiles</span>}
            </div>
            <div className="sidebar-item" onClick={() => navigate('/record-donation')}>
              <Gift size={20} /> 
              {sidebarOpen && <span>Donations</span>}
            </div>
            <div className="sidebar-item" onClick={() => navigate('/campaigns')}>
              <Target size={20} /> 
              {sidebarOpen && <span>Campaigns</span>}
            </div>
          </div>
          <div className="sidebar-footer">
            <div className="sidebar-support">
              <Lock size={20} className="support-icon" />
              {sidebarOpen && (
                <div className="support-text">
                  <div className="support-title">Premium Support</div>
                  <div className="support-label">Dedicated Advisor</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* MAIN CONTENT */}
        <div className="dashboard-main">
          {/* Toggle Button */}
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <Menu size={20} />
          </button>

          {/* Header */}
          <div className="dashboard-header">
            <div className="header-title">
              <h1>Executive Dashboard</h1>
              <p>Real-time Alumni & Engagement Analytics</p>
            </div>
            <div className="header-actions">
              <button className="btn-export" onClick={() => {
                const reportData = {
                  timestamp: new Date().toISOString(),
                  user: user?.name,
                  stats: stats,
                };
                const dataStr = JSON.stringify(reportData, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `alumni-report-${Date.now()}.json`;
                link.click();
              }}>
                <Download size={18} /> Export Report
              </button>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-icon">
                <Users size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">TOTAL ALUMNI</div>
                <div className="metric-value">42,850</div>
                <div className="metric-change">↑ 2.4% YoY</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">
                <TrendingUp size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">HIGH-ENGAGEMENT</div>
                <div className="metric-value">12,420</div>
                <div className="metric-change">↑ 5.1% MoM</div>
              </div>
            </div>

            <div className="metric-card featured">
              <div className="metric-icon featured">
                <Gift size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">PREDICTED DONORS</div>
                <div className="metric-value">3,150</div>
                <div className="metric-change">🤖 AI SCORING</div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="charts-section">
            {/* Engagement Trends */}
            <div className="chart-card">
              <div className="chart-header">
                <h3>Engagement Trends</h3>
                <div className="chart-filters">
                  <button className="filter-btn">Yearly</button>
                  <button className="filter-btn active">Monthly</button>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats?.engagementTrend || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="month" 
                    stroke="#999"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis stroke="#999" style={{ fontSize: '12px' }} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '2px solid #DC143C',
                      borderRadius: '4px',
                    }}
                  />
                  <Line 
                    type="natural" 
                    dataKey="engagement" 
                    stroke="#DC143C" 
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 6 }}
                    isAnimationActive={true}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Donation Probability Heatmap */}
            <div className="chart-card">
              <div className="chart-header">
                <h3>Donation Probability</h3>
                <span className="chart-subtitle">Likelihood Heatmap by Region</span>
              </div>
              <div className="heatmap-container">
                <div className="heatmap-grid">
                  {stats?.donationsByRegion?.slice(0, 15).map((item, idx) => (
                    <div 
                      key={idx}
                      className="heatmap-cell"
                      style={{
                        backgroundColor: `rgba(220, 20, 60, ${item.probability})`,
                        borderColor: item.probability > 0.7 ? '#DC143C' : '#ddd',
                      }}
                    >
                      <span>{item.region}</span>
                    </div>
                  ))}
                </div>
                <div className="heatmap-legend">
                  <span>Low Prob.</span>
                  <div className="legend-gradient"></div>
                  <span>High Prob.</span>
                </div>
              </div>
            </div>
          </div>

          {/* High-Value Alumni Table */}
          <div className="table-card">
            <div className="table-header">
              <div className="table-title">
                <h3>High-Value Alumni Prospects</h3>
                <p>Prioritized by AI Engagement Scoring</p>
              </div>
              <button className="btn-export-list">📥 Export List</button>
            </div>
            <div className="table-wrapper">
              <table className="alumni-table">
                <thead>
                  <tr>
                    <th>ALUMNI NAME</th>
                    <th>GRAD YEAR</th>
                    <th>ENGAGEMENT SCORE</th>
                    <th>PREDICTED POTENTIAL</th>
                    <th>ACTION</th>
                  </tr>
                </thead>
                <tbody>
                  {stats?.highValueProspects?.map((prospect, idx) => (
                    <tr key={idx} className="table-row">
                      <td className="name-cell">
                        <div className="avatar">{prospect.name.charAt(0)}</div>
                        <div className="name-info">
                          <span className="name">{prospect.name}</span>
                          <span className="degree">{prospect.company}</span>
                        </div>
                      </td>
                      <td className="grad-year">{prospect.gradYear}</td>
                      <td className="score-cell">
                        <div className="score-bar">
                          <div 
                            className="score-fill" 
                            style={{ width: `${prospect.engagementScore * 100}%` }}
                          />
                        </div>
                        <span>{(prospect.engagementScore * 100).toFixed(0)}%</span>
                      </td>
                      <td className="potential-cell">{prospect.potential}</td>
                      <td className="action-cell">
                        <button className="btn-review">Review Profile</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
