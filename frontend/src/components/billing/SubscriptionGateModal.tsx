import { theme } from '@/config/theme';
import frontendApiClient from '@/client/frontend-api-client';
import { useState, useEffect } from 'react';
import { useWristbandAuth } from '@/context/AuthContext';

interface StripeProduct {
  id: string;
  name: string;
  description: string | null;
  price_id: string;
  price_amount: number;
  price_currency: string;
  price_interval: string | null;
}

const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const formatPrice = (amount: number, currency: string, interval: string | null) => {
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(amount / 100);
  
  return interval ? `${formatted}/${interval}` : formatted;
};

/**
 * Blocking modal that requires users to subscribe before accessing the app.
 * Cannot be dismissed - users must either subscribe or logout.
 */
export function SubscriptionGateModal() {
  const { logout, tenantName } = useWristbandAuth();
  
  // State
  const [isLoading, setIsLoading] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [products, setProducts] = useState<StripeProduct[]>([]);
  const [selectedPriceId, setSelectedPriceId] = useState<string | null>(null);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  
  // Alternate email state
  const [useAlternateEmail, setUseAlternateEmail] = useState(false);
  const [alternateEmail, setAlternateEmail] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);

  // Fetch products on mount
  useEffect(() => {
    fetchProducts();
  }, []);

  // Validate email when it changes
  useEffect(() => {
    if (useAlternateEmail && alternateEmail) {
      if (!isValidEmail(alternateEmail)) {
        setEmailError('Please enter a valid email address');
      } else {
        setEmailError(null);
      }
    } else {
      setEmailError(null);
    }
  }, [alternateEmail, useAlternateEmail]);

  // Prevent body scroll when modal is shown
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const fetchProducts = async () => {
    try {
      setIsLoadingProducts(true);
      const response = await frontendApiClient.get('/billing/products');
      const productList = response.data as StripeProduct[];
      setProducts(productList);
      // Auto-select first paid product
      const firstPaidProduct = productList.find(p => p.price_amount > 0);
      if (firstPaidProduct) {
        setSelectedPriceId(firstPaidProduct.price_id);
      } else if (productList.length > 0) {
        setSelectedPriceId(productList[0].price_id);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  // Derived state
  const isEmailInvalid = useAlternateEmail && alternateEmail && !isValidEmail(alternateEmail);
  const isFormValid = selectedPriceId && (!useAlternateEmail || (alternateEmail && isValidEmail(alternateEmail)));

  const getCheckoutUrl = async (): Promise<string | null> => {
    if (!selectedPriceId) {
      alert('Please select a plan');
      return null;
    }

    if (useAlternateEmail && !isValidEmail(alternateEmail)) {
      setEmailError('Please enter a valid email address');
      return null;
    }

    try {
      const response = await frontendApiClient.post('/billing/checkout', null, {
        params: { 
          price_id: selectedPriceId,
          ...(useAlternateEmail && alternateEmail ? { billing_email: alternateEmail } : {})
        }
      });
      
      return response.data.url || null;
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to create checkout session');
      return null;
    }
  };

  const handleCheckout = async () => {
    setIsLoading(true);
    try {
      const url = await getCheckoutUrl();
      if (url) {
        window.location.href = url;
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = async () => {
    setIsCopying(true);
    try {
      const url = await getCheckoutUrl();
      if (url) {
        await navigator.clipboard.writeText(url);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      }
    } catch (error) {
      console.error('Error copying link:', error);
    } finally {
      setIsCopying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop - no click handler, cannot dismiss */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
      />
      
      {/* Modal Content */}
      <div 
        className="relative w-full max-w-lg rounded-xl border shadow-2xl animate-in fade-in zoom-in duration-300"
        style={{
          backgroundColor: '#1a1a1a',
          borderColor: 'rgba(255, 255, 255, 0.1)'
        }}
      >
        {/* Header */}
        <div className="px-6 pt-6 pb-4 text-center">
          {/* Icon */}
          <div 
            className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
            style={{ backgroundColor: 'rgba(37, 99, 235, 0.15)' }}
          >
            <svg 
              className="w-8 h-8" 
              style={{ color: theme.colors.primary }} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" 
              />
            </svg>
          </div>
          
          <h2 className="text-xl font-semibold mb-2" style={{ color: theme.colors.textPrimary }}>
            Subscription Required
          </h2>
          <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
            {tenantName ? `Welcome to ${tenantName}! ` : ''}
            Your free trial has ended. Please choose a plan to continue using the application.
          </p>
        </div>

        {/* Body */}
        <div className="px-6 pb-6 space-y-4">
          {/* Plan Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium" style={{ color: theme.colors.textPrimary }}>
              Select a plan
            </label>
            
            {isLoadingProducts ? (
              <div className="flex items-center justify-center py-8">
                <div 
                  className="w-6 h-6 border-2 rounded-full animate-spin"
                  style={{ 
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderTopColor: theme.colors.primary 
                  }}
                />
              </div>
            ) : products.length === 0 ? (
              <div className="py-8 text-center">
                <p className="text-sm mb-2" style={{ color: theme.colors.textSecondary }}>
                  No plans available at this time.
                </p>
                <p className="text-xs" style={{ color: theme.colors.textSecondary }}>
                  Please contact support for assistance.
                </p>
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {products.map((product) => (
                  <label
                    key={product.price_id}
                    className="flex items-center gap-3 p-4 rounded-lg cursor-pointer transition-all hover:opacity-90"
                    style={{
                      backgroundColor: selectedPriceId === product.price_id 
                        ? 'rgba(37, 99, 235, 0.15)' 
                        : 'rgba(255, 255, 255, 0.02)',
                      borderWidth: '1px',
                      borderStyle: 'solid',
                      borderColor: selectedPriceId === product.price_id 
                        ? theme.colors.primary 
                        : 'rgba(255, 255, 255, 0.1)'
                    }}
                  >
                    <input
                      type="radio"
                      name="product"
                      value={product.price_id}
                      checked={selectedPriceId === product.price_id}
                      onChange={() => setSelectedPriceId(product.price_id)}
                      className="sr-only"
                    />
                    <div 
                      className="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                      style={{ 
                        borderColor: selectedPriceId === product.price_id 
                          ? theme.colors.primary 
                          : 'rgba(255, 255, 255, 0.3)'
                      }}
                    >
                      {selectedPriceId === product.price_id && (
                        <div 
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: theme.colors.primary }}
                        />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium truncate" style={{ color: theme.colors.textPrimary }}>
                          {product.description || product.name}
                        </span>
                        <span className="text-sm font-semibold flex-shrink-0" style={{ color: theme.colors.primary }}>
                          {formatPrice(product.price_amount, product.price_currency, product.price_interval)}
                        </span>
                      </div>
                      {product.description && (
                        <p className="text-xs mt-0.5 truncate" style={{ color: theme.colors.textSecondary }}>
                          {product.name}
                        </p>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Alternate billing email */}
          {products.length > 0 && (
            <>
              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={useAlternateEmail}
                    onChange={(e) => setUseAlternateEmail(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div 
                    className="w-5 h-5 rounded border-2 transition-all peer-focus:ring-2 peer-focus:ring-offset-2 peer-focus:ring-offset-[#1a1a1a]"
                    style={{ 
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                      backgroundColor: useAlternateEmail ? theme.colors.primary : 'transparent'
                    }}
                  >
                    {useAlternateEmail && (
                      <svg className="w-full h-full text-white p-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </div>
                <span className="text-sm" style={{ color: theme.colors.textSecondary }}>
                  Use a different email for billing
                </span>
              </label>

              {useAlternateEmail && (
                <div className="pl-8 space-y-1">
                  <input
                    type="email"
                    value={alternateEmail}
                    onChange={(e) => setAlternateEmail(e.target.value)}
                    placeholder="billing@example.com"
                    className="w-full px-3 py-2 rounded-lg text-sm transition-colors focus:outline-none focus:ring-2"
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      borderWidth: '1px',
                      borderStyle: 'solid',
                      borderColor: isEmailInvalid ? '#ef4444' : 'rgba(255, 255, 255, 0.1)',
                      color: theme.colors.textPrimary,
                    }}
                  />
                  {emailError && (
                    <p className="text-xs" style={{ color: '#ef4444' }}>
                      {emailError}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 pb-6 space-y-3">
          {/* Action Buttons */}
          {products.length > 0 && (
            <div className="flex gap-3">
              <button
                onClick={handleCopyLink}
                disabled={isCopying || isLoading || !isFormValid}
                className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all hover:opacity-80 disabled:opacity-50 flex items-center justify-center gap-2"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  color: theme.colors.textSecondary
                }}
              >
                {copySuccess ? (
                  <svg className="w-5 h-5 text-green-400 animate-in zoom-in duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : isCopying ? (
                  <div 
                    className="w-4 h-4 border-2 rounded-full animate-spin"
                    style={{ 
                      borderColor: 'rgba(255, 255, 255, 0.1)',
                      borderTopColor: theme.colors.textSecondary 
                    }}
                  />
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                    Copy Link
                  </>
                )}
              </button>
              <button
                onClick={handleCheckout}
                disabled={isLoading || isCopying || !isFormValid}
                className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors hover:opacity-90 disabled:opacity-50"
                style={{
                  backgroundColor: theme.colors.primary,
                  color: 'white'
                }}
              >
                {isLoading ? 'Processing...' : 'Subscribe Now'}
              </button>
            </div>
          )}

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />
            <span className="text-xs" style={{ color: theme.colors.textSecondary }}>or</span>
            <div className="flex-1 h-px" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />
          </div>

          {/* Logout Button */}
          <button
            onClick={logout}
            className="w-full px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80"
            style={{
              backgroundColor: 'transparent',
              color: theme.colors.textSecondary
            }}
          >
            Sign out and use a different account
          </button>
        </div>
      </div>
    </div>
  );
}
