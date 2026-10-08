/**
 * CropTile.jsx - Botanical Field Journal Crop Selection Tile
 *
 * Implements:
 * - Pipal-arch geometric framing with antique gold hairline border
 * - Authentic botanical plate illustration
 * - Clear crop identity, scientific name, and observation scope
 * - 48px+ accessible touch target selection button
 */

import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function CropTile({
  cropKey,
  title,
  scientificName,
  description,
  actionText,
  imageSrc,
  onSelect,
  className = '',
}) {
  const { language } = useLanguage();
  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(cropKey);
    }
  };

  return (
    <article
      className={`drishya-crop-tile ${className}`}
      tabIndex={0}
      role="region"
      aria-label={`${title} - ${scientificName}`}
      onKeyDown={handleKeyDown}
      style={{
        background: '#FAF5EB',
        border: '1.5px solid rgba(201, 154, 60, 0.35)',
        borderRadius: '20px',
        overflow: 'hidden',
        boxShadow: '0 12px 32px rgba(28, 17, 10, 0.08), 0 2px 6px rgba(201, 154, 60, 0.12)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transition: 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease',
        cursor: 'pointer',
        position: 'relative',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 20px 40px rgba(58, 36, 18, 0.16), 0 0 0 1px rgba(201, 154, 60, 0.5)';
        e.currentTarget.style.borderColor = '#C99A3C';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 12px 32px rgba(28, 17, 10, 0.08), 0 2px 6px rgba(201, 154, 60, 0.12)';
        e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.35)';
      }}
    >
      {/* Decorative Botanical Hairline Header Ribbon */}
      <div
        style={{
          padding: '1rem 1.4rem 0.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid rgba(201, 154, 60, 0.2)',
          background: 'rgba(244, 234, 211, 0.5)',
        }}
      >
        <span
          style={{
            fontFamily: 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '0.82rem',
            fontStyle: 'italic',
            letterSpacing: '0.04em',
            color: '#8A5A2B',
          }}
        >
          {scientificName}
        </span>
        <span
          style={{
            fontSize: '0.72rem',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: '#6F5F52',
            fontWeight: '600',
          }}
        >
          DRISHYA SPECIES • ACTIVE
        </span>
      </div>

      {/* Botanical Plate Illustration Frame with Pipal Arch contour */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '240px',
          overflow: 'hidden',
          backgroundColor: '#F4EAD3',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <img
          src={imageSrc}
          alt={`${title} botanical plate`}
          loading="lazy"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: cropKey === 'turmeric' ? '20% 65%' : '50% 40%',
            transition: 'transform 0.4s ease',
          }}
        />
        {/* Subtle warm vignette overlay */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(180deg, transparent 70%, rgba(28, 17, 10, 0.15) 100%)',
            pointerEvents: 'none',
          }}
        />
      </div>

      {/* Editorial Content Description Block */}
      <div
        style={{
          padding: '1.5rem 1.6rem 1.6rem',
          display: 'flex',
          flexDirection: 'column',
          flex: 1,
          justifyContent: 'space-between',
          backgroundColor: '#FAF5EB',
        }}
      >
        <div style={{ marginBottom: '1.25rem' }}>
          <h3
            style={{
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.65rem',
              fontWeight: '700',
              color: '#1C110A',
              lineHeight: 1.25,
              marginBottom: '0.5rem',
            }}
          >
            {title}
          </h3>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1.02rem',
              color: '#4A3728',
              lineHeight: 1.55,
            }}
          >
            {description}
          </p>
        </div>

        {/* Clear Selection Affordance Button (min 48px target) */}
        <button
          type="button"
          onClick={() => onSelect(cropKey)}
          style={{
            width: '100%',
            minHeight: '48px',
            padding: '0.75rem 1.4rem',
            background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
            border: 'none',
            borderRadius: '10px',
            color: '#140C07',
            fontFamily: isHindiOrMarathi
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: isHindiOrMarathi ? '1rem' : '1.05rem',
            fontWeight: '700',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.6rem',
            boxShadow: '0 4px 14px rgba(201, 154, 60, 0.35)',
            transition: 'transform 0.15s ease, filter 0.15s ease',
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.98)')}
          onMouseUp={(e) => (e.currentTarget.style.transform = 'scale(1)')}
        >
          <span>{actionText}</span>
          <ArrowRight size={18} />
        </button>
      </div>
    </article>
  );
}
