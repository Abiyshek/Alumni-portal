import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { BarChart3, Calendar, Heart, LogOut, Bell, Brain, Zap, GraduationCap } from 'lucide-react';
import './PageStyle.css';

function AlumniProfile({ user, onLogout }) {
  const { alumniId } = useParams();
  const navigate = useNavigate();
  const [alumniData, setAlumniData] = useState(null);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    // Fetch alumni profile from backend
    const fetchAlumniData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/alumni/${alumniId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setAlumniData(data);
        } else {
          // Fallback to mock data
          setAlumniData({
            id: alumniId,
            name: 'John Doe',
            email: 'john.doe@alumni.edu',
            graduationYear: 2012,
            department: 'Computer Science',
            currentRole: 'Senior Software Engineer',
            company: 'Tech Corp Inc.',
            location: 'San Francisco, CA',
            donationScore: 0.87,
            engagementLevel: 'high',
            totalDonations: 15000,
            donationHistory: [
              { date: '2024-06-15', amount: 5000, type: 'General Fund' },
              { date: '2024-03-20', amount: 3000, type: 'Scholarship Fund' },
              { date: '2023-12-10', amount: 7000, type: 'Infrastructure' },
            ],
            engagementEvents: [
              { date: '2024-07-01', type: 'Attended Alumni Event', details: 'Annual Gala' },
              { date: '2024-06-15', type: 'Newsletter Signup', details: 'Monthly Updates' },
              { date: '2024-05-10', type: 'Made Donation', details: '$3,000 to Scholarship Fund' },
            ],
            predictedScore: 0.89,
            scoreReason: 'High engagement frequency and consistent donations indicate strong alumni loyalty',
          });
        }
      } catch (err) {
        console.error('Error fetching alumni data:', err);
        setAlumniData({
          id: alumniId,
          name: 'John Doe',
          email: 'john.doe@alumni.edu',
          graduationYear: 2012,
          department: 'Computer Science',
          currentRole: 'Senior Software Engineer',
          company: 'Tech Corp Inc.',
          location: 'San Francisco, CA',
          donationScore: 0.87,
          engagementLevel: 'high',
          totalDonations: 15000,
          donationHistory: [
            { date: '2024-06-15', amount: 5000, type: 'General Fund' },
            { date: '2024-03-20', amount: 3000, type: 'Scholarship Fund' },
            { date: '2023-12-10', amount: 7000, type: 'Infrastructure' },
          ],
          engagementEvents: [
            { date: '2024-07-01', type: 'Attended Alumni Event', details: 'Annual Gala' },
            { date: '2024-06-15', type: 'Newsletter Signup', details: 'Monthly Updates' },
            { date: '2024-05-10', type: 'Made Donation', details: '$3,000 to Scholarship Fund' },
          ],
          predictedScore: 0.89,
          scoreReason: 'High engagement frequency and consistent donations indicate strong alumni loyalty',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAlumniData();
  }, [alumniId]);

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="page-navbar">
          <div className="navbar-brand">
            <GraduationCap size={28} />
            <div className="brand-text">
              <div className="brand-main">Alumni</div>
              <div className="brand-sub">ML</div>
            </div>
          </div>
        </div>
        <div className="page-content" style={{ textAlign: 'center', paddingTop: '3rem' }}>
          <p>Loading alumni profile...</p>
        </div>
      </div>
    );
  }

  if (!alumniData) {
    return (
      <div className="page-wrapper">
        <div className="page-navbar">
          <div className="navbar-brand">
            <GraduationCap size={28} />
          </div>
        </div>
        <div className="page-content">
          <p>Alumni not found</p>
        </div>
      </div>
    );
  }

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
          <h1>Alumni Profile</h1>
          <p>Detailed information and engagement history</p>
        </div>

        {!alumniData ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>Unable to load alumni profile</div>
        ) : (
        <>

        {/* Header Section */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
            <div style={{ minWidth: '80px' }}>
              <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: '#4da6ff', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px', fontWeight: '700' }}>
                {alumniData?.name?.charAt(0) || 'A'}
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <h2 style={{ fontSize: '24px', fontWeight: '700', margin: '0 0 0.5rem 0', color: '#1a2332' }}>{alumniData.name}</h2>
              <p style={{ fontSize: '14px', color: '#666', margin: '0.25rem 0', fontWeight: '500' }}>{alumniData.currentRole} at {alumniData.company}</p>
              <p style={{ fontSize: '13px', color: '#888', margin: '0.25rem 0' }}>{alumniData.department} • Class of {alumniData.graduationYear}</p>
              <p style={{ fontSize: '13px', color: '#888', margin: '0.5rem 0 0 0' }}>📍 {alumniData.location}</p>
            </div>
            <div style={{ display: 'flex', gap: '2rem' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '12px', fontWeight: '600', color: '#666', marginBottom: '0.5rem' }}>Donation Score</div>
                <div style={{ fontSize: '24px', fontWeight: '700', color: '#27ae60' }}>{(alumniData.donationScore * 100).toFixed(0)}%</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '12px', fontWeight: '600', color: '#666', marginBottom: '0.5rem' }}>Predicted Score</div>
                <div style={{ fontSize: '24px', fontWeight: '700', color: '#3498db' }}>{(alumniData.predictedScore * 100).toFixed(0)}%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#4da6ff', marginBottom: '0.5rem' }}>${alumniData.totalDonations.toLocaleString()}</div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#666' }}>Total Donations</div>
            </div>
          </div>
          <div className="card">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#4da6ff', marginBottom: '0.5rem' }}>{alumniData.donationHistory.length}</div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#666' }}>Donation Events</div>
            </div>
          </div>
          <div className="card">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#4da6ff', marginBottom: '0.5rem' }}>{alumniData.engagementEvents.length}</div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#666' }}>Engagement Events</div>
            </div>
          </div>
          <div className="card">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#4da6ff', marginBottom: '0.5rem', textTransform: 'capitalize' }}>{alumniData.engagementLevel}</div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#666' }}>Engagement Level</div>
            </div>
          </div>
        </div>

        {/* ML Insights */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '1rem' }}>ML Prediction Insights</h3>
          <div style={{ padding: '1rem', backgroundColor: '#f0f7ff', borderRadius: '6px', borderLeft: '4px solid #4da6ff' }}>
            <div style={{ fontSize: '14px', marginBottom: '1rem' }}>
              Predicted Next Donation Score: <strong>{(alumniData.predictedScore * 100).toFixed(0)}%</strong>
            </div>
            <div>
              <strong style={{ fontSize: '13px' }}>Why this score?</strong>
              <p style={{ fontSize: '13px', margin: '0.5rem 0 0 0', color: '#555', lineHeight: '1.6' }}>{alumniData.scoreReason}</p>
            </div>
          </div>
        </div>

        {/* Donation History */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '1rem' }}>Donation History</h3>
          {alumniData.donationHistory.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Type</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {alumniData.donationHistory.map((donation, idx) => (
                  <tr key={idx}>
                    <td>{new Date(donation.date).toLocaleDateString()}</td>
                    <td style={{ fontWeight: '600', color: '#27ae60' }}>${donation.amount.toLocaleString()}</td>
                    <td>{donation.type}</td>
                    <td><span style={{ backgroundColor: '#d4edda', color: '#155724', padding: '0.25rem 0.75rem', borderRadius: '12px', fontSize: '12px', fontWeight: '500' }}>Completed</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: '#888', fontSize: '13px' }}>No donations recorded</p>
          )}
        </div>

        {/* Engagement Timeline */}
        <div className="card">
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '1.5rem' }}>Engagement Timeline</h3>
          {alumniData.engagementEvents.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {alumniData.engagementEvents.map((event, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '1rem' }}>
                  <div style={{ minWidth: '100px', fontSize: '12px', fontWeight: '600', color: '#666' }}>
                    {new Date(event.date).toLocaleDateString()}
                  </div>
                  <div style={{ flex: 1, paddingLeft: '1rem', borderLeft: '2px solid #4da6ff' }}>
                    <div style={{ fontSize: '13px', fontWeight: '600', color: '#1a2332' }}>{event.type}</div>
                    <div style={{ fontSize: '13px', color: '#666', marginTop: '0.25rem' }}>{event.details}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#888', fontSize: '13px' }}>No engagement events recorded</p>
          )}
        </div>
        </>
        )}
      </div>
    </div>
  );
}

export default AlumniProfile;
