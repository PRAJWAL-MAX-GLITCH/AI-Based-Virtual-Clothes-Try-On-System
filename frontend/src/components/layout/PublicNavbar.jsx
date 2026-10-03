import React, { useState, useEffect } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { Sparkles, Menu, X } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import './PublicNavbar.css'

export default function PublicNavbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, logout } = useAuth()

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/')
    setMobileMenuOpen(false)
  }

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Try On', path: '/try-on' },
    { name: 'Clothing', path: '/clothing' },
    { name: 'History', path: '/history' },
  ]

  return (
    <nav className={`public-navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="container public-navbar-inner">
        
        {/* Logo */}
        <Link to="/" className="nav-logo">
          <div className="nav-logo-icon">
            <Sparkles size={18} />
          </div>
          <span className="nav-logo-text">
            Virtual<span className="gradient-text">TryOn</span>
          </span>
        </Link>

        {/* Desktop Links */}
        <div className="nav-center hidden-mobile">
          {navLinks.map(link => (
            <NavLink 
              key={link.name} 
              to={link.path} 
              className={({isActive}) => `nav-link ${isActive && link.path !== '/' ? 'active' : ''}`}
            >
              {link.name}
            </NavLink>
          ))}
        </div>

        {/* Desktop Auth */}
        <div className="nav-right hidden-mobile">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="nav-btn-login">Dashboard</Link>
              <Link to="/profile" className="nav-btn-login">Profile</Link>
              <button onClick={handleLogout} className="nav-btn-register" style={{ border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-btn-login">Login</Link>
              <Link to="/register" className="nav-btn-register">Get Started</Link>
            </>
          )}
        </div>

        {/* Mobile Toggle */}
        <button 
          className="mobile-menu-toggle visible-mobile"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

      </div>

      {/* Mobile Menu Drawer */}
      <div className={`mobile-drawer ${mobileMenuOpen ? 'open' : ''}`}>
        <div className="mobile-drawer-links">
          {navLinks.map(link => (
            <NavLink 
              key={link.name} 
              to={link.path} 
              className={({isActive}) => `mobile-nav-link ${isActive && link.path !== '/' ? 'active' : ''}`}
            >
              {link.name}
            </NavLink>
          ))}
        </div>
        <div className="mobile-drawer-auth">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="mobile-btn-login">Dashboard</Link>
              <Link to="/profile" className="mobile-btn-login">Profile</Link>
              <button onClick={handleLogout} className="mobile-btn-register" style={{ border: 'none', cursor: 'pointer', fontFamily: 'inherit', width: '100%' }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="mobile-btn-login">Login</Link>
              <Link to="/register" className="mobile-btn-register">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
