/**
 * PredictionRibbons.jsx - Botanical Stacked Flowing Ribbons Breakdown
 *
 * Implements:
 * - Displays top 3–5 backend candidate predictions with real probabilities
 * - Prioritizes calibrated candidate probabilities where available (falls back to raw)
 * - Handcrafted botanical flowing ribbons with proportional pill segments
 * - GSAP-animated width transitions (0 -> actual percentage)
 * - Highlights top-1 predicted condition with warm antique gold/terracotta accent
 * - Uses localized condition names via getConditionDisplayName
 * - Full prefers-reduced-motion support (instant final widths)
 */

import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { useLanguage } from '../../context/LanguageContext';

export default function PredictionRibbons({
  crop = 'turmeric',
  predictedClass = '',
  candidates = [],
  isCalibrationActive = false,
}) {
  const { t, language, getConditionDisplayName } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';
  const containerRef = useRef(null);

  // Take top 3 to 5 candidate classes
  // Ensure the list is sorted by probability descending
  const sortedCandidates = [...(candidates || [])]
    .map((c) => {
      // Prioritize calibrated_probability when calibration is active
      const probValue =
        isCalibrationActive && typeof c.calibrated_probability === 'number'
          ? c.calibrated_probability
          : typeof c.probability === 'number'
          ? c.probability
          : typeof c.raw_probability === 'number'
          ? c.raw_probability
          : 0;

      return {
        ...c,
        activeProb: probValue,
        percent: Math.max(0, Math.min(100, Math.round(probValue * 100))),
      };
    })
    .sort((a, b) => b.activeProb - a.activeProb)
    .slice(0, 4); // Top 4 candidate conditions

  useEffect(() => {
    if (!containerRef.current) return;

    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const ribbonFills = containerRef.current.querySelectorAll('.drishya-ribbon-fill');

    if (prefersReduced) {
      ribbonFills.forEach((el) => {
        const target = el.getAttribute('data-target-width') || '0%';
        gsap.set(el, { width: target });
      });
      return;
    }

    const ctx = gsap.context(() => {
      // Start all fills at 0%
      gsap.set(ribbonFills, { width: '0%' });

      // Animate flowing ribbon fills sequentially
      gsap.to(ribbonFills, {
        width: (i, target) => target.getAttribute('data-target-width') || '0%',
        duration: 0.65,
        stagger: 0.08,
        ease: 'power2.out',
        delay: 0.15,
      });
    }, containerRef);

    return () => ctx.revert();
  }, [sortedCandidates]);

  if (sortedCandidates.length === 0) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      className="drishya-prediction-breakdown"
      style={{
        background: '#FAF5EB',
        border: '1.5px solid rgba(201, 154, 60, 0.28)',
        borderRadius: '22px',
        padding: '1.6rem 1.75rem',
        boxShadow: '0 8px 28px rgba(28, 17, 10, 0.04)',
      }}
    >
      {/* Section Header */}
      <div style={{ marginBottom: '1.1rem' }}>
        <h3
          style={{
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '1.15rem',
            color: '#1C110A',
            fontWeight: '700',
            marginBottom: '0.25rem',
            letterSpacing: isDevanagari ? '0' : '-0.01em',
          }}
        >
          {t('result.prediction_breakdown')}
        </h3>
        <p
          style={{
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: '0.86rem',
            color: '#6F5F52',
            lineHeight: 1.4,
          }}
        >
          {t('result.prediction_breakdown_desc')}
        </p>
      </div>

      {/* Stacked Flowing Ribbons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {sortedCandidates.map((c, idx) => {
          const isTopPredicted =
            idx === 0 ||
            c.class_name.toLowerCase().trim() ===
              predictedClass.toLowerCase().trim();

          const displayName = getConditionDisplayName(crop, c.class_name);
          const percentVal = c.percent;

          // Theme for top vs subsequent ribbons
          const ribbonTrackBg = isTopPredicted
            ? 'rgba(201, 154, 60, 0.16)'
            : 'rgba(111, 95, 82, 0.08)';

          const ribbonGradient = isTopPredicted
            ? 'linear-gradient(90deg, #F2C14E 0%, #C99A3C 70%, #8A5A2B 100%)'
            : 'linear-gradient(90deg, #D8C7A3 0%, #A4937A 100%)';

          const textColor = isTopPredicted ? '#1C110A' : '#4A3728';
          const badgeBg = isTopPredicted ? 'rgba(201, 154, 60, 0.22)' : 'rgba(111, 95, 82, 0.12)';
          const badgeColor = isTopPredicted ? '#3A2412' : '#6F5F52';

          return (
            <div
              key={c.class_name || idx}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.35rem',
              }}
              aria-label={t('result.breakdown_aria', {
                condition: displayName,
                percent: percentVal,
              })}
            >
              {/* Row Header: Name + Percentage */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '0.9rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <span
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      background: isTopPredicted ? '#C99A3C' : '#8A7768',
                      display: 'inline-block',
                    }}
                  />
                  <span
                    style={{
                      fontWeight: isTopPredicted ? '700' : '500',
                      color: textColor,
                    }}
                  >
                    {displayName}
                  </span>
                </div>

                <span
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontWeight: isTopPredicted ? '700' : '600',
                    fontSize: '0.85rem',
                    color: badgeColor,
                    background: badgeBg,
                    padding: '0.12rem 0.5rem',
                    borderRadius: '9999px',
                    letterSpacing: '0.01em',
                  }}
                >
                  {percentVal}%
                </span>
              </div>

              {/* Botanical Ribbon Bar */}
              <div
                style={{
                  width: '100%',
                  height: '9px',
                  background: ribbonTrackBg,
                  borderRadius: '9999px',
                  overflow: 'hidden',
                  position: 'relative',
                  border: isTopPredicted
                    ? '1px solid rgba(201, 154, 60, 0.28)'
                    : '1px solid rgba(111, 95, 82, 0.12)',
                }}
              >
                <div
                  className="drishya-ribbon-fill"
                  data-target-width={`${Math.max(percentVal, 2)}%`}
                  style={{
                    width: '0%',
                    height: '100%',
                    background: ribbonGradient,
                    borderRadius: '9999px',
                    boxShadow: isTopPredicted ? '0 1px 4px rgba(201, 154, 60, 0.35)' : 'none',
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
