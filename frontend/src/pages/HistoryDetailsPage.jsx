import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Sparkles, Download, AlertCircle, Loader2 } from 'lucide-react'
import { getHistoryItem } from '../services/historyService'
import { getImageUrl } from '../utils/imageUrl'
import './HistoryDetailsPage.css'

export default function HistoryDetailsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getHistoryItem(id)
        setResult(data.data.record || data.data)
      } catch (err) {
        const status = err.response?.status
        if (status === 404) setError('This history record could not be found.')
        else if (status === 403) setError('You do not have permission to view this record.')
        else setError('Failed to load history details.')
      } finally {
        setIsLoading(false)
      }
    }
    fetch()
  }, [id])

  if (isLoading) {
    return (
      <div className="history-details-page flex-center" style={{ minHeight: '60vh', justifyContent: 'center' }}>
        <Loader2 size={40} className="animate-spin text-primary" />
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="history-details-page">
        <button onClick={() => navigate('/history')} className="btn-icon mb-6">
          <ArrowLeft size={20} /> <span className="ml-2 font-medium">Back to History</span>
        </button>
        <div className="catalog-empty-state mt-8">
          <AlertCircle size={48} className="text-error mb-4" />
          <h3>{error || 'Result not found'}</h3>
          <div className="flex gap-4 mt-6">
            <Link to="/history" className="btn-secondary">Back to History</Link>
            <Link to="/try-on" className="btn-primary">Start New Try-On</Link>
          </div>
        </div>
      </div>
    )
  }

  const isCompleted = result.status === 'completed'
  const resultImageUrl = result.result_image_path ? getImageUrl(result.result_image_path) : null
  const clothingName = result.clothing_name || result.clothingName || 'Unknown'
  const clothingCategory = result.clothing_category || result.clothingCategory || ''
  const clothingId = result.clothing_id || result.clothingId
  const createdAt = result.created_at || result.createdAt

  return (
    <div className="history-details-page animate-fade-in">
      <div className="details-header flex-between align-center">
        <button onClick={() => navigate('/history')} className="btn-icon">
          <ArrowLeft size={20} /> <span className="ml-2 font-medium">Back to History</span>
        </button>
      </div>

      <div className="details-layout">
        {/* Left: Image Viewer */}
        <div className="details-image-section">
          <div className="details-image-viewer">
            {resultImageUrl ? (
              <img src={resultImageUrl} alt="Try-On Result" className="viewer-img"
                onError={(e) => { e.target.style.display = 'none' }} />
            ) : (
              <div className="viewer-placeholder">
                {isCompleted ? (
                  <>
                    <Sparkles size={64} className="text-primary opacity-50 mb-4" />
                    <h3 className="text-xl font-semibold mb-2 text-primary">Try-On Complete</h3>
                    <p className="text-muted">Result image could not be loaded.</p>
                  </>
                ) : (
                  <>
                    <AlertCircle size={64} className="text-error opacity-50 mb-4" />
                    <h3 className="text-xl font-semibold mb-2 text-error">Generation Failed</h3>
                    <p className="text-muted">Unable to complete the virtual try-on.</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Info & Actions */}
        <div className="details-info-section">
          <div className="details-card">
            <div className="flex-between align-start mb-6">
              <div>
                <h1 className="details-title">{clothingName}</h1>
                {clothingCategory && <p className="details-category capitalize">{clothingCategory}</p>}
              </div>
              <span className={`status-badge ${isCompleted ? 'success' : 'error'}`}>
                {isCompleted ? 'Completed' : 'Failed'}
              </span>
            </div>

            <div className="details-meta-grid">
              {createdAt && (
                <div className="meta-item">
                  <span className="meta-label">Try-On Date</span>
                  <span className="meta-value">
                    {new Date(createdAt).toLocaleDateString(undefined, {
                      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                  </span>
                </div>
              )}
              <div className="meta-item">
                <span className="meta-label">Result ID</span>
                <span className="meta-value text-mono text-sm">{result._id || result.id}</span>
              </div>
            </div>
          </div>

          <div className="details-actions">
            {clothingId && (
              <Link to={`/try-on?clothing=${clothingId}`} className="btn-primary btn-large flex-center gap-2 full-width">
                <Sparkles size={18} /> Try Again with this Outfit
              </Link>
            )}
            <button
              className="btn-secondary btn-large flex-center gap-2 full-width mt-4"
              disabled={!resultImageUrl}
              title={!resultImageUrl ? 'No result image available' : 'Download Result'}
              onClick={() => {
                if (resultImageUrl) {
                  const a = document.createElement('a')
                  a.href = resultImageUrl
                  a.download = 'virtual-try-on-result.jpg'
                  a.click()
                }
              }}
            >
              <Download size={18} /> Download Result
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
