/**
 * CropContext.jsx - Crop Selection Banner for Check a Leaf Workspace
 *
 * Shows the selected crop (Turmeric / Citrus) with real crop photo
 * and a "Change" control.
 * Designed for the editorial parchment aesthetic — no technical internals.
 */

import React from 'react';
import { ChevronDown } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import CropIdentity from '../brand/CropIdentity';

export default function CropContext({ selectedCrop, onChangeCrop }) {
  const { t } = useLanguage();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(201, 154, 60, 0.12)',
        border: '1px solid rgba(201, 154, 60, 0.32)',
        borderRadius: '12px',
        padding: '0.75rem 1.1rem',
        marginBottom: '2rem',
        gap: '0.75rem',
      }}
    >
      {/* Crop identity with real photo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
        <div>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.78rem',
              color: '#8A5A2B',
              fontWeight: '600',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              marginBottom: '0.35rem',
            }}
          >
            {t('check.selected_crop_label')}
          </p>
          <CropIdentity
            crop={selectedCrop}
            size={32}
            fontSize="1.05rem"
            style={{ color: '#1C110A' }}
          />
        </div>
      </div>

      {/* Change crop button */}
      <button
        type="button"
        id="btn-change-crop"
        onClick={onChangeCrop}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.3rem',
          padding: '0.45rem 0.9rem',
          background: 'rgba(244, 234, 211, 0.7)',
          border: '1px solid rgba(201, 154, 60, 0.4)',
          borderRadius: '9999px',
          color: '#5A3A1A',
          fontSize: '0.85rem',
          fontWeight: '600',
          fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          cursor: 'pointer',
          minHeight: '36px',
          whiteSpace: 'nowrap',
          transition: 'background 0.15s ease, border-color 0.15s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(244, 234, 211, 1)';
          e.currentTarget.style.borderColor = '#C99A3C';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'rgba(244, 234, 211, 0.7)';
          e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.4)';
        }}
        aria-label={t('check.change_crop_aria')}
      >
        <span>{t('check.change_crop')}</span>
        <ChevronDown size={14} aria-hidden="true" />
      </button>
    </div>
  );
}
