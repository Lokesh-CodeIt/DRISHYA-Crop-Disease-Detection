/**
 * ConditionKnowledge.jsx - DRISHYA Step D Condition Knowledge & Safe Advisory
 *
 * Renders deterministic, source-backed pathology intelligence:
 * 1. Condition Profile Header with status badge (Verified Advisory / General Guidance / Expert Escalation)
 * 2. Visual Signs to Inspect in Field (field verification guide)
 * 3. What You Can Do Now (safe, cultural, non-chemical immediate actions)
 * 4. Prevention & Continuous Monitoring (long-term agronomic practices)
 * 5. When to Consult Agronomists / KVK (clear threshold for expert intervention)
 * 6. Scientific Traceability & Institutional Sources (traceable references + safe disclaimer)
 *
 * Adheres strictly to:
 * - DRISHYA botanical daylight parchment aesthetic (#FAF5EB, #1C110A, #C99A3C, #3B5E2B, #A24A2B)
 * - Safe rejection semantics: uncertain predictions never claim confirmed disease
 * - Trilingual localization (English, Hindi, Marathi)
 * - Zero hallucination / no dynamically generated synthetic chemical doses
 */

import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  Eye,
  ShieldCheck,
  CalendarCheck,
  PhoneCall,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Award,
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export default function ConditionKnowledge({
  knowledge = null,
  isRejected = false,
  crop = 'turmeric',
  predictedClass = '',
}) {
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';
  const [sourcesOpen, setSourcesOpen] = useState(false);

  // If knowledge is not available, render safe institutional fallback
  if (!knowledge || !knowledge.knowledge_available) {
    return (
      <div
        className="drishya-knowledge-card drishya-knowledge-fallback"
        style={{
          background: '#FAF5EB',
          border: '1.5px solid rgba(201, 154, 60, 0.28)',
          borderRadius: '20px',
          padding: '1.75rem',
          marginBottom: '1.75rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'rgba(162, 74, 43, 0.1)',
              border: '1px solid rgba(162, 74, 43, 0.3)',
              borderRadius: '9999px',
              padding: '0.35rem 0.85rem',
              color: '#8A2C10',
              fontSize: '0.82rem',
              fontWeight: '700',
            }}
          >
            <AlertTriangle size={14} aria-hidden="true" />
            <span>{t('knowledge.status_uncertain')}</span>
          </div>
        </div>

        <h2
          style={{
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '1.35rem',
            color: '#1C110A',
            fontWeight: '700',
            marginBottom: '0.5rem',
          }}
        >
          {t('knowledge.fallback_title')}
        </h2>

        <p
          style={{
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: '0.96rem',
            color: '#4A3728',
            lineHeight: 1.6,
            marginBottom: '1rem',
          }}
        >
          {t('knowledge.fallback_desc')}
        </p>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.85rem 1rem',
            background: 'rgba(201, 154, 60, 0.08)',
            border: '1px solid rgba(201, 154, 60, 0.25)',
            borderRadius: '12px',
            color: '#5C442A',
            fontSize: '0.88rem',
          }}
        >
          <PhoneCall size={16} color="#8A5A2B" aria-hidden="true" />
          <span>Kisan Call Center: <strong>1800-180-1551</strong> (Toll-Free, Pan-India)</span>
        </div>
      </div>
    );
  }

  // Determine badge styling based on advisory status and rejection state
  const status = isRejected
    ? 'EXPERT_CONFIRMATION_RECOMMENDED'
    : knowledge.advisory_status || 'SUPPORTED';

  let badgeBg = 'rgba(59, 94, 43, 0.1)';
  let badgeBorder = 'rgba(59, 94, 43, 0.3)';
  let badgeColor = '#2D4B1E';
  let badgeIcon = <CheckCircle2 size={14} aria-hidden="true" />;
  let badgeText = t('knowledge.status_supported');

  if (status === 'GENERAL_GUIDANCE') {
    badgeBg = 'rgba(201, 154, 60, 0.14)';
    badgeBorder = 'rgba(201, 154, 60, 0.4)';
    badgeColor = '#7A5416';
    badgeIcon = <BookOpen size={14} aria-hidden="true" />;
    badgeText = t('knowledge.status_guidance');
  } else if (status === 'EXPERT_CONFIRMATION_RECOMMENDED' || isRejected) {
    badgeBg = 'rgba(162, 74, 43, 0.12)';
    badgeBorder = 'rgba(162, 74, 43, 0.4)';
    badgeColor = '#8A2C10';
    badgeIcon = <AlertTriangle size={14} aria-hidden="true" />;
    badgeText = t('knowledge.status_uncertain');
  }

  const containerBorder =
    isRejected || status === 'EXPERT_CONFIRMATION_RECOMMENDED'
      ? '1.5px solid rgba(162, 74, 43, 0.35)'
      : '1.5px solid rgba(201, 154, 60, 0.28)';

  return (
    <section
      aria-labelledby="condition-knowledge-heading"
      className="drishya-knowledge-card"
      style={{
        background: '#FAF5EB',
        border: containerBorder,
        borderRadius: '20px',
        padding: '1.75rem',
        marginBottom: '1.75rem',
        boxShadow: '0 2px 12px rgba(28, 17, 10, 0.04)',
      }}
    >
      {/* ─── 1. Header & Status Badge ───────────────────────────────────── */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.75rem',
            flexWrap: 'wrap',
            marginBottom: '0.6rem',
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: badgeBg,
              border: `1px solid ${badgeBorder}`,
              borderRadius: '9999px',
              padding: '0.35rem 0.85rem',
              color: badgeColor,
              fontSize: '0.82rem',
              fontWeight: '700',
              letterSpacing: '0.02em',
            }}
          >
            {badgeIcon}
            <span>{badgeText}</span>
          </div>

          <span
            style={{
              fontSize: '0.78rem',
              color: '#8A7768',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              fontWeight: '600',
            }}
          >
            {crop.toUpperCase()} • STEP D ADVISORY
          </span>
        </div>

        <h2
          id="condition-knowledge-heading"
          style={{
            fontFamily: isDevanagari
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: 'clamp(1.25rem, 2vw, 1.55rem)',
            color: '#1C110A',
            fontWeight: '700',
            lineHeight: 1.3,
            marginBottom: '0.4rem',
          }}
        >
          {knowledge.display_name}
        </h2>

        {knowledge.short_description && (
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.98rem',
              color: '#5C442A',
              lineHeight: 1.55,
              margin: 0,
            }}
          >
            {knowledge.short_description}
          </p>
        )}
      </div>

      {/* ─── 2. What This Means (Context & Pathology) ───────────────────── */}
      {knowledge.what_it_means && (
        <div
          style={{
            background: '#F4EBD9',
            border: '1px solid rgba(201, 154, 60, 0.22)',
            borderRadius: '12px',
            padding: '1rem 1.15rem',
            marginBottom: '1.25rem',
          }}
        >
          <strong
            style={{
              display: 'block',
              fontSize: '0.88rem',
              color: '#3A2412',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              marginBottom: '0.35rem',
            }}
          >
            {t('knowledge.what_it_means')}
          </strong>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.94rem',
              color: '#3A281A',
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            {knowledge.what_it_means}
          </p>
        </div>
      )}

      {/* ─── 3. Visual Signs to Inspect in Field ────────────────────────── */}
      {Array.isArray(knowledge.visual_signs) && knowledge.visual_signs.length > 0 && (
        <div style={{ marginBottom: '1.25rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              marginBottom: '0.55rem',
            }}
          >
            <Eye size={16} color="#8A5A2B" aria-hidden="true" />
            <h3
              style={{
                fontSize: '0.98rem',
                fontWeight: '700',
                color: '#23160E',
                margin: 0,
              }}
            >
              {t('knowledge.visual_signs')}
            </h3>
          </div>
          <ul
            style={{
              listStyleType: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '0.4rem',
            }}
          >
            {knowledge.visual_signs.map((sign, idx) => (
              <li
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                  fontSize: '0.92rem',
                  color: '#4A3728',
                  lineHeight: 1.5,
                }}
              >
                <span
                  style={{
                    color: '#8A5A2B',
                    fontWeight: 'bold',
                    fontSize: '1rem',
                    lineHeight: 1.2,
                  }}
                  aria-hidden="true"
                >
                  •
                </span>
                <span>{sign}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ─── 4. Recommended Immediate Actions ──────────────────────────── */}
      {Array.isArray(knowledge.immediate_actions) && knowledge.immediate_actions.length > 0 && (
        <div style={{ marginBottom: '1.25rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              marginBottom: '0.55rem',
            }}
          >
            <ShieldCheck size={16} color="#3B5E2B" aria-hidden="true" />
            <h3
              style={{
                fontSize: '0.98rem',
                fontWeight: '700',
                color: '#23160E',
                margin: 0,
              }}
            >
              {t('knowledge.immediate_actions')}
            </h3>
          </div>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '0.45rem',
            }}
          >
            {knowledge.immediate_actions.map((act, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.6rem',
                  padding: '0.6rem 0.85rem',
                  background: 'rgba(255, 255, 255, 0.7)',
                  border: '1px solid rgba(201, 154, 60, 0.18)',
                  borderRadius: '10px',
                  fontSize: '0.92rem',
                  color: '#2A1C12',
                  lineHeight: 1.5,
                }}
              >
                <span
                  style={{
                    background: '#3B5E2B',
                    color: '#FFF',
                    borderRadius: '50%',
                    width: '18px',
                    height: '18px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.72rem',
                    fontWeight: '700',
                    flexShrink: 0,
                    marginTop: '2px',
                  }}
                >
                  {idx + 1}
                </span>
                <span>{act}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── 5. Prevention & Continuous Monitoring ──────────────────────── */}
      {Array.isArray(knowledge.prevention_or_monitoring) &&
        knowledge.prevention_or_monitoring.length > 0 && (
          <div style={{ marginBottom: '1.25rem' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                marginBottom: '0.55rem',
              }}
            >
              <CalendarCheck size={16} color="#8A5A2B" aria-hidden="true" />
              <h3
                style={{
                  fontSize: '0.98rem',
                  fontWeight: '700',
                  color: '#23160E',
                  margin: 0,
                }}
              >
                {t('knowledge.prevention_monitoring')}
              </h3>
            </div>
            <ul
              style={{
                listStyleType: 'none',
                padding: 0,
                margin: 0,
                display: 'flex',
                flexDirection: 'column',
                gap: '0.35rem',
              }}
            >
              {knowledge.prevention_or_monitoring.map((prev, idx) => (
                <li
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.5rem',
                    fontSize: '0.91rem',
                    color: '#4A3728',
                    lineHeight: 1.5,
                  }}
                >
                  <span
                    style={{
                      color: '#3B5E2B',
                      fontSize: '0.95rem',
                      lineHeight: 1.2,
                    }}
                    aria-hidden="true"
                  >
                    ✓
                  </span>
                  <span>{prev}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

      {/* ─── 6. When to Consult Agronomists / KVK ───────────────────────── */}
      {knowledge.expert_escalation && (
        <div
          style={{
            padding: '0.85rem 1rem',
            background: 'rgba(162, 74, 43, 0.08)',
            border: '1px solid rgba(162, 74, 43, 0.28)',
            borderRadius: '12px',
            marginBottom: '1.25rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              marginBottom: '0.35rem',
            }}
          >
            <PhoneCall size={15} color="#8A2C10" aria-hidden="true" />
            <strong
              style={{
                color: '#8A2C10',
                fontSize: '0.88rem',
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
              }}
            >
              {t('knowledge.expert_escalation')}
            </strong>
          </div>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.92rem',
              color: '#5A1E0C',
              lineHeight: 1.55,
              margin: 0,
            }}
          >
            {knowledge.expert_escalation}
          </p>
        </div>
      )}

      {/* ─── 7. Scientific Traceability & Institutional Sources ─────────── */}
      <div
        style={{
          borderTop: '1px solid rgba(201, 154, 60, 0.22)',
          paddingTop: '0.85rem',
        }}
      >
        <button
          type="button"
          id="btn-toggle-sources"
          onClick={() => setSourcesOpen(!sourcesOpen)}
          aria-expanded={sourcesOpen}
          aria-controls="sources-disclosure-content"
          style={{
            background: 'transparent',
            border: 'none',
            padding: '0.25rem 0',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%',
            color: '#6F5F52',
            fontSize: '0.86rem',
            fontWeight: '600',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Award size={15} color="#8A5A2B" aria-hidden="true" />
            <span>
              {sourcesOpen
                ? t('knowledge.hide_sources')
                : t('knowledge.view_sources', { count: knowledge.sources?.length || 0 })}
            </span>
          </div>
          {sourcesOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {sourcesOpen && (
          <div
            id="sources-disclosure-content"
            style={{
              marginTop: '0.75rem',
              padding: '0.85rem 1rem',
              background: '#F7EFE1',
              borderRadius: '12px',
              border: '1px solid rgba(201, 154, 60, 0.2)',
            }}
          >
            <p
              style={{
                fontSize: '0.82rem',
                color: '#6F5F52',
                lineHeight: 1.55,
                fontStyle: 'italic',
                marginBottom: '0.75rem',
              }}
            >
              {t('knowledge.sources_disclaimer')}
            </p>

            {Array.isArray(knowledge.sources) && knowledge.sources.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem' }}>
                {knowledge.sources.map((src, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '0.55rem 0.75rem',
                      background: 'rgba(255, 255, 255, 0.8)',
                      borderRadius: '8px',
                      border: '1px solid rgba(201, 154, 60, 0.16)',
                      fontSize: '0.85rem',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '0.5rem',
                      }}
                    >
                      <strong style={{ color: '#23160E' }}>{src.source_title}</strong>
                      {src.source_url && (
                        <a
                          href={src.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.2rem',
                            color: '#8A5A2B',
                            textDecoration: 'none',
                            fontSize: '0.8rem',
                          }}
                          aria-label={`Open external link for ${src.source_title}`}
                        >
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                    <div style={{ color: '#6A5442', fontSize: '0.8rem', marginTop: '0.15rem' }}>
                      {src.source_organization}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
