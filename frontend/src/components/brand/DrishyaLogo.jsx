/**
 * DrishyaLogo.jsx - DRISHYA Brand Logo (Real PNG)
 *
 * Uses the authoritative real DRISHYA logo PNG:
 *   /logo/drishya-logo.png
 *
 * The old SVG recreation has been removed.
 * The PNG itself is the single source of truth for the emblem.
 * Any tagline/subtitle displayed below uses i18next — never hardcoded.
 *
 * Props:
 *   size         — height of the logo image in px (default 48)
 *   showWordmark — if true, show "DRISHYA" text + i18n tagline (default true)
 *   className    — optional className for the wrapper
 *   emblemRef    — optional React ref forwarded to the <img> wrapper div
 *   wordmarkRef  — optional React ref forwarded to the wordmark div
 */

import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

export default function DrishyaLogo({
  size = 48,
  showWordmark = true,
  className = '',
  emblemRef = null,
  wordmarkRef = null,
}) {
  const { t } = useLanguage();

  return (
    <div
      className={`drishya-logo-container ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.75rem',
        textDecoration: 'none',
        flexShrink: 0,
      }}
    >
      {/* Real DRISHYA logo PNG emblem */}
      <div
        ref={emblemRef}
        className="drishya-logo-emblem"
        style={{ flexShrink: 0, lineHeight: 0 }}
      >
        <img
          src="/logo/drishya-logo.png"
          alt="DRISHYA logo"
          width={size}
          height={Math.round(size * 1.533)} /* natural aspect ratio 630:966 */
          style={{
            width: `${size}px`,
            height: `${Math.round(size * 1.533)}px`,
            objectFit: 'contain',
            objectPosition: 'center',
            display: 'block',
            userSelect: 'none',
            pointerEvents: 'none',
          }}
          draggable={false}
        />
      </div>

      {/* Brand wordmark — fully i18n, no hardcoded Devanagari */}
      {showWordmark && (
        <div
          ref={wordmarkRef}
          className="drishya-logo-wordmark"
          style={{ display: 'flex', flexDirection: 'column' }}
        >
          <span
            style={{
              fontFamily: 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.35rem',
              fontWeight: '700',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: 'var(--c-parchment, #F4EAD3)',
              lineHeight: 1.1,
            }}
          >
            DRISHYA
          </span>
          <span
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.72rem',
              color: 'var(--c-antique-gold, #C99A3C)',
              letterSpacing: '0.06em',
              opacity: 0.85,
              marginTop: '0.15rem',
              whiteSpace: 'nowrap',
            }}
          >
            {t('app.tagline')}
          </span>
        </div>
      )}
    </div>
  );
}
