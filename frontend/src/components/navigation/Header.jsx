/**
 * Header.jsx - Refined DRISHYA Authenticated Header
 *
 * Implements:
 * - Brand leaf emblem & DRISHYA wordmark on left
 * - Visual language selector (English, हिन्दी, मराठी)
 * - User identity badge
 * - Accessible logout control
 * - Mobile-first compact layout
 */

import React, { useState } from 'react';
import { LogOut, User as UserIcon, BookOpen, Info, Home as HomeIcon, Camera, Compass } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import DrishyaLogo from '../brand/DrishyaLogo';
import LanguageSelector from '../auth/LanguageSelector';

export default function Header() {
  const { user, logout, navigate, currentPath = '' } = useAuth();
  const { t, language } = useLanguage();
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
    } finally {
      setLoggingOut(false);
    }
  };

  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  return (
    <header
      className="drishya-app-header"
      style={{
        width: '100%',
        backgroundColor: '#1C110A',
        borderBottom: '1px solid rgba(201, 154, 60, 0.28)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        boxShadow: '0 4px 20px rgba(12, 7, 3, 0.45)',
      }}
    >
      <div
        style={{
          maxWidth: '1240px',
          margin: '0 auto',
          padding: '0.85rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
        }}
      >
        {/* Brand Anchor */}
        <div
          role="button"
          tabIndex={0}
          onClick={() => navigate('/home')}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              navigate('/home');
            }
          }}
          style={{
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            textDecoration: 'none',
            outline: 'none',
          }}
          aria-label="DRISHYA Home"
        >
          <DrishyaLogo size={42} showWordmark={true} />
        </div>

        {/* Center Desktop Navigation Links (Home, Check, Journal, Guide, About) */}
        <nav
          className="drishya-header-nav-links"
          aria-label="Main navigation"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
          }}
        >
          {/* Home */}
          <button
            type="button"
            id="nav-link-home"
            onClick={() => navigate('/home')}
            style={{
              background: (currentPath === '/home' || currentPath === '/') ? 'rgba(201, 154, 60, 0.15)' : 'transparent',
              border: (currentPath === '/home' || currentPath === '/') ? '1px solid rgba(201, 154, 60, 0.35)' : '1px solid transparent',
              color: (currentPath === '/home' || currentPath === '/') ? '#F2C14E' : '#D8C7A3',
              cursor: 'pointer',
              fontSize: '0.88rem',
              fontWeight: '600',
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-body, "Mukta", sans-serif)',
              padding: '0.45rem 0.75rem',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              minHeight: '44px',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#F2C14E')}
            onMouseLeave={(e) => (e.currentTarget.style.color = (currentPath === '/home' || currentPath === '/') ? '#F2C14E' : '#D8C7A3')}
          >
            <HomeIcon size={15} />
            <span>{t('nav.home')}</span>
          </button>

          {/* Check a Leaf */}
          <button
            type="button"
            id="nav-link-check"
            onClick={() => navigate('/check')}
            style={{
              background: currentPath.startsWith('/check') ? 'rgba(201, 154, 60, 0.15)' : 'transparent',
              border: currentPath.startsWith('/check') ? '1px solid rgba(201, 154, 60, 0.35)' : '1px solid transparent',
              color: currentPath.startsWith('/check') ? '#F2C14E' : '#D8C7A3',
              cursor: 'pointer',
              fontSize: '0.88rem',
              fontWeight: '600',
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-body, "Mukta", sans-serif)',
              padding: '0.45rem 0.75rem',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              minHeight: '44px',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#F2C14E')}
            onMouseLeave={(e) => (e.currentTarget.style.color = currentPath.startsWith('/check') ? '#F2C14E' : '#D8C7A3')}
          >
            <Camera size={15} />
            <span>{t('nav.check')}</span>
          </button>

          {/* Leaf Journal */}
          <button
            type="button"
            id="nav-link-journal"
            onClick={() => navigate('/journal')}
            style={{
              background: currentPath.startsWith('/journal') ? 'rgba(201, 154, 60, 0.15)' : 'transparent',
              border: currentPath.startsWith('/journal') ? '1px solid rgba(201, 154, 60, 0.35)' : '1px solid transparent',
              color: currentPath.startsWith('/journal') ? '#F2C14E' : '#D8C7A3',
              cursor: 'pointer',
              fontSize: '0.88rem',
              fontWeight: '600',
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-body, "Mukta", sans-serif)',
              padding: '0.45rem 0.75rem',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              minHeight: '44px',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#F2C14E')}
            onMouseLeave={(e) => (e.currentTarget.style.color = currentPath.startsWith('/journal') ? '#F2C14E' : '#D8C7A3')}
          >
            <BookOpen size={15} />
            <span>{t('nav.journal')}</span>
          </button>

          {/* Field Guide */}
          <button
            type="button"
            id="nav-link-guide"
            onClick={() => navigate('/guide')}
            style={{
              background: currentPath.startsWith('/guide') ? 'rgba(201, 154, 60, 0.15)' : 'transparent',
              border: currentPath.startsWith('/guide') ? '1px solid rgba(201, 154, 60, 0.35)' : '1px solid transparent',
              color: currentPath.startsWith('/guide') ? '#F2C14E' : '#D8C7A3',
              cursor: 'pointer',
              fontSize: '0.88rem',
              fontWeight: '600',
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-body, "Mukta", sans-serif)',
              padding: '0.45rem 0.75rem',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              minHeight: '44px',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#F2C14E')}
            onMouseLeave={(e) => (e.currentTarget.style.color = currentPath.startsWith('/guide') ? '#F2C14E' : '#D8C7A3')}
          >
            <Compass size={15} />
            <span>{t('nav.guide')}</span>
          </button>

          {/* About DRISHYA */}
          <button
            type="button"
            id="nav-link-about"
            onClick={() => navigate('/about')}
            style={{
              background: currentPath.startsWith('/about') ? 'rgba(201, 154, 60, 0.15)' : 'transparent',
              border: currentPath.startsWith('/about') ? '1px solid rgba(201, 154, 60, 0.35)' : '1px solid transparent',
              color: currentPath.startsWith('/about') ? '#F2C14E' : '#D8C7A3',
              cursor: 'pointer',
              fontSize: '0.88rem',
              fontWeight: '600',
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-body, "Mukta", sans-serif)',
              padding: '0.45rem 0.75rem',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              minHeight: '44px',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#F2C14E')}
            onMouseLeave={(e) => (e.currentTarget.style.color = currentPath.startsWith('/about') ? '#F2C14E' : '#D8C7A3')}
          >
            <Info size={15} />
            <span>{t('nav.about')}</span>
          </button>
        </nav>

        {/* Right Controls: Language Selector + User Identity + Logout */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            flexWrap: 'nowrap',
          }}
        >
          {/* Language Selector */}
          <LanguageSelector />

          {/* User Account / Profile Info */}
          <div
            className="drishya-header-user-badge"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.4rem 0.85rem',
              background: 'rgba(58, 36, 18, 0.65)',
              border: '1px solid rgba(201, 154, 60, 0.25)',
              borderRadius: '9999px',
              color: '#F4EAD3',
              fontSize: '0.85rem',
            }}
          >
            <UserIcon size={16} color="#C99A3C" aria-hidden="true" />
            <span
              style={{
                fontFamily: isHindiOrMarathi
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-body, "Mukta", sans-serif)',
                fontWeight: '500',
                maxWidth: '150px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user?.name || 'Farmer'}
            </span>
          </div>

          {/* Logout Button (Minimum 48px Touch Target) */}
          <button
            type="button"
            id="btn-header-logout"
            onClick={handleLogout}
            disabled={loggingOut}
            aria-label={t('nav.logout')}
            title={t('nav.logout')}
            style={{
              minHeight: '44px',
              minWidth: '96px',
              padding: '0.45rem 1.1rem',
              background: 'rgba(162, 74, 43, 0.15)',
              border: '1px solid rgba(162, 74, 43, 0.45)',
              borderRadius: '9999px',
              color: '#F4D4CA',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              cursor: loggingOut ? 'wait' : 'pointer',
              fontSize: '0.85rem',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontWeight: '500',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(162, 74, 43, 0.3)';
              e.currentTarget.style.borderColor = '#A24A2B';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(162, 74, 43, 0.15)';
              e.currentTarget.style.borderColor = 'rgba(162, 74, 43, 0.45)';
            }}
          >
            <LogOut size={16} />
            <span className="drishya-logout-label">{t('nav.logout')}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
