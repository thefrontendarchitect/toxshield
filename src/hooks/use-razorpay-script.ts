'use client';

import { useState, useEffect } from 'react';

export function useRazorpayScript() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && window.Razorpay) {
      setIsLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => setIsLoaded(true);
    script.onerror = () => setIsError(true);
    document.body.appendChild(script);

    return () => {
      // Don't remove — other components may need it
    };
  }, []);

  return { isLoaded, isError };
}
