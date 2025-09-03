import React, { useState } from 'react';
import { Heart, Search, Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = ({ onWatchlistClick, onSearchClick, currentView }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const { user, isAuthenticated } = useAuth();

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Sidebar */}
      <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <button 
            className="sidebar-toggle"
            onClick={toggleSidebar}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <Menu size={20} /> : <X size={20} />}
          </button>
          {!isCollapsed && (
            <div className="sidebar-brand">
              <span className="brand-text">Menu</span>
            </div>
          )}
        </div>

        <nav className="sidebar-nav">
          <ul className="nav-list">
            <li className="nav-item">
              <button 
                className={`nav-link ${currentView === 'search' ? 'active' : ''}`}
                onClick={onSearchClick}
                title="Search"
              >
                <Search size={20} />
                {!isCollapsed && <span>Search</span>}
              </button>
            </li>
            
            <li className="nav-item">
              <button 
                className={`nav-link ${currentView === 'watchlist' ? 'active' : ''}`}
                onClick={onWatchlistClick}
                title="Watchlist"
              >
                <Heart size={20} />
                {!isCollapsed && <span>Watchlist</span>}
              </button>
            </li>
            
          </ul>
        </nav>

        {!isCollapsed && (
          <div className="sidebar-footer">
            <div className="user-info">
              <div className="user-avatar">
                {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </div>
              <div className="user-details">
                <span className="user-name">{user?.full_name || user?.username}</span>
                <span className="user-email">{user?.email}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Overlay for mobile */}
      {!isCollapsed && (
        <div className="sidebar-overlay" onClick={toggleSidebar}></div>
      )}
    </>
  );
};

export default Sidebar;
