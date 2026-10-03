import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { validateRegisterForm } from '../utils/validators'
import { InputField } from '../components/ui/InputField'
import { PasswordInput } from '../components/ui/PasswordInput'
import { Button } from '../components/ui/Button'
import { AlertCircle } from 'lucide-react'
import './AuthPages.css'

export default function RegisterPage() {
  const [formData, setFormData] = useState({ 
    name: '', 
    email: '', 
    password: '', 
    confirmPassword: '',
    terms: false 
  })
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const { register, isLoading } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }))
    }
    setApiError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validate
    const validationErrors = validateRegisterForm(formData)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    // Attempt mock registration
    const result = await register({
      name: formData.name,
      email: formData.email,
      password: formData.password
    })

    if (result.success) {
      navigate('/login', { state: { message: 'Account created! Please sign in.' } })
    } else {
      setApiError(result.error)
    }
  }

  return (
    <div className="auth-container animate-fade-in">
      <div className="auth-header">
        <h1 className="auth-title">Create Your Account</h1>
        <p className="auth-desc">Start exploring AI-powered virtual try-on.</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        {apiError && (
          <div className="form-error-msg" style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
            <AlertCircle size={16} />
            <span>{apiError}</span>
          </div>
        )}

        <InputField
          label="Full Name"
          id="name"
          name="name"
          type="text"
          placeholder="Jane Doe"
          value={formData.name}
          onChange={handleChange}
          error={errors.name}
          autoComplete="name"
          disabled={isLoading}
        />

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
          autoComplete="new-password"
          disabled={isLoading}
        />

        <PasswordInput
          label="Confirm Password"
          id="confirmPassword"
          name="confirmPassword"
          placeholder="••••••••"
          value={formData.confirmPassword}
          onChange={handleChange}
          error={errors.confirmPassword}
          autoComplete="new-password"
          disabled={isLoading}
        />

        <div className="form-extras" style={{ marginTop: '4px' }}>
          <label className="checkbox-group">
            <input 
              type="checkbox" 
              name="terms" 
              checked={formData.terms}
              onChange={handleChange}
              disabled={isLoading}
            />
            <span className="checkbox-label" style={{ fontSize: '0.85rem' }}>
              I agree to the <a href="#" className="forgot-link">Terms & Conditions</a>
            </span>
          </label>
        </div>
        {errors.terms && (
          <span className="form-error-msg" style={{ marginTop: '-12px', marginBottom: '8px' }}>
            <AlertCircle size={14} />
            {errors.terms}
          </span>
        )}

        <Button type="submit" isLoading={isLoading}>
          Create Account
        </Button>
      </form>

      <div className="auth-footer">
        Already have an account? 
        <Link to="/login" className="auth-link">Sign In</Link>
      </div>
      
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <Link to="/" className="auth-link" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          ← Back to Home
        </Link>
      </div>
    </div>
  )
}
