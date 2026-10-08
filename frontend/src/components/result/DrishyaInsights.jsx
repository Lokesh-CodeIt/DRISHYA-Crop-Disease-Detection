/**
 * DrishyaInsights.jsx - Signature Botanical DRISHYA Insights & Grad-CAM Experience
 *
 * Implements:
 * - Signature product feature section: "DRISHYA Insights"
 * - Polished interactive toggle: "Original Leaf" ↔ "Model Attention"
 * - GSAP crossfade transition between authentic original leaf photo and authoritative backend Grad-CAM overlay
 * - Real attention-region thumbnails consumed directly from backend `region.crop_base64`
 * - Honest, scientific labeling: "Higher-attention area", "Attention region 01" (never "lesion/defect")
 * - Limitations stated clearly: "Model attention is not proof of causation"
 * - Interactive region focus: clicking any thumbnail expands into focused botanical inspection drawer/card
 *   displaying real backend attention score and exact pixel coordinates
 * - Graceful localized fallback when explanation is missing or explanation_available === false
 * - Full prefers-reduced-motion support
 */

import React, { useState, useRef, useEffect } from 'react';
import gsap from 'gsap';
import { Eye, EyeOff, Layers, ZoomIn, X, Info } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function DrishyaInsights({
  imageObjectUrl = '',
  explanation = null,
}) {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  // State: 'original' | 'attention'
  const [viewMode, setViewMode] = useState('attention');
  // Selected attention region for interactive inspection (or null)
  const [selectedRegion, setSelectedRegion] = useState(null);

  // Animation refs
  const containerRef = useRef(null);
  const imageFrameRef = useRef(null);
  const originalImgRef = useRef(null);
  const overlayImgRef = useRef(null);
  const detailModalRef = useRef(null);

  // Check if real explanation is available
  const hasValidExplanation = Boolean(
    explanation &&
    explanation.explanation_available !== false &&
    explanation.overlay_base64
  );

  const regions = (hasValidExplanation && Array.isArray(explanation.regions))
    ? explanation.regions
    : [];

  // GSAP crossfade when toggling between Original and Attention overlay
  useEffect(() => {
    if (!hasValidExplanation || !originalImgRef.current || !overlayImgRef.current) return;

    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced) {
      if (viewMode === 'original') {
        gsap.set(overlayImgRef.current, { opacity: 0, visibility: 'hidden' });
        gsap.set(originalImgRef.current, { opacity: 1, visibility: 'visible' });
      } else {
        gsap.set(overlayImgRef.current, { opacity: 1, visibility: 'visible' });
        gsap.set(originalImgRef.current, { opacity: 0.18, visibility: 'visible' });
      }
      return;
    }

    const ctx = gsap.context(() => {
      if (viewMode === 'original') {
        gsap.to(overlayImgRef.current, {
          opacity: 0,
          duration: 0.35,
          ease: 'power2.inOut',
          onComplete: () => {
            if (overlayImgRef.current) overlayImgRef.current.style.visibility = 'hidden';
          },
        });
        gsap.to(originalImgRef.current, {
          opacity: 1,
          duration: 0.35,
          ease: 'power2.inOut',
          onStart: () => {
            if (originalImgRef.current) originalImgRef.current.style.visibility = 'visible';
          },
        });
      } else {
        if (overlayImgRef.current) overlayImgRef.current.style.visibility = 'visible';
        gsap.to(overlayImgRef.current, {
          opacity: 1,
          duration: 0.4,
          ease: 'power2.inOut',
        });
        gsap.to(originalImgRef.current, {
          opacity: 0.18, // subtle background context under overlay
          duration: 0.4,
          ease: 'power2.inOut',
        });
      }
    }, imageFrameRef);

    return () => ctx.revert();
  }, [viewMode, hasValidExplanation]);

  // GSAP animation for region detail card expansion
  useEffect(() => {
    if (!selectedRegion || !detailModalRef.current) return;

    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced) {
      gsap.set(detailModalRef.current, { opacity: 1, scale: 1 });
      return;
    }

    const ctx = gsap.context(() => {
      gsap.fromTo(
        detailModalRef.current,
        { opacity: 0, y: 12, scale: 0.96 },
        { opacity: 1, y: 0, scale: 1, duration: 0.32, ease: 'back.out(1.4)' }
      );
    }, detailModalRef);

    return () => ctx.revert();
  }, [selectedRegion]);

  return (
    <div
      ref={containerRef}
      className="drishya-insights-card"
      style={{
        background: '#FAF5EB',
        border: '1.5px solid rgba(201, 154, 60, 0.35)',
        borderRadius: '24px',
        padding: '2rem',
        boxShadow: '0 12px 36px rgba(28, 17, 10, 0.05)',
        marginBottom: '2rem',
        position: 'relative',
      }}
    >
      {/* ─── Header: DRISHYA Insights ────────────────────────────────────── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '1.25rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={20} color="#8A5A2B" aria-hidden="true" />
            <h2
              style={{
                fontFamily: isDevanagari
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: '1.35rem',
                color: '#1C110A',
                fontWeight: '700',
                letterSpacing: isDevanagari ? '0' : '-0.015em',
              }}
            >
              {t('result.drishya_insights')}
            </h2>
          </div>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.88rem',
              color: '#6F5F52',
              marginTop: '0.2rem',
            }}
          >
            {t('result.drishya_insights_subtitle')}
          </p>
        </div>

        {/* Polished Toggle Switch: Original ↔ Model Attention */}
        {hasValidExplanation && (
          <div
            role="tablist"
            aria-label={t('result.drishya_insights')}
            style={{
              display: 'inline-flex',
              background: '#F4EAD3',
              padding: '0.25rem',
              borderRadius: '9999px',
              border: '1px solid rgba(201, 154, 60, 0.35)',
            }}
          >
            <button
              type="button"
              role="tab"
              aria-selected={viewMode === 'original'}
              id="btn-toggle-original-view"
              onClick={() => setViewMode('original')}
              style={{
                minHeight: '38px',
                padding: '0.35rem 0.95rem',
                borderRadius: '9999px',
                border: 'none',
                background: viewMode === 'original' ? '#FAF5EB' : 'transparent',
                color: viewMode === 'original' ? '#1C110A' : '#6F5F52',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.84rem',
                fontWeight: viewMode === 'original' ? '700' : '500',
                cursor: 'pointer',
                boxShadow:
                  viewMode === 'original'
                    ? '0 2px 8px rgba(0, 0, 0, 0.08)'
                    : 'none',
                transition: 'all 0.15s ease',
              }}
            >
              {t('result.toggle_original')}
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={viewMode === 'attention'}
              id="btn-toggle-attention-view"
              onClick={() => setViewMode('attention')}
              style={{
                minHeight: '38px',
                padding: '0.35rem 0.95rem',
                borderRadius: '9999px',
                border: 'none',
                background: viewMode === 'attention' ? '#FAF5EB' : 'transparent',
                color: viewMode === 'attention' ? '#1C110A' : '#6F5F52',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.84rem',
                fontWeight: viewMode === 'attention' ? '700' : '500',
                cursor: 'pointer',
                boxShadow:
                  viewMode === 'attention'
                    ? '0 2px 8px rgba(0, 0, 0, 0.08)'
                    : 'none',
                transition: 'all 0.15s ease',
              }}
            >
              {t('result.toggle_attention')}
            </button>
          </div>
        )}
      </div>

      {/* ─── Main Viewport: Leaf Photo / Grad-CAM Overlay ──────────────────── */}
      {hasValidExplanation ? (
        <div>
          <div
            ref={imageFrameRef}
            style={{
              width: '100%',
              maxWidth: '680px',
              aspectRatio: '4 / 3',
              margin: '0 auto 1.5rem',
              borderRadius: '16px',
              overflow: 'hidden',
              background: '#0D0704',
              border: '1.5px solid rgba(201, 154, 60, 0.35)',
              position: 'relative',
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.14)',
            }}
          >
            {/* Original Image Layer */}
            <img
              ref={originalImgRef}
              src={imageObjectUrl}
              alt={t('result.toggle_original')}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                display: 'block',
              }}
            />

            {/* Grad-CAM Authoritative Heatmap Overlay Layer */}
            <img
              ref={overlayImgRef}
              src={`data:image/png;base64,${explanation.overlay_base64}`}
              alt={t('result.toggle_attention')}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                display: 'block',
              }}
            />

            {/* Current View Badge */}
            <div
              style={{
                position: 'absolute',
                bottom: '0.85rem',
                right: '0.85rem',
                background: 'rgba(28, 17, 10, 0.85)',
                backdropFilter: 'blur(4px)',
                border: '1px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                padding: '0.25rem 0.75rem',
                color: '#F4EAD3',
                fontSize: '0.78rem',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}
            >
              <Eye size={13} color="#F2C14E" aria-hidden="true" />
              <span>
                {viewMode === 'attention'
                  ? t('result.toggle_attention')
                  : t('result.toggle_original')}
              </span>
            </div>
          </div>

          {/* ─── Attention Regions Subsection ────────────────────────────── */}
          {regions.length > 0 && (
            <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid rgba(201, 154, 60, 0.2)' }}>
              <div style={{ marginBottom: '0.85rem' }}>
                <h3
                  style={{
                    fontFamily: isDevanagari
                      ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                      : 'var(--font-display, "Fraunces", Georgia, serif)',
                    fontSize: '1.1rem',
                    color: '#1C110A',
                    fontWeight: '700',
                    marginBottom: '0.2rem',
                  }}
                >
                  {t('result.attention_regions_title')}
                </h3>
                <p
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.86rem',
                    color: '#6F5F52',
                  }}
                >
                  {t('result.attention_regions_desc')}
                </p>
              </div>

              {/* Thumbnails Row: Direct backend base64 crops */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                  gap: '1rem',
                  marginBottom: '1rem',
                }}
              >
                {regions.map((region) => {
                  const isSelected = selectedRegion?.region_id === region.region_id;
                  const scorePercent = Math.round((region.attention_score || 0) * 100);

                  return (
                    <button
                      key={region.region_id}
                      type="button"
                      id={`btn-insight-region-${region.region_id}`}
                      onClick={() =>
                        setSelectedRegion(isSelected ? null : region)
                      }
                      style={{
                        background: isSelected ? '#F4EAD3' : '#FAF5EB',
                        border: isSelected
                          ? '2px solid #C99A3C'
                          : '1px solid rgba(201, 154, 60, 0.35)',
                        borderRadius: '14px',
                        padding: '0.65rem',
                        textAlign: 'left',
                        cursor: 'pointer',
                        transition: 'transform 0.15s ease, border-color 0.15s ease',
                        boxShadow: isSelected
                          ? '0 6px 16px rgba(201, 154, 60, 0.25)'
                          : '0 2px 8px rgba(0, 0, 0, 0.04)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.45rem',
                      }}
                      aria-pressed={isSelected}
                    >
                      {/* Authentic thumbnail directly from backend */}
                      <div
                        style={{
                          width: '100%',
                          aspectRatio: '1 / 1',
                          borderRadius: '8px',
                          overflow: 'hidden',
                          background: '#0D0704',
                          position: 'relative',
                        }}
                      >
                        <img
                          src={`data:image/jpeg;base64,${region.crop_base64}`}
                          alt={t('result.attention_region_label', { id: region.region_id })}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            display: 'block',
                          }}
                        />
                        <div
                          style={{
                            position: 'absolute',
                            bottom: '4px',
                            right: '4px',
                            background: 'rgba(28, 17, 10, 0.8)',
                            borderRadius: '4px',
                            padding: '2px 4px',
                            color: '#F4EAD3',
                            fontSize: '0.68rem',
                            fontWeight: '600',
                          }}
                        >
                          <ZoomIn size={10} aria-hidden="true" />
                        </div>
                      </div>

                      {/* Region Metadata */}
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span
                          style={{
                            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                            fontSize: '0.82rem',
                            fontWeight: '700',
                            color: '#1C110A',
                          }}
                        >
                          {t('result.attention_region_label', { id: region.region_id })}
                        </span>
                        <span
                          style={{
                            fontSize: '0.74rem',
                            color: '#8A5A2B',
                            fontWeight: '600',
                          }}
                        >
                          {t('result.attention_score_label', { score: scorePercent })}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Interactive Focused Inspection Drawer */}
              {selectedRegion && (
                <div
                  ref={detailModalRef}
                  style={{
                    background: '#F4EAD3',
                    border: '1.5px solid rgba(201, 154, 60, 0.45)',
                    borderRadius: '16px',
                    padding: '1.25rem',
                    marginBottom: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '1.25rem',
                    boxShadow: '0 8px 24px rgba(28, 17, 10, 0.06)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div
                      style={{
                        width: '90px',
                        height: '90px',
                        borderRadius: '10px',
                        overflow: 'hidden',
                        background: '#0D0704',
                        border: '1.5px solid #C99A3C',
                        flexShrink: 0,
                      }}
                    >
                      <img
                        src={`data:image/jpeg;base64,${selectedRegion.crop_base64}`}
                        alt={t('result.attention_region_label', { id: selectedRegion.region_id })}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          display: 'block',
                        }}
                      />
                    </div>

                    <div>
                      <h4
                        style={{
                          fontFamily: isDevanagari
                            ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                            : 'var(--font-display, "Fraunces", Georgia, serif)',
                          fontSize: '1.05rem',
                          color: '#1C110A',
                          fontWeight: '700',
                          marginBottom: '0.2rem',
                        }}
                      >
                        {t('result.attention_region_label', { id: selectedRegion.region_id })}
                      </h4>
                      <p
                        style={{
                          fontSize: '0.85rem',
                          color: '#3A2412',
                          fontWeight: '600',
                          marginBottom: '0.25rem',
                        }}
                      >
                        {t('result.attention_score_label', {
                          score: Math.round((selectedRegion.attention_score || 0) * 100),
                        })}
                      </p>
                      <p
                        style={{
                          fontSize: '0.78rem',
                          color: '#6F5F52',
                          fontFamily: 'monospace',
                        }}
                      >
                        {t('result.region_coordinates', {
                          x: selectedRegion.x,
                          y: selectedRegion.y,
                          w: selectedRegion.width,
                          h: selectedRegion.height,
                        })}
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => setSelectedRegion(null)}
                    style={{
                      minHeight: '40px',
                      padding: '0.4rem 0.85rem',
                      background: '#FAF5EB',
                      border: '1px solid rgba(201, 154, 60, 0.4)',
                      borderRadius: '8px',
                      color: '#3A2412',
                      fontSize: '0.82rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                    }}
                    aria-label={t('result.close_detail')}
                  >
                    <X size={15} aria-hidden="true" />
                    <span>{t('result.close_detail')}</span>
                  </button>
                </div>
              )}

              {/* Smaller Scientific Limitation Note */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: '#8A7768',
                  fontSize: '0.82rem',
                  fontStyle: 'italic',
                }}
              >
                <Info size={14} color="#8A5A2B" aria-hidden="true" style={{ flexShrink: 0 }} />
                <span>{t('result.attention_regions_disclaimer')}</span>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ─── Graceful No Explanation Fallback ─────────────────────────────── */
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '1.25rem 1.5rem',
            background: 'rgba(201, 154, 60, 0.08)',
            border: '1px solid rgba(201, 154, 60, 0.25)',
            borderRadius: '14px',
            color: '#6F5F52',
            fontSize: '0.92rem',
            lineHeight: 1.5,
          }}
        >
          <EyeOff size={20} color="#8A5A2B" aria-hidden="true" style={{ flexShrink: 0 }} />
          <span>{t('result.evidence_unavailable')}</span>
        </div>
      )}
    </div>
  );
}
