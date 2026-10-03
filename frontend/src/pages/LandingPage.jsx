import React from 'react'
import { Link } from 'react-router-dom'
import { Sparkles, ArrowRight, Scan, Upload, Shirt, ImagePlus, History, Cpu, Zap, Lock } from 'lucide-react'
import './LandingPage.css'

export default function LandingPage() {
  return (
    <div className="landing">
      {/* HERO SECTION */}
      <section className="landing-hero">
        <div className="container hero-container">
          <div className="hero-content animate-fade-in">
            <h1 className="hero-title">
              Try On Your Style.<br />
              <span className="gradient-text">Virtually.</span>
            </h1>
            <p className="hero-desc">
              Experience the next generation of e-commerce. Our AI-powered virtual clothing try-on system uses advanced 2D compositing to show exactly how an outfit looks on you—before you even wear it.
            </p>
            <div className="hero-actions">
              <Link to="/try-on" className="btn-hero-primary">
                Try It Now <ArrowRight size={18} />
              </Link>
              <Link to="/clothing" className="btn-hero-secondary">
                Explore Collection
              </Link>
            </div>
          </div>

          <div className="hero-visual animate-float">
            <div className="hero-visual-card">
              <div className="visual-image-placeholder">
                <div className="visual-scan-line"></div>
                <div className="visual-points">
                  <div className="point p1"></div>
                  <div className="point p2"></div>
                  <div className="point p3"></div>
                </div>
                <Scan className="visual-icon" size={64} />
              </div>
              <div className="visual-badge">
                <Sparkles size={14} className="gradient-text" />
                <span>AI Virtual Try-On</span>
              </div>
              <div className="visual-floating-card top-right">
                <Shirt size={16} /> Matches found
              </div>
              <div className="visual-floating-card bottom-left">
                <span className="dot success"></span> 2D Compositing
              </div>
            </div>
            <div className="glow-orb orb-1"></div>
            <div className="glow-orb orb-2"></div>
          </div>
        </div>
      </section>

      {/* THE THEORY / TECHNOLOGY SECTION */}
      <section className="theory-section">
        <div className="container">
          <div className="theory-layout">
            <div className="theory-text">
              <div className="section-badge">The Science</div>
              <h2 className="section-title">How Our AI Understands Your Body</h2>
              <p className="theory-desc">
                Our virtual try-on system relies on state-of-the-art 2D pose estimation and body landmark detection. Unlike clumsy 3D models, we use highly accurate media pipelines to analyze the unique contours, shoulders, and hips of the person in the uploaded photo.
              </p>
              <p className="theory-desc">
                Once the pose is extracted, our intelligent garment alignment algorithm maps the selected clothing onto those exact 2D landmarks. Finally, advanced compositing seamlessly blends the garment onto the original image, preserving lighting and proportions for a hyper-realistic preview.
              </p>
            </div>
            <div className="theory-visual">
              <div className="theory-visual-box">
                <div className="theory-grid-bg"></div>
                <Cpu size={80} className="text-primary animate-float" />
                <div className="theory-stats">
                  <div className="stat"><strong>33+</strong> <br/>Body Landmarks</div>
                  <div className="stat"><strong>99%</strong> <br/>Alignment Accuracy</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Everything You Need for Virtual Styling</h2>
            <p className="section-desc">Designed for fashion enthusiasts and modern shoppers.</p>
          </div>
          <div className="features-grid">
            {[
              { icon: <Sparkles size={24} />, title: 'AI-Powered Try-On', desc: 'Visualize clothing on your uploaded photo using lightning-fast AI-assisted image processing.' },
              { icon: <Upload size={24} />, title: 'Upload Your Own', desc: 'Upload clothing directly from your device and build your own digital wardrobe in seconds.' },
              { icon: <Shirt size={24} />, title: 'Curated Collection', desc: 'Explore a vast catalog of available clothing items and filter by categories, colors, and styles.' },
              { icon: <History size={24} />, title: 'Try-On History', desc: 'Your past looks are securely saved so you can review and compare your virtual try-on results anytime.' },
              { icon: <Zap size={24} />, title: 'Lightning Fast', desc: 'No heavy 3D rendering. Get your results in seconds using optimized 2D compositing.' },
              { icon: <Lock size={24} />, title: 'Privacy First', desc: 'Your photos are processed securely. We prioritize your privacy and do not store sensitive biometric data.' },
            ].map((f) => (
              <div key={f.title} className="feature-card">
                <div className="feature-icon">{f.icon}</div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section id="how-it-works" className="how-it-works-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Experience it in 4 Simple Steps</h2>
            <p className="section-desc">No complicated 3D modeling or AR glasses required.</p>
          </div>
          <div className="steps-container">
            {[
              { step: '01', title: 'Upload Your Photo', detail: 'Take a well-lit, full-body photo against a plain background.' },
              { step: '02', title: 'Choose Clothing', detail: 'Select an item from our catalog or upload your own garment.' },
              { step: '03', title: 'AI Processing', detail: 'Our AI detects your body posture and aligns the clothing.' },
              { step: '04', title: 'View Result', detail: 'See your virtual try-on and download or save it to history.' },
            ].map((s, index) => (
              <div key={s.step} className="step-item">
                <div className="step-number-wrap">
                  <div className="step-number">{s.step}</div>
                  {index < 3 && <div className="step-connector"></div>}
                </div>
                <h3 className="step-title">{s.title}</h3>
                <p className="step-detail">{s.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CALL TO ACTION SECTION */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-box">
            <h2 className="cta-title">Ready to Try Your Next Look?</h2>
            <p className="cta-desc">
              Join thousands of users who are transforming the way they shop for clothes.
            </p>
            <Link to="/try-on" className="btn-hero-primary" style={{ padding: '16px 32px', fontSize: '1.1rem' }}>
              Start Virtual Try-On For Free
            </Link>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <div className="container">
          <div className="footer-content flex-between align-center">
            <div className="footer-brand flex-center gap-2">
              <div className="brand-logo bg-gradient-brand">
                <Sparkles size={18} fill="white" />
              </div>
              <span className="brand-text">Virtual<strong>Try-On</strong></span>
            </div>
            <p className="footer-copyright text-muted text-sm">
              &copy; {new Date().getFullYear()} AI Virtual Try-On System. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
