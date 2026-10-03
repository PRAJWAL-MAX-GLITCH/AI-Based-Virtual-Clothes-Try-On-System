import React, { useState, useRef } from 'react'
import { User, Mail, Lock, ShieldAlert, Camera, Check, AlertTriangle, Phone, MapPin } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { updateUserProfile, changePassword, deactivateAccount } from '../services/userService'
import { uploadUserImage } from '../services/uploadService'
import { getImageUrl } from '../utils/imageUrl'
import './ProfilePage.css'

export default function ProfilePage() {
  const { user, setUser, logout } = useAuth()
  const { showToast } = useToast()
  const fileInputRef = useRef(null)

  // Local UI State
  const [activeTab, setActiveTab] = useState('profile')
  const [profileData, setProfileData] = useState({ 
    name: user?.name || '', 
    email: user?.email || '',
    phone: user?.phone || '',
    location: user?.location || '',
    profile_image_path: user?.profile_image_path || ''
  })
  const [passwordData, setPasswordData] = useState({ current: '', new: '', confirm: '' })
  const [isDeactivateOpen, setIsDeactivateOpen] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleProfileChange = (e) => setProfileData(prev => ({ ...prev, [e.target.name]: e.target.value }))
  const handlePasswordChange = (e) => setPasswordData(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('image', file)

    try {
      // 1. Upload the image to get the file path
      const res = await uploadUserImage(formData)
      const imagePath = res.data.file_path || res.data.filename
      
      // 2. Immediately update the profile with the new image path
      const updatedProfile = await updateUserProfile({ ...profileData, profile_image_path: imagePath })
      if (setUser) setUser(updatedProfile.data.user)
      
      setProfileData(prev => ({ ...prev, profile_image_path: imagePath }))
      showToast('Profile photo updated!', 'success')
    } catch (err) {
      showToast('Failed to upload photo.', 'error')
    } finally {
      setIsUploading(false)
    }
  }

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      const data = await updateUserProfile(profileData)
      // Update local AuthContext user too
      if (setUser) setUser(data.data.user)
      showToast('Profile updated successfully.', 'success')
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to update profile.'
      showToast(msg, 'error')
    } finally {
      setIsSaving(false)
    }
  }

  const handleUpdatePassword = async (e) => {
    e.preventDefault()
    if (passwordData.new !== passwordData.confirm) {
      showToast('New passwords do not match.', 'error')
      return
    }
    if (passwordData.new.length < 8) {
      showToast('Password must be at least 8 characters.', 'error')
      return
    }
    setIsSaving(true)
    try {
      await changePassword({ current_password: passwordData.current, new_password: passwordData.new })
      setPasswordData({ current: '', new: '', confirm: '' })
      showToast('Password updated successfully.', 'success')
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to change password.'
      showToast(msg, 'error')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeactivate = async () => {
    try {
      await deactivateAccount()
      logout()
      showToast('Account deactivated.', 'info')
    } catch (err) {
      showToast('Failed to deactivate account.', 'error')
    }
    setIsDeactivateOpen(false)
  }

  const triggerFileInput = () => fileInputRef.current?.click()

  return (
    <div className="profile-page animate-fade-in">
      <div className="page-header mb-8">
        <h1 className="page-title">My Profile</h1>
        <p className="page-desc">Manage your account and profile information.</p>
      </div>

      <div className="profile-layout">
        
        {/* Left Column - Navigation / Overview */}
        <div className="profile-sidebar">
          
          <div className="profile-avatar-card">
            <div className="avatar-wrapper">
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleImageUpload} 
                accept="image/jpeg, image/png, image/webp" 
                style={{ display: 'none' }} 
              />
              {user?.profile_image_path ? (
                <div className="avatar-image-container">
                  <img 
                    src={getImageUrl(user.profile_image_path)} 
                    alt="Profile" 
                    className="avatar-image"
                    style={{ opacity: isUploading ? 0.5 : 1 }}
                  />
                </div>
              ) : (
                <div className="avatar-circle" style={{ opacity: isUploading ? 0.5 : 1 }}>
                  <span className="text-4xl font-bold">{user?.name ? user.name.charAt(0) : 'U'}</span>
                </div>
              )}
              
              <button 
                className="avatar-upload-btn" 
                title="Change Profile Photo" 
                onClick={triggerFileInput}
                disabled={isUploading}
              >
                <Camera size={18} />
              </button>
            </div>
            
            <h3 className="profile-name mt-4">{user?.name || 'User Name'}</h3>
            <p className="profile-email text-muted text-sm">{user?.email || 'user@example.com'}</p>
            {user?.location && <p className="text-muted text-xs mt-1 flex items-center justify-center gap-1"><MapPin size={12}/> {user.location}</p>}
            
            <div className="mt-4 inline-flex items-center gap-2 status-badge success">
              <Check size={14} /> Active Account
            </div>
          </div>

          <div className="profile-nav mt-6">
            <button 
              className={`profile-nav-item ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <User size={18} /> Edit Profile
            </button>
            <button 
              className={`profile-nav-item ${activeTab === 'security' ? 'active' : ''}`}
              onClick={() => setActiveTab('security')}
            >
              <Lock size={18} /> Security
            </button>
            <button 
              className={`profile-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              <ShieldAlert size={18} /> Account Settings
            </button>
          </div>
        </div>

        {/* Right Column - Content */}
        <div className="profile-content">
          
          {activeTab === 'profile' && (
            <div className="profile-section-card animate-fade-in">
              <h2 className="section-title">Edit Profile</h2>
              <form onSubmit={handleSaveProfile} className="profile-form mt-6">
                
                <div className="form-row">
                  <div className="form-group flex-1">
                    <label className="form-label">Full Name</label>
                    <div className="input-with-icon">
                      <User size={18} className="input-icon" />
                      <input 
                        type="text" 
                        name="name" 
                        value={profileData.name} 
                        onChange={handleProfileChange} 
                        className="form-input pl-10" 
                        required 
                      />
                    </div>
                  </div>
                  
                  <div className="form-group flex-1">
                    <label className="form-label">Email Address</label>
                    <div className="input-with-icon">
                      <Mail size={18} className="input-icon" />
                      <input 
                        type="email" 
                        name="email" 
                        value={profileData.email} 
                        onChange={handleProfileChange} 
                        className="form-input pl-10" 
                        required 
                      />
                    </div>
                  </div>
                </div>

                <div className="form-row mt-4">
                  <div className="form-group flex-1">
                    <label className="form-label">Phone Number</label>
                    <div className="input-with-icon">
                      <Phone size={18} className="input-icon" />
                      <input 
                        type="tel" 
                        name="phone" 
                        value={profileData.phone} 
                        onChange={handleProfileChange} 
                        className="form-input pl-10" 
                        placeholder="+1 (555) 000-0000"
                      />
                    </div>
                  </div>

                  <div className="form-group flex-1">
                    <label className="form-label">Location / City</label>
                    <div className="input-with-icon">
                      <MapPin size={18} className="input-icon" />
                      <input 
                        type="text" 
                        name="location" 
                        value={profileData.location} 
                        onChange={handleProfileChange} 
                        className="form-input pl-10" 
                        placeholder="New York, USA"
                      />
                    </div>
                  </div>
                </div>

                <div className="form-actions mt-8">
                  <button type="submit" className="btn-primary" disabled={isSaving}>
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="profile-section-card animate-fade-in">
              <h2 className="section-title">Change Password</h2>
              <form onSubmit={handleUpdatePassword} className="profile-form mt-6">
                <div className="form-group">
                  <label className="form-label">Current Password</label>
                  <input 
                    type="password" 
                    name="current" 
                    value={passwordData.current} 
                    onChange={handlePasswordChange} 
                    className="form-input" 
                    required 
                  />
                </div>
                
                <div className="form-group mt-4">
                  <label className="form-label">New Password</label>
                  <input 
                    type="password" 
                    name="new" 
                    value={passwordData.new} 
                    onChange={handlePasswordChange} 
                    className="form-input" 
                    required 
                    minLength={8}
                  />
                </div>

                <div className="form-group mt-4">
                  <label className="form-label">Confirm New Password</label>
                  <input 
                    type="password" 
                    name="confirm" 
                    value={passwordData.confirm} 
                    onChange={handlePasswordChange} 
                    className="form-input" 
                    required 
                    minLength={8}
                  />
                </div>

                <div className="form-actions mt-8">
                  <button type="submit" className="btn-primary" disabled={isSaving}>
                    {isSaving ? 'Updating...' : 'Update Password'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="profile-section-card animate-fade-in">
              <h2 className="section-title text-error flex items-center gap-2">
                <ShieldAlert size={20} /> Danger Zone
              </h2>
              
              <div className="danger-zone-box mt-6">
                <div>
                  <h4 className="font-semibold text-primary">Deactivate Account</h4>
                  <p className="text-muted text-sm mt-1">
                    Deactivating your account will prevent you from using the application until the account is reactivated.
                  </p>
                </div>
                <button 
                  onClick={() => setIsDeactivateOpen(true)}
                  className="btn-danger mt-4 sm:mt-0"
                >
                  Deactivate Account
                </button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Deactivate Modal */}
      {isDeactivateOpen && (
        <div className="modal-overlay">
          <div className="dialog-box animate-scale-in">
            <div className="dialog-icon-warning">
              <AlertTriangle size={24} />
            </div>
            <h3>Deactivate your account?</h3>
            <p>You can reactivate it later by logging back in, but your current sessions will be terminated.</p>
            <div className="dialog-actions mt-6">
              <button onClick={() => setIsDeactivateOpen(false)} className="btn-secondary flex-1">
                Cancel
              </button>
              <button onClick={handleDeactivate} className="btn-danger flex-1">
                Deactivate
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
