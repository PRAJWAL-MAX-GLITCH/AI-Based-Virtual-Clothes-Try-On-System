import React from 'react'
import { ArrowLeft, Sparkles, Plus, Image as ImageIcon, Shirt } from 'lucide-react'
import { getImageUrl } from '../../utils/imageUrl'

export default function TryOnReview({ personImage, selectedClothing, onStart, onBack }) {
  // personImage is now a raw URL string (object URL from browser)
  const personImgSrc = typeof personImage === 'string' ? personImage : personImage?.preview
  const clothingImgUrl = getImageUrl(selectedClothing?.image_path || selectedClothing?.image)

  return (
    <div className="step-container animate-fade-in">
      <div className="step-header text-center">
        <h2>You're ready to try this outfit.</h2>
        <p>Review your selection before we start processing.</p>
      </div>

      <div className="review-layout">
        <div className="review-card">
          <div className="review-img-wrap">
            {personImgSrc ? (
              <img src={personImgSrc} alt="Person" className="review-img" />
            ) : (
              <div className="review-placeholder"><ImageIcon size={48} className="text-muted" /></div>
            )}
          </div>
          <div className="review-info">
            <ImageIcon size={16} className="text-muted" />
            <span>Your Photo</span>
          </div>
        </div>

        <div className="review-plus">
          <Plus size={32} className="text-muted" />
        </div>

        <div className="review-card">
          <div className="review-img-wrap">
            {clothingImgUrl ? (
              <img src={clothingImgUrl} alt={selectedClothing?.name} className="review-img" />
            ) : (
              <div className="review-placeholder"><Shirt size={48} className="text-muted" /></div>
            )}
          </div>
          <div className="review-info">
            <Shirt size={16} className="text-muted" />
            <span className="truncate" title={selectedClothing?.name}>{selectedClothing?.name}</span>
          </div>
        </div>
      </div>

      <div className="step-actions mt-8 justify-center">
        <button onClick={onBack} className="btn-secondary flex-center gap-2">
          <ArrowLeft size={18} /> Back
        </button>
        <button onClick={onStart} className="btn-primary btn-large flex-center gap-2">
          <Sparkles size={20} /> Start Virtual Try-On
        </button>
      </div>
    </div>
  )
}
