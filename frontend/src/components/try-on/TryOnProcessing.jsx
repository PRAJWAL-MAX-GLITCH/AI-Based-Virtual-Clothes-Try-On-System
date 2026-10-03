import React, { useEffect, useState } from 'react'
import { Loader2, CheckCircle2 } from 'lucide-react'

const STAGES = [
  "Uploading Image...",
  "Analyzing Pose & Landmarks...",
  "Processing Clothing Item...",
  "Aligning Garment to Body...",
  "Generating Final Result..."
]

export default function TryOnProcessing({ onComplete }) {
  const [currentStage, setCurrentStage] = useState(0)

  useEffect(() => {
    // Simulate the processing stages
    let stage = 0;
    const interval = setInterval(() => {
      stage += 1;
      if (stage < STAGES.length) {
        setCurrentStage(stage)
      } else {
        clearInterval(interval)
        setTimeout(() => {
          onComplete()
        }, 500)
      }
    }, 1500) // 1.5s per stage for UI simulation

    return () => clearInterval(interval)
  }, [onComplete])

  return (
    <div className="processing-container animate-fade-in">
      <div className="processing-spinner-box">
        <Loader2 size={64} className="processing-spinner" />
      </div>
      
      <h2 className="processing-title">Creating Your Virtual Look</h2>
      <p className="processing-desc">Please wait while our AI engine prepares your try-on.</p>
      
      <div className="processing-stages">
        {STAGES.map((stageText, index) => (
          <div 
            key={index} 
            className={`processing-stage-item ${index < currentStage ? 'completed' : index === currentStage ? 'active' : 'pending'}`}
          >
            <div className="stage-icon">
              {index < currentStage ? (
                <CheckCircle2 size={16} />
              ) : index === currentStage ? (
                <div className="stage-dot active"></div>
              ) : (
                <div className="stage-dot"></div>
              )}
            </div>
            <span className="stage-text">{stageText}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
