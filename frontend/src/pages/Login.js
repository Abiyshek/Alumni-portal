import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Login.css';
import Button from '../components/Button';
import Alert from '../components/Alert';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Make real API call to backend
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Login failed');
      }

      const data = await response.json();
      
      // Store minimal user data (name + email + token)
      const userData = {
        name: data.user.name,
        email: data.user.email,
        role: data.user.role,
        token: data.token,
      };
      
      onLogin(userData);
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🎓 Alumni ML Pipeline</h1>
          <p>Donation & Engagement Prediction System</p>
        </div>

        {error && <Alert type="error" message={error} onClose={() => setError('')} />}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <Button
            variant="primary"
            size="lg"
            type="submit"
            loading={loading}
            className="login-btn"
          >
            Sign In
          </Button>
        </form>

        <div className="login-footer">
          <p>Demo credentials:</p>
          <p className="demo-cred">📧 admin@alumni.edu</p>
          <p className="demo-cred">🔑 admin123</p>
          <hr style={{ margin: '15px 0', opacity: 0.3 }} />
          <p style={{ fontSize: '14px' }}>or</p>
          <p className="demo-cred">📧 user@alumni.edu</p>
          <p className="demo-cred">🔑 user123</p>
          <hr style={{ margin: '15px 0', opacity: 0.3 }} />
          <p style={{ fontSize: '14px' }}>Don't have an account?</p>
          <Link to="/signup" style={{ color: '#007bff', textDecoration: 'none', fontWeight: 'bold', fontSize: '14px' }}>
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
