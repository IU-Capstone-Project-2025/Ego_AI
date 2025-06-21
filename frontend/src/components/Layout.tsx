import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { signOut } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    signOut();
    navigate("/reg-page", { replace: true });
  };
  
  return (
    <div className="layout">
      <nav className="nav">
        <div className="nav-links">
          <Link to="/calendar" className="nav-link">Calendar</Link>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout; 