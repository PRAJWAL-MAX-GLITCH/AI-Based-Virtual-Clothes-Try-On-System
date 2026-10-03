import React, { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import {
  Sparkles, Bell, User, LogOut, Settings,
  Menu, X, ChevronDown
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import './Navbar.css'

export default function Navbar({ onMenuToggle, sidebarOpen }) {
  const { user, isAuthenticated, logout } = useAuth()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
    setDropdownOpen(false)
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Left: Logo + Menu Toggle */}
        <div className="navbar-left">
          {isAuthenticated && (
            <button
              className="navbar-menu-btn"
              onClick={onMenuToggle}
              aria-label="Toggle sidebar"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          )}
          <Link to={isAuthenticated ? '/dashboard' : '/'} className="navbar-logo">
            <div className="navbar-logo-icon">
              <Sparkles size={18} />
            </div>
            <span className="navbar-logo-text">
              Virtual<span className="gradient-text">Try-On</span>
            </span>
          </Link>
        </div>

        {/* Right: Auth controls */}
        <div className="navbar-right">
          {isAuthenticated ? (
            <>
              {/* Notifications */}
              <button className="navbar-icon-btn" aria-label="Notifications">
                <Bell size={18} />
                <span className="navbar-notif-dot" />
              </button>

              {/* User dropdown */}
              <div className="navbar-user" onClick={() => setDropdownOpen(!dropdownOpen)}>
                <div className="navbar-avatar">
                  {user?.name ? user.name[0].toUpperCase() : 'U'}
                </div>
                <span className="navbar-user-name">{user?.name || 'User'}</span>
                <ChevronDown size={14} className={`navbar-chevron ${dropdownOpen ? 'open' : ''}`} />

                {dropdownOpen && (
                  <div className="navbar-dropdown">
                    <div className="navbar-dropdown-header">
                      <p className="navbar-dropdown-name">{user?.name || 'User'}</p>
                      <p className="navbar-dropdown-email">{user?.email || 'user@example.com'}</p>
                    </div>
                    <div className="navbar-dropdown-divider" />
                    <NavDropdownItem to="/profile" icon={<User size={14} />} label="My Profile" onClick={() => setDropdownOpen(false)} />
                    <NavDropdownItem to="/settings" icon={<Settings size={14} />} label="Settings" onClick={() => setDropdownOpen(false)} />
                    <div className="navbar-dropdown-divider" />
                    <button className="navbar-dropdown-item logout" onClick={handleLogout}>
                      <LogOut size={14} />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="navbar-auth-links">
              <NavLink to="/login" className="navbar-link">Sign In</NavLink>
              <Link to="/register" className="btn-primary-sm">Get Started</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

function NavDropdownItem({ to, icon, label, onClick }) {
  return (
    <NavLink to={to} className="navbar-dropdown-item" onClick={onClick}>
      {icon}
      {label}
    </NavLink>
  )
}
