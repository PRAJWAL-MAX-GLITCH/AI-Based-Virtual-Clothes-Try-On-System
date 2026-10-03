import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Sparkles, Shirt,
  FolderHeart, History, User, ChevronRight, LogOut
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import './Sidebar.css'

const navItems = [
  {
    group: 'Main',
    items: [
      { to: '/dashboard',   icon: <LayoutDashboard size={18} />, label: 'Dashboard' },
      { to: '/try-on',      icon: <Sparkles size={18} />,        label: 'Virtual Try-On', badge: 'AI' },
    ],
  },
  {
    group: 'Wardrobe',
    items: [
      { to: '/clothing',    icon: <Shirt size={18} />,       label: 'Clothing' },
      { to: '/my-clothing', icon: <FolderHeart size={18} />, label: 'My Clothes' },
      { to: '/history',     icon: <History size={18} />,     label: 'History' },
    ],
  },
  {
    group: 'Account',
    items: [
      { to: '/profile', icon: <User size={18} />, label: 'Profile' },
    ],
  },
]

export default function Sidebar({ open }) {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <>
      {/* Backdrop for mobile */}
      {open && <div className="sidebar-backdrop" />}

      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <nav className="sidebar-nav">
          {navItems.map((section) => (
            <div key={section.group} className="sidebar-section">
              <span className="sidebar-section-label">{section.group}</span>
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `sidebar-item ${isActive ? 'active' : ''}`
                  }
                >
                  <span className="sidebar-item-icon">{item.icon}</span>
                  <span className="sidebar-item-label">{item.label}</span>
                  {item.badge && (
                    <span className="sidebar-badge">{item.badge}</span>
                  )}
                  <ChevronRight size={12} className="sidebar-item-arrow" />
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <button onClick={handleLogout} className="sidebar-item" style={{ width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left', color: 'var(--error)' }}>
            <span className="sidebar-item-icon"><LogOut size={18} /></span>
            <span className="sidebar-item-label">Logout</span>
          </button>
        </div>
      </aside>
    </>
  )
}
