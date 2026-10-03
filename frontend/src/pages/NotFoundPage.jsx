import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'

export default function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg-default)',
      color: 'var(--text-primary)',
      textAlign: 'center',
      padding: '20px'
    }}>
      <h1 style={{ fontSize: '6rem', fontWeight: '800', color: 'var(--primary-500)', lineHeight: '1' }}>404</h1>
      <h2 style={{ fontSize: '2rem', marginBottom: '16px', fontWeight: '600' }}>Page Not Found</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '40px', maxWidth: '400px' }}>
        The page you're looking for doesn't exist or has been moved.
      </p>
      
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
        <button 
          onClick={() => navigate(-1)} 
          className="btn-secondary flex-center gap-2"
        >
          <ArrowLeft size={18} /> Go Back
        </button>
        <Link to="/dashboard" className="btn-primary flex-center gap-2">
          <Home size={18} /> Go to Dashboard
        </Link>
      </div>
    </div>
  )
}
