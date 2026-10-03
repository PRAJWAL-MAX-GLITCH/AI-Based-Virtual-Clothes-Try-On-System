import React, { useState, useEffect } from 'react'
import { Plus, FolderHeart, AlertTriangle, Loader2 } from 'lucide-react'
import MyClothingCard from '../components/my-clothing/MyClothingCard'
import ClothingUpload from '../components/my-clothing/ClothingUpload'
import { getUserClothing, deleteUserClothing, uploadCustomClothing } from '../services/userClothingService'
import { useToast } from '../context/ToastContext'
import './MyClothingPage.css'

export default function MyClothingPage() {
  const { showToast } = useToast()
  const [myClothes, setMyClothes] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [itemToDelete, setItemToDelete] = useState(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const fetchMyClothes = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getUserClothing()
      setMyClothes(data.data.items || [])
    } catch (err) {
      setError('Failed to load your clothing. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { fetchMyClothes() }, [])

  const handleSaveClothing = async (formData) => {
    // formData is a FormData object from ClothingUpload
    try {
      const data = await uploadCustomClothing(formData)
      setMyClothes(prev => [data.data.clothing, ...prev])
      setIsUploadOpen(false)
      showToast('Clothing uploaded successfully.', 'success')
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to upload clothing.'
      showToast(msg, 'error')
      throw err // Re-throw so ClothingUpload can show the error state
    }
  }

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return
    setIsDeleting(true)
    try {
      await deleteUserClothing(itemToDelete._id)
      setMyClothes(prev => prev.filter(c => c._id !== itemToDelete._id))
      showToast('Clothing removed.', 'success')
      setItemToDelete(null)
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to delete clothing.'
      showToast(msg, 'error')
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="my-clothing-page animate-fade-in">
      <div className="page-header flex-between align-center">
        <div>
          <h1 className="page-title">My Clothes</h1>
          <p className="page-desc">Upload and manage your own clothing for virtual try-on.</p>
        </div>
        <button onClick={() => setIsUploadOpen(true)} className="btn-primary flex-center gap-2 hidden-mobile">
          <Plus size={18} /> Upload Clothing
        </button>
      </div>

      <div className="mobile-cta-row hidden-desktop">
        <button onClick={() => setIsUploadOpen(true)} className="btn-primary full-width flex-center gap-2">
          <Plus size={18} /> Upload Clothing
        </button>
      </div>

      <div className="my-clothing-content">
        {isLoading ? (
          <div className="catalog-empty-state mt-8">
            <Loader2 size={40} className="animate-spin text-primary" />
            <p className="mt-4 text-muted">Loading your clothes...</p>
          </div>
        ) : error ? (
          <div className="catalog-empty-state mt-8">
            <h3>Something went wrong</h3>
            <p>{error}</p>
            <button onClick={fetchMyClothes} className="btn-primary-sm mt-4">Retry</button>
          </div>
        ) : myClothes.length > 0 ? (
          <div className="clothing-grid">
            {myClothes.map(item => (
              <MyClothingCard key={item._id} item={item} onDelete={setItemToDelete} />
            ))}
          </div>
        ) : (
          <div className="catalog-empty-state" style={{ marginTop: '40px' }}>
            <FolderHeart size={48} className="empty-icon" />
            <h3>No clothes uploaded yet</h3>
            <p>Upload your own clothing and use it for virtual try-on.</p>
            <button onClick={() => setIsUploadOpen(true)} className="btn-primary-sm mt-4">Upload Your First Clothing</button>
          </div>
        )}
      </div>

      {isUploadOpen && (
        <ClothingUpload
          onClose={() => setIsUploadOpen(false)}
          onSave={handleSaveClothing}
        />
      )}

      {itemToDelete && (
        <div className="upload-modal-overlay">
          <div className="dialog-box animate-scale-in">
            <div className="dialog-icon-warning">
              <AlertTriangle size={24} />
            </div>
            <h3>Delete this clothing?</h3>
            <p>Are you sure you want to remove "{itemToDelete.name}"? This cannot be undone.</p>
            <div className="dialog-actions mt-6">
              <button onClick={() => setItemToDelete(null)} className="btn-secondary flex-1" disabled={isDeleting}>Cancel</button>
              <button onClick={handleDeleteConfirm} className="btn-danger flex-1" disabled={isDeleting}>
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
