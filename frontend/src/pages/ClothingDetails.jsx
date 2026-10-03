import React, { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Sparkles, Shirt, Info, Check, X, Loader2 } from 'lucide-react'
import { getClothingById } from '../services/clothingService'
import { getImageUrl } from '../utils/imageUrl'
import './ClothingDetails.css'

export default function ClothingDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [clothing, setClothing] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getClothingById(id)
        setClothing(data.data.clothing)
      } catch (err) {
        const status = err.response?.status
        if (status === 404) setError('This clothing item could not be found.')
        else setError('Failed to load clothing details.')
      } finally {
        setIsLoading(false)
      }
    }
    fetch()
  }, [id])

  if (isLoading) {
    return (
      <div className="clothing-details-page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Loader2 size={40} className="animate-spin text-primary" />
      </div>
    )
  }

  if (error || !clothing) {
    return (
      <div className="clothing-details-page">
        <Link to="/clothing" className="back-link"><ArrowLeft size={18} /> Back to Clothing</Link>
        <div className="catalog-empty-state mt-8">
          <Shirt size={48} className="empty-icon" />
          <h3>{error || 'Item not found'}</h3>
          <Link to="/clothing" className="btn-primary mt-4" style={{ display: 'inline-flex' }}>Browse Catalog</Link>
        </div>
      </div>
    )
  }

  const imageUrl = getImageUrl(clothing.image_path || clothing.image)

  return (
    <div className="clothing-details-page animate-fade-in">
      <Link to="/clothing" className="back-link"><ArrowLeft size={18} /> Back to Clothing</Link>

      <div className="details-container">
        <div className="details-image-section">
          <div className="details-image-card">
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={clothing.name}
                className="details-img"
                onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex' }}
              />
            ) : null}
            <div className="details-placeholder" style={{ display: imageUrl ? 'none' : 'flex' }}>
              <Shirt size={64} className="text-muted" />
              <p>No Image Available</p>
            </div>
            {!clothing.available && (
              <div className="details-overlay">
                <span className="badge-unavailable-lg">Out of Stock</span>
              </div>
            )}
          </div>
        </div>

        <div className="details-info-section">
          <div className="details-header">
            <span className="details-category">{clothing.category}</span>
            <h1 className="details-title">{clothing.name}</h1>
            {clothing.price && <p className="details-price">₹{clothing.price}</p>}
          </div>

          <div className="details-divider"></div>

          {clothing.description && (
            <div className="details-description">
              <h3><Info size={16} /> Description</h3>
              <p>{clothing.description}</p>
            </div>
          )}

          <div className="details-options">
            {clothing.color && (
              <div className="option-group">
                <h3>Color</h3>
                <div className="color-display">
                  <span className={`color-dot-lg bg-${clothing.color.toLowerCase()}`}></span>
                  {clothing.color}
                </div>
              </div>
            )}
            {clothing.sizes?.length > 0 && (
              <div className="option-group">
                <h3>Available Sizes</h3>
                <div className="sizes-list">
                  {clothing.sizes.map(size => (
                    <span key={size} className="size-pill">{size}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="details-availability">
            {clothing.available ? (
              <span className="text-success flex-center gap-2"><Check size={18} /> In Stock and ready for virtual try-on</span>
            ) : (
              <span className="text-error flex-center gap-2"><X size={18} /> Currently unavailable</span>
            )}
          </div>

          <div className="details-actions">
            <button
              onClick={() => navigate(`/try-on?clothing=${clothing._id}`)}
              className="btn-primary btn-large full-width flex-center gap-2"
              disabled={!clothing.available}
            >
              <Sparkles size={20} /> Try On Now
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
