import React from 'react'
import { AlertCircle } from 'lucide-react'

export function InputField({ label, id, error, className = '', ...props }) {
  return (
    <div className={`form-group ${className}`}>
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <div className="input-wrapper">
        <input 
          id={id}
          className={`form-input ${error ? 'input-error' : ''}`}
          {...props}
        />
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
