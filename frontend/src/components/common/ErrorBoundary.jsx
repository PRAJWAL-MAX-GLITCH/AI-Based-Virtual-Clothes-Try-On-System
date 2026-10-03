import React from 'react'
import { AlertOctagon, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo)
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
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
          <AlertOctagon size={64} style={{ color: 'var(--error)', marginBottom: '24px' }} />
          <h1 style={{ fontSize: '2rem', marginBottom: '16px' }}>Something went wrong.</h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '400px' }}>
            An unexpected error occurred in the application. Please reload the page to continue.
          </p>
          <button 
            onClick={this.handleReload}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              background: 'var(--primary-500)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            <RefreshCw size={18} /> Reload Application
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
