/**
 * PhotoTipsTeaser.jsx - Truthful Field Photography Guidance Teaser
 *
 * Implements:
 * - Three gentle, practical field habits for capturing clear crop leaves
 * - Grounded truthful advice (no claims of automated quality validation)
 * - Botanical field journal aesthetic with antique gold & parchment framing
 */

import React from 'react';
import { Camera, Sun, Focus } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function PhotoTipsTeaser() {
  const { t, language } = useLanguage();
  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  const tips = [
    {
      icon: <Camera size={22} color="#8A5A2B" />,
      title: t('home.tip_single_leaf_title'),
      desc: t('home.tip_single_leaf_desc'),
    },
    {
      icon: <Sun size={22} color="#C99A3C" />,
      title: t('home.tip_lighting_title'),
      desc: t('home.tip_lighting_desc'),
    },
    {
      icon: <Focus size={22} color="#5E6B38" />,
      title: t('home.tip_sharp_title'),
      desc: t('home.tip_sharp_desc'),
    },
  ];

  return (
    <section
      className="drishya-photo-tips"
      style={{
        width: '100%',
        margin: '2rem 0 3.5rem',
        background: '#FAF5EB',
        border: '1.5px solid rgba(201, 154, 60, 0.3)',
        borderRadius: '18px',
        padding: '1.8rem 2rem',
        boxShadow: '0 8px 24px rgba(28, 17, 10, 0.04)',
      }}
      aria-labelledby="photo-tips-heading"
    >
      <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <h2
          id="photo-tips-heading"
          style={{
            fontFamily: isHindiOrMarathi
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '1.45rem',
            color: '#1C110A',
            fontWeight: '700',
            marginBottom: '0.35rem',
          }}
        >
          {t('home.photo_tips_title')}
        </h2>
        <p
          style={{
            color: '#6F5F52',
            fontSize: '0.92rem',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          }}
        >
          {t('home.photo_tips_subtitle')}
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.5rem',
        }}
      >
        {tips.map((tip, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              padding: '1rem',
              borderRadius: '12px',
              background: 'rgba(244, 234, 211, 0.4)',
              border: '1px solid rgba(201, 154, 60, 0.2)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: '#F4EAD3',
                border: '1px solid rgba(201, 154, 60, 0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '0.85rem',
              }}
            >
              {tip.icon}
            </div>
            <h3
              style={{
                fontFamily: isHindiOrMarathi
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: '1.05rem',
                color: '#1C110A',
                fontWeight: '700',
                marginBottom: '0.4rem',
              }}
            >
              {tip.title}
            </h3>
            <p
              style={{
                fontSize: '0.88rem',
                color: '#4A3728',
                lineHeight: 1.5,
              }}
            >
              {tip.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
