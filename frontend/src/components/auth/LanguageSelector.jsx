/**
 * LanguageSelector.jsx - DRISHYA Editorial Language Switcher
 *
 * Implements accessible, elegant switching between English, हिन्दी, and मराठी.
 * Uses warm antique gold indicators with natural Devanagari typography.
 */

import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

export default function LanguageSelector({ className = '' }) {
  const { language, setLanguage, supportedLanguages, t } = useLanguage();

  return (
    <div
      className={`language-selector-wrapper ${className}`}
      role="group"
      aria-label={t('account.language_selection')}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        background: 'rgba(28, 17, 10, 0.75)',
        border: '1px solid var(--border-rich, rgba(201, 154, 60, 0.28))',
        borderRadius: '9999px',
        padding: '0.25rem',
        boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.5)',
      }}
    >
      {supportedLanguages.map((lang) => {
        const isActive = language === lang.code;
        return (
          <button
            key={lang.code}
            type="button"
            onClick={() => setLanguage(lang.code)}
            aria-pressed={isActive}
            style={{
              border: 'none',
              cursor: 'pointer',
              minHeight: '40px',
              padding: '0.45rem 1.05rem',
              borderRadius: '9999px',
              fontFamily:
                lang.code === 'en'
                  ? 'var(--font-sans, "Plus Jakarta Sans", sans-serif)'
                  : 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)',
              fontSize: lang.code === 'en' ? '0.85rem' : '0.92rem',
              fontWeight: isActive ? '600' : '400',
              lineHeight: 1.4,
              color: isActive ? '#140C07' : 'var(--c-dust, #D8C7A3)',
              background: isActive
                ? 'linear-gradient(135deg, #F4EAD3 0%, #F2C14E 50%, #C99A3C 100%)'
                : 'transparent',
              boxShadow: isActive ? '0 2px 8px rgba(201, 154, 60, 0.35)' : 'none',
              transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
              outline: 'none',
            }}
            onFocus={(e) => {
              if (!isActive) e.currentTarget.style.color = '#FBF6EA';
            }}
            onBlur={(e) => {
              if (!isActive) e.currentTarget.style.color = 'var(--c-dust, #D8C7A3)';
            }}
            onMouseEnter={(e) => {
              if (!isActive) e.currentTarget.style.color = '#FBF6EA';
            }}
            onMouseLeave={(e) => {
              if (!isActive) e.currentTarget.style.color = 'var(--c-dust, #D8C7A3)';
            }}
          >
            {lang.label}
          </button>
        );
      })}
    </div>
  );
}
