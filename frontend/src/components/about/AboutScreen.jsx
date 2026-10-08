/**
 * AboutScreen.jsx - DRISHYA Research Monograph & System Documentation
 *
 * Implements:
 * - Authoritative research monograph aesthetic (deep espresso, bark, warm bronze, antique gold, crisp ivory)
 * - 8 Comprehensive Sections:
 *   1. Why DRISHYA (Rural livelihoods, field context, human-in-the-loop assistance)
 *   2. How It Works (7-step end-to-end pipeline from capture to journal)
 *   3. Supported Crops (Turmeric Curcuma longa L. & Citrus Citrus limon)
 *   4. Models Currently in Use (ConvNeXt-Tiny Seed 42, EfficientNetV2-S Seed 42, CPU PyTorch runtime)
 *   5. Explainability (Grad-CAM visual attention mapping & clear causal caveat)
 *   6. Responsible AI (5 core tenets of ethical agricultural AI)
 *   7. Privacy & Data (SHA-256 fingerprinting, no permanent image retention, strict scoping)
 *   8. Research & Prototype Status (Prominent ICAR/KVK disclaimer, non-certified prototype notice)
 * - Strict adherence to verified repository facts (no fabricated accuracy, no fake certifications)
 * - GSAP entrance animations respecting prefers-reduced-motion
 * - Multilingual support (English, Hindi, Marathi) via LanguageContext
 * - Touch targets >= 48px
 */

import React, { useRef, useEffect } from 'react';
import {
  ArrowLeft,
  Cpu,
  Shield,
  Eye,
  Lock,
  Layers,
  Sparkles,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Activity,
  FileCode,
  Wheat,
  Scale,
} from 'lucide-react';
import gsap from 'gsap';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import CropIdentity from '../brand/CropIdentity';

export default function AboutScreen({ onBackToHome }) {
  const { navigate } = useAuth();
  const { t, language } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  const handleBack = () => {
    if (onBackToHome) {
      onBackToHome();
    } else {
      navigate('/home');
    }
  };

  // GSAP animation refs
  const pageRef = useRef(null);
  const heroRef = useRef(null);
  const sectionsRef = useRef(null);

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });
      tl.fromTo(
        heroRef.current,
        { opacity: 0, y: -16 },
        { opacity: 1, y: 0, duration: 0.5 }
      ).fromTo(
        sectionsRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.55 },
        '-=0.2'
      );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const pipelineSteps = [
    { num: 1, text: t('about.how_works_1') },
    { num: 2, text: t('about.how_works_2') },
    { num: 3, text: t('about.how_works_3') },
    { num: 4, text: t('about.how_works_4') },
    { num: 5, text: t('about.how_works_5') },
    { num: 6, text: t('about.how_works_6') },
    { num: 7, text: t('about.how_works_7') },
  ];

  const responsiblePrinciples = [
    t('about.responsible_1'),
    t('about.responsible_2'),
    t('about.responsible_3'),
    t('about.responsible_4'),
    t('about.responsible_5'),
  ];

  const privacyPoints = [
    t('about.privacy_1'),
    t('about.privacy_2'),
    t('about.privacy_3'),
    t('about.privacy_4'),
  ];

  return (
    <div
      ref={pageRef}
      className="drishya-about-page"
      style={{
        minHeight: '100%',
        backgroundColor: '#160E08',
        color: '#FBF6EA',
        padding: '1.5rem 1rem 5rem',
      }}
    >
      <div style={{ maxWidth: '980px', margin: '0 auto' }}>
        {/* Navigation & Hero */}
        <header ref={heroRef} style={{ marginBottom: '2.5rem' }}>
          <button
            type="button"
            onClick={handleBack}
            aria-label={t('about.back')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'transparent',
              border: 'none',
              color: '#D8C7A3',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: '600',
              padding: '0.5rem 0',
              marginBottom: '1.25rem',
              minHeight: '48px',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              transition: 'color 0.2s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#F2C14E')}
            onMouseLeave={(e) => (e.currentTarget.style.color = '#D8C7A3')}
          >
            <ArrowLeft size={20} />
            <span>{t('about.back')}</span>
          </button>

          <div
            style={{
              background: 'linear-gradient(135deg, #24160E 0%, #1A1009 100%)',
              border: '1.5px solid rgba(201, 154, 60, 0.35)',
              borderRadius: '22px',
              padding: '2.5rem 2rem',
              boxShadow: '0 12px 35px rgba(0, 0, 0, 0.45)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Subtle emblem watermark */}
            <div
              aria-hidden="true"
              style={{
                position: 'absolute',
                top: '-30px',
                right: '-30px',
                opacity: 0.05,
                pointerEvents: 'none',
              }}
            >
              <Cpu size={260} color="#C99A3C" />
            </div>

            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                background: 'rgba(201, 154, 60, 0.15)',
                border: '1px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                padding: '0.35rem 0.95rem',
                color: '#F2C14E',
                fontSize: '0.82rem',
                fontWeight: '600',
                letterSpacing: '0.05em',
                marginBottom: '1.25rem',
              }}
            >
              <Activity size={15} color="#F2C14E" />
              <span>RESEARCH MONOGRAPH</span>
            </div>

            <h1
              style={{
                fontFamily: isDevanagari
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: 'clamp(2.1rem, 4vw, 3.2rem)',
                fontWeight: '700',
                color: '#FAF4E6',
                lineHeight: 1.2,
                marginBottom: '0.85rem',
              }}
            >
              {t('about.title')}
            </h1>

            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '1.15rem',
                color: '#D8C7A3',
                maxWidth: '720px',
                lineHeight: 1.6,
                margin: '0 0 1.25rem 0',
              }}
            >
              {t('about.subtitle')}
            </p>

            <div
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.92rem',
                color: '#A99878',
                borderTop: '1px solid rgba(201, 154, 60, 0.2)',
                paddingTop: '1rem',
              }}
            >
              <strong>DRISHYA</strong>: Deep Robust Intelligence for Sustainable Harvest & Yield Assessment
            </div>
          </div>
        </header>

        {/* Content Sections Container */}
        <div ref={sectionsRef} style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
          {/* SECTION 1: Why DRISHYA */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.1rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Wheat size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.why_title')}
              </h2>
            </div>
            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '1.05rem',
                color: '#D8C7A3',
                lineHeight: 1.7,
                margin: 0,
              }}
            >
              {t('about.why_desc')}
            </p>
          </section>

          {/* SECTION 2: How It Works (7-Step Pipeline) */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.5rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Layers size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.how_works_title')}
              </h2>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {pipelineSteps.map((step) => (
                <div
                  key={step.num}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '1.1rem',
                    padding: '1rem 1.25rem',
                    backgroundColor: 'rgba(38, 24, 15, 0.75)',
                    border: '1px solid rgba(201, 154, 60, 0.18)',
                    borderRadius: '12px',
                  }}
                >
                  <div
                    style={{
                      width: '30px',
                      height: '30px',
                      borderRadius: '50%',
                      backgroundColor: '#C99A3C',
                      color: '#1C110A',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: '700',
                      fontSize: '0.9rem',
                      flexShrink: 0,
                      marginTop: '0.1rem',
                    }}
                  >
                    {step.num}
                  </div>
                  <div
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.98rem',
                      color: '#E8DCC4',
                      lineHeight: 1.55,
                    }}
                  >
                    {step.text}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 3: Supported Crops */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.5rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Wheat size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.crops_title')}
              </h2>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.5rem',
              }}
            >
              {/* Turmeric Card */}
              <div
                style={{
                  padding: '1.5rem',
                  backgroundColor: 'rgba(38, 24, 15, 0.85)',
                  border: '1.5px solid rgba(201, 154, 60, 0.3)',
                  borderRadius: '14px',
                }}
              >
                <div style={{ marginBottom: '0.75rem' }}>
                  <CropIdentity crop="turmeric" size={42} fontSize="1.15rem" style={{ color: '#F4EAD3' }} />
                </div>
                <div style={{ fontStyle: 'italic', color: '#B39E7E', fontSize: '0.92rem', marginBottom: '0.85rem' }}>
                  {t('about.crops_turmeric_sci')}
                </div>
                <p
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.95rem',
                    color: '#D8C7A3',
                    lineHeight: 1.5,
                    margin: 0,
                  }}
                >
                  {t('about.crops_turmeric_classes')}
                </p>
              </div>

              {/* Citrus Card */}
              <div
                style={{
                  padding: '1.5rem',
                  backgroundColor: 'rgba(38, 24, 15, 0.85)',
                  border: '1.5px solid rgba(201, 154, 60, 0.3)',
                  borderRadius: '14px',
                }}
              >
                <div style={{ marginBottom: '0.75rem' }}>
                  <CropIdentity crop="citrus" size={42} fontSize="1.15rem" style={{ color: '#F4EAD3' }} />
                </div>
                <div style={{ fontStyle: 'italic', color: '#B39E7E', fontSize: '0.92rem', marginBottom: '0.85rem' }}>
                  {t('about.crops_citrus_sci')}
                </div>
                <p
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.95rem',
                    color: '#D8C7A3',
                    lineHeight: 1.5,
                    margin: 0,
                  }}
                >
                  {t('about.crops_citrus_classes')}
                </p>
              </div>
            </div>
          </section>

          {/* SECTION 4: Models Currently in Use (Factual Specs Only) */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '0.85rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Cpu size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.models_title')}
              </h2>
            </div>

            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.96rem',
                color: '#C4B293',
                marginBottom: '1.5rem',
                lineHeight: 1.5,
              }}
            >
              {t('about.models_note')}
            </p>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.5rem',
                marginBottom: '1.5rem',
              }}
            >
              {/* Turmeric Model Spec */}
              <div
                style={{
                  padding: '1.35rem',
                  backgroundColor: 'rgba(30, 18, 11, 0.95)',
                  border: '1px solid rgba(201, 154, 60, 0.25)',
                  borderRadius: '12px',
                }}
              >
                <div style={{ fontSize: '0.82rem', color: '#F2C14E', fontWeight: '700', marginBottom: '0.5rem' }}>
                  TURMERIC ACTIVE MODEL
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#FFFDF9', marginBottom: '1rem' }}>
                  {t('about.model_turmeric_arch')}
                </div>
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.45rem',
                    fontSize: '0.9rem',
                    color: '#D8C7A3',
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  }}
                >
                  <div>
                    <span style={{ color: '#8F7E66' }}>Seed: </span>
                    <strong>{t('about.model_turmeric_seed')}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#8F7E66' }}>Resolution: </span>
                    <strong>{t('about.model_turmeric_input')}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#8F7E66' }}>Target Classes: </span>
                    <strong>{t('about.model_turmeric_classes')}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#8F7E66' }}>Execution: </span>
                    <strong>{t('about.model_turmeric_runtime')}</strong>
                  </div>
                </div>
              </div>

              {/* Citrus Model Spec */}
              <div
                style={{
                  padding: '1.35rem',
                  backgroundColor: 'rgba(30, 18, 11, 0.95)',
                  border: '1px solid rgba(201, 154, 60, 0.25)',
                  borderRadius: '12px',
                }}
              >
                <div style={{ fontSize: '0.82rem', color: '#F2C14E', fontWeight: '700', marginBottom: '0.5rem' }}>
                  CITRUS ACTIVE MODEL
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#FFFDF9', marginBottom: '1rem' }}>
                  {t('about.model_citrus_arch')}
                </div>
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.45rem',
                    fontSize: '0.9rem',
                    color: '#D8C7A3',
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  }}
                >
                  <div>
                    <span style={{ color: '#8F7E66' }}>Seed: </span>
                    <strong>{t('about.model_citrus_seed')}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#8F7E66' }}>Resolution: </span>
                    <strong>{t('about.model_citrus_input')}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#8F7E66' }}>Target Classes: </span>
                    <strong>{t('about.model_citrus_classes')}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#8F7E66' }}>Execution: </span>
                    <strong>{t('about.model_citrus_runtime')}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div
              style={{
                padding: '0.95rem 1.15rem',
                backgroundColor: 'rgba(201, 154, 60, 0.08)',
                borderLeft: '3px solid #C99A3C',
                borderRadius: '6px',
                fontSize: '0.92rem',
                color: '#D8C7A3',
                lineHeight: 1.5,
              }}
            >
              {t('about.models_pretrained_note')}
            </div>
          </section>

          {/* SECTION 5: Explainability */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.1rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Eye size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.explainability_title')}
              </h2>
            </div>
            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '1.02rem',
                color: '#D8C7A3',
                lineHeight: 1.65,
                margin: '0 0 1.25rem 0',
              }}
            >
              {t('about.explainability_desc')}
            </p>
            <div
              style={{
                padding: '1rem 1.25rem',
                backgroundColor: 'rgba(162, 74, 43, 0.12)',
                border: '1px solid rgba(162, 74, 43, 0.35)',
                borderRadius: '10px',
                fontSize: '0.92rem',
                color: '#F4D4CA',
                lineHeight: 1.55,
                fontStyle: 'italic',
              }}
            >
              <strong>Caveat: </strong>
              {t('about.explainability_caveat')}
            </div>
          </section>

          {/* SECTION 6: Responsible AI */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.25rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Scale size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.responsible_title')}
              </h2>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {responsiblePrinciples.map((principle, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.85rem',
                    padding: '0.85rem 1.15rem',
                    backgroundColor: 'rgba(38, 24, 15, 0.75)',
                    borderRadius: '10px',
                    border: '1px solid rgba(201, 154, 60, 0.15)',
                  }}
                >
                  <Shield
                    size={18}
                    color="#C99A3C"
                    style={{ flexShrink: 0, marginTop: '0.2rem' }}
                  />
                  <span
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.96rem',
                      color: '#E8DCC4',
                      lineHeight: 1.55,
                    }}
                  >
                    {principle}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 7: Privacy & Data */}
          <section
            style={{
              background: '#20140D',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '18px',
              padding: '2rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.25rem' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(201, 154, 60, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <Lock size={22} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.privacy_title')}
              </h2>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {privacyPoints.map((point, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.85rem',
                    padding: '0.85rem 1.15rem',
                    backgroundColor: 'rgba(38, 24, 15, 0.75)',
                    borderRadius: '10px',
                    border: '1px solid rgba(201, 154, 60, 0.15)',
                  }}
                >
                  <Lock
                    size={16}
                    color="#C99A3C"
                    style={{ flexShrink: 0, marginTop: '0.25rem' }}
                  />
                  <span
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.96rem',
                      color: '#E8DCC4',
                      lineHeight: 1.55,
                    }}
                  >
                    {point}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 8: Research & Prototype Status (Prominent Plaque) */}
          <section
            style={{
              background: 'linear-gradient(135deg, rgba(62, 34, 18, 0.6) 0%, rgba(32, 18, 10, 0.8) 100%)',
              border: '2px solid rgba(201, 154, 60, 0.45)',
              borderRadius: '20px',
              padding: '2.2rem 2rem',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.1rem' }}>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(235, 178, 55, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#F2C14E',
                }}
              >
                <AlertTriangle size={24} />
              </div>
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.5rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: 0,
                }}
              >
                {t('about.prototype_title')}
              </h2>
            </div>

            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '1.02rem',
                color: '#D8C7A3',
                lineHeight: 1.65,
                margin: '0 0 1.25rem 0',
              }}
            >
              {t('about.prototype_desc')}
            </p>

            <div
              style={{
                padding: '1.1rem 1.3rem',
                backgroundColor: 'rgba(242, 193, 78, 0.1)',
                border: '1.5px solid rgba(242, 193, 78, 0.35)',
                borderRadius: '12px',
                color: '#F8E8C8',
                fontWeight: '600',
                fontSize: '0.98rem',
                lineHeight: 1.5,
              }}
            >
              ⚠️ {t('about.prototype_disclaimer')}
            </div>
          </section>
        </div>

        {/* Footer Back Action */}
        <div style={{ marginTop: '4rem', textAlign: 'center' }}>
          <button
            type="button"
            onClick={handleBack}
            style={{
              minHeight: '48px',
              padding: '0.75rem 2.2rem',
              backgroundColor: '#C99A3C',
              color: '#1C110A',
              border: 'none',
              borderRadius: '9999px',
              fontSize: '1rem',
              fontWeight: '700',
              cursor: 'pointer',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F2C14E';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#C99A3C';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <ArrowLeft size={18} />
            <span>{t('about.back')}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
