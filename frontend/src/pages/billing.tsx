import { theme } from '@/config/theme'
import { SubscriptionSection } from '@/components/billing/SubscriptionSection'
import { useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function Billing() {
  const searchParams = useSearchParams()
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)
  const [showCanceledMessage, setShowCanceledMessage] = useState(false)

  useEffect(() => {
    if (searchParams?.get('success') === 'true') {
      setShowSuccessMessage(true)
      // Remove query params from URL
      window.history.replaceState({}, '', '/billing')
    }
    if (searchParams?.get('canceled') === 'true') {
      setShowCanceledMessage(true)
      // Remove query params from URL
      window.history.replaceState({}, '', '/billing')
    }
  }, [searchParams])

  return (
    <main className="p-4 md:p-6">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold mb-2" style={{ color: theme.colors.textPrimary }}>
            Billing
          </h1>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            Manage your subscription and billing preferences.
          </p>
        </div>

        {/* Success Message */}
        {showSuccessMessage && (
          <div 
            className="mb-6 p-4 rounded-lg border flex items-center gap-3"
            style={{
              backgroundColor: 'rgba(34, 197, 94, 0.1)',
              borderColor: 'rgba(34, 197, 94, 0.3)',
            }}
          >
            <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <div>
              <p className="font-medium" style={{ color: theme.colors.textPrimary }}>
                Payment successful!
              </p>
              <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
                Your subscription has been activated. Thank you for your purchase!
              </p>
            </div>
            <button 
              onClick={() => setShowSuccessMessage(false)}
              className="ml-auto p-1 hover:opacity-70 transition-opacity"
              style={{ color: theme.colors.textSecondary }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Canceled Message */}
        {showCanceledMessage && (
          <div 
            className="mb-6 p-4 rounded-lg border flex items-center gap-3"
            style={{
              backgroundColor: 'rgba(251, 191, 36, 0.1)',
              borderColor: 'rgba(251, 191, 36, 0.3)',
            }}
          >
            <svg className="w-5 h-5 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="font-medium" style={{ color: theme.colors.textPrimary }}>
                Checkout canceled
              </p>
              <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
                Your checkout session was canceled. No charges were made.
              </p>
            </div>
            <button 
              onClick={() => setShowCanceledMessage(false)}
              className="ml-auto p-1 hover:opacity-70 transition-opacity"
              style={{ color: theme.colors.textSecondary }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Subscription Section */}
        <div 
          className="rounded-lg border p-6"
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            borderColor: 'rgba(255, 255, 255, 0.1)',
          }}
        >
          <SubscriptionSection />
        </div>
      </div>
    </main>
  )
}
