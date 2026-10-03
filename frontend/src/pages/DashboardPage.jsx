import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Sparkles, Shirt, Upload, FolderHeart, History, ArrowRight } from 'lucide-react'
import { mockDashboardStats, mockRecentTryOns } from '../data/mockDashboardData'
import './DashboardPage.css'

export default function DashboardPage() {
  const { user } = useAuth()

  // Welcome Section Component
  const WelcomeSection = () => (
    <div className="dashboard-welcome">
      <div className="welcome-content">
        <h1 className="welcome-title">Welcome back, {user?.name || 'User'}!</h1>
        <p className="welcome-desc">Ready to discover your next look?</p>
        <div className="welcome-actions">
          <Link to="/try-on" className="btn-primary">
            Start Virtual Try-On <Sparkles size={16} />
          </Link>
          <Link to="/clothing" className="btn-secondary">
            Explore Clothing
          </Link>
        </div>
      </div>
      <div className="welcome-visual hidden-mobile">
        <div className="welcome-orb"></div>
        <Sparkles className="welcome-icon" size={64} />
      </div>
    </div>
  )

  // Quick Action Card Component
  const QuickActionCard = ({ icon, title, desc, btnText, to }) => (
    <div className="quick-action-card hover-lift">
      <div className="quick-action-icon">{icon}</div>
      <h3 className="quick-action-title">{title}</h3>
      <p className="quick-action-desc">{desc}</p>
      <Link to={to} className="quick-action-btn">
        {btnText} <ArrowRight size={14} />
      </Link>
    </div>
  )

  // Stats Card Component
  const StatsCard = ({ title, value }) => (
    <div className="stats-card">
      <p className="stats-title">{title}</p>
      <h3 className="stats-value">{value}</h3>
    </div>
  )

  // Empty State Component
  const EmptyState = () => (
    <div className="empty-state">
      <div className="empty-state-icon">
        <History size={32} />
      </div>
      <h3 className="empty-state-title">No try-ons yet</h3>
      <p className="empty-state-desc">Your virtual styling journey starts here.</p>
      <Link to="/try-on" className="btn-primary-sm mt-4">
        Try Your First Outfit
      </Link>
    </div>
  )

  // Recent Try-On Item
  const RecentTryOnCard = ({ item }) => (
    <div className="recent-item">
      <div className="recent-item-thumb">
        <Shirt size={20} className="text-muted" />
      </div>
      <div className="recent-item-info">
        <h4 className="recent-item-name">{item.clothingName}</h4>
        <p className="recent-item-meta">{item.category} • {item.date}</p>
      </div>
      <div className="recent-item-status">
        <span className="status-badge success">{item.status}</span>
      </div>
    </div>
  )

  // Profile Summary Component
  const ProfileSummary = () => (
    <div className="profile-summary-card">
      <div className="profile-summary-avatar">
        {user?.name ? user.name[0].toUpperCase() : 'U'}
      </div>
      <div className="profile-summary-info">
        <h3 className="profile-summary-name">{user?.name || 'User'}</h3>
        <p className="profile-summary-email">{user?.email}</p>
      </div>
      <Link to="/profile" className="profile-summary-btn">
        View Profile
      </Link>
    </div>
  )

  return (
    <div className="dashboard-container animate-fade-in">
      <WelcomeSection />

      <div className="dashboard-grid">
        {/* Main Column */}
        <div className="dashboard-main-col">
          
          <section className="dashboard-section">
            <h2 className="section-heading">Quick Actions</h2>
            <div className="quick-actions-grid">
              <QuickActionCard 
                icon={<Sparkles size={24} />}
                title="Start Virtual Try-On"
                desc="Upload your photo and see how a new outfit looks on you."
                btnText="Try Now"
                to="/try-on"
              />
              <QuickActionCard 
                icon={<Shirt size={24} />}
                title="Browse Clothing"
                desc="Explore available clothing and find your next look."
                btnText="Browse"
                to="/clothing"
              />
              <QuickActionCard 
                icon={<Upload size={24} />}
                title="Upload Your Clothes"
                desc="Use clothing from your own device for virtual try-on."
                btnText="Upload"
                to="/my-clothing"
              />
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-header-flex">
              <h2 className="section-heading">Recent Try-Ons</h2>
              <Link to="/history" className="view-all-link">View All History</Link>
            </div>
            
            <div className="recent-list-container">
              {mockRecentTryOns.length > 0 ? (
                <div className="recent-list">
                  {mockRecentTryOns.map(item => (
                    <RecentTryOnCard key={item.id} item={item} />
                  ))}
                </div>
              ) : (
                <EmptyState />
              )}
            </div>
          </section>
          
        </div>

        {/* Side Column */}
        <div className="dashboard-side-col">
          
          <section className="dashboard-section">
            <h2 className="section-heading">Profile</h2>
            <ProfileSummary />
          </section>

          <section className="dashboard-section">
            <h2 className="section-heading">Statistics</h2>
            <div className="stats-grid">
              <StatsCard title="Total Try-Ons" value={mockDashboardStats.totalTryOns} />
              <StatsCard title="Saved Results" value={mockDashboardStats.savedResults} />
              <StatsCard title="My Clothes" value={mockDashboardStats.myClothes} />
              <StatsCard title="Available Clothing" value={mockDashboardStats.availableClothing} />
            </div>
          </section>

        </div>
      </div>
    </div>
  )
}
