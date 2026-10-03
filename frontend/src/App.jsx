import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'

// Layouts
import AppLayout from './layouts/AppLayout'
import AuthLayout from './layouts/AuthLayout'
import PublicLayout from './layouts/PublicLayout'
import ProtectedRoute from './components/common/ProtectedRoute'

// Pages
import LandingPage    from './pages/LandingPage'
import LoginPage      from './pages/LoginPage'
import RegisterPage   from './pages/RegisterPage'
import DashboardPage  from './pages/DashboardPage'
import TryOnPage      from './pages/TryOnPage'
import ClothingPage   from './pages/ClothingPage'
import ClothingDetails from './pages/ClothingDetails'
import MyClothingPage from './pages/MyClothingPage'
import HistoryPage    from './pages/HistoryPage'
import HistoryDetailsPage from './pages/HistoryDetailsPage'
import ProfilePage    from './pages/ProfilePage'
import NotFoundPage   from './pages/NotFoundPage'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public landing */}
          <Route element={<PublicLayout />}>
            <Route path="/" element={<LandingPage />} />
          </Route>

          {/* Auth pages — split-panel layout */}
          <Route element={<AuthLayout />}>
            <Route path="/login"    element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          {/* Protected App pages */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard"   element={<DashboardPage />} />
              <Route path="/try-on"      element={<TryOnPage />} />
              <Route path="/clothing"    element={<ClothingPage />} />
              <Route path="/clothing/:id" element={<ClothingDetails />} />
              <Route path="/my-clothing" element={<MyClothingPage />} />
              <Route path="/history"     element={<HistoryPage />} />
              <Route path="/history/:id" element={<HistoryDetailsPage />} />
              <Route path="/profile"     element={<ProfilePage />} />
            </Route>
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
