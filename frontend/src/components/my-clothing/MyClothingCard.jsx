import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Trash2, Shirt } from 'lucide-react'
import { getImageUrl } from '../../utils/imageUrl'

export default function MyClothingCard({ item, onDelete }) {
  const navigate = useNavigate()
  const imageUrl = getImageUrl(item.image_path || item.image)

  const handleTryOn = () => {
    navigate(`/try-on?customClothing=${item._id}`)
  }

  return (
    <div className="clothing-card group">
      <div className="clothing-card-image-wrap">
        {imageUrl ? (
          <img src={imageUrl} alt={item.name} className="clothing-card-image"
            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex' }} />
        ) : null}
        <div className="clothing-card-placeholder" style={{ display: imageUrl ? 'none' : 'flex' }}>
          <Shirt size={48} className="placeholder-icon" />
        </div>

        <div className="clothing-card-actions">
          <button onClick={handleTryOn} className="btn-primary-sm full-width flex-center gap-2">
            <Sparkles size={14} /> Try On
          </button>
        </div>
      </div>

      <div className="clothing-card-info">
        <div className="flex-between align-start">
          <div>
            <h3 className="clothing-card-title" title={item.name}>{item.name}</h3>
            <p className="clothing-card-category">{item.category}</p>
          </div>
          <button onClick={() => onDelete(item)} className="btn-icon text-error" title="Delete this clothing">
            <Trash2 size={16} />
          </button>
        </div>

        <div className="flex-between align-center mt-3">
          {item.color && (
            <div className="clothing-card-color">
              <span className={`color-dot bg-${item.color.toLowerCase()}`}></span>
              {item.color}
            </div>
          )}
          <span className="status-badge success">Available</span>
        </div>
      </div>
    </div>
  )
}
