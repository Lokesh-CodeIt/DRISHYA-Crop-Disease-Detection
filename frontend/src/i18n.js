/**
 * i18n.js - DRISHYA Internationalization Configuration
 *
 * Configures i18next with English, Hindi, and Marathi locale resources.
 * Safe fallback to English for any missing translation key.
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './locales/en.json';
import hi from './locales/hi.json';
import mr from './locales/mr.json';

export const SUPPORTED_LOCALES = ['en', 'hi', 'mr'];
export const DEFAULT_LOCALE = 'en';
export const STORAGE_KEY_LOCALE = 'drishya_user_language';

// Get initial locale from local preference or fallback
const getInitialLocale = () => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(STORAGE_KEY_LOCALE);
    if (saved && SUPPORTED_LOCALES.includes(saved)) {
      return saved;
    }
  }
  return DEFAULT_LOCALE;
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      mr: { translation: mr },
    },
    lng: getInitialLocale(),
    fallbackLng: DEFAULT_LOCALE,
    supportedLngs: SUPPORTED_LOCALES,
    interpolation: {
      escapeValue: false, // React already escapes XSS
    },
    react: {
      useSuspense: false,
    },
    // Developer visibility for missing translation keys during development
    saveMissing: true,
    missingKeyHandler: (lngs, ns, key) => {
      if (process.env.NODE_ENV !== 'production') {
        console.warn(`[DRISHYA i18n missing key]: "${key}" for locale [${lngs.join(', ')}]`);
      }
    },
  });

export default i18n;
