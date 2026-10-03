import React, { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Sidebar from '../components/layout/Sidebar'
import './AppLayout.css'

/**
 * AppLayout — wraps all authenticated pages.
 * Provides Navbar + Sidebar + main content area.
 */
export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const toggleSidebar = () => setSidebarOpen((prev) => !prev)

  return (
    <div className="app-layout">
      <Navbar onMenuToggle={toggleSidebar} sidebarOpen={sidebarOpen} />
      <Sidebar open={sidebarOpen} />

      <main className={`app-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="app-content animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
