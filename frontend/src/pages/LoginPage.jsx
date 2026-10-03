import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { validateLoginForm } from '../utils/validators'
import { InputField } from '../components/ui/InputField'
import { PasswordInput } from '../components/ui/PasswordInput'
import { Button } from '../components/ui/Button'
import { AlertCircle } from 'lucide-react'
import './AuthPages.css'

export default function LoginPage() {
  const [formData, setFormData] = useState({ email: '', password: '', remember: false })
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = location.state?.from?.pathname || '/dashboard'

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    // Clear error for field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }))
    }
    setApiError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validate
    const validationErrors = validateLoginForm(formData)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    // Attempt login (mocked for Stage 3)
    const result = await login({
      email: formData.email,
      password: formData.password
    })

    if (result.success) {
      navigate(from, { replace: true })
    } else {
      setApiError(result.error)
    }
  }

  return (
    <div className="auth-container animate-fade-in">
      <div className="auth-header">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-desc">Sign in to continue your virtual styling experience.</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        {apiError && (
          <div className="form-error-msg" style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
            <AlertCircle size={16} />
            <span>{apiError}</span>
          </div>
        )}

        <InputField
          label="Email Address"
          id="email"
          name="email"
          type="email"
          placeholder="you@example.com"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
          autoComplete="email"
          disabled={isLoading}
        />

        <PasswordInput
          label="Password"
          id="password"
          name="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={handleChange}
          error={errors.password}
          autoComplete="current-password"
          disabled={isLoading}
        />

        <div className="form-extras">
          <label className="checkbox-group">
            <input 
              type="checkbox" 
              name="remember" 
              checked={formData.remember}
              onChange={handleChange}
              disabled={isLoading}
            />
            <span className="checkbox-label">Remember me</span>
          </label>
          <a href="#" className="forgot-link" onClick={(e) => e.preventDefault()}>
            Forgot password?
          </a>
        </div>

        <Button type="submit" isLoading={isLoading}>
          Sign In
        </Button>
      </form>

      <div className="auth-footer">
        Don't have an account? 
        <Link to="/register" className="auth-link">Create one</Link>
      </div>
      
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <Link to="/" className="auth-link" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          ← Back to Home
        </Link>
      </div>
    </div>
  )
}
