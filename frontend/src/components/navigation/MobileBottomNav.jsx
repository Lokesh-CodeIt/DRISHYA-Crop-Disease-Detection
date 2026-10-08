/**
 * MobileBottomNav.jsx - Compact Mobile Navigation Bar
 *
 * Implements:
 * - Three core actions: Home, Check (prominent center), Journal
 * - Accessible 48px+ touch targets
 * - Active state indicators with antique gold styling
 * - Hidden on desktop viewports (via CSS)
 */

import React from 'react';
import { Home, Camera, BookOpen } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';

export default function MobileBottomNav({ currentRoute = '/home' }) {
  const { navigate } = useAuth();
  const { t } = useLanguage();

  return (
    <nav
      className="drishya-mobile-bottom-nav"
      aria-label="Mobile Bottom Navigation"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: '#1C110A',
        borderTop: '1px solid rgba(201, 154, 60, 0.3)',
        zIndex: 60,
        boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.4)',
        display: 'none', // Shown via CSS @media (max-width: 768px)
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-around',
          height: '64px',
          maxWidth: '500px',
          margin: '0 auto',
          padding: '0 1rem',
        }}
      >
        {/* 1. Home */}
        <button
          type="button"
          onClick={() => navigate('/home')}
          aria-label={t('nav.home')}
          aria-current={currentRoute === '/home' ? 'page' : undefined}
          style={{
            flex: 1,
            height: '100%',
            background: 'none',
            border: 'none',
            color: currentRoute === '/home' ? '#F2C14E' : '#D8C7A3',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.2rem',
            cursor: 'pointer',
            fontSize: '0.72rem',
            fontWeight: currentRoute === '/home' ? '700' : '400',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          }}
        >
          <Home size={20} />
          <span>{t('nav.home')}</span>
        </button>

        {/* 2. Check (Visually Prominent Center Action) */}
        <button
          type="button"
          onClick={() => navigate('/check')}
          aria-label={t('check.title')}
          aria-current={currentRoute === '/check' ? 'page' : undefined}
          style={{
            width: '56px',
            height: '56px',
            transform: 'translateY(-12px)',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
            border: '3px solid #1C110A',
            color: '#140C07',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(201, 154, 60, 0.45)',
          }}
        >
          <Camera size={26} />
        </button>

        {/* 3. Journal */}
        <button
          type="button"
          onClick={() => navigate('/journal')}
          aria-label={t('journal.title')}
          aria-current={currentRoute === '/journal' ? 'page' : undefined}
          style={{
            flex: 1,
            height: '100%',
            background: 'none',
            border: 'none',
            color: currentRoute === '/journal' ? '#F2C14E' : '#D8C7A3',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.2rem',
            cursor: 'pointer',
            fontSize: '0.72rem',
            fontWeight: currentRoute === '/journal' ? '700' : '400',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          }}
        >
          <BookOpen size={20} />
          <span>{t('journal.title')}</span>
        </button>
      </div>
    </nav>
  );
}
