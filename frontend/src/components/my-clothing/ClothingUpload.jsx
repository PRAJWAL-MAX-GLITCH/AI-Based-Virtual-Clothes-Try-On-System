import React, { useState, useRef } from 'react'
import { UploadCloud, X, Image as ImageIcon, AlertCircle, Loader2 } from 'lucide-react'
import { validateClothingImage } from '../../utils/imageValidation'
const CATEGORIES = ['t-shirt', 'shirt', 'hoodie', 'jacket', 'dress', 'top']
const COLORS = ['Black', 'White', 'Red', 'Blue', 'Green', 'Grey', 'Navy', 'Beige', 'Brown', 'Pink', 'Purple', 'Other']

export default function ClothingUpload({ onClose, onSave }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [fileError, setFileError] = useState('')
  
  const [formData, setFormData] = useState({
    name: '',
    category: 't-shirt',
    color: 'Black'
  })
  const [formErrors, setFormErrors] = useState({})
  
  const [isSaving, setIsSaving] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (selectedFile) => {
    const { valid, error } = validateClothingImage(selectedFile)
    if (!valid) {
      setFileError(error)
      return
    }
    setFileError('')
    setFile(selectedFile)
    
    // Clean up old preview if exists
    if (preview) URL.revokeObjectURL(preview)
    
    // Create preview
    const objectUrl = URL.createObjectURL(selectedFile)
    setPreview(objectUrl)
  }

  const handleRemoveImage = () => {
    setFile(null)
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setFileError('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: null }))
    }
  }

  const validateForm = () => {
    const errors = {}
    if (!formData.name.trim()) errors.name = 'Name is required'
    if (formData.name.length > 50) errors.name = 'Name is too long'
    if (!formData.category) errors.category = 'Category is required'
    if (!formData.color) errors.color = 'Color is required'
    if (!file) errors.file = 'Image is required'
    return errors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errors = validateForm()
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    setIsSaving(true)
    try {
      // Build real FormData for multipart upload
      const fd = new FormData()
      fd.append('image', file)
      fd.append('name', formData.name)
      fd.append('category', formData.category)
      fd.append('color', formData.color)
      await onSave(fd)
      // Cleanup preview URL
      if (preview) URL.revokeObjectURL(preview)
    } catch (err) {
      // Error toasted by parent; stay open
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="upload-modal-overlay animate-fade-in">
      <div className="upload-modal" onClick={e => e.stopPropagation()}>
        
        <div className="upload-modal-header">
          <h2>Upload Custom Clothing</h2>
          <button onClick={onClose} className="btn-icon">
            <X size={20} />
          </button>
        </div>

        <div className="upload-modal-content">
          
          {/* Left: Dropzone / Preview */}
          <div className="upload-section">
            {!preview ? (
              <div 
                className={`dropzone ${dragActive ? 'drag-active' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  ref={fileInputRef}
                  type="file" 
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleChange}
                  className="hidden-input"
                />
                <UploadCloud size={48} className="dropzone-icon" />
                <h3>Choose an image from your device</h3>
                <p>or drag & drop here</p>
                <span className="dropzone-hint">Max 5MB (JPG, PNG, WEBP)</span>
              </div>
            ) : (
              <div className="preview-container">
                <img src={preview} alt="Preview" className="image-preview" />
                <div className="preview-actions">
                  <span className="preview-filename">{file?.name}</span>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => fileInputRef.current?.click()} className="btn-secondary-sm">
                      Change
                    </button>
                    <button type="button" onClick={handleRemoveImage} className="btn-danger-sm">
                      Remove
                    </button>
                    <input 
                      ref={fileInputRef}
                      type="file" 
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleChange}
                      className="hidden-input"
                    />
                  </div>
                </div>
              </div>
            )}
            
            {fileError && (
              <div className="form-error-msg mt-2">
                <AlertCircle size={14} /> {fileError}
              </div>
            )}
            {formErrors.file && !fileError && (
              <div className="form-error-msg mt-2">
                <AlertCircle size={14} /> {formErrors.file}
              </div>
            )}
          </div>

          {/* Right: Form */}
          <div className="form-section">
            <div className="form-group">
              <label className="form-label">Clothing Name *</label>
              <input 
                type="text" 
                name="name"
                value={formData.name}
                onChange={handleFormChange}
                placeholder="e.g. My Favorite Black Shirt"
                className={`form-input ${formErrors.name ? 'input-error' : ''}`}
                disabled={isSaving}
              />
              {formErrors.name && <span className="form-error-msg"><AlertCircle size={14} />{formErrors.name}</span>}
            </div>

            <div className="form-group mt-4">
              <label className="form-label">Category *</label>
              <select 
                name="category"
                value={formData.category}
                onChange={handleFormChange}
                className="form-input"
                disabled={isSaving}
              >
                {CATEGORIES.map(cat => (
                  <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                ))}
              </select>
            </div>

            <div className="form-group mt-4">
              <label className="form-label">Color *</label>
              <select 
                name="color"
                value={formData.color}
                onChange={handleFormChange}
                className="form-input"
                disabled={isSaving}
              >
                {COLORS.map(color => (
                  <option key={color} value={color}>{color}</option>
                ))}
              </select>
            </div>

            <div className="upload-modal-footer mt-auto pt-6">
              <button onClick={onClose} className="btn-secondary" disabled={isSaving}>Cancel</button>
              <button onClick={handleSubmit} className="btn-primary flex-center gap-2" disabled={isSaving}>
                {isSaving ? (
                  <><Loader2 size={16} className="animate-spin" /> Saving...</>
                ) : (
                  'Save Clothing'
                )}
              </button>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  )
}
