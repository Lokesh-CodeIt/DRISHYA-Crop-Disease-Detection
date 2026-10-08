/**
 * AnalysisScreen.jsx - The DRISHYA Analysis Experience & Transition
 *
 * Implements:
 * - Quiet examination chamber (dark espresso/bark field + warm antique-gold light)
 * - Large original leaf image as continuous visual hero (zero filters, zero artificial blur)
 * - Restrained GSAP transition: smooth scaling, gentle warm light sweep, minimal typography
 * - Respects prefers-reduced-motion: removes decorative movement, shortens transition to ~250ms
 * - Never fakes analysis data: NO fake percentages, NO fake disease regions, NO fake Grad-CAM
 * - Safe response branching:
 *     - Valid diagnosis payload -> transitions smoothly toward /result
 *     - Unexpected/interrupted response -> calm error state with return affordance
 *     - Missing/refreshed payload -> calm "No active leaf" state with safe return to /check
 * - Accessible: keyboard navigable, screen reader status announcements (aria-live), 48px+ touch targets
 * - Responsive: 375px, 390px, 768px, desktop (zero horizontal overflow)
 */

import React, { useEffect, useRef, useState } from 'react';
import { ArrowLeft, AlertCircle, Sparkles } from 'lucide-react';
import gsap from 'gsap';
import { useLanguage } from '../../context/LanguageContext';
import CropIdentity from '../brand/CropIdentity';

export default function AnalysisScreen({
  diagnosisPayload = null,
  onComplete,
  onBackToCheck,
}) {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  // Refs for GSAP animation
  const containerRef = useRef(null);
  const leafFrameRef = useRef(null);
  const lightPassRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);
  const indicatorRef = useRef(null);
  const tlRef = useRef(null);

  // Validate the diagnosis payload
  const hasPayload = Boolean(
    diagnosisPayload &&
    diagnosisPayload.imageObjectUrl
  );

  const isValidResponse = Boolean(
    hasPayload &&
    diagnosisPayload.diagnosisResponse &&
    diagnosisPayload.diagnosisResponse.prediction &&
    typeof diagnosisPayload.diagnosisResponse.prediction.predicted_class === 'string'
  );

  // Determine state: 'transitioning' | 'interrupted' | 'no_payload'
  const screenState = !hasPayload
    ? 'no_payload'
    : !isValidResponse
    ? 'interrupted'
    : 'transitioning';

  // GSAP Transition sequence for valid diagnosis
  useEffect(() => {
    if (screenState !== 'transitioning') return;

    let timeoutId = null;
    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const ctx = gsap.context(() => {
      if (prefersReduced) {
        // Reduced motion: instantaneous fade, no scale or light sweep
        gsap.set(
          [leafFrameRef.current, titleRef.current, subtitleRef.current, indicatorRef.current].filter(Boolean),
          { opacity: 1 }
        );
        timeoutId = setTimeout(() => {
          onComplete?.();
        }, 250);
        return;
      }

      // Standard cinematic examination transition (~900ms total)
      const tl = gsap.timeline({
        defaults: { ease: 'power2.out' },
        onComplete: () => {
          onComplete?.();
        },
      });
      tlRef.current = tl;

      // 1. Initial positions
      gsap.set(leafFrameRef.current, { opacity: 0, scale: 0.94, y: 14 });
      gsap.set(lightPassRef.current, { xPercent: -130, opacity: 0 });
      gsap.set(titleRef.current, { opacity: 0, y: 12 });
      gsap.set(subtitleRef.current, { opacity: 0, y: 8 });
      gsap.set(indicatorRef.current, { opacity: 0 });

      // 2. Leaf frame entrance (0 to 0.45s)
      tl.to(leafFrameRef.current, {
        opacity: 1,
        scale: 1,
        y: 0,
        duration: 0.45,
        ease: 'power2.out',
      })
      // 3. Subtle warm golden light sweep across leaf (0.2s to 0.85s)
      .to(
        lightPassRef.current,
        {
          opacity: 0.7,
          duration: 0.15,
          ease: 'power1.in',
        },
        0.2
      )
      .to(
        lightPassRef.current,
        {
          xPercent: 130,
          duration: 0.65,
          ease: 'power1.inOut',
        },
        0.2
      )
      .to(
        lightPassRef.current,
        {
          opacity: 0,
          duration: 0.2,
        },
        0.65
      )
      // 4. "Looking closely at your leaf..." title appears (0.35s to 0.75s)
      .to(
        titleRef.current,
        {
          opacity: 1,
          y: 0,
          duration: 0.4,
        },
        0.35
      )
      // 5. Supporting text & quiet examination indicator appear (0.5s to 0.85s)
      .to(
        subtitleRef.current,
        {
          opacity: 1,
          y: 0,
          duration: 0.35,
        },
        0.5
      )
      .to(
        indicatorRef.current,
        {
          opacity: 1,
          duration: 0.3,
        },
        0.55
      );
    }, containerRef);

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (tlRef.current) tlRef.current.kill();
      ctx.revert();
    };
  }, [screenState, onComplete]);

  // Handle user intentionally canceling / returning to Check
  const handleReturn = () => {
    if (tlRef.current) tlRef.current.kill();
    onBackToCheck?.();
  };

  const cropName = diagnosisPayload?.crop
    ? diagnosisPayload.crop === 'turmeric'
      ? t('check.crop_turmeric')
      : t('check.crop_citrus')
    : null;

  // ─── STATE A: No Payload (Direct URL access or refreshed page) ───────────
  if (screenState === 'no_payload') {
    return (
      <div
        style={{
          width: '100%',
          minHeight: 'calc(100vh - 65px)',
          backgroundColor: '#160E08',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem 1.5rem',
        }}
      >
        <div
          style={{
            maxWidth: '480px',
            width: '100%',
            background: '#23160E',
            border: '1.5px solid rgba(201, 154, 60, 0.35)',
            borderRadius: '20px',
            padding: '2.5rem 2rem',
            textAlign: 'center',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
          }}
        >
          <div
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: 'rgba(201, 154, 60, 0.15)',
              border: '1px solid rgba(201, 154, 60, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem',
              color: '#F2C14E',
            }}
          >
            <AlertCircle size={28} aria-hidden="true" />
          </div>

          <h2
            style={{
              fontFamily: isDevanagari
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.5rem',
              color: '#F4EAD3',
              marginBottom: '0.6rem',
            }}
          >
            {t('analysis.no_leaf_title')}
          </h2>

          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.98rem',
              color: '#D8C7A3',
              lineHeight: 1.55,
              marginBottom: '2rem',
            }}
          >
            {t('analysis.no_leaf_desc')}
          </p>

          <button
            type="button"
            id="btn-analysis-go-to-check"
            onClick={handleReturn}
            style={{
              minHeight: '48px',
              padding: '0.75rem 1.75rem',
              background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
              border: 'none',
              borderRadius: '10px',
              color: '#140C07',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 4px 14px rgba(201, 154, 60, 0.35)',
            }}
          >
            <ArrowLeft size={18} aria-hidden="true" />
            <span>{t('analysis.go_to_check')}</span>
          </button>
        </div>
      </div>
    );
  }

  // ─── STATE B: Interrupted / Invalid Response ─────────────────────────────
  if (screenState === 'interrupted') {
    return (
      <div
        style={{
          width: '100%',
          minHeight: 'calc(100vh - 65px)',
          backgroundColor: '#160E08',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem 1.5rem',
        }}
      >
        <div
          style={{
            maxWidth: '480px',
            width: '100%',
            background: '#23160E',
            border: '1.5px solid rgba(201, 154, 60, 0.35)',
            borderRadius: '20px',
            padding: '2.5rem 2rem',
            textAlign: 'center',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
          }}
        >
          <div
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: 'rgba(162, 74, 43, 0.2)',
              border: '1px solid rgba(162, 74, 43, 0.45)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem',
              color: '#F4D4CA',
            }}
          >
            <AlertCircle size={28} aria-hidden="true" />
          </div>

          <h2
            style={{
              fontFamily: isDevanagari
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.5rem',
              color: '#F4EAD3',
              marginBottom: '0.6rem',
            }}
          >
            {t('analysis.error_title')}
          </h2>

          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.98rem',
              color: '#D8C7A3',
              lineHeight: 1.55,
              marginBottom: '2rem',
            }}
          >
            {t('analysis.error_desc')}
          </p>

          <button
            type="button"
            id="btn-analysis-interrupted-return"
            onClick={handleReturn}
            style={{
              minHeight: '48px',
              padding: '0.75rem 1.75rem',
              background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
              border: 'none',
              borderRadius: '10px',
              color: '#140C07',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 4px 14px rgba(201, 154, 60, 0.35)',
            }}
          >
            <ArrowLeft size={18} aria-hidden="true" />
            <span>{t('analysis.return_to_check')}</span>
          </button>
        </div>
      </div>
    );
  }

  // ─── STATE C: Real Analysis Transition (Quiet Examination Chamber) ────────
  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        minHeight: 'calc(100vh - 65px)',
        backgroundColor: '#160E08',
        backgroundImage: `
          radial-gradient(circle at 50% 38%, rgba(201, 154, 60, 0.14) 0%, rgba(242, 193, 78, 0.04) 40%, rgba(22, 14, 8, 0) 70%),
          radial-gradient(circle at 80% 80%, rgba(58, 36, 18, 0.3) 0%, transparent 60%)
        `,
        padding: '1.5rem 1.5rem 4rem',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative Pipal Silhouette in Background */}
      <svg
        width="460"
        height="460"
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: '42%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          pointerEvents: 'none',
          opacity: 0.06,
          zIndex: 0,
        }}
      >
        <path
          d="M 50 86
             C 42 78, 20 62, 18 42
             C 16 26, 32 14, 46 12
             C 49 11.5, 50 8, 50 5
             C 50 8, 51 11.5, 54 12
             C 68 14, 84 26, 82 42
             C 80 62, 58 78, 50 86 Z"
          stroke="#C99A3C"
          strokeWidth="1.2"
        />
        <path d="M 50 84 Q 50 45, 50 6" stroke="#C99A3C" strokeWidth="1" />
      </svg>

      {/* Screen Reader Live Region */}
      <div
        role="status"
        aria-live="polite"
        style={{
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: 0,
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          border: 0,
        }}
      >
        {t('analysis.title')} — {t('analysis.supporting_text')}
      </div>

      {/* Top Header Row: Return Button + Crop Context */}
      <div
        style={{
          width: '100%',
          maxWidth: '680px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.75rem',
          zIndex: 1,
        }}
      >
        {/* Return affordance */}
        <button
          type="button"
          id="btn-analysis-cancel"
          onClick={handleReturn}
          style={{
            minHeight: '48px',
            minWidth: '48px',
            background: 'none',
            border: 'none',
            color: '#D8C7A3',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: '0.88rem',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.5rem 0.25rem',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#F4EAD3')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#D8C7A3')}
          aria-label={t('analysis.cancel')}
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span>{t('analysis.cancel')}</span>
        </button>

        {/* Crop Context Badge */}
        {diagnosisPayload?.crop && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              background: 'rgba(201, 154, 60, 0.12)',
              border: '1px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '9999px',
              padding: '0.3rem 0.8rem 0.3rem 0.35rem',
              color: '#F4EAD3',
            }}
          >
            <CropIdentity
              crop={diagnosisPayload.crop}
              size={26}
              fontSize="0.82rem"
              style={{ color: '#F4EAD3', fontWeight: 600, letterSpacing: '0.04em' }}
            />
          </div>
        )}
      </div>

      {/* Central Visual Hero: The Uploaded Leaf in Quiet Examination Frame */}
      <div
        ref={leafFrameRef}
        style={{
          width: '100%',
          maxWidth: '480px',
          height: 'clamp(260px, 48vw, 380px)',
          background: '#0B0603',
          border: '1.5px solid rgba(201, 154, 60, 0.42)',
          borderRadius: '24px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 24px 60px rgba(0, 0, 0, 0.7), 0 0 35px rgba(201, 154, 60, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1,
        }}
      >
        {/* Original leaf image - unaltered hero */}
        <img
          src={diagnosisPayload.imageObjectUrl}
          alt={t('check.preview_alt')}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            display: 'block',
          }}
        />

        {/* Subtle Warm Sunlight Pass (Sweeps across leaf once) */}
        <div
          ref={lightPassRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '65%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent 0%, rgba(242, 193, 78, 0.22) 50%, transparent 100%)',
            transform: 'skewX(-20deg)',
            pointerEvents: 'none',
            zIndex: 2,
          }}
        />
      </div>

      {/* Typography & Quiet Examination Status */}
      <div
        style={{
          marginTop: '2rem',
          textAlign: 'center',
          maxWidth: '560px',
          padding: '0 1rem',
          zIndex: 1,
        }}
      >
        {/* Primary Copy: “Looking closely at your leaf…” */}
        <h1
          ref={titleRef}
          style={{
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: 'clamp(1.5rem, 3.2vw, 2.2rem)',
            fontWeight: '600',
            color: '#F4EAD3',
            lineHeight: 1.25,
            letterSpacing: isDevanagari ? 0 : '-0.015em',
          }}
        >
          {t('analysis.title')}
        </h1>

        {/* Minimal Supporting Text */}
        <p
          ref={subtitleRef}
          style={{
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: 'clamp(0.95rem, 1.6vw, 1.08rem)',
            color: '#D8C7A3',
            marginTop: '0.65rem',
            lineHeight: 1.55,
          }}
        >
          {t('analysis.supporting_text')}
        </p>

        {/* Quiet Observation Pulse Indicator */}
        <div
          ref={indicatorRef}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.6rem',
            marginTop: '1.35rem',
            padding: '0.4rem 1rem',
            background: 'rgba(58, 36, 18, 0.5)',
            border: '1px solid rgba(201, 154, 60, 0.25)',
            borderRadius: '9999px',
          }}
        >
          <span
            className="drishya-pulse-dot"
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#F2C14E',
              boxShadow: '0 0 10px #F2C14E',
              display: 'inline-block',
            }}
          />
          <span
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.84rem',
              color: '#F4EAD3',
              letterSpacing: '0.02em',
            }}
          >
            {t('analysis.examining')}
          </span>
        </div>
      </div>

      {/* Gentle Pulsing Animation for Indicator Dot */}
      <style>{`
        @keyframes drishyaGlowPulse {
          0%, 100% {
            opacity: 0.65;
            transform: scale(0.95);
            box-shadow: 0 0 6px #F2C14E;
          }
          50% {
            opacity: 1;
            transform: scale(1.15);
            box-shadow: 0 0 14px #F2C14E;
          }
        }
        .drishya-pulse-dot {
          animation: drishyaGlowPulse 2s ease-in-out infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .drishya-pulse-dot {
            animation: none !important;
          }
        }
      `}</style>
    </div>
  );
}
