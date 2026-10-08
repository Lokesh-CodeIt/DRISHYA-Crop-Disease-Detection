/**
 * ProtectedRoute.jsx - Reusable Route Guard Component for DRISHYA
 *
 * Ensures only authenticated users can view wrapped routes.
 * If unauthenticated, navigates to /welcome.
 */

import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children, fallback = null }) {
  const { isAuthenticated, loading, navigate } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/welcome');
    }
  }, [loading, isAuthenticated, navigate]);

  if (loading) {
    return (
      fallback || (
        <div style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
          Verifying session...
        </div>
      )
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return children;
}
