/**
 * PhotoPreparation.jsx - Leaf Photo Guidance Section
 *
 * Provides three truthful, calibrated guidance tips for field photography.
 * No false claims about automatic detection, validation, or AI scanning.
 */

import React from 'react';
import { Sun, Focus, Layers } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

const TIPS = [
  {
    id: 'single-leaf',
    icon: Layers,
    titleKey: 'home.tip_single_leaf_title',
    descKey: 'home.tip_single_leaf_desc',
  },
  {
    id: 'good-light',
    icon: Sun,
    titleKey: 'home.tip_lighting_title',
    descKey: 'home.tip_lighting_desc',
  },
  {
    id: 'sharp-focus',
    icon: Focus,
    titleKey: 'home.tip_sharp_title',
    descKey: 'home.tip_sharp_desc',
  },
];

export default function PhotoPreparation() {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  return (
    <section
      aria-labelledby="prep-heading"
      style={{ marginBottom: '2rem' }}
    >
      {/* Section heading */}
      <h2
        id="prep-heading"
        style={{
          fontFamily: isDevanagari
            ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
            : 'var(--font-display, "Fraunces", Georgia, serif)',
          fontSize: '1.3rem',
          fontWeight: '700',
          color: '#1C110A',
          marginBottom: '1rem',
          lineHeight: 1.25,
        }}
      >
        {t('check.prepare_heading')}
      </h2>

      {/* Three guidance rows */}
      <ul
        style={{
          listStyle: 'none',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
          padding: 0,
          margin: 0,
        }}
        role="list"
      >
        {TIPS.map(({ id, icon: Icon, titleKey, descKey }) => (
          <li
            key={id}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              background: 'rgba(244, 234, 211, 0.55)',
              border: '1px solid rgba(201, 154, 60, 0.2)',
              borderRadius: '10px',
            }}
          >
            {/* Icon badge */}
            <div
              aria-hidden="true"
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                background: 'rgba(201, 154, 60, 0.18)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                color: '#8A5A2B',
              }}
            >
              <Icon size={18} />
            </div>

            {/* Text */}
            <div>
              <p
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '0.92rem',
                  fontWeight: '700',
                  color: '#1C110A',
                  marginBottom: '0.15rem',
                  lineHeight: 1.3,
                }}
              >
                {t(titleKey)}
              </p>
              <p
                style={{
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '0.85rem',
                  color: '#4A3728',
                  lineHeight: 1.5,
                }}
              >
                {t(descKey)}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
