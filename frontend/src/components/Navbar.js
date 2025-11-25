import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import './Navbar.css';

function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-left"></div>
        <div className="navbar-center">
          <Link to={isAuthenticated ? "/dashboard" : "/login"} className="navbar-logo">
            <span className="logo-accent">AI -</span> <span className="logo-main">Document Studio</span>
          </Link>
        </div>
        <div className="navbar-right">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <Link to="/projects/create" className="navbar-link">
                New Project
              </Link>
              <span className="navbar-user">
                {user?.username || user?.email}
              </span>
              <button onClick={handleLogout} className="navbar-link btn-logout">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">
                Login
              </Link>
              <Link to="/signup" className="navbar-link">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

