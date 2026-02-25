import { theme } from '@/config/theme'
import { useWristbandAuth } from '@/context/AuthContext'
import { useUser } from '@/context/UserContext'
import { useState, useEffect } from 'react'
import frontendApiClient from '@/client/frontend-api-client'
import { Toast } from '@/components/Toast'
import { IdpCard } from '@/components/IdpCard'

interface ToastMessage {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

export default function Profile() {
  const { tenantName, tenantId, logout, email, idpName } = useWristbandAuth()
  const { currentUser, tenantOptions, isLoadingTenants, setCurrentUser } = useUser()
  
  // State for editable fields
  const [firstName, setFirstName] = useState(currentUser?.givenName || '')
  const [lastName, setLastName] = useState(currentUser?.familyName || '')
  const [isSaving, setIsSaving] = useState(false)
  
  // State for password change
  const [password, setPassword] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  })
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  // Toast notifications
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
  }

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  // Update form when user data changes
  useEffect(() => {
    setFirstName(currentUser?.givenName || '')
    setLastName(currentUser?.familyName || '')
  }, [currentUser])

  const handleSaveName = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      const response = await frontendApiClient.patch('/user/me', {
        givenName: firstName,
        familyName: lastName
      })
      
      // Update the current user in context with the updated data
      setCurrentUser(response.data)
      
      showToast('Name updated successfully', 'success')
    } catch (error) {
      console.error('Error updating name:', error)
      showToast('Error updating name. Please try again.', 'error')
    } finally {
      setIsSaving(false)
    }
  }

  const handleTenantSelect = (tenantName: string, loginUrl: string) => {
    const confirmed = window.confirm(`Are you sure you want to switch to ${tenantName}?`)
    if (confirmed) {
      window.location.href = loginUrl
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (password.newPassword !== password.confirmPassword) {
      showToast('New passwords do not match', 'error')
      return
    }
    
    if (password.currentPassword === password.newPassword) {
      showToast('New password must be different from current password', 'error')
      return
    }
    
    if (password.newPassword.length < 8 || password.newPassword.length > 64) {
      showToast('Password must be 8-64 characters long', 'error')
      return
    }
    
    setIsChangingPassword(true)
    try {
      await frontendApiClient.post('/user/me/change-password', {
        currentPassword: password.currentPassword,
        newPassword: password.newPassword
      })
      
      // Clear password fields on success
      setPassword({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      })
      
      showToast('Password updated successfully', 'success')
    } catch (error: any) {
      console.error('Error changing password:', error)
      const errorData = error.response?.data
      if (error.response?.status === 400) {
        showToast(errorData?.message || 'Password change failed. Please check your current password.', 'error')
      } else if (error.response?.status === 403) {
        showToast(errorData?.message || 'You are not authorized to change passwords.', 'error')
      } else {
        showToast('An error occurred while updating your password. Please try again.', 'error')
      }
    } finally {
      setIsChangingPassword(false)
    }
  }

  const togglePasswordVisibility = (field: keyof typeof showPasswords) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }))
  }

  const hasNameChanged = firstName !== (currentUser?.givenName || '') || lastName !== (currentUser?.familyName || '')
  const passwordsMatch = password.newPassword === password.confirmPassword && password.confirmPassword.length > 0
  const isPasswordValid = password.currentPassword.length > 0 && password.newPassword.length >= 8 && password.newPassword.length <= 64 && passwordsMatch

  return (
    <main className="p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-semibold mb-8" style={{ color: theme.colors.textPrimary }}>
          Profile Settings
        </h1>

        {/* Email Section - Non-editable */}
        <div className="mb-8">
          <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
            Email
          </label>
          <input
            type="email"
            value={email || ''}
            disabled
            className="w-full px-4 py-2 rounded-lg border"
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              color: theme.colors.textSecondary,
              cursor: 'not-allowed'
            }}
          />
        </div>

        {/* Name Section - Editable */}
        <div className="mb-8 pb-8 border-b" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
          <h2 className="text-lg font-medium mb-4" style={{ color: theme.colors.textPrimary }}>
            Name
          </h2>
          
          <form onSubmit={handleSaveName} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                First
              </label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Enter your first name"
                className="w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  color: theme.colors.textPrimary
                }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                Last
              </label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Enter your last name"
                className="w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  color: theme.colors.textPrimary
                }}
              />
            </div>

            <button
              type="submit"
              disabled={!hasNameChanged || isSaving}
              className="w-full py-2 px-4 rounded-lg font-medium transition-colors hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: theme.colors.primary,
                color: 'white'
              }}
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>
          </form>
        </div>

        {/* Wristband Change Password Section - Only show for Wristband IDP */}
        {idpName?.toLowerCase() === 'wristband' && (
          <div className="mb-8 pb-8 border-b relative" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
            <div className="absolute top-0 right-0 group">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden cursor-pointer">
                <img src="/authentication/wristband-icon.svg" alt="Wristband" className="w-full h-full object-contain" />
              </div>
              {/* Tooltip */}
              <div className="absolute right-0 top-full mt-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-10 shadow-lg">
                Secured by Wristband
                <div className="absolute bottom-full right-4 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900"></div>
              </div>
            </div>
            <h2 className="text-lg font-medium mb-4" style={{ color: theme.colors.textPrimary }}>
              Password
            </h2>
            
            <form onSubmit={handlePasswordChange} className="space-y-4">
              {/* Current Password */}
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                  Current
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.current ? 'text' : 'password'}
                    value={password.currentPassword}
                    onChange={(e) => setPassword(prev => ({ ...prev, currentPassword: e.target.value }))}
                    placeholder="Enter your current password"
                    className="w-full px-4 py-2 pr-12 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                      color: theme.colors.textPrimary
                    }}
                    autoComplete="current-password"
                    minLength={8}
                    maxLength={64}
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('current')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    style={{ color: theme.colors.textSecondary }}
                  >
                    {showPasswords.current ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                  New
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.new ? 'text' : 'password'}
                    value={password.newPassword}
                    onChange={(e) => setPassword(prev => ({ ...prev, newPassword: e.target.value }))}
                    placeholder="Enter your new password"
                    className="w-full px-4 py-2 pr-12 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                      color: theme.colors.textPrimary
                    }}
                    autoComplete="new-password"
                    minLength={8}
                    maxLength={64}
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('new')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    style={{ color: theme.colors.textSecondary }}
                  >
                    {showPasswords.new ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm New Password */}
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                  Confirm
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    value={password.confirmPassword}
                    onChange={(e) => setPassword(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    placeholder="Confirm your new password"
                    className="w-full px-4 py-2 pr-12 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderColor: password.confirmPassword.length > 0 
                        ? (passwordsMatch ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)')
                        : 'rgba(255, 255, 255, 0.2)',
                      color: theme.colors.textPrimary
                    }}
                    autoComplete="new-password"
                    minLength={8}
                    maxLength={64}
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('confirm')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    style={{ color: theme.colors.textSecondary }}
                  >
                    {showPasswords.confirm ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
                {password.confirmPassword.length > 0 && (
                  <p className="text-xs mt-1" style={{ 
                    color: passwordsMatch && password.newPassword.length >= 8 && password.newPassword.length <= 64 ? '#22c55e' : '#ef4444' 
                  }}>
                    {!passwordsMatch 
                      ? '✗ Passwords do not match' 
                      : (password.newPassword.length < 8 || password.newPassword.length > 64)
                        ? '✗ Password must be 8-64 characters long'
                        : '✓ Passwords match'}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={!isPasswordValid || isChangingPassword}
                className="w-full py-2 px-4 rounded-lg font-medium transition-colors hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: theme.colors.primary,
                  color: 'white'
                }}
              >
                {isChangingPassword ? 'Updating...' : 'Update Password'}
              </button>
            </form>
          </div>
        )}

        {/* Identity Provider Section - Show for non-Wristband IDPs */}
        {idpName && idpName.toLowerCase() !== 'wristband' && (
          <div className="mb-8 pb-8 border-b" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
            <h2 className="text-lg font-medium mb-4" style={{ color: theme.colors.textPrimary }}>
              Identity Provider
            </h2>
            
            <IdpCard
              displayName={
                idpName.toLowerCase().includes('google') 
                  ? 'Google Workspace' 
                  : idpName.toLowerCase().includes('okta') 
                    ? 'Okta Workforce' 
                    : idpName
              }
              logoPath={
                idpName.toLowerCase().includes('google')
                  ? '/identity_providers/google-logo.svg'
                  : idpName.toLowerCase().includes('okta')
                    ? '/identity_providers/okta-logo.svg'
                    : undefined
              }
              showActions={false}
            />
          </div>
        )}

        {/* Tenant Section */}
        <div className="mb-8 pb-8 border-b" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
          <h2 className="text-lg font-medium mb-4" style={{ color: theme.colors.textPrimary }}>
            Organization
          </h2>
          
          {isLoadingTenants ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: theme.colors.primary }}></div>
            </div>
          ) : (
            <div className="space-y-2">
              {/* Current Organization */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                  Current
                </label>
                <div 
                  className="px-4 py-3 rounded-lg border"
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderColor: 'rgba(34, 197, 94, 0.3)',
                    color: theme.colors.textPrimary
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{tenantName || 'No organization'}</span>
                    <svg 
                      className="w-5 h-5" 
                      fill="none" 
                      stroke="#22c55e" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Other Organizations */}
              {tenantOptions.filter(option => option.tenantId !== tenantId).length > 0 && (
                <>
                  <label className="block text-sm font-medium mb-2" style={{ color: theme.colors.textPrimary }}>
                    Other Organizations
                  </label>
                  {tenantOptions
                    .filter(option => option.tenantId !== tenantId)
                    .map((option) => (
                      <button
                        key={option.tenantId}
                        onClick={() => handleTenantSelect(option.tenantDisplayName, option.tenantLoginUrl)}
                        className="w-full p-4 rounded-lg border text-left transition-all hover:opacity-80"
                        style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.05)',
                          borderColor: 'rgba(255, 255, 255, 0.1)',
                          color: theme.colors.textPrimary
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium">{option.tenantDisplayName}</p>
                            <p className="text-xs mt-1" style={{ color: theme.colors.textSecondary }}>
                              {option.tenantDomainName}
                            </p>
                          </div>
                          <svg 
                            className="w-5 h-5" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                            style={{ color: theme.colors.textSecondary }}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </button>
                    ))}
                </>
              )}
            </div>
          )}
        </div>

        {/* Logout Section */}
        <div>
          <button
            onClick={logout}
            className="w-full py-2 px-4 rounded-lg font-medium transition-colors"
            style={{
              backgroundColor: theme.colors.logoutBg,
              color: 'white'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.logoutHover
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.logoutBg
            }}
          >
            Log Out
          </button>
        </div>
      </div>

      {/* Toast Notifications */}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </main>
  )
}