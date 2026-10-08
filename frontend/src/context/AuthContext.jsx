/**
 * AuthContext.jsx - DRISHYA Authentication Context & Routing Foundation
 *
 * Implements:
 * - Session state management (user, loading, isAuthenticated)
 * - HttpOnly cookie-based lifecycle (login, register, logout, me)
 * - Zero-token client storage (NO localStorage/sessionStorage tokens)
 * - Protected route guard and route classification (PUBLIC vs AUTHENTICATED)
 * - Automatic redirect to /welcome on unauthenticated access or logout
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from '../services/authApi';

// Route specifications per project requirements
export const PUBLIC_ROUTES = ['/welcome'];
export const AUTHENTICATED_ROUTES = [
  '/home',
  '/check',
  '/analysis',
  '/result',
  '/journal',
  '/guide',
  '/about',
  '/account',
];

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPath, setCurrentPath] = useState(
    typeof window !== 'undefined' ? window.location.pathname : '/'
  );

  // Client router navigation helper
  const navigate = useCallback((path) => {
    if (typeof window !== 'undefined') {
      window.history.pushState(null, '', path);
      setCurrentPath(path);
    }
  }, []);

  // Listen for browser back/forward buttons
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Initial user session verification from HttpOnly cookie
  const refreshUser = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      return userData;
    } catch (err) {
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Route protection guard
  useEffect(() => {
    if (loading) return;

    const isProtectedPath = AUTHENTICATED_ROUTES.some(
      (prefix) => currentPath === prefix || currentPath.startsWith(`${prefix}/`)
    );

    if (isProtectedPath && !user) {
      navigate('/welcome');
    }
  }, [currentPath, user, loading, navigate]);

  // Login handler
  const login = useCallback(
    async (email, password) => {
      setError(null);
      try {
        const loggedInUser = await loginUser({ email, password });
        setUser(loggedInUser);
        return loggedInUser;
      } catch (err) {
        setError(err.message || 'Login failed.');
        throw err;
      }
    },
    []
  );

  // Register handler
  const register = useCallback(
    async ({ name, email, password, preferred_language = 'en' }) => {
      setError(null);
      try {
        const registeredUser = await registerUser({
          name,
          email,
          password,
          preferred_language,
        });
        return registeredUser;
      } catch (err) {
        setError(err.message || 'Registration failed.');
        throw err;
      }
    },
    []
  );

  // Logout handler - clears session, wipes state, and redirects to /welcome
  const logout = useCallback(async () => {
    try {
      await logoutUser();
    } catch (err) {
      console.warn('Backend logout encountered error, clearing client state anyway:', err);
    } finally {
      setUser(null);
      setError(null);
      navigate('/welcome');
    }
  }, [navigate]);

  const value = {
    user,
    loading,
    error,
    isAuthenticated: Boolean(user),
    currentPath,
    navigate,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to consume AuthContext safely
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
