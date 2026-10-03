import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shirt, Sparkles } from 'lucide-react'
import { getImageUrl } from '../../utils/imageUrl'

export default function ClothingCard({ item }) {
  const navigate = useNavigate()
  const imageUrl = getImageUrl(item.image_path || item.image)

  const handleTryOn = (e) => {
    e.preventDefault()
    navigate(`/try-on?clothing=${item._id}`)
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

        {!item.available && (
          <div className="clothing-card-overlay">
            <span className="badge-unavailable">Out of Stock</span>
          </div>
        )}

        <div className="clothing-card-actions">
          <button
            onClick={handleTryOn}
            className="btn-primary-sm full-width flex-center gap-2"
            disabled={!item.available}
          >
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
          {item.price && <p className="clothing-card-price">₹{item.price}</p>}
        </div>

        <div className="flex-between align-center mt-3">
          {item.color && (
            <div className="clothing-card-color">
              <span className={`color-dot bg-${item.color.toLowerCase()}`}></span>
              {item.color}
            </div>
          )}
          <Link to={`/clothing/${item._id}`} className="clothing-card-details-link">View Details</Link>
        </div>
      </div>
    </div>
  )
}
