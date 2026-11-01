import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, LogOut, Home, Users, PieChart, Brain, BarChart3 } from 'lucide-react';
import './Navigation.css';

function Navigation({ user, onLogout }) {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/record-engagement', label: 'Record Engagement', icon: Users },
    { path: '/record-donation', label: 'Record Donation', icon: BarChart3 },
    { path: '/forecast', label: 'Forecast', icon: PieChart },
    { path: '/insights', label: 'AI Insights', icon: Brain },
  ];

  return (
    <>
      <nav className="navbar">
        <div className="navbar-container">
          <Link to="/dashboard" className="navbar-brand">
            🎓 Alumni ML
          </Link>

          <button
            className="navbar-toggle"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          <ul className={`nav-menu ${isOpen ? 'active' : ''}`}>
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path} className="nav-item">
                  <Link
                    to={item.path}
                    className="nav-link"
                    onClick={() => setIsOpen(false)}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                </li>
              );
            })}
            <li className="nav-item user-info">
              <span className="username">👤 {user?.name || 'Guest'}</span>
            </li>
            <li className="nav-item">
              <button
                className="nav-link logout-btn"
                onClick={handleLogout}
              >
                <LogOut size={18} />
                Logout
              </button>
            </li>
          </ul>
        </div>
      </nav>
    </>
  );
}

export default Navigation;
