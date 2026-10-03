import React, { useState, useEffect, useRef } from 'react'
import { CheckCircle2, ArrowLeft, ArrowRight, Shirt, Loader2, Plus } from 'lucide-react'
import { getClothingCatalog } from '../../services/clothingService'
import { getUserClothing, uploadCustomClothing } from '../../services/userClothingService'
import { getImageUrl } from '../../utils/imageUrl'
import { useToast } from '../../context/ToastContext'

function SelectionCard({ item, isSelected, onSelect, disabled, imageUrl }) {
  return (
    <div
      className={`selection-card ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={() => !disabled && onSelect(item)}
    >
      <div className="selection-card-img-wrap">
        {imageUrl ? (
          <img src={imageUrl} alt={item.name} className="selection-card-img"
            onError={(e) => { e.target.style.display = 'none' }} />
        ) : (
          <div className="selection-card-placeholder"><Shirt size={32} /></div>
        )}
        {isSelected && (
          <div className="selection-badge">
            <CheckCircle2 size={24} className="text-success" fill="white" />
          </div>
        )}
      </div>
      <div className="selection-card-info">
        <h4>{item.name}</h4>
        <p>{item.category}</p>
      </div>
    </div>
  )
}

export default function ClothingSelector({ selectedClothing, setSelectedClothing, onNext, onBack }) {
  const [activeTab, setActiveTab] = useState('catalog')
  const [catalogItems, setCatalogItems] = useState([])
  const [myClothesItems, setMyClothesItems] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef(null)
  const { showToast } = useToast()

  const fetchMyClothes = async () => {
    try {
      const data = await getUserClothing()
      setMyClothesItems(data.data.items || [])
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        if (activeTab === 'catalog') {
          const data = await getClothingCatalog({ available: true, limit: 24 })
          setCatalogItems(data.data.items || [])
        } else {
          await fetchMyClothes()
        }
      } catch (err) {
        // silently fail
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [activeTab])

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('image', file)
    formData.append('name', 'Custom Garment')
    formData.append('category', 'top') // default category MUST be one of: t-shirt, shirt, hoodie, jacket, dress, top

    try {
      const data = await uploadCustomClothing(formData)
      showToast('Clothing uploaded successfully!', 'success')
      await fetchMyClothes() // Refresh list
      setSelectedClothing(data.data.clothing) // Auto-select the newly uploaded item
    } catch (err) {
      showToast('Failed to upload clothing', 'error')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <div className="step-container animate-fade-in">
      <div className="step-header">
        <h2>Choose Clothing</h2>
        <p>Select the garment you want to try on.</p>
      </div>

      <div className="clothing-selector-tabs">
        <button className={`tab-btn ${activeTab === 'catalog' ? 'active' : ''}`} onClick={() => setActiveTab('catalog')}>
          Clothing Catalog
        </button>
        <button className={`tab-btn ${activeTab === 'my-clothes' ? 'active' : ''}`} onClick={() => setActiveTab('my-clothes')}>
          My Clothes
        </button>
      </div>

      <div className="clothing-selection-grid">
        {isLoading ? (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '40px' }}>
            <Loader2 size={32} className="animate-spin text-primary" style={{ margin: '0 auto' }} />
          </div>
        ) : activeTab === 'catalog' ? (
          catalogItems.length > 0 ? catalogItems.map(item => (
            <SelectionCard
              key={item.id}
              item={item}
              isSelected={selectedClothing?.id === item.id}
              onSelect={setSelectedClothing}
              disabled={!item.available}
              imageUrl={getImageUrl(item.image_path || item.image)}
            />
          )) : (
            <div className="empty-selection" style={{ gridColumn: '1/-1' }}>
              <Shirt size={48} className="text-muted mb-4" />
              <h3>No catalog items available</h3>
            </div>
          )
        ) : (
          <>
            {/* Hidden file input for uploading custom clothing */}
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept="image/jpeg, image/png, image/webp"
              onChange={handleFileUpload} 
            />
            
            {/* Upload New Card */}
            <div 
              className={`selection-card ${isUploading ? 'disabled' : ''}`} 
              onClick={() => !isUploading && fileInputRef.current?.click()}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '200px', cursor: 'pointer', borderStyle: 'dashed' }}
            >
              {isUploading ? (
                <Loader2 size={32} className="animate-spin text-primary mb-2" />
              ) : (
                <Plus size={32} className="text-primary mb-2" />
              )}
              <h4 style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                {isUploading ? 'Uploading...' : 'Upload New'}
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>From your device</p>
            </div>

            {myClothesItems.map(item => (
              <SelectionCard
                key={item.id}
                item={item}
                isSelected={selectedClothing?.id === item.id}
                onSelect={setSelectedClothing}
                disabled={false}
                imageUrl={getImageUrl(item.image_path || item.image)}
              />
            ))}
          </>
        )}
      </div>

      <div className="step-actions mt-8 pt-6 border-top">
        <button onClick={onBack} className="btn-secondary flex-center gap-2">
          <ArrowLeft size={18} /> Back
        </button>
        <button onClick={onNext} className="btn-primary flex-center gap-2" disabled={!selectedClothing}>
          Review Try-On <ArrowRight size={18} />
        </button>
      </div>
    </div>
  )
}
