/**
 * LanguageContext.jsx - DRISHYA Multilingual State & Language Provider
 *
 * Implements:
 * 1. Synchronized language switching (en, hi, mr) using react-i18next
 * 2. Persistence via localStorage (drishya_user_language)
 * 3. Server-side synchronization for authenticated users (/api/v1/auth/me/preferences)
 * 4. Precedence rule:
 *    - On initial load: loads localStorage preference (default 'en')
 *    - On authentication: account's preferred_language takes precedence
 *    - On explicit switch: updates i18n, saves to localStorage, and syncs to backend if authenticated
 * 5. State preservation: does NOT reset auth, diagnostics, or UI state
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import i18n, { SUPPORTED_LOCALES, DEFAULT_LOCALE, STORAGE_KEY_LOCALE } from '../i18n';
import { LOCALE_CONFIG, formatDate, formatTime, formatNumber, getConditionDisplayName } from '../utils/formatters';
import { updateUserPreferences } from '../services/authApi';
import { useAuth } from './AuthContext';

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const { t } = useTranslation();
  const { user, isAuthenticated } = useAuth();
  const [currentLanguage, setCurrentLanguage] = useState(() => i18n.language || DEFAULT_LOCALE);

  // Sync with authenticated user's preferred_language when session loads
  useEffect(() => {
    if (isAuthenticated && user?.preferred_language) {
      const userLang = user.preferred_language.toLowerCase().trim();
      if (SUPPORTED_LOCALES.includes(userLang) && userLang !== i18n.language) {
        i18n.changeLanguage(userLang).then(() => {
          setCurrentLanguage(userLang);
          try {
            localStorage.setItem(STORAGE_KEY_LOCALE, userLang);
          } catch (e) {
            // ignore localStorage quota error
          }
        });
      }
    }
  }, [isAuthenticated, user?.preferred_language]);

  // Language switch function
  const setLanguage = useCallback(
    async (newLang) => {
      const cleanLang = (newLang || '').toLowerCase().trim();
      if (!SUPPORTED_LOCALES.includes(cleanLang)) {
        console.warn(`[DRISHYA Language] Unsupported locale attempted: ${newLang}. Ignoring.`);
        return;
      }

      try {
        await i18n.changeLanguage(cleanLang);
        setCurrentLanguage(cleanLang);
        try {
          localStorage.setItem(STORAGE_KEY_LOCALE, cleanLang);
        } catch (e) {
          // ignore localStorage quota error
        }

        // If authenticated, sync with server profile
        if (isAuthenticated) {
          try {
            await updateUserPreferences({ preferred_language: cleanLang });
          } catch (apiErr) {
            console.warn('[DRISHYA Language] Failed to sync preference to server:', apiErr);
          }
        }
      } catch (err) {
        console.error('[DRISHYA Language] Error switching language:', err);
      }
    },
    [isAuthenticated]
  );

  const value = {
    language: currentLanguage,
    setLanguage,
    t,
    supportedLanguages: Object.values(LOCALE_CONFIG),
    formatDate: (date, options) => formatDate(date, currentLanguage, options),
    formatTime: (date) => formatTime(date, currentLanguage),
    formatNumber: (num, options) => formatNumber(num, currentLanguage, options),
    getConditionDisplayName: (crop, rawClass) => getConditionDisplayName(crop, rawClass, t),
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
