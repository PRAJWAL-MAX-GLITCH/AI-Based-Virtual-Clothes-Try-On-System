import React from 'react'
import { Link } from 'react-router-dom'
import { Trash2, Sparkles, AlertCircle } from 'lucide-react'
import { getImageUrl } from '../../utils/imageUrl'

export default function HistoryCard({ item, onDelete }) {
  const isCompleted = item.status === 'completed'
  const itemId = item._id || item.id

  // Handle both snake_case (backend) and camelCase (legacy mock) field names
  const clothingName = item.clothing_name || item.clothingName || 'Unknown'
  const clothingCategory = item.clothing_category || item.clothingCategory || ''
  const createdAt = item.created_at || item.createdAt
  const resultImageUrl = item.result_image_path ? getImageUrl(item.result_image_path) : (item.resultImage || null)

  return (
    <div className="history-card group">
      <div className="history-card-image-wrap">
        {resultImageUrl ? (
          <img src={resultImageUrl} alt={clothingName} className="history-card-image"
            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex' }} />
        ) : null}
        <div className="history-card-placeholder" style={{ display: resultImageUrl ? 'none' : 'flex' }}>
          {isCompleted ? (
            <Sparkles size={48} className="text-primary opacity-50" />
          ) : (
            <AlertCircle size={48} className="text-error opacity-50" />
          )}
          <span className="mt-2 text-sm text-muted">
            {isCompleted ? 'View Result' : 'Failed'}
          </span>
        </div>

        <div className="history-status-badge">
          <span className={`status-badge ${isCompleted ? 'success' : 'error'}`}>
            {isCompleted ? 'Completed' : 'Failed'}
          </span>
        </div>

        <div className="history-card-actions">
          <Link to={`/history/${itemId}`} className="btn-primary-sm full-width flex-center gap-2">
            View Result
          </Link>
        </div>
      </div>

      <div className="history-card-info">
        <div className="flex-between align-start">
          <div>
            <h3 className="history-card-title" title={clothingName}>{clothingName}</h3>
            {clothingCategory && (
              <p className="history-card-meta">
                <span className="capitalize">{clothingCategory}</span>
              </p>
            )}
          </div>
          <button onClick={() => onDelete(item)} className="btn-icon text-error" title="Delete from history">
            <Trash2 size={16} />
          </button>
        </div>

        {createdAt && (
          <div className="history-card-date mt-3">
            {new Date(createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
          </div>
        )}
      </div>
    </div>
  )
}
