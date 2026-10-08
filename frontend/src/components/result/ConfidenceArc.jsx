/**
 * ConfidenceArc.jsx - Botanical Organic Confidence Arc Visualization
 *
 * Implements:
 * - Handcrafted botanical partial-ring SVG arc tracing around a warm illuminated core
 * - Displays backend-authoritative confidence (calibrated when active, raw labeled otherwise)
 * - True percentage conversion: Math.round(confidence * 100)
 * - GSAP-driven strokeDashoffset draw animation + live percentage counter
 * - Honest labeling: "Model confidence" + "Confidence reflects the model's prediction, not field confirmation"
 * - Rejection / Uncertainty visual treatment for low-confidence or rejected predictions
 * - Full prefers-reduced-motion support (instant final state)
 */

import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function ConfidenceArc({
  calibratedConfidence = null,
  rawConfidence = 0.0,
  isCalibrationActive = false,
  isRejected = false,
  rejectionThreshold = 0.65,
}) {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  // Determine active confidence value and whether it is calibrated
  const isUsingCalibrated = isCalibrationActive && typeof calibratedConfidence === 'number';
  const confidenceValue = isUsingCalibrated ? calibratedConfidence : rawConfidence;
  const targetPercent = Math.max(0, Math.min(100, Math.round(confidenceValue * 100)));

  // Component state and DOM refs
  const [displayedPercent, setDisplayedPercent] = useState(targetPercent);
  const containerRef = useRef(null);
  const pathRef = useRef(null);
  const counterObjRef = useRef({ val: 0 });

  // Geometry: SVG 200x200 viewBox, center at (100, 100), radius 72
  // We use a 270-degree organic circular arc starting from bottom-left (135 deg) to bottom-right (405 deg = 45 deg)
  const radius = 72;
  const circumference = 2 * Math.PI * radius;
  // Arc angle: 260 degrees of the full 360 circle
  const arcLength = circumference * (260 / 360);
  const startOffset = arcLength;
  const targetOffset = arcLength * (1 - targetPercent / 100);

  useEffect(() => {
    if (!pathRef.current) return;

    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced) {
      gsap.set(pathRef.current, { strokeDashoffset: targetOffset });
      setDisplayedPercent(targetPercent);
      return;
    }

    // Set initial values
    gsap.set(pathRef.current, {
      strokeDasharray: `${arcLength} ${circumference}`,
      strokeDashoffset: startOffset,
    });
    counterObjRef.current.val = 0;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

      // Trace arc with natural botanical light line
      tl.to(
        pathRef.current,
        {
          strokeDashoffset: targetOffset,
          duration: 0.8,
        },
        0.1
      );

      // Animate percentage number counter
      tl.to(
        counterObjRef.current,
        {
          val: targetPercent,
          duration: 0.8,
          roundProps: 'val',
          onUpdate: () => {
            setDisplayedPercent(Math.round(counterObjRef.current.val));
          },
        },
        0.1
      );
    }, containerRef);

    return () => ctx.revert();
  }, [targetPercent, targetOffset, arcLength, circumference, startOffset]);

  // Color palette based on status
  // For normal high confidence: warm antique gold into lamp glow
  // For rejected/uncertain: terracotta/amber alert
  const primaryStroke = isRejected ? '#A24A2B' : '#C99A3C';
  const glowStroke = isRejected ? 'rgba(162, 74, 43, 0.25)' : 'rgba(242, 193, 78, 0.3)';
  const trackStroke = isRejected ? 'rgba(162, 74, 43, 0.15)' : 'rgba(201, 154, 60, 0.18)';
  const badgeBg = isRejected
    ? 'rgba(162, 74, 43, 0.12)'
    : isUsingCalibrated
    ? 'rgba(94, 107, 56, 0.12)'
    : 'rgba(201, 154, 60, 0.12)';
  const badgeBorder = isRejected
    ? 'rgba(162, 74, 43, 0.35)'
    : isUsingCalibrated
    ? 'rgba(94, 107, 56, 0.35)'
    : 'rgba(201, 154, 60, 0.35)';
  const badgeColor = isRejected ? '#8F3819' : isUsingCalibrated ? '#3B5E2B' : '#8A5A2B';

  return (
    <div
      ref={containerRef}
      className="drishya-confidence-card"
      style={{
        background: '#FAF5EB',
        border: '1.5px solid rgba(201, 154, 60, 0.32)',
        borderRadius: '22px',
        padding: '1.6rem 1.4rem',
        boxShadow: '0 8px 28px rgba(28, 17, 10, 0.04)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        width: '100%',
      }}
      aria-label={t('result.confidence_aria', { percent: targetPercent })}
    >
      {/* Top Header Label */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '0.4rem',
          width: '100%',
          justifyContent: 'center',
        }}
      >
        <span
          style={{
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '1.05rem',
            fontWeight: '700',
            color: '#1C110A',
            letterSpacing: isDevanagari ? '0' : '-0.01em',
          }}
        >
          {isUsingCalibrated
            ? t('result.model_confidence')
            : t('result.raw_model_confidence')}
        </span>
      </div>

      {/* SVG Botanical Arc */}
      <div
        style={{
          position: 'relative',
          width: '180px',
          height: '160px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg
          viewBox="0 0 200 200"
          style={{
            width: '100%',
            height: '100%',
            overflow: 'visible',
            transform: 'rotate(140deg)', // Centers the 260-degree opening at the bottom
          }}
          aria-hidden="true"
        >
          {/* Subtle Ambient Leaf Glow */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={glowStroke}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={`${arcLength} ${circumference}`}
          />

          {/* Background Track Arc */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={trackStroke}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${arcLength} ${circumference}`}
          />

          {/* Active Animated Botanical Light Line */}
          <circle
            ref={pathRef}
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={primaryStroke}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={startOffset}
            style={{
              transition: 'stroke 0.3s ease',
            }}
          />

          {/* Subtle Leaf Vein Accent Node at start */}
          <circle
            cx="100"
            cy="28"
            r="3"
            fill="#F2C14E"
            opacity="0.8"
          />
        </svg>

        {/* Center Percentage & Status Readout */}
        <div
          style={{
            position: 'absolute',
            top: '46%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '2.5rem',
              fontWeight: '700',
              lineHeight: 1,
              color: isRejected ? '#8F3819' : '#1C110A',
              letterSpacing: '-0.02em',
            }}
          >
            {displayedPercent}
            <span
              style={{
                fontSize: '1.25rem',
                fontWeight: '500',
                color: isRejected ? '#A24A2B' : '#8A5A2B',
                marginLeft: '1px',
              }}
            >
              %
            </span>
          </div>

          {/* Small Indicator Badge */}
          <div
            style={{
              marginTop: '0.35rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.25rem',
              padding: '0.15rem 0.55rem',
              borderRadius: '9999px',
              background: badgeBg,
              border: `1px solid ${badgeBorder}`,
              color: badgeColor,
              fontSize: '0.72rem',
              fontWeight: '700',
              letterSpacing: '0.02em',
              textTransform: 'uppercase',
            }}
          >
            {isRejected ? (
              <>
                <AlertTriangle size={11} aria-hidden="true" />
                <span>{t('result.state_unsure')}</span>
              </>
            ) : isUsingCalibrated ? (
              <>
                <ShieldCheck size={11} aria-hidden="true" />
                <span>{t('result.calibrated_badge')}</span>
              </>
            ) : (
              <span>{t('result.uncalibrated_badge')}</span>
            )}
          </div>
        </div>
      </div>

      {/* Honest Scientific Disclaimer */}
      <p
        style={{
          fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          fontSize: '0.82rem',
          color: '#6F5F52',
          textAlign: 'center',
          lineHeight: 1.45,
          marginTop: '0.5rem',
          maxWidth: '280px',
        }}
      >
        {t('result.confidence_honesty_note')}
      </p>

      {/* Rejection threshold explanation if uncertain */}
      {isRejected && (
        <div
          style={{
            marginTop: '0.65rem',
            padding: '0.5rem 0.75rem',
            background: 'rgba(162, 74, 43, 0.08)',
            border: '1px solid rgba(162, 74, 43, 0.25)',
            borderRadius: '8px',
            fontSize: '0.78rem',
            color: '#7A2E12',
            textAlign: 'center',
            lineHeight: 1.4,
          }}
        >
          <span>
            {t('result.explanation_uncertain_desc')}
          </span>
        </div>
      )}
    </div>
  );
}
