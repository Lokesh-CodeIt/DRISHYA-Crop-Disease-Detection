/**
 * GuideScreen.jsx - DRISHYA Field Diagnostic Guide
 *
 * Implements:
 * - Authentic botanical field guide aesthetic (parchment, ivory, deep espresso, antique gold, sage linework)
 * - 6 Comprehensive Sections:
 *   1. Using DRISHYA (5 numbered field steps)
 *   2. Photo Tips (5 practical leaf photography habits)
 *   3. Understanding Your Result (Condition name, Unclear safety gate, Visual attention mapping & caveat)
 *   4. When to Seek Expert Help (Unclear, symptoms mismatch, widespread issues, KVK advisory)
 *   5. What DRISHYA Can Do (5 capabilities with checkmarks)
 *   6. What DRISHYA Cannot Do (6 safety boundaries & disclaimers)
 * - Keyboard-accessible interactive accordions (aria-expanded, aria-controls, Enter/Space toggling)
 * - Responsive quick-jump TOC pills
 * - GSAP entrance animations with strict prefers-reduced-motion check
 * - Multilingual support (English, Hindi, Marathi) via LanguageContext
 * - Touch targets >= 48px
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  ArrowLeft,
  BookOpen,
  Camera,
  Sun,
  Focus,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  ChevronDown,
  Sparkles,
  ShieldAlert,
  Eye,
  Info,
  Check,
  X,
  Compass,
} from 'lucide-react';
import gsap from 'gsap';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';

export default function GuideScreen({ onBackToHome }) {
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

  // Accordion state: initialize with all sections open for immediate readability or toggleable
  const [openSections, setOpenSections] = useState({
    using: true,
    photoTips: true,
    understanding: true,
    expertHelp: true,
    canDo: true,
    cannotDo: true,
  });

  const toggleSection = (key) => {
    setOpenSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Smooth scroll to section
  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // GSAP animation refs
  const pageRef = useRef(null);
  const headerRef = useRef(null);
  const tocRef = useRef(null);
  const sectionsRef = useRef(null);

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });
      tl.fromTo(
        headerRef.current,
        { opacity: 0, y: -16 },
        { opacity: 1, y: 0, duration: 0.45 }
      )
        .fromTo(
          tocRef.current,
          { opacity: 0, y: 12 },
          { opacity: 1, y: 0, duration: 0.4 },
          '-=0.2'
        )
        .fromTo(
          sectionsRef.current,
          { opacity: 0, y: 16 },
          { opacity: 1, y: 0, duration: 0.5 },
          '-=0.25'
        );
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const tocItems = [
    { id: 'section-using', label: t('guide.toc_using'), key: 'using' },
    { id: 'section-photo-tips', label: t('guide.toc_photo_tips'), key: 'photoTips' },
    { id: 'section-understanding', label: t('guide.toc_understanding'), key: 'understanding' },
    { id: 'section-expert-help', label: t('guide.toc_expert_help'), key: 'expertHelp' },
    { id: 'section-can-do', label: t('guide.toc_can_do'), key: 'canDo' },
    { id: 'section-cannot-do', label: t('guide.toc_cannot_do'), key: 'cannotDo' },
  ];

  const usingSteps = [
    { num: 1, title: t('guide.using_step1_title'), desc: t('guide.using_step1_desc') },
    { num: 2, title: t('guide.using_step2_title'), desc: t('guide.using_step2_desc') },
    { num: 3, title: t('guide.using_step3_title'), desc: t('guide.using_step3_desc') },
    { num: 4, title: t('guide.using_step4_title'), desc: t('guide.using_step4_desc') },
    { num: 5, title: t('guide.using_step5_title'), desc: t('guide.using_step5_desc') },
  ];

  const photoTips = [
    {
      icon: <Camera size={22} color="#8A5A2B" />,
      title: t('guide.tip_one_leaf_title'),
      desc: t('guide.tip_one_leaf_desc'),
    },
    {
      icon: <Sun size={22} color="#C99A3C" />,
      title: t('guide.tip_light_title'),
      desc: t('guide.tip_light_desc'),
    },
    {
      icon: <Focus size={22} color="#5E6B38" />,
      title: t('guide.tip_focus_title'),
      desc: t('guide.tip_focus_desc'),
    },
    {
      icon: <Eye size={22} color="#A24A2B" />,
      title: t('guide.tip_glare_title'),
      desc: t('guide.tip_glare_desc'),
    },
    {
      icon: <Compass size={22} color="#7E5C3B" />,
      title: t('guide.tip_center_title'),
      desc: t('guide.tip_center_desc'),
    },
  ];

  const canDoItems = [
    t('guide.can_do_1'),
    t('guide.can_do_2'),
    t('guide.can_do_3'),
    t('guide.can_do_4'),
    t('guide.can_do_5'),
  ];

  const cannotDoItems = [
    t('guide.cannot_do_1'),
    t('guide.cannot_do_2'),
    t('guide.cannot_do_3'),
    t('guide.cannot_do_4'),
    t('guide.cannot_do_5'),
    t('guide.cannot_do_6'),
  ];

  return (
    <div
      ref={pageRef}
      className="drishya-guide-page"
      style={{
        minHeight: '100%',
        backgroundColor: '#FBF6EA',
        color: '#1C110A',
        padding: '1.5rem 1rem 4rem',
      }}
    >
      <div style={{ maxWidth: '960px', margin: '0 auto' }}>
        {/* Top Navigation & Header */}
        <header ref={headerRef} style={{ marginBottom: '2rem' }}>
          <button
            type="button"
            onClick={handleBack}
            aria-label={t('guide.back')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'transparent',
              border: 'none',
              color: '#8A5A2B',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: '600',
              padding: '0.5rem 0',
              marginBottom: '1rem',
              minHeight: '48px',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            }}
          >
            <ArrowLeft size={20} />
            <span>{t('guide.back')}</span>
          </button>

          <div
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(201, 154, 60, 0.35)',
              borderRadius: '20px',
              padding: '2rem 1.8rem',
              boxShadow: '0 8px 30px rgba(42, 24, 16, 0.05)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Linework decorative watermark */}
            <div
              aria-hidden="true"
              style={{
                position: 'absolute',
                top: '-20px',
                right: '-20px',
                opacity: 0.07,
                pointerEvents: 'none',
              }}
            >
              <BookOpen size={200} color="#8A5A2B" />
            </div>

            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                background: 'rgba(201, 154, 60, 0.15)',
                border: '1px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                padding: '0.3rem 0.85rem',
                color: '#8A5A2B',
                fontSize: '0.82rem',
                fontWeight: '600',
                marginBottom: '1rem',
              }}
            >
              <BookOpen size={15} color="#8A5A2B" />
              <span>DRISHYA FIELD PROTOCOL</span>
            </div>

            <h1
              style={{
                fontFamily: isDevanagari
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: 'clamp(2rem, 3.8vw, 2.8rem)',
                fontWeight: '700',
                color: '#1C110A',
                lineHeight: 1.25,
                marginBottom: '0.65rem',
              }}
            >
              {t('guide.title')}
            </h1>

            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '1.1rem',
                color: '#5A4634',
                maxWidth: '680px',
                lineHeight: 1.6,
                margin: 0,
              }}
            >
              {t('guide.subtitle')}
            </p>
          </div>
        </header>

        {/* Quick Jump TOC Pills (Horizontally Scrollable) */}
        <nav
          ref={tocRef}
          aria-label="Table of contents"
          style={{
            marginBottom: '2.5rem',
            overflowX: 'auto',
            paddingBottom: '0.5rem',
            WebkitOverflowScrolling: 'touch',
          }}
        >
          <div
            style={{
              display: 'flex',
              gap: '0.65rem',
              minWidth: 'max-content',
            }}
          >
            {tocItems.map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => {
                  setOpenSections((prev) => ({ ...prev, [item.key]: true }));
                  setTimeout(() => scrollToSection(item.id), 50);
                }}
                style={{
                  minHeight: '44px',
                  padding: '0.5rem 1.1rem',
                  backgroundColor: '#FAF4E6',
                  border: '1px solid rgba(201, 154, 60, 0.35)',
                  borderRadius: '9999px',
                  color: '#4A3728',
                  fontSize: '0.88rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-body, "Mukta", sans-serif)',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#F4EAD3';
                  e.currentTarget.style.borderColor = '#C99A3C';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#FAF4E6';
                  e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.35)';
                }}
              >
                {item.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Sections Container */}
        <div ref={sectionsRef} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* SECTION 1: Using DRISHYA */}
          <section
            id="section-using"
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '18px',
              padding: '1.8rem',
              boxShadow: '0 6px 20px rgba(42, 24, 16, 0.04)',
            }}
          >
            <div
              role="button"
              tabIndex={0}
              aria-expanded={openSections.using}
              aria-controls="content-using"
              onClick={() => toggleSection('using')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection('using');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                minHeight: '48px',
                userSelect: 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(201, 154, 60, 0.18)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#8A5A2B',
                  }}
                >
                  <Compass size={22} />
                </div>
                <h2
                  style={{
                    fontFamily: isDevanagari
                      ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                      : 'var(--font-display, "Fraunces", Georgia, serif)',
                    fontSize: '1.45rem',
                    color: '#1C110A',
                    fontWeight: '700',
                    margin: 0,
                  }}
                >
                  {t('guide.using_title')}
                </h2>
              </div>
              <ChevronDown
                size={22}
                color="#8A5A2B"
                style={{
                  transform: openSections.using ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                }}
              />
            </div>

            {openSections.using && (
              <div id="content-using" style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {usingSteps.map((step) => (
                  <div
                    key={step.num}
                    style={{
                      display: 'flex',
                      gap: '1.1rem',
                      alignItems: 'flex-start',
                      padding: '1rem 1.15rem',
                      backgroundColor: '#FAF5EB',
                      borderRadius: '12px',
                      border: '1px solid rgba(201, 154, 60, 0.22)',
                    }}
                  >
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: '#C99A3C',
                        color: '#FFF',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: '700',
                        fontSize: '0.95rem',
                        flexShrink: 0,
                        marginTop: '0.1rem',
                      }}
                    >
                      {step.num}
                    </div>
                    <div>
                      <h3
                        style={{
                          fontFamily: isDevanagari
                            ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                            : 'var(--font-display, "Fraunces", Georgia, serif)',
                          fontSize: '1.15rem',
                          color: '#1C110A',
                          fontWeight: '700',
                          margin: '0 0 0.35rem 0',
                        }}
                      >
                        {step.title}
                      </h3>
                      <p
                        style={{
                          fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                          fontSize: '0.98rem',
                          color: '#554232',
                          margin: 0,
                          lineHeight: 1.55,
                        }}
                      >
                        {step.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* SECTION 2: Photo Tips */}
          <section
            id="section-photo-tips"
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '18px',
              padding: '1.8rem',
              boxShadow: '0 6px 20px rgba(42, 24, 16, 0.04)',
            }}
          >
            <div
              role="button"
              tabIndex={0}
              aria-expanded={openSections.photoTips}
              aria-controls="content-photo-tips"
              onClick={() => toggleSection('photoTips')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection('photoTips');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                minHeight: '48px',
                userSelect: 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(201, 154, 60, 0.18)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#8A5A2B',
                  }}
                >
                  <Camera size={22} />
                </div>
                <div>
                  <h2
                    style={{
                      fontFamily: isDevanagari
                        ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                        : 'var(--font-display, "Fraunces", Georgia, serif)',
                      fontSize: '1.45rem',
                      color: '#1C110A',
                      fontWeight: '700',
                      margin: 0,
                    }}
                  >
                    {t('guide.photo_tips_title')}
                  </h2>
                  <p
                    style={{
                      fontSize: '0.88rem',
                      color: '#6F5F52',
                      margin: '0.15rem 0 0',
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    }}
                  >
                    {t('guide.photo_tips_subtitle')}
                  </p>
                </div>
              </div>
              <ChevronDown
                size={22}
                color="#8A5A2B"
                style={{
                  transform: openSections.photoTips ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                }}
              />
            </div>

            {openSections.photoTips && (
              <div
                id="content-photo-tips"
                style={{
                  marginTop: '1.5rem',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                  gap: '1.25rem',
                }}
              >
                {photoTips.map((tip, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '1.2rem',
                      backgroundColor: '#FAF5EB',
                      borderRadius: '14px',
                      border: '1px solid rgba(201, 154, 60, 0.22)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.65rem',
                    }}
                  >
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '10px',
                        backgroundColor: '#F4EAD3',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '1px solid rgba(201, 154, 60, 0.3)',
                      }}
                    >
                      {tip.icon}
                    </div>
                    <h3
                      style={{
                        fontFamily: isDevanagari
                          ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                          : 'var(--font-display, "Fraunces", Georgia, serif)',
                        fontSize: '1.1rem',
                        color: '#1C110A',
                        fontWeight: '700',
                        margin: 0,
                      }}
                    >
                      {tip.title}
                    </h3>
                    <p
                      style={{
                        fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                        fontSize: '0.92rem',
                        color: '#554232',
                        margin: 0,
                        lineHeight: 1.5,
                      }}
                    >
                      {tip.desc}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* SECTION 3: Understanding Your Result */}
          <section
            id="section-understanding"
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '18px',
              padding: '1.8rem',
              boxShadow: '0 6px 20px rgba(42, 24, 16, 0.04)',
            }}
          >
            <div
              role="button"
              tabIndex={0}
              aria-expanded={openSections.understanding}
              aria-controls="content-understanding"
              onClick={() => toggleSection('understanding')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection('understanding');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                minHeight: '48px',
                userSelect: 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(201, 154, 60, 0.18)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#8A5A2B',
                  }}
                >
                  <HelpCircle size={22} />
                </div>
                <h2
                  style={{
                    fontFamily: isDevanagari
                      ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                      : 'var(--font-display, "Fraunces", Georgia, serif)',
                    fontSize: '1.45rem',
                    color: '#1C110A',
                    fontWeight: '700',
                    margin: 0,
                  }}
                >
                  {t('guide.understanding_title')}
                </h2>
              </div>
              <ChevronDown
                size={22}
                color="#8A5A2B"
                style={{
                  transform: openSections.understanding ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                }}
              />
            </div>

            {openSections.understanding && (
              <div id="content-understanding" style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* 1. Condition Name */}
                <div
                  style={{
                    padding: '1.2rem',
                    backgroundColor: '#FAF5EB',
                    borderRadius: '12px',
                    border: '1px solid rgba(201, 154, 60, 0.22)',
                  }}
                >
                  <h3
                    style={{
                      fontFamily: isDevanagari
                        ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                        : 'var(--font-display, "Fraunces", Georgia, serif)',
                      fontSize: '1.15rem',
                      color: '#1C110A',
                      fontWeight: '700',
                      margin: '0 0 0.4rem 0',
                    }}
                  >
                    {t('guide.understanding_condition_title')}
                  </h3>
                  <p
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.96rem',
                      color: '#554232',
                      margin: 0,
                      lineHeight: 1.6,
                    }}
                  >
                    {t('guide.understanding_condition_desc')}
                  </p>
                </div>

                {/* 2. Unclear Safety Feature */}
                <div
                  style={{
                    padding: '1.2rem',
                    backgroundColor: 'rgba(235, 178, 55, 0.09)',
                    borderRadius: '12px',
                    border: '1px solid rgba(201, 154, 60, 0.35)',
                  }}
                >
                  <h3
                    style={{
                      fontFamily: isDevanagari
                        ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                        : 'var(--font-display, "Fraunces", Georgia, serif)',
                      fontSize: '1.15rem',
                      color: '#8A5A2B',
                      fontWeight: '700',
                      margin: '0 0 0.4rem 0',
                    }}
                  >
                    {t('guide.understanding_unclear_title')}
                  </h3>
                  <p
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.96rem',
                      color: '#4A3728',
                      margin: 0,
                      lineHeight: 1.6,
                    }}
                  >
                    {t('guide.understanding_unclear_desc')}
                  </p>
                </div>

                {/* 3. Visual Attention Mapping + Caveat */}
                <div
                  style={{
                    padding: '1.2rem',
                    backgroundColor: '#FAF5EB',
                    borderRadius: '12px',
                    border: '1px solid rgba(201, 154, 60, 0.22)',
                  }}
                >
                  <h3
                    style={{
                      fontFamily: isDevanagari
                        ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                        : 'var(--font-display, "Fraunces", Georgia, serif)',
                      fontSize: '1.15rem',
                      color: '#1C110A',
                      fontWeight: '700',
                      margin: '0 0 0.4rem 0',
                    }}
                  >
                    {t('guide.understanding_attention_title')}
                  </h3>
                  <p
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.96rem',
                      color: '#554232',
                      margin: '0 0 0.85rem 0',
                      lineHeight: 1.6,
                    }}
                  >
                    {t('guide.understanding_attention_desc')}
                  </p>
                  <div
                    style={{
                      padding: '0.85rem 1rem',
                      backgroundColor: 'rgba(28, 17, 10, 0.04)',
                      borderLeft: '3px solid #8A5A2B',
                      borderRadius: '4px',
                      fontSize: '0.9rem',
                      color: '#6F5F52',
                      fontStyle: 'italic',
                      lineHeight: 1.5,
                    }}
                  >
                    {t('guide.understanding_attention_caveat')}
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* SECTION 4: When to Seek Expert Help */}
          <section
            id="section-expert-help"
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(162, 74, 43, 0.35)',
              borderRadius: '18px',
              padding: '1.8rem',
              boxShadow: '0 6px 20px rgba(162, 74, 43, 0.04)',
            }}
          >
            <div
              role="button"
              tabIndex={0}
              aria-expanded={openSections.expertHelp}
              aria-controls="content-expert-help"
              onClick={() => toggleSection('expertHelp')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection('expertHelp');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                minHeight: '48px',
                userSelect: 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(162, 74, 43, 0.14)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#A24A2B',
                  }}
                >
                  <ShieldAlert size={22} />
                </div>
                <h2
                  style={{
                    fontFamily: isDevanagari
                      ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                      : 'var(--font-display, "Fraunces", Georgia, serif)',
                    fontSize: '1.45rem',
                    color: '#1C110A',
                    fontWeight: '700',
                    margin: 0,
                  }}
                >
                  {t('guide.expert_help_title')}
                </h2>
              </div>
              <ChevronDown
                size={22}
                color="#A24A2B"
                style={{
                  transform: openSections.expertHelp ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                }}
              />
            </div>

            {openSections.expertHelp && (
              <div id="content-expert-help" style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
                <p
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '1rem',
                    color: '#4A3728',
                    fontWeight: '500',
                    margin: 0,
                    lineHeight: 1.6,
                  }}
                >
                  {t('guide.expert_help_intro')}
                </p>

                <ul
                  style={{
                    margin: 0,
                    padding: '0 0 0 1.25rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.75rem',
                    color: '#4A3728',
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.96rem',
                    lineHeight: 1.55,
                  }}
                >
                  <li>{t('guide.expert_help_unclear')}</li>
                  <li>{t('guide.expert_help_mismatch')}</li>
                  <li>{t('guide.expert_help_serious')}</li>
                  <li>
                    <strong>{t('guide.expert_help_treatment')}</strong>
                  </li>
                </ul>

                {/* KVK Callout Box */}
                <div
                  style={{
                    padding: '1.1rem 1.3rem',
                    backgroundColor: 'rgba(94, 107, 56, 0.12)',
                    border: '1.5px solid rgba(94, 107, 56, 0.35)',
                    borderRadius: '12px',
                    display: 'flex',
                    gap: '0.85rem',
                    alignItems: 'center',
                    marginTop: '0.5rem',
                  }}
                >
                  <Info size={24} color="#5E6B38" style={{ flexShrink: 0 }} />
                  <p
                    style={{
                      fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                      fontSize: '0.95rem',
                      color: '#344018',
                      fontWeight: '600',
                      margin: 0,
                      lineHeight: 1.5,
                    }}
                  >
                    {t('guide.expert_help_kvk')}
                  </p>
                </div>
              </div>
            )}
          </section>

          {/* SECTION 5: What DRISHYA Can Do */}
          <section
            id="section-can-do"
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(94, 107, 56, 0.3)',
              borderRadius: '18px',
              padding: '1.8rem',
              boxShadow: '0 6px 20px rgba(94, 107, 56, 0.04)',
            }}
          >
            <div
              role="button"
              tabIndex={0}
              aria-expanded={openSections.canDo}
              aria-controls="content-can-do"
              onClick={() => toggleSection('canDo')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection('canDo');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                minHeight: '48px',
                userSelect: 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(94, 107, 56, 0.16)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#5E6B38',
                  }}
                >
                  <CheckCircle2 size={22} />
                </div>
                <h2
                  style={{
                    fontFamily: isDevanagari
                      ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                      : 'var(--font-display, "Fraunces", Georgia, serif)',
                    fontSize: '1.45rem',
                    color: '#1C110A',
                    fontWeight: '700',
                    margin: 0,
                  }}
                >
                  {t('guide.can_do_title')}
                </h2>
              </div>
              <ChevronDown
                size={22}
                color="#5E6B38"
                style={{
                  transform: openSections.canDo ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                }}
              />
            </div>

            {openSections.canDo && (
              <div id="content-can-do" style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {canDoItems.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.85rem',
                      padding: '0.75rem 1rem',
                      backgroundColor: '#FAF5EB',
                      borderRadius: '10px',
                    }}
                  >
                    <Check
                      size={18}
                      color="#5E6B38"
                      style={{ flexShrink: 0, marginTop: '0.2rem' }}
                    />
                    <span
                      style={{
                        fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                        fontSize: '0.96rem',
                        color: '#4A3728',
                        lineHeight: 1.5,
                      }}
                    >
                      {item}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* SECTION 6: What DRISHYA Cannot Do */}
          <section
            id="section-cannot-do"
            style={{
              background: '#FFFDF9',
              border: '1.5px solid rgba(162, 74, 43, 0.3)',
              borderRadius: '18px',
              padding: '1.8rem',
              boxShadow: '0 6px 20px rgba(162, 74, 43, 0.04)',
            }}
          >
            <div
              role="button"
              tabIndex={0}
              aria-expanded={openSections.cannotDo}
              aria-controls="content-cannot-do"
              onClick={() => toggleSection('cannotDo')}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleSection('cannotDo');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                minHeight: '48px',
                userSelect: 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(162, 74, 43, 0.14)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#A24A2B',
                  }}
                >
                  <XCircle size={22} />
                </div>
                <h2
                  style={{
                    fontFamily: isDevanagari
                      ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                      : 'var(--font-display, "Fraunces", Georgia, serif)',
                    fontSize: '1.45rem',
                    color: '#1C110A',
                    fontWeight: '700',
                    margin: 0,
                  }}
                >
                  {t('guide.cannot_do_title')}
                </h2>
              </div>
              <ChevronDown
                size={22}
                color="#A24A2B"
                style={{
                  transform: openSections.cannotDo ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                }}
              />
            </div>

            {openSections.cannotDo && (
              <div id="content-cannot-do" style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {cannotDoItems.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.85rem',
                      padding: '0.75rem 1rem',
                      backgroundColor: 'rgba(162, 74, 43, 0.05)',
                      borderRadius: '10px',
                    }}
                  >
                    <X
                      size={18}
                      color="#A24A2B"
                      style={{ flexShrink: 0, marginTop: '0.2rem' }}
                    />
                    <span
                      style={{
                        fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                        fontSize: '0.96rem',
                        color: '#4A3728',
                        lineHeight: 1.5,
                      }}
                    >
                      {item}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Footer Back Button */}
        <div style={{ marginTop: '3.5rem', textAlign: 'center' }}>
          <button
            type="button"
            onClick={handleBack}
            style={{
              minHeight: '48px',
              padding: '0.75rem 2rem',
              backgroundColor: '#1C110A',
              color: '#F4EAD3',
              border: '1px solid #C99A3C',
              borderRadius: '9999px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#2C1B10';
              e.currentTarget.style.color = '#FFFFFF';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#1C110A';
              e.currentTarget.style.color = '#F4EAD3';
            }}
          >
            <ArrowLeft size={18} />
            <span>{t('guide.back')}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
