/**
 * CheckLeafScreen.jsx - The Real DRISHYA "Check a Leaf" Workspace
 *
 * User journey:
 *   Home (crop selected) → Check a Leaf → prepare → pick/capture photo
 *   → preview → "Check this leaf" → real backend diagnosis → result handoff
 *
 * Contract:
 * - POST /api/v1/diagnose  multipart: file, crop, language
 * - Auth via HttpOnly cookie (credentials: 'include') — no JWT in JS
 * - Raw image kept in React state only; never persisted to localStorage / URL
 * - On success: calls onDiagnosisComplete(result, file, crop) for future Result step
 * - On auth failure (401/403): triggers re-auth via AuthContext
 *
 * Design:
 * - Parchment / ivory base, espresso sections, antique-gold accents
 * - Desktop: two-column (prep + upload left, preview right)
 * - Mobile 375px+: single column, preview first then actions
 * - GSAP restrained entrance; respects prefers-reduced-motion
 * - No fake AI scanning, no invented disease labels, no fake confidence
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import gsap from 'gsap';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { submitLeafDiagnosis, DiagnosisApiError } from '../../services/diagnosisApi';
import CropContext from './CropContext';
import PhotoPreparation from './PhotoPreparation';
import ImageUploader from './ImageUploader';
import ImagePreview from './ImagePreview';

/**
 * Translate structured backend/network errors into calm user-facing messages.
 * Never exposes Python tracebacks, model internals, or raw exception text.
 */
function mapErrorToUserMessage(err, t) {
  if (!err) return t('error.generic');

  if (err instanceof DiagnosisApiError) {
    if (err.status === 401 || err.status === 403) {
      return t('error.unauthorized');
    }
    if (err.status === 422) {
      return t('check.error_invalid_type');
    }
    if (err.status === 503) {
      return t('check.error_service_unavailable');
    }
    if (err.status === 0) {
      return t('error.network');
    }
    // Generic backend message — already safe from backend
    return t('check.error_diagnosis_failed');
  }

  return t('error.generic');
}

export default function CheckLeafScreen({
  initialCrop = null,
  onChangeCrop,
  onDiagnosisComplete,
  initialImageFile = null,
  initialImageObjectUrl = null,
}) {
  const { navigate, logout } = useAuth();
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  // State
  const [selectedCrop, setSelectedCrop] = useState(initialCrop || 'turmeric');
  const [imageFile, setImageFile] = useState(initialImageFile || null);           // Raw File object (in-memory only)
  const [imageObjectUrl, setImageObjectUrl] = useState(initialImageObjectUrl || null); // Object URL for preview
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Track if payload was handed off to analysis/result to preserve object URL
  const handedOffRef = useRef(false);

  // Refs for file inputs (passed down to ImageUploader for retake/choose-another)
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  // GSAP screen entrance
  const screenRef = useRef(null);
  const headerRef = useRef(null);
  const leftColRef = useRef(null);
  const rightColRef = useRef(null);

  useEffect(() => {
    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced || !screenRef.current) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });
      gsap.set([headerRef.current, leftColRef.current, rightColRef.current].filter(Boolean), {
        opacity: 0,
        y: 18,
      });
      tl.to(headerRef.current, { opacity: 1, y: 0, duration: 0.55 }, 0.05)
        .to(leftColRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.2)
        .to(rightColRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.35);
    }, screenRef);

    return () => ctx.revert();
  }, []);

  // Keep selectedCrop in sync if parent re-routes with different crop
  useEffect(() => {
    if (initialCrop && initialCrop !== selectedCrop) {
      setSelectedCrop(initialCrop);
    }
  }, [initialCrop]);

  // Revoke object URL when image changes or unmounts (unless handed off to analysis)
  useEffect(() => {
    return () => {
      if (imageObjectUrl && !handedOffRef.current && imageObjectUrl !== initialImageObjectUrl) {
        URL.revokeObjectURL(imageObjectUrl);
      }
    };
  }, [imageObjectUrl, initialImageObjectUrl]);

  // Handle an image file being selected or validated
  const handleImageSelected = useCallback((file) => {
    if (imageObjectUrl && imageObjectUrl !== initialImageObjectUrl) {
      URL.revokeObjectURL(imageObjectUrl);
    }
    const url = URL.createObjectURL(file);
    setImageFile(file);
    setImageObjectUrl(url);
    setErrorMessage(null);
    handedOffRef.current = false;
  }, [imageObjectUrl, initialImageObjectUrl]);

  // Validation errors from ImageUploader
  const handleValidationError = useCallback((msg) => {
    setErrorMessage(msg);
    setImageFile(null);
    if (imageObjectUrl) {
      URL.revokeObjectURL(imageObjectUrl);
      setImageObjectUrl(null);
    }
  }, [imageObjectUrl]);

  // "Change crop" — go back to home for re-selection
  const handleChangeCrop = () => {
    if (onChangeCrop) {
      onChangeCrop();
    } else {
      navigate('/home');
    }
  };

  // Clear current image and return to uploader
  const handleRetake = () => {
    if (imageObjectUrl) URL.revokeObjectURL(imageObjectUrl);
    setImageFile(null);
    setImageObjectUrl(null);
    setErrorMessage(null);
    // Trigger camera input
    cameraInputRef.current?.click();
  };

  const handleChooseAnother = () => {
    if (imageObjectUrl) URL.revokeObjectURL(imageObjectUrl);
    setImageFile(null);
    setImageObjectUrl(null);
    setErrorMessage(null);
    // Trigger gallery input
    fileInputRef.current?.click();
  };

  // ─── Primary action: submit to backend ────────────────────────────────────
  const handleCheckLeaf = async () => {
    if (!imageFile) {
      setErrorMessage(t('check.error_no_image'));
      return;
    }
    if (isSubmitting) return;

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const result = await submitLeafDiagnosis({
        file: imageFile,
        crop: selectedCrop,
        language,
      });

      // Hand off to the Analysis screen
      // We pass: diagnosis response, crop, in-session object URL, and in-memory File
      // Raw file bytes are NOT stored in localStorage or URL params
      handedOffRef.current = true;
      if (onDiagnosisComplete) {
        onDiagnosisComplete({
          diagnosisResponse: result,
          crop: selectedCrop,
          imageObjectUrl: imageObjectUrl, // in-memory only for this session
          imageFileName: imageFile.name,
          imageFile: imageFile,           // in-memory File reference for back navigation
        });
      }
    } catch (err) {
      const userMsg = mapErrorToUserMessage(err, t);
      setErrorMessage(userMsg);

      // Session expired: force re-auth
      if (err instanceof DiagnosisApiError && (err.status === 401 || err.status === 403)) {
        setTimeout(() => {
          logout();
        }, 1800);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // ─── Render ───────────────────────────────────────────────────────────────
  const hasImage = Boolean(imageFile && imageObjectUrl);

  return (
    <div
      ref={screenRef}
      style={{
        width: '100%',
        minHeight: 'calc(100vh - 65px)',
        backgroundColor: '#FBF6EA',
        padding: '2rem 1.5rem 5rem',
      }}
    >
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>

        {/* Back nav */}
        <div ref={headerRef} style={{ marginBottom: '1.75rem' }}>
          <button
            type="button"
            id="btn-back-to-home"
            onClick={() => navigate('/home')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'none',
              border: 'none',
              color: '#6F5F52',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.88rem',
              fontWeight: '600',
              cursor: 'pointer',
              padding: '0.35rem 0',
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#3A2412')}
            onMouseLeave={(e) => (e.currentTarget.style.color = '#6F5F52')}
            aria-label={t('home.back_to_home')}
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>{t('home.back_to_home')}</span>
          </button>

          {/* Page heading */}
          <h1
            style={{
              fontFamily: isDevanagari
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: 'clamp(1.8rem, 3.5vw, 2.6rem)',
              fontWeight: '700',
              color: '#1C110A',
              lineHeight: 1.2,
              marginTop: '0.6rem',
              letterSpacing: isDevanagari ? 0 : '-0.02em',
            }}
          >
            {t('check.title')}
          </h1>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: 'clamp(0.95rem, 1.6vw, 1.1rem)',
              color: '#4A3728',
              marginTop: '0.4rem',
              lineHeight: 1.55,
              maxWidth: '580px',
            }}
          >
            {t('check.subtitle')}
          </p>
        </div>

        {/* Crop context banner */}
        <CropContext
          selectedCrop={selectedCrop}
          onChangeCrop={handleChangeCrop}
        />

        {/* Error message */}
        {errorMessage && (
          <div
            role="alert"
            aria-live="assertive"
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.65rem',
              background: 'rgba(162, 74, 43, 0.1)',
              border: '1px solid rgba(162, 74, 43, 0.4)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
              marginBottom: '1.5rem',
              color: '#7A2E12',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.92rem',
            }}
          >
            <AlertCircle size={18} aria-hidden="true" style={{ flexShrink: 0, marginTop: '1px' }} />
            <div style={{ flex: 1 }}>
              <strong style={{ display: 'block', marginBottom: '0.1rem' }}>
                {t('common.error')}
              </strong>
              <span>{errorMessage}</span>
              {/* Retry affordance when an image exists */}
              {hasImage && (
                <button
                  type="button"
                  onClick={() => {
                    setErrorMessage(null);
                    handleCheckLeaf();
                  }}
                  style={{
                    display: 'inline-block',
                    marginTop: '0.5rem',
                    background: 'none',
                    border: 'none',
                    color: '#7A2E12',
                    fontWeight: '700',
                    textDecoration: 'underline',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.9rem',
                    padding: 0,
                  }}
                >
                  {t('check.retry')}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Main two-column layout (desktop) / stacked (mobile) */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: hasImage ? '1fr 1fr' : '1fr',
            gap: '2rem',
            alignItems: 'start',
          }}
          className="drishya-check-grid"
        >
          {/* LEFT: Preparation + Uploader */}
          <div ref={leftColRef}>
            {/* Preparation tips */}
            {!hasImage && <PhotoPreparation />}

            {/* When image exists on mobile, show the uploader controls below preview */}
            {!hasImage && (
              <ImageUploader
                onImageSelected={handleImageSelected}
                onValidationError={handleValidationError}
                fileInputRef={fileInputRef}
                cameraInputRef={cameraInputRef}
              />
            )}

            {/* On desktop with image: show minimal "change photo" option in left column */}
            {hasImage && (
              <div
                style={{
                  padding: '1.5rem',
                  background: '#FAF5EB',
                  border: '1.5px solid rgba(201, 154, 60, 0.25)',
                  borderRadius: '16px',
                }}
              >
                <PhotoPreparation />
                <div style={{ marginTop: '1.5rem' }}>
                  <ImageUploader
                    onImageSelected={handleImageSelected}
                    onValidationError={handleValidationError}
                    fileInputRef={fileInputRef}
                    cameraInputRef={cameraInputRef}
                  />
                </div>
              </div>
            )}
          </div>

          {/* RIGHT: Image Preview (only when image selected) */}
          {hasImage && (
            <div ref={rightColRef}>
              <ImagePreview
                imageFile={imageFile}
                imageObjectUrl={imageObjectUrl}
                selectedCrop={selectedCrop}
                onCheckLeaf={handleCheckLeaf}
                onRetake={handleRetake}
                onChooseAnother={handleChooseAnother}
                isSubmitting={isSubmitting}
                fileInputRef={fileInputRef}
                cameraInputRef={cameraInputRef}
              />
            </div>
          )}
        </div>
      </div>

      {/* Responsive grid rules */}
      <style>{`
        @media (max-width: 768px) {
          .drishya-check-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
