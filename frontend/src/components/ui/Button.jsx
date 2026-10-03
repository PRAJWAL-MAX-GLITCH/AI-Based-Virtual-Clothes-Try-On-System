import React from 'react'
import { Loader2 } from 'lucide-react'

export function Button({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  isLoading = false, 
  disabled = false,
  className = '',
  ...props 
}) {
  const baseClass = variant === 'primary' ? 'btn-primary' : 'btn-secondary'
  
  return (
    <button 
      type={type} 
      className={`${baseClass} ${className} ${isLoading ? 'loading' : ''}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 className="animate-spin" size={18} />
          <span>Please wait...</span>
        </>
      ) : children}
    </button>
  )
}
