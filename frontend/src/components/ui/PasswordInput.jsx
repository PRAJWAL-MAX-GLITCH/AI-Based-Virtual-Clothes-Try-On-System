import React, { useState } from 'react'
import { AlertCircle, Eye, EyeOff } from 'lucide-react'

export function PasswordInput({ label, id, error, className = '', ...props }) {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className={`form-group ${className}`}>
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <div className="input-wrapper relative">
        <input 
          id={id}
          type={showPassword ? 'text' : 'password'}
          className={`form-input ${error ? 'input-error' : ''}`}
          style={{ paddingRight: '40px' }}
          {...props}
        />
        <button 
          type="button"
          className="password-toggle-btn"
          onClick={() => setShowPassword(!showPassword)}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
      {error && (
        <span className="form-error-msg">
          <AlertCircle size={14} />
          {error}
        </span>
      )}
    </div>
  )
}
