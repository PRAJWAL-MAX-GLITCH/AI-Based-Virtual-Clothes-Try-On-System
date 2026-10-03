import React from 'react'
import { Link } from 'react-router-dom'
import { Sparkles, Globe, Mail, Link2 } from 'lucide-react'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        
        {/* Brand Column */}
        <div className="footer-col brand-col">
          <Link to="/" className="footer-logo">
            <div className="footer-logo-icon">
              <Sparkles size={16} />
            </div>
            <span className="footer-logo-text">
              Virtual<span className="gradient-text">TryOn</span>
            </span>
          </Link>
          <p className="footer-desc">
            Experience AI-powered virtual clothing try-on. 
            Upload your image, choose an outfit, and see how it looks before you wear it.
          </p>
          <div className="footer-socials">
            <a href="#" className="social-link"><Globe size={18} /></a>
            <a href="#" className="social-link"><Mail size={18} /></a>
            <a href="#" className="social-link"><Link2 size={18} /></a>
          </div>
        </div>

        {/* Links Columns */}
        <div className="footer-links-group">
          <div className="footer-col">
            <h4 className="footer-heading">Quick Links</h4>
            <Link to="/" className="footer-link">Home</Link>
            <Link to="/try-on" className="footer-link">Try On</Link>
            <Link to="/clothing" className="footer-link">Clothing</Link>
            <Link to="/history" className="footer-link">History</Link>
          </div>
          
          <div className="footer-col">
            <h4 className="footer-heading">Account</h4>
            <Link to="/login" className="footer-link">Login</Link>
            <Link to="/register" className="footer-link">Register</Link>
            <Link to="/profile" className="footer-link">Profile</Link>
          </div>
        </div>

      </div>
      
      <div className="footer-bottom">
        <div className="container footer-bottom-inner">
          <p>© {new Date().getFullYear()} AI-Based Virtual Try-On System. All rights reserved.</p>
          <div className="footer-legal">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
