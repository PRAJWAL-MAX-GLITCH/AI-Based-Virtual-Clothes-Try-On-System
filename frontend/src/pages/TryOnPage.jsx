import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Check, Loader2, AlertCircle } from 'lucide-react'
import PersonImageUpload from '../components/try-on/PersonImageUpload'
import ClothingSelector from '../components/try-on/ClothingSelector'
import TryOnReview from '../components/try-on/TryOnReview'
import TryOnResult from '../components/try-on/TryOnResult'
import { uploadUserImage } from '../services/uploadService'
import { runTryOn } from '../services/tryOnService'
import { getClothingById } from '../services/clothingService'
import { useToast } from '../context/ToastContext'
import './TryOnPage.css'

const STEPS = [
  { id: 1, label: 'Upload Photo' },
  { id: 2, label: 'Choose Clothing' },
  { id: 3, label: 'Review' },
  { id: 4, label: 'Try On' }
]

const PROCESSING_STAGES = [
  'Preparing Image',
  'Analyzing Pose',
  'Processing Clothing',
  'Aligning Garment',
  'Generating Result',
]

export default function TryOnPage() {
  const [searchParams] = useSearchParams()
  const { showToast } = useToast()
  const [currentStep, setCurrentStep] = useState(1)

  // Step 1 state: local file + backend path after upload
  const [personImage, setPersonImage] = useState(null)       // local preview URL
  const [personImageId, setPersonImageId] = useState(null)   // backend path/id

  // Step 2 state
  const [selectedClothing, setSelectedClothing] = useState(null)

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStage, setProcessingStage] = useState(0)
  const [processingError, setProcessingError] = useState(null)
  const [tryOnResult, setTryOnResult] = useState(null)
  const [showResult, setShowResult] = useState(false)

  // Handle URL pre-selection
  useEffect(() => {
    const clothingId = searchParams.get('clothing')
    if (clothingId) {
      getClothingById(clothingId)
        .then(data => {
          setSelectedClothing(data.data.clothing)
        })
        .catch(() => {/* ignore prefill errors */})
    }
    // customClothing param for user clothing - handled in ClothingSelector
  }, [searchParams])

  const handleNext = () => setCurrentStep(prev => prev + 1)
  const handleBack = () => setCurrentStep(prev => prev - 1)

  // Called by PersonImageUpload after user selects a file
  const handlePersonImageSelected = async (file, previewUrl) => {
    setPersonImage(previewUrl)
    setPersonImageId(null) // reset old
    try {
      const fd = new FormData()
      fd.append('image', file)
      const data = await uploadUserImage(fd)
      // Backend returns { data: { path, type, ... } }
      setPersonImageId(data.data.path)
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to upload person image.'
      showToast(msg, 'error')
      setPersonImage(null)
    }
  }

  const handleStartTryOn = async () => {
    if (!personImageId) {
      showToast('Please upload your person photo first.', 'error')
      return
    }
    if (!selectedClothing) {
      showToast('Please select a clothing item.', 'error')
      return
    }

    setIsProcessing(true)
    setProcessingError(null)
    setCurrentStep(4)

    // Animate through stages while request is in progress
    let stageIndex = 0
    const stageInterval = setInterval(() => {
      stageIndex = Math.min(stageIndex + 1, PROCESSING_STAGES.length - 1)
      setProcessingStage(stageIndex)
    }, 1200)

    try {
      const data = await runTryOn(personImageId, selectedClothing.id)
      clearInterval(stageInterval)
      setTryOnResult(data.data)
      setShowResult(true)
      setIsProcessing(false)
    } catch (err) {
      clearInterval(stageInterval)
      const msg = err.response?.data?.message || 'Virtual try-on failed. Please try again.'
      setProcessingError(msg)
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setCurrentStep(1)
    setPersonImage(null)
    setPersonImageId(null)
    setSelectedClothing(null)
    setIsProcessing(false)
    setProcessingStage(0)
    setProcessingError(null)
    setTryOnResult(null)
    setShowResult(false)
  }

  return (
    <div className="try-on-page animate-fade-in">
      <div className="page-header text-center mb-8">
        <h1 className="page-title">Virtual Try-On</h1>
        <p className="page-desc">Upload your photo, choose an outfit, and preview your look.</p>
      </div>

      {/* Stepper */}
      <div className="try-on-stepper">
        {STEPS.map((step, index) => {
          const isCompleted = step.id < currentStep || (step.id === 4 && showResult)
          const isActive = step.id === currentStep && !showResult
          return (
            <React.Fragment key={step.id}>
              <div className={`stepper-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                <div className="stepper-circle">
                  {isCompleted ? <Check size={14} /> : step.id}
                </div>
                <span className="stepper-label">{step.label}</span>
              </div>
              {index < STEPS.length - 1 && (
                <div className={`stepper-line ${isCompleted ? 'completed' : ''}`}></div>
              )}
            </React.Fragment>
          )
        })}
      </div>

      {/* Main Content Area */}
      <div className="try-on-content">
        {currentStep === 1 && (
          <PersonImageUpload
            personImage={personImage}
            setPersonImage={setPersonImage}
            onFileSelected={handlePersonImageSelected}
            personImageId={personImageId}
            onNext={handleNext}
          />
        )}

        {currentStep === 2 && (
          <ClothingSelector
            selectedClothing={selectedClothing}
            setSelectedClothing={setSelectedClothing}
            onNext={handleNext}
            onBack={handleBack}
          />
        )}

        {currentStep === 3 && (
          <TryOnReview
            personImage={personImage}
            selectedClothing={selectedClothing}
            onStart={handleStartTryOn}
            onBack={handleBack}
          />
        )}

        {currentStep === 4 && isProcessing && (
          <div className="processing-container text-center">
            <Loader2 size={56} className="animate-spin text-primary mb-6" style={{ margin: '0 auto 24px' }} />
            <h2 className="text-xl font-semibold mb-2">Creating Your Virtual Look</h2>
            <p className="text-muted mb-8">This may take a moment. Please don't close this page.</p>
            <div className="processing-stages">
              {PROCESSING_STAGES.map((stage, i) => (
                <div key={stage} className={`stage-item ${i <= processingStage ? 'active' : ''} ${i < processingStage ? 'done' : ''}`}>
                  {i < processingStage ? <Check size={16} /> : i === processingStage ? <Loader2 size={16} className="animate-spin" /> : <span className="stage-dot" />}
                  <span>{stage}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentStep === 4 && processingError && !isProcessing && !showResult && (
          <div className="catalog-empty-state">
            <AlertCircle size={48} className="text-error mb-4" />
            <h3>Try-On Failed</h3>
            <p>{processingError}</p>
            <button onClick={() => { setCurrentStep(3); setProcessingError(null) }} className="btn-secondary mt-4 mr-3">Go Back</button>
            <button onClick={handleReset} className="btn-primary mt-4">Start Over</button>
          </div>
        )}

        {currentStep === 4 && showResult && (
          <TryOnResult result={tryOnResult} onReset={handleReset} />
        )}
      </div>
    </div>
  )
}
