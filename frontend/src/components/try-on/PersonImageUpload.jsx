import React, { useRef, useState } from 'react'
import { UploadCloud, AlertCircle, Image as ImageIcon, Trash2, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react'
import { validateClothingImage } from '../../utils/imageValidation'

export default function PersonImageUpload({ personImage, setPersonImage, onFileSelected, personImageId, onNext }) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0])
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) handleFile(e.target.files[0])
  }

  const handleFile = async (selectedFile) => {
    const { valid, error: validationError } = validateClothingImage(selectedFile)
    if (!valid) {
      setError(validationError)
      return
    }
    setError('')
    setIsUploading(true)
    const previewUrl = URL.createObjectURL(selectedFile)
    // setPersonImage stores the preview URL for display
    if (typeof setPersonImage === 'function') setPersonImage(previewUrl)

    try {
      await onFileSelected(selectedFile, previewUrl)
    } catch (e) {
      // error toasted by parent
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemove = () => {
    if (personImage) URL.revokeObjectURL(personImage)
    setPersonImage(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="step-container animate-fade-in">
      <div className="step-header">
        <h2>Upload Your Photo</h2>
        <p>Upload a clear front-facing photo for the best virtual try-on result.</p>
      </div>

      {!personImage ? (
        <div className="upload-wrapper">
          <div
            className={`dropzone large ${dragActive ? 'drag-active' : ''}`}
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
            <UploadCloud size={64} className="dropzone-icon" />
            <h3>Choose an image from your device</h3>
            <p>or drag &amp; drop here</p>
            <span className="dropzone-hint">Max 5MB (JPG, PNG, WEBP)</span>
          </div>
          {error && (
            <div className="form-error-msg mt-4 justify-center">
              <AlertCircle size={16} /> {error}
            </div>
          )}
        </div>
      ) : (
        <div className="preview-layout">
          <div className="preview-large-container">
            <img src={personImage} alt="Person Preview" className="preview-large-img" />
          </div>
          <div className="preview-controls">
            <div className="preview-info-box">
              {isUploading ? (
                <>
                  <Loader2 size={24} className="animate-spin text-primary" />
                  <div><p className="file-name">Uploading to server...</p></div>
                </>
              ) : personImageId ? (
                <>
                  <CheckCircle2 size={24} className="text-success" />
                  <div><p className="file-name text-success">Image uploaded successfully</p></div>
                </>
              ) : (
                <>
                  <ImageIcon size={24} className="text-muted" />
                  <div><p className="file-name">Image selected</p></div>
                </>
              )}
            </div>
            <div className="flex gap-4">
              <button onClick={() => fileInputRef.current?.click()} className="btn-secondary flex-1" disabled={isUploading}>
                Change Photo
              </button>
              <button onClick={handleRemove} className="btn-icon text-error" title="Remove Photo" disabled={isUploading}>
                <Trash2 size={20} />
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleChange}
                className="hidden-input"
              />
            </div>
            <button
              onClick={onNext}
              className="btn-primary flex-center gap-2 mt-4 btn-large"
              disabled={!personImageId || isUploading}
            >
              {isUploading ? <><Loader2 size={16} className="animate-spin" /> Uploading...</> : <>Continue to Clothing <ArrowRight size={18} /></>}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
