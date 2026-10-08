/**
 * ImagePreview.jsx - Honest Leaf Image Preview Panel
 *
 * Shows the actual selected image as the visual focus.
 * No fake AI scanning overlays, no disease labels, no fake confidence.
 * Provides three clean actions: "Check this leaf", "Take another", "Choose another".
 *
 * The imageObjectUrl is created from the raw File in CheckLeafScreen and
 * revoked when the component unmounts or image changes.
 */

import React, { useEffect, useRef } from 'react';
import { CheckCircle, RotateCcw, Upload, Loader2 } from 'lucide-react';
import gsap from 'gsap';
import { useLanguage } from '../../context/LanguageContext';

export default function ImagePreview({
  imageFile,
  imageObjectUrl,
  selectedCrop,
  onCheckLeaf,
  onRetake,
  onChooseAnother,
  isSubmitting,
}) {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  const containerRef = useRef(null);
  const imgRef = useRef(null);
  const actionsRef = useRef(null);

  // GSAP entrance when image first appears
  useEffect(() => {
    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced || !containerRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 16 },
        { opacity: 1, y: 0, duration: 0.55, ease: 'power2.out' }
      );
    });

    return () => ctx.revert();
  }, [imageObjectUrl]);

  // Subtle pulse on primary action once image is ready (draws eye gently)
  useEffect(() => {
    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced || !actionsRef.current || isSubmitting) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        actionsRef.current,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.45, delay: 0.3, ease: 'power2.out' }
      );
    });

    return () => ctx.revert();
  }, [imageObjectUrl, isSubmitting]);

  const cropDisplay =
    selectedCrop === 'turmeric'
      ? t('check.crop_turmeric')
      : t('check.crop_citrus');

  return (
    <div ref={containerRef} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* Image Frame */}
      <div
        style={{
          position: 'relative',
          borderRadius: '16px',
          overflow: 'hidden',
          border: '1.5px solid rgba(201, 154, 60, 0.35)',
          boxShadow: '0 12px 32px rgba(28, 17, 10, 0.12)',
          background: '#F4EAD3',
          aspectRatio: '4 / 3',
          width: '100%',
        }}
      >
        <img
          ref={imgRef}
          src={imageObjectUrl}
          alt={t('check.preview_alt')}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            display: 'block',
          }}
        />

        {/* Crop badge overlay — top left */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            top: '0.85rem',
            left: '0.85rem',
            background: 'rgba(28, 17, 10, 0.72)',
            backdropFilter: 'blur(4px)',
            borderRadius: '9999px',
            padding: '0.3rem 0.75rem',
            color: '#F2C14E',
            fontSize: '0.78rem',
            fontWeight: '700',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            letterSpacing: '0.04em',
          }}
        >
          {cropDisplay}
        </div>

        {/* Submitting overlay — calm, no fake scanning */}
        {isSubmitting && (
          <div
            role="status"
            aria-live="polite"
            aria-label={t('check.checking_leaf')}
            style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(28, 17, 10, 0.55)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
            }}
          >
            <Loader2
              size={40}
              color="#F2C14E"
              style={{ animation: 'spin 1.2s linear infinite' }}
              aria-hidden="true"
            />
            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.95rem',
                color: '#F4EAD3',
                fontWeight: '600',
              }}
            >
              {t('check.checking_leaf')}
            </p>
          </div>
        )}
      </div>

      {/* File meta — name only, nothing sensitive */}
      {imageFile && (
        <p
          style={{
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: '0.8rem',
            color: '#6F5F52',
            textAlign: 'center',
          }}
        >
          {imageFile.name}
        </p>
      )}

      {/* Action buttons */}
      <div
        ref={actionsRef}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.65rem',
          opacity: 0, // GSAP will animate in
        }}
      >
        {/* Primary: Check this leaf */}
        <button
          type="button"
          id="btn-check-leaf"
          onClick={onCheckLeaf}
          disabled={isSubmitting}
          style={{
            width: '100%',
            minHeight: '52px',
            padding: '0.85rem 1.5rem',
            background: isSubmitting
              ? 'rgba(201, 154, 60, 0.5)'
              : 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
            border: 'none',
            borderRadius: '12px',
            color: '#140C07',
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '1.05rem',
            fontWeight: '700',
            cursor: isSubmitting ? 'wait' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.6rem',
            boxShadow: isSubmitting
              ? 'none'
              : '0 6px 20px rgba(201, 154, 60, 0.4)',
            transition: 'filter 0.15s ease, box-shadow 0.15s ease',
          }}
          onMouseEnter={(e) => {
            if (!isSubmitting) e.currentTarget.style.filter = 'brightness(1.06)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.filter = 'none';
          }}
        >
          {isSubmitting ? (
            <>
              <Loader2
                size={18}
                aria-hidden="true"
                style={{ animation: 'spin 1.2s linear infinite' }}
              />
              <span>{t('check.checking_leaf')}</span>
            </>
          ) : (
            <>
              <CheckCircle size={18} aria-hidden="true" />
              <span>{t('check.check_leaf')}</span>
            </>
          )}
        </button>

        {/* Secondary action row */}
        <div style={{ display: 'flex', gap: '0.65rem' }}>
          {/* Retake (camera) */}
          <button
            type="button"
            id="btn-retake-photo"
            onClick={onRetake}
            disabled={isSubmitting}
            style={{
              flex: 1,
              minHeight: '44px',
              padding: '0.55rem 0.85rem',
              background: 'rgba(244, 234, 211, 0.6)',
              border: '1px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '10px',
              color: '#3A2412',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.85rem',
              fontWeight: '600',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.4rem',
              opacity: isSubmitting ? 0.55 : 1,
              transition: 'background 0.15s ease',
            }}
            onMouseEnter={(e) => {
              if (!isSubmitting) e.currentTarget.style.background = 'rgba(244, 234, 211, 1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(244, 234, 211, 0.6)';
            }}
          >
            <RotateCcw size={14} aria-hidden="true" />
            <span>{t('check.retake_photo')}</span>
          </button>

          {/* Choose another from gallery */}
          <button
            type="button"
            id="btn-choose-another"
            onClick={onChooseAnother}
            disabled={isSubmitting}
            style={{
              flex: 1,
              minHeight: '44px',
              padding: '0.55rem 0.85rem',
              background: 'rgba(244, 234, 211, 0.6)',
              border: '1px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '10px',
              color: '#3A2412',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.85rem',
              fontWeight: '600',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.4rem',
              opacity: isSubmitting ? 0.55 : 1,
              transition: 'background 0.15s ease',
            }}
            onMouseEnter={(e) => {
              if (!isSubmitting) e.currentTarget.style.background = 'rgba(244, 234, 211, 1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(244, 234, 211, 0.6)';
            }}
          >
            <Upload size={14} aria-hidden="true" />
            <span>{t('check.choose_another')}</span>
          </button>
        </div>
      </div>

      {/* CSS for spinner */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
