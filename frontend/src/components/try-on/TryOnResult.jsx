import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, History, Download, CheckCircle2, Shirt } from 'lucide-react'
import { getImageUrl } from '../../utils/imageUrl'

export default function TryOnResult({ result, onReset }) {
  const navigate = useNavigate()

  const resultImageUrl = result?.result_image_path ? getImageUrl(result.result_image_path) : null

  return (
    <div className="step-container animate-fade-in">
      <div className="step-header text-center">
        <div className="flex-center gap-2 mb-2">
          <CheckCircle2 size={24} className="text-success" />
          <h2>Your Virtual Look is Ready!</h2>
        </div>
        <p>Here's how the outfit looks on you.</p>
      </div>

      <div className="result-layout">
        <div className="result-presentation">
          {resultImageUrl ? (
            <img
              src={resultImageUrl}
              alt="Virtual Try-On Result"
              className="result-image"
              style={{ width: '100%', borderRadius: '12px', objectFit: 'contain', maxHeight: '70vh' }}
            />
          ) : (
            <div className="result-mock-image">
              <Shirt size={48} className="text-primary opacity-50 mb-4" />
              <p className="result-mock-text">Result image not available</p>
              <p className="result-mock-subtext text-muted">The try-on was completed but the result image could not be loaded.</p>
            </div>
          )}
        </div>

        {result && (
          <div className="result-meta mt-4" style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            <p>Status: <strong style={{ color: 'var(--success)' }}>Completed</strong></p>
          </div>
        )}

        <div className="result-actions-grid mt-6">
          <button onClick={onReset} className="btn-primary flex-center gap-2">
            <Sparkles size={18} /> Try Another Outfit
          </button>
          <button onClick={() => navigate('/history')} className="btn-secondary flex-center gap-2">
            <History size={18} /> View History
          </button>
          <button
            className="btn-secondary flex-center gap-2"
            disabled={!resultImageUrl}
            title={!resultImageUrl ? 'No result image available' : 'Download result'}
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
  )
}
