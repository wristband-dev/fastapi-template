import { theme } from '@/config/theme';
import frontendApiClient from '@/client/frontend-api-client';
import { useState, useEffect } from 'react';

interface StripeProduct {
  id: string;
  name: string;
  description: string | null;
  price_id: string;
  price_amount: number;
  price_currency: string;
  price_interval: string | null;
}

interface StripeSubscription {
  id: string;
  status: string;
  current_period_start: number;
  current_period_end: number;
  cancel_at_period_end: boolean;
  cancel_at: number | null;
  product_id: string;
  product_name: string;
  product_description: string | null;
  price_id: string;
  price_amount: number;
  price_currency: string;
  price_interval: string | null;
}

interface BillingInfo {
  billing_email: string;
  has_payment_method: boolean;
}

interface UsageItem {
  id: string;
  amount: number;
  currency: string;
  description: string;
  date: number;
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

const formatCurrency = (amount: number, currency: string) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(amount / 100);
};

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

interface SubscriptionSectionProps {
  onSuccess?: () => void;
}

export function SubscriptionSection({ onSuccess }: SubscriptionSectionProps) {
  // Subscription state
  const [activeSubscription, setActiveSubscription] = useState<StripeSubscription | null>(null);
  const [isLoadingSubscription, setIsLoadingSubscription] = useState(true);
  
  // Action state
  const [isLoading, setIsLoading] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [isOpeningPortal, setIsOpeningPortal] = useState(false);
  
  // Form state
  const [useAlternateEmail, setUseAlternateEmail] = useState(false);
  const [alternateEmail, setAlternateEmail] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);
  const [products, setProducts] = useState<StripeProduct[]>([]);
  const [selectedPriceId, setSelectedPriceId] = useState<string | null>(null);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);

  // Billing info state
  const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null);
  const [isEditingEmail, setIsEditingEmail] = useState(false);
  const [newBillingEmail, setNewBillingEmail] = useState('');
  const [isSavingEmail, setIsSavingEmail] = useState(false);
  const [billingEmailError, setBillingEmailError] = useState<string | null>(null);

  // Usage state
  const [pendingUsage, setPendingUsage] = useState<UsageItem[]>([]);
  const [isLoadingUsage, setIsLoadingUsage] = useState(false);
  const [isAddingUsage, setIsAddingUsage] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    fetchActiveSubscription();
    fetchProducts();
    fetchBillingInfo();
    fetchPendingUsage();
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

  // Validate billing email when editing
  useEffect(() => {
    if (isEditingEmail && newBillingEmail) {
      if (!isValidEmail(newBillingEmail)) {
        setBillingEmailError('Please enter a valid email address');
      } else {
        setBillingEmailError(null);
      }
    } else {
      setBillingEmailError(null);
    }
  }, [newBillingEmail, isEditingEmail]);

  const fetchActiveSubscription = async () => {
    try {
      setIsLoadingSubscription(true);
      const response = await frontendApiClient.get('/billing/subscription');
      setActiveSubscription(response.data as StripeSubscription | null);
      if (response.data) {
        setSelectedPriceId(response.data.price_id);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
      setActiveSubscription(null);
    } finally {
      setIsLoadingSubscription(false);
    }
  };

  const fetchProducts = async () => {
    try {
      setIsLoadingProducts(true);
      const response = await frontendApiClient.get('/billing/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  const fetchBillingInfo = async () => {
    try {
      const response = await frontendApiClient.get('/billing/billing-info');
      setBillingInfo(response.data);
    } catch (error) {
      console.error('Error fetching billing info:', error);
    }
  };

  const fetchPendingUsage = async () => {
    try {
      setIsLoadingUsage(true);
      const response = await frontendApiClient.get('/billing/usage');
      setPendingUsage(response.data);
    } catch (error) {
      console.error('Error fetching usage:', error);
    } finally {
      setIsLoadingUsage(false);
    }
  };

  const handleSaveBillingEmail = async () => {
    if (!newBillingEmail || !isValidEmail(newBillingEmail)) {
      setBillingEmailError('Please enter a valid email address');
      return;
    }

    setIsSavingEmail(true);
    try {
      const response = await frontendApiClient.put('/billing/billing-email', null, {
        params: { email: newBillingEmail }
      });
      setBillingInfo(prev => prev ? { ...prev, billing_email: response.data.billing_email } : null);
      setIsEditingEmail(false);
      setNewBillingEmail('');
    } catch (error) {
      console.error('Error updating billing email:', error);
      setBillingEmailError('Failed to update email. Please try again.');
    } finally {
      setIsSavingEmail(false);
    }
  };

  const handleAddUsage = async (amount: number, description: string) => {
    setIsAddingUsage(true);
    try {
      await frontendApiClient.post('/billing/usage', null, {
        params: { amount, description }
      });
      // Refresh pending usage
      await fetchPendingUsage();
    } catch (error) {
      console.error('Error adding usage:', error);
      alert('Failed to add usage charge. Please ensure you have an active subscription with a payment method.');
    } finally {
      setIsAddingUsage(false);
    }
  };

  // Derived state
  const isOnFreePlan = activeSubscription?.price_amount === 0;
  const selectedProduct = products.find(p => p.price_id === selectedPriceId);
  const isSelectingPaidPlan = selectedProduct && selectedProduct.price_amount > 0;
  const needsCheckout = isOnFreePlan && isSelectingPaidPlan;
  const isChangingPlan = selectedPriceId !== activeSubscription?.price_id;
  const isEmailInvalid = useAlternateEmail && alternateEmail && !isValidEmail(alternateEmail);
  const isFormValid = selectedPriceId && (!useAlternateEmail || (alternateEmail && isValidEmail(alternateEmail)));
  const isCanceling = activeSubscription?.cancel_at_period_end || activeSubscription?.cancel_at;

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

  const handleChangePlan = async () => {
    if (!activeSubscription || !selectedPriceId || !isChangingPlan) {
      return;
    }

    if (useAlternateEmail && !isValidEmail(alternateEmail)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    if (needsCheckout) {
      await handleCheckout();
      return;
    }

    setIsLoading(true);
    try {
      const response = await frontendApiClient.put(
        `/billing/subscriptions/${activeSubscription.id}`,
        null,
        { 
          params: { 
            new_price_id: selectedPriceId,
            ...(useAlternateEmail && alternateEmail ? { billing_email: alternateEmail } : {})
          } 
        }
      );
      
      setActiveSubscription(response.data);
      setUseAlternateEmail(false);
      setAlternateEmail('');
      onSuccess?.();
      alert('Plan updated successfully! Your billing will be adjusted accordingly.');
    } catch (error) {
      console.error('Error updating subscription:', error);
      alert('Failed to update subscription. Please try again.');
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

  const handleOpenPortal = async () => {
    setIsOpeningPortal(true);
    try {
      const response = await frontendApiClient.post('/billing/portal');
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Error opening portal:', error);
      alert('Failed to open billing portal. Please try again.');
    } finally {
      setIsOpeningPortal(false);
    }
  };

  // Loading state
  if (isLoadingSubscription) {
    return (
      <div className="flex items-center justify-center py-8">
        <div 
          className="w-6 h-6 border-2 rounded-full animate-spin"
          style={{ borderColor: 'rgba(255, 255, 255, 0.1)', borderTopColor: theme.colors.primary }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Plan Status */}
      {activeSubscription && (
        <div 
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: isOnFreePlan 
              ? 'rgba(251, 191, 36, 0.1)' 
              : isCanceling 
                ? 'rgba(251, 146, 60, 0.1)'
                : 'rgba(34, 197, 94, 0.1)',
            borderColor: isOnFreePlan 
              ? 'rgba(251, 191, 36, 0.3)' 
              : isCanceling 
                ? 'rgba(251, 146, 60, 0.3)'
                : 'rgba(34, 197, 94, 0.3)',
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div 
                className={`w-3 h-3 rounded-full ${isOnFreePlan ? 'bg-amber-400' : isCanceling ? 'bg-orange-400' : 'bg-green-500'}`}
              />
              <div>
                <p className="font-medium" style={{ color: theme.colors.textPrimary }}>
                  {activeSubscription.product_description || activeSubscription.product_name}
                </p>
                <p className="text-sm" style={{ color: theme.colors.textSecondary }}>
                  {formatPrice(activeSubscription.price_amount, activeSubscription.price_currency, activeSubscription.price_interval)}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p 
                className="text-sm font-medium"
                style={{ 
                  color: isCanceling ? '#f59e0b' : theme.colors.textSecondary 
                }}
              >
                {activeSubscription.cancel_at
                  ? `Cancels ${formatDate(activeSubscription.cancel_at)}`
                  : activeSubscription.cancel_at_period_end 
                    ? `Cancels ${formatDate(activeSubscription.current_period_end)}`
                    : `Renews ${formatDate(activeSubscription.current_period_end)}`
                }
              </p>
              <p className="text-xs" style={{ color: theme.colors.textSecondary }}>
                Status: {activeSubscription.status}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Plan Selection */}
      <div className="space-y-3">
        <label className="text-sm font-medium" style={{ color: theme.colors.textPrimary }}>
          {isOnFreePlan ? 'Upgrade to a paid plan' : 'Change plan'}
        </label>
        
        {isLoadingProducts ? (
          <div className="flex items-center justify-center py-8">
            <div 
              className="w-6 h-6 border-2 rounded-full animate-spin"
              style={{ borderColor: 'rgba(255, 255, 255, 0.1)', borderTopColor: theme.colors.primary }}
            />
          </div>
        ) : products.length === 0 ? (
          <p className="text-sm py-4 text-center" style={{ color: theme.colors.textSecondary }}>
            No plans available
          </p>
        ) : (
          <div className="space-y-2">
            {products.map((product) => {
              const isCurrentPlan = activeSubscription?.price_id === product.price_id;
              return (
                <label
                  key={product.price_id}
                  className="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all"
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
                    className="w-4 h-4 rounded-full border-2 flex items-center justify-center"
                    style={{ 
                      borderColor: selectedPriceId === product.price_id 
                        ? theme.colors.primary 
                        : 'rgba(255, 255, 255, 0.3)'
                    }}
                  >
                    {selectedPriceId === product.price_id && (
                      <div 
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: theme.colors.primary }}
                      />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium flex items-center gap-2" style={{ color: theme.colors.textPrimary }}>
                        {product.description || product.name}
                        {isCurrentPlan && (
                          <span 
                            className="text-xs px-2 py-0.5 rounded-full"
                            style={{ backgroundColor: 'rgba(34, 197, 94, 0.2)', color: '#22c55e' }}
                          >
                            Current
                          </span>
                        )}
                      </span>
                      <span className="text-sm font-semibold" style={{ color: theme.colors.primary }}>
                        {formatPrice(product.price_amount, product.price_currency, product.price_interval)}
                      </span>
                    </div>
                    {product.description && (
                      <p className="text-xs mt-0.5" style={{ color: theme.colors.textSecondary }}>
                        {product.name}
                      </p>
                    )}
                  </div>
                </label>
              );
            })}
          </div>
        )}
      </div>

      {/* Alternate billing email */}
      {isChangingPlan && (
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={useAlternateEmail}
              onChange={(e) => setUseAlternateEmail(e.target.checked)}
              className="w-4 h-4 rounded"
            />
            <span className="text-sm" style={{ color: theme.colors.textSecondary }}>
              Use another email for billing
            </span>
          </label>

          {useAlternateEmail && (
            <div className="space-y-1">
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
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        {needsCheckout && isChangingPlan ? (
          <>
            <button
              onClick={handleCopyLink}
              disabled={isCopying || isLoading || !isFormValid}
              className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-80 disabled:opacity-50 flex items-center justify-center gap-2"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: 'rgba(255, 255, 255, 0.2)',
                color: theme.colors.textSecondary
              }}
            >
              {copySuccess ? (
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : isCopying ? (
                <div 
                  className="w-4 h-4 border-2 rounded-full animate-spin"
                  style={{ borderColor: 'rgba(255, 255, 255, 0.1)', borderTopColor: theme.colors.textSecondary }}
                />
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                  </svg>
                  Copy Payment Link
                </>
              )}
            </button>
            <button
              onClick={handleCheckout}
              disabled={isLoading || isCopying || !isFormValid}
              className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-90 disabled:opacity-50"
              style={{
                backgroundColor: theme.colors.primary,
                color: 'white'
              }}
            >
              {isLoading ? 'Processing...' : 'Upgrade Now'}
            </button>
          </>
        ) : (
          <button
            onClick={handleChangePlan}
            disabled={isLoading || !isChangingPlan}
            className="w-full px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-90 disabled:opacity-50"
            style={{
              backgroundColor: isChangingPlan ? theme.colors.primary : 'rgba(255, 255, 255, 0.1)',
              color: isChangingPlan ? 'white' : theme.colors.textSecondary
            }}
          >
            {isLoading ? 'Updating...' : isChangingPlan ? 'Change Plan' : 'Current Plan'}
          </button>
        )}
      </div>

      {/* Payment Method Management - only show for paid subscriptions */}
      {activeSubscription && !isOnFreePlan && (
        <div 
          className="pt-4 border-t"
          style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
        >
          <button
            onClick={handleOpenPortal}
            disabled={isOpeningPortal}
            className="w-full px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-80 disabled:opacity-50 flex items-center justify-center gap-2"
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderWidth: '1px',
              borderStyle: 'solid',
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: theme.colors.textSecondary
            }}
          >
            {isOpeningPortal ? (
              <div 
                className="w-4 h-4 border-2 rounded-full animate-spin"
                style={{ borderColor: 'rgba(255, 255, 255, 0.1)', borderTopColor: theme.colors.textSecondary }}
              />
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                Update Payment Method
              </>
            )}
          </button>
        </div>
      )}

      {/* Billing Email Section */}
      {billingInfo && (
        <div 
          className="pt-4 border-t"
          style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
        >
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium" style={{ color: theme.colors.textPrimary }}>
              Billing Email
            </label>
            {!isEditingEmail && (
              <button
                onClick={() => {
                  setIsEditingEmail(true);
                  setNewBillingEmail(billingInfo.billing_email);
                }}
                className="text-xs px-2 py-1 rounded transition-all hover:opacity-80"
                style={{ color: theme.colors.primary }}
              >
                Change
              </button>
            )}
          </div>
          
          {isEditingEmail ? (
            <div className="space-y-2">
              <input
                type="email"
                value={newBillingEmail}
                onChange={(e) => setNewBillingEmail(e.target.value)}
                placeholder="billing@example.com"
                className="w-full px-3 py-2 rounded-lg text-sm transition-colors focus:outline-none focus:ring-2"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: billingEmailError ? '#ef4444' : 'rgba(255, 255, 255, 0.1)',
                  color: theme.colors.textPrimary,
                }}
              />
              {billingEmailError && (
                <p className="text-xs" style={{ color: '#ef4444' }}>
                  {billingEmailError}
                </p>
              )}
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setIsEditingEmail(false);
                    setNewBillingEmail('');
                    setBillingEmailError(null);
                  }}
                  className="flex-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all hover:opacity-80"
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    color: theme.colors.textSecondary
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveBillingEmail}
                  disabled={isSavingEmail || !newBillingEmail || !isValidEmail(newBillingEmail)}
                  className="flex-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50"
                  style={{
                    backgroundColor: theme.colors.primary,
                    color: 'white'
                  }}
                >
                  {isSavingEmail ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          ) : (
            <div 
              className="p-3 rounded-lg"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: 'rgba(255, 255, 255, 0.1)'
              }}
            >
              <p className="text-sm" style={{ color: theme.colors.textPrimary }}>
                {billingInfo.billing_email}
              </p>
              <p className="text-xs mt-1" style={{ color: theme.colors.textSecondary }}>
                {billingInfo.has_payment_method ? 'Payment method on file' : 'No payment method on file'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Usage Charges Section - show for active subscriptions */}
      {activeSubscription && (activeSubscription.status === 'active' || activeSubscription.status === 'trialing') && (
        <div 
          className="pt-4 border-t"
          style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
        >
          <label className="text-sm font-medium block mb-3" style={{ color: theme.colors.textPrimary }}>
            Usage Charges
          </label>
          <p className="text-xs mb-3" style={{ color: theme.colors.textSecondary }}>
            Add one-time usage charges to your next invoice. These charges will be processed with your next billing cycle.
          </p>

          {/* Add Usage Buttons */}
          <div className="flex gap-2 mb-4">
            {[
              { amount: 500, label: '$5' },
              { amount: 1000, label: '$10' },
              { amount: 2500, label: '$25' },
            ].map(({ amount, label }) => (
              <button
                key={amount}
                onClick={() => handleAddUsage(amount, `Usage charge - ${label}`)}
                disabled={isAddingUsage}
                className="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-80 disabled:opacity-50"
                style={{
                  backgroundColor: 'rgba(37, 99, 235, 0.15)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: 'rgba(37, 99, 235, 0.3)',
                  color: theme.colors.primary
                }}
              >
                {isAddingUsage ? '...' : `Add ${label}`}
              </button>
            ))}
          </div>

          {/* Pending Usage List */}
          {isLoadingUsage ? (
            <div className="flex items-center justify-center py-4">
              <div 
                className="w-5 h-5 border-2 rounded-full animate-spin"
                style={{ borderColor: 'rgba(255, 255, 255, 0.1)', borderTopColor: theme.colors.primary }}
              />
            </div>
          ) : pendingUsage.length > 0 ? (
            <div className="space-y-2">
              <p className="text-xs font-medium" style={{ color: theme.colors.textSecondary }}>
                Pending charges ({pendingUsage.length})
              </p>
              {pendingUsage.map((item) => (
                <div 
                  key={item.id}
                  className="flex items-center justify-between p-2 rounded-lg"
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    borderWidth: '1px',
                    borderStyle: 'solid',
                    borderColor: 'rgba(255, 255, 255, 0.1)'
                  }}
                >
                  <span className="text-sm" style={{ color: theme.colors.textSecondary }}>
                    {item.description}
                  </span>
                  <span className="text-sm font-medium" style={{ color: theme.colors.textPrimary }}>
                    {formatCurrency(item.amount, item.currency)}
                  </span>
                </div>
              ))}
              <p className="text-xs" style={{ color: theme.colors.textSecondary }}>
                Total pending: {formatCurrency(
                  pendingUsage.reduce((sum, item) => sum + item.amount, 0),
                  'usd'
                )}
              </p>
            </div>
          ) : (
            <p className="text-xs text-center py-2" style={{ color: theme.colors.textSecondary }}>
              No pending usage charges
            </p>
          )}
        </div>
      )}
    </div>
  );
}
