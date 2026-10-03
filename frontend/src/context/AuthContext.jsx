import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import * as authService from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true) // For initial token check
  const [isActionLoading, setIsActionLoading] = useState(false) // For login/register

  const initializeAuth = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const data = await authService.getCurrentUser()
        setUser(data.data.user)
        setIsAuthenticated(true)
      } catch (error) {
        localStorage.removeItem('access_token')
        setUser(null)
        setIsAuthenticated(false)
      }
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    initializeAuth()

    const handleUnauthorized = () => {
      setUser(null)
      setIsAuthenticated(false)
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [initializeAuth])

  const login = useCallback(async (credentials) => {
    setIsActionLoading(true)
    try {
      const data = await authService.login(credentials.email, credentials.password)
      const token = data.data.access_token
      localStorage.setItem('access_token', token)
      
      const userData = await authService.getCurrentUser()
      setUser(userData.data.user)
      setIsAuthenticated(true)
      return { success: true }
    } catch (error) {
      const msg = error.response?.data?.message || 'Login failed. Please try again.'
      return { success: false, error: msg }
    } finally {
      setIsActionLoading(false)
    }
  }, [])

  const register = useCallback(async (data) => {
    setIsActionLoading(true)
    try {
      await authService.register(data.name, data.email, data.password)
      return { success: true }
    } catch (error) {
      const msg = error.response?.data?.message || 'Registration failed. Please try again.'
      return { success: false, error: msg }
    } finally {
      setIsActionLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  const value = {
    user,
    setUser,
    isAuthenticated,
    isLoading: isLoading || isActionLoading,
    login,
    register,
    logout,
  }

  // Prevent flashing protected routes before token check completes
  // ONLY block rendering on initial token check, NOT during login/register actions
  if (isLoading) {
    return <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading...</div>
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
