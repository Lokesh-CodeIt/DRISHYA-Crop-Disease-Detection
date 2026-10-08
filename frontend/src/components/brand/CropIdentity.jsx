/**
 * CropIdentity.jsx - Reusable Crop Visual Identity Component
 *
 * Displays a small real crop photo alongside the localized crop name.
 * Use wherever DRISHYA presents a user-facing crop identity.
 *
 * Props:
 *   crop     — "turmeric" | "citrus"
 *   size     — image circle size in px (default 36)
 *   fontSize — text font size (default "0.95rem")
 *   showName — whether to show the text label (default true)
 *   style    — optional extra style for the outer wrapper
 *   className — optional extra className
 */

import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

const CROP_CONFIG = {
  turmeric: {
    src: '/logo/turmuric.jpg',       // exact filename as uploaded
    objectPosition: '20% 70%',        // focus on the turmeric roots/rhizome
    accentColor: '#C99A3C',
    labelKey: 'check.crop_turmeric',
  },
  citrus: {
    src: '/logo/citrus.jpg',
    objectPosition: '50% 40%',        // focus on the cross-section center
    accentColor: '#C07A2B',
    labelKey: 'check.crop_citrus',
  },
};

export default function CropIdentity({
  crop,
  size = 36,
  fontSize = '0.95rem',
  showName = true,
  style = {},
  className = '',
}) {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  const config = CROP_CONFIG[crop];
  if (!config) return null;

  const { src, objectPosition, accentColor, labelKey } = config;
  const name = t(labelKey);

  return (
    <span
      className={`drishya-crop-identity ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: `${Math.round(size * 0.33)}px`,
        flexShrink: 0,
        ...style,
      }}
    >
      {/* Small circular crop photo */}
      <span
        style={{
          display: 'inline-block',
          width: `${size}px`,
          height: `${size}px`,
          borderRadius: '50%',
          overflow: 'hidden',
          flexShrink: 0,
          border: `1.5px solid ${accentColor}55`,
          boxShadow: `0 0 0 1px ${accentColor}22`,
          lineHeight: 0,
        }}
        aria-hidden="true"
      >
        <img
          src={src}
          alt=""
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition,
            display: 'block',
            pointerEvents: 'none',
            userSelect: 'none',
          }}
          loading="lazy"
          draggable={false}
        />
      </span>

      {/* Localized crop name */}
      {showName && (
        <span
          style={{
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-body, "Mukta", sans-serif)',
            fontSize,
            fontWeight: '600',
            color: 'currentColor',
            whiteSpace: 'nowrap',
            lineHeight: 1.2,
          }}
        >
          {name}
        </span>
      )}
    </span>
  );
}
