import React from 'react'
import { Outlet } from 'react-router-dom'
import PublicNavbar from '../components/layout/PublicNavbar'
import Footer from '../components/layout/Footer'

export default function PublicLayout() {
  return (
    <div className="public-layout">
      <PublicNavbar />
      <main className="public-main">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
