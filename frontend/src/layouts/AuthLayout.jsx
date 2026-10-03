import React from 'react'
import { Outlet, Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import './AuthLayout.css'

/**
 * AuthLayout — wraps login and register pages.
 * Clean centered layout with brand panel.
 */
export default function AuthLayout() {
  return (
    <div className="auth-layout">
      {/* Left: Brand panel */}
      <div className="auth-brand">
        <div className="auth-brand-glow" />
        <div className="auth-brand-content">
          <Link to="/" className="auth-logo">
            <div className="auth-logo-icon">
              <Sparkles size={22} />
            </div>
            <span className="auth-logo-text">
              Virtual<span className="gradient-text">Try-On</span>
            </span>
          </Link>

          <div className="auth-brand-hero">
            <h1 className="auth-brand-title">
              Experience Fashion<br />
              <span className="gradient-text">Powered by AI</span>
            </h1>
            <p className="auth-brand-desc">
              Upload your photo, browse garments, and see exactly how clothes look on you — instantly, with AI-driven 2D virtual try-on.
            </p>
          </div>

          <div className="auth-features">
            {[
              { label: 'AI Body Analysis', desc: 'Intelligent pose detection' },
              { label: 'Instant Try-On',   desc: 'Real-time garment overlay' },
              { label: 'Save & Share',     desc: 'Build your wardrobe history' },
            ].map((f) => (
              <div key={f.label} className="auth-feature-item">
                <div className="auth-feature-dot" />
                <div>
                  <p className="auth-feature-label">{f.label}</p>
                  <p className="auth-feature-desc">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right: Auth form */}
      <div className="auth-form-area">
        <div className="auth-form-card animate-fade-in">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
