import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import AlumniProfile from './pages/AlumniProfile';
import AlumniProfiles from './pages/AlumniProfiles';
import AddAlumni from './pages/AddAlumni';
import RecordEngagement from './pages/RecordEngagement';
import RecordDonation from './pages/RecordDonation';
import Forecast from './pages/Forecast';
import Insights from './pages/Insights';
import Campaigns from './pages/Campaigns';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try {
        setIsAuthenticated(true);
        setUser(JSON.parse(savedUser));
      } catch (err) {
        console.warn('Failed to parse saved user:', err);
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    // Store essential user info (name, email, role)
    const minimalUser = {
      name: userData.name,
      email: userData.email,
      role: userData.role,
    };
    setUser(minimalUser);
    localStorage.setItem('authToken', userData.token);
    localStorage.setItem('user', JSON.stringify(minimalUser));
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/signup"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Signup onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <Dashboard user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/alumni-profiles"
          element={
            isAuthenticated ? (
              <AlumniProfiles user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/add-alumni"
          element={
            isAuthenticated ? (
              <AddAlumni user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/alumni/:alumniId"
          element={
            isAuthenticated ? (
              <AlumniProfile user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/campaigns"
          element={
            isAuthenticated ? (
              <Campaigns user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/record-engagement"
          element={
            isAuthenticated ? (
              <RecordEngagement user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/record-donation"
          element={
            isAuthenticated ? (
              <RecordDonation user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/donation"
          element={
            isAuthenticated ? (
              <RecordDonation user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/forecast"
          element={
            isAuthenticated ? (
              <Forecast user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/insights"
          element={
            isAuthenticated ? (
              <Insights user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
