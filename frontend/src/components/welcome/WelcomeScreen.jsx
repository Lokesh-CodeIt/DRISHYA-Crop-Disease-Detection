/**
 * WelcomeScreen.jsx - DRISHYA Cinematic Opening Experience
 *
 * Implements:
 * - Cinematic black-canvas opening (Darkness → Logo → Light → World)
 * - Real PNG logo asset (/logo/drishya-logo.png) as the visual star
 * - GSAP single controlled timeline with gsap.context()
 * - prefers-reduced-motion: show immediately with no animation
 * - Animation runs only on mount — does NOT replay on state changes
 * - Logout, language switching, form typing → NO animation replay
 * - Visual language selector (English, हिन्दी, मराठी)
 * - Real Sign In & Create Account integration (unchanged)
 */

import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import DrishyaLogo from '../brand/DrishyaLogo';
import CropIdentity from '../brand/CropIdentity';
import LanguageSelector from '../auth/LanguageSelector';
import AuthForm from '../auth/AuthForm';

export default function WelcomeScreen() {
  const { user, isAuthenticated, navigate, logout } = useAuth();
  const { t, language } = useLanguage();

  // ── Cinematic layer refs ─────────────────────────────────────────────────
  const containerRef    = useRef(null);
  const cinematicRef    = useRef(null);   // full-screen black canvas
  const logoWrapRef     = useRef(null);   // centered logo wrapper (cinematic phase)
  const glowLayerRef    = useRef(null);   // warm glow disc behind logo
  const bloomLayerRef   = useRef(null);   // expanding warm light bloom
  const worldRef        = useRef(null);   // the actual welcome UI world

  // ── Inner UI refs (for staggered content reveal) ─────────────────────────
  const bgRef           = useRef(null);
  const lightRef        = useRef(null);
  const emblemRef       = useRef(null);
  const wordmarkRef     = useRef(null);
  const headlineRef     = useRef(null);
  const statementRef    = useRef(null);
  const badgeRef        = useRef(null);
  const langSelectorRef = useRef(null);
  const authPanelRef    = useRef(null);
  const apertureRef     = useRef(null);

  // ── Animation runs ONCE on mount only ────────────────────────────────────
  // Empty dependency array → fires once, cleaned up on unmount.
  // Language switches, form typing, login toggling → no effect.
  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      // Accessibility: skip cinematic, reveal immediately
      if (cinematicRef.current) cinematicRef.current.style.display = 'none';
      if (worldRef.current) {
        worldRef.current.style.opacity = '1';
        worldRef.current.style.visibility = 'visible';
      }
      gsap.set(
        [
          bgRef.current, lightRef.current, apertureRef.current,
          emblemRef.current, wordmarkRef.current, langSelectorRef.current,
          badgeRef.current, headlineRef.current, statementRef.current,
          authPanelRef.current,
        ],
        { opacity: 1, y: 0, x: 0, scale: 1, clearProps: 'all' }
      );
      return;
    }

    const ctx = gsap.context(() => {
      // ── Initial state: cinematic canvas fills screen, world hidden ─────
      gsap.set(cinematicRef.current, { opacity: 1, display: 'flex' });
      gsap.set(worldRef.current, { opacity: 0, visibility: 'hidden' });

      // Logo: tiny, invisible, no scale bump
      gsap.set(logoWrapRef.current,  { opacity: 0, scale: 0.72 });
      gsap.set(glowLayerRef.current, { opacity: 0, scale: 0.5 });
      gsap.set(bloomLayerRef.current, { opacity: 0, scale: 0.3 });

      // World content: all hidden
      gsap.set(bgRef.current,           { opacity: 0 });
      gsap.set(lightRef.current,        { opacity: 0, scale: 0.85 });
      gsap.set(apertureRef.current,     { opacity: 0, scale: 0.94 });
      gsap.set(emblemRef.current,       { opacity: 0, y: -14, scale: 0.92 });
      gsap.set(wordmarkRef.current,     { opacity: 0, x: -12 });
      gsap.set(langSelectorRef.current, { opacity: 0, y: -8 });
      gsap.set(badgeRef.current,        { opacity: 0, y: 14 });
      gsap.set(headlineRef.current,     { opacity: 0, y: 20 });
      gsap.set(statementRef.current,    { opacity: 0, y: 18 });
      gsap.set(authPanelRef.current,    { opacity: 0, y: 24 });

      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

      // ── FRAME 1 · 0.0 – 0.4 s · Complete darkness ────────────────────
      // (cinematic canvas is already black — just hold)

      // ── FRAME 2 · 0.4 – 1.1 s · Logo emerges from darkness ──────────
      tl.to(logoWrapRef.current, {
        opacity: 1, scale: 1, duration: 0.7, ease: 'sine.inOut',
      }, 0.4)

      // ── FRAME 3 · 1.1 – 1.8 s · Warm glow illumination builds ───────
      .to(glowLayerRef.current, {
        opacity: 1, scale: 1, duration: 0.9, ease: 'sine.out',
      }, 0.9)

      // ── FRAME 4 · 1.8 – 2.5 s · Cinematic warm bloom expands ────────
      .to(bloomLayerRef.current, {
        opacity: 1, scale: 1, duration: 0.75, ease: 'power1.inOut',
      }, 1.6)
      .to(bloomLayerRef.current, {
        scale: 3.5, opacity: 0.88, duration: 0.8, ease: 'power2.inOut',
      }, 2.0)

      // ── FRAME 5 · 2.5 – 3.2 s · Reveal the DRISHYA world ─────────────
      // Fade out cinematic canvas
      .to(cinematicRef.current, {
        opacity: 0, duration: 0.5, ease: 'power2.inOut',
        onStart: () => {
          if (worldRef.current) {
            worldRef.current.style.opacity = '0';
            worldRef.current.style.visibility = 'visible';
          }
        },
        onComplete: () => {
          if (cinematicRef.current) cinematicRef.current.style.display = 'none';
        },
      }, 2.5)

      // World background establishes
      .to(bgRef.current,    { opacity: 1, duration: 0.6, ease: 'sine.inOut' }, 2.5)
      .to(lightRef.current, { opacity: 1, scale: 1, duration: 0.9, ease: 'sine.out' }, 2.55)
      .to(apertureRef.current, { opacity: 1, scale: 1, duration: 1.0, ease: 'power2.out' }, 2.6)

      // World logo (in header)
      .to(emblemRef.current,    { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: 'power2.out' }, 2.6)
      .to(wordmarkRef.current,  { opacity: 1, x: 0, duration: 0.55, ease: 'power2.out' }, 2.75)
      .to(langSelectorRef.current, { opacity: 1, y: 0, duration: 0.5 }, 2.8)

      // Editorial text
      .to(badgeRef.current,     { opacity: 1, y: 0, duration: 0.45 }, 2.85)
      .to(headlineRef.current,  { opacity: 1, y: 0, duration: 0.6  }, 2.9)
      .to(statementRef.current, { opacity: 1, y: 0, duration: 0.55 }, 3.0)

      // Auth panel — the world opens
      .to(worldRef.current, {
        opacity: 1, duration: 0.4, ease: 'power2.out',
      }, 2.55)
      .to(authPanelRef.current, {
        opacity: 1, y: 0, duration: 0.7, ease: 'power2.out',
      }, 3.0);

    }, containerRef);

    return () => ctx.revert();
  }, []); // ← empty array: ONE-TIME mount animation only

  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  return (
    <div ref={containerRef} style={{ position: 'relative', minHeight: '100vh', width: '100%' }}>

      {/* ── CINEMATIC CANVAS ─────────────────────────────────────────────
          Full-screen black. Sits on top of everything during opening.
          Removed from DOM after animation completes.
      ──────────────────────────────────────────────────────────────────── */}
      <div
        ref={cinematicRef}
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 9999,
          background: '#0A0603',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        {/* Warm radial glow — builds behind the logo */}
        <div
          ref={glowLayerRef}
          style={{
            position: 'absolute',
            width: '420px',
            height: '420px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(242, 193, 78, 0.22) 0%, rgba(201, 154, 60, 0.14) 35%, rgba(138, 90, 43, 0.06) 60%, transparent 75%)',
            filter: 'blur(40px)',
            pointerEvents: 'none',
          }}
        />

        {/* Bloom expansion layer — warm ivory/gold disc that fills screen */}
        <div
          ref={bloomLayerRef}
          style={{
            position: 'absolute',
            width: '380px',
            height: '380px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(251, 246, 234, 0.96) 0%, rgba(242, 193, 78, 0.75) 30%, rgba(201, 154, 60, 0.4) 55%, rgba(28, 17, 10, 0.0) 78%)',
            pointerEvents: 'none',
          }}
        />

        {/* The real DRISHYA logo PNG — centered, emerges from darkness */}
        <div
          ref={logoWrapRef}
          style={{
            position: 'relative',
            zIndex: 2,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1.2rem',
          }}
        >
          <img
            src="/logo/drishya-logo.png"
            alt="DRISHYA"
            style={{
              width: 'clamp(110px, 18vw, 160px)',
              height: 'auto',
              objectFit: 'contain',
              display: 'block',
              filter: 'drop-shadow(0 0 28px rgba(242, 193, 78, 0.45)) drop-shadow(0 0 8px rgba(201, 154, 60, 0.3))',
              userSelect: 'none',
              pointerEvents: 'none',
            }}
            draggable={false}
          />
          {/* Brand name under logo on cinematic canvas */}
          <div
            style={{
              fontFamily: 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: 'clamp(1.1rem, 3vw, 1.55rem)',
              fontWeight: '700',
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: 'rgba(244, 234, 211, 0.92)',
              textShadow: '0 0 30px rgba(242, 193, 78, 0.4)',
            }}
          >
            DRISHYA
          </div>
        </div>
      </div>

      {/* ── WELCOME WORLD ────────────────────────────────────────────────
          The actual screen. Hidden until cinematic bloom reveals it.
      ──────────────────────────────────────────────────────────────────── */}
      <div
        ref={worldRef}
        className="drishya-welcome-screen"
        style={{ visibility: 'hidden' }}
      >
        {/* Background ambient layer */}
        <div
          ref={bgRef}
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(circle at 72% 28%, rgba(201, 154, 60, 0.09) 0%, transparent 60%)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />

        {/* Ambient warm backlight glow */}
        <div
          ref={lightRef}
          aria-hidden="true"
          style={{
            position: 'absolute',
            top: '15%',
            right: '8%',
            width: '550px',
            height: '550px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(242, 193, 78, 0.18) 0%, rgba(138, 90, 43, 0.09) 45%, transparent 70%)',
            filter: 'blur(60px)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />

        {/* Top Navigation Row: Real PNG Logo + Language Selector */}
        <header className="drishya-header">
          <div>
            <DrishyaLogo
              size={52}
              showWordmark={true}
              emblemRef={emblemRef}
              wordmarkRef={wordmarkRef}
            />
          </div>

          <div ref={langSelectorRef}>
            <LanguageSelector />
          </div>
        </header>

        {/* Main Editorial Hero & Auth Section */}
        <main
          style={{
            width: '100%',
            maxWidth: '1240px',
            margin: 'auto auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            alignItems: 'center',
            gap: '3.5rem',
            padding: '2rem 0',
            position: 'relative',
            zIndex: 10,
          }}
        >
          {/* Left Editorial Text Column */}
          <div style={{ maxWidth: '540px' }}>
            {/* Botanical concept pill */}
            <div
              ref={badgeRef}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'rgba(201, 154, 60, 0.12)',
                border: '1px solid rgba(201, 154, 60, 0.3)',
                borderRadius: '9999px',
                padding: '0.35rem 0.9rem',
                color: 'var(--c-antique-gold, #C99A3C)',
                fontSize: '0.82rem',
                fontWeight: '500',
                marginBottom: '1.25rem',
                letterSpacing: '0.04em',
              }}
            >
              <span>🍃</span>
              <span>{t('auth.concept')}</span>
            </div>

            {/* Primary Brand Headline */}
            <h1
              ref={headlineRef}
              style={{
                fontFamily: isHindiOrMarathi
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: 'clamp(2.3rem, 5.5vw, 3.8rem)',
                fontWeight: '700',
                lineHeight: isHindiOrMarathi ? 1.3 : 1.15,
                color: 'var(--c-ivory, #FBF6EA)',
                letterSpacing: isHindiOrMarathi ? '0' : '-0.02em',
                marginBottom: '1.2rem',
              }}
            >
              {t('auth.headline')}
            </h1>

            {/* Brand Statement */}
            <p
              ref={statementRef}
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: 'clamp(1.05rem, 1.8vw, 1.25rem)',
                color: 'var(--c-dust, #D8C7A3)',
                lineHeight: 1.6,
                marginBottom: '2rem',
                maxWidth: '480px',
              }}
            >
              {t('auth.brand_statement')}
            </p>

            {/* Status Badge: Supported Crops — real crop photos */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.25rem',
                color: 'var(--c-dusk, #6F5F52)',
              }}
            >
              <CropIdentity crop="turmeric" size={28} fontSize="0.85rem" />
              <span style={{ color: 'rgba(201, 154, 60, 0.35)', fontSize: '0.9rem' }}>•</span>
              <CropIdentity crop="citrus" size={28} fontSize="0.85rem" />
            </div>
          </div>

          {/* Right Composition Column: Auth Panel */}
          <div
            ref={authPanelRef}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
            }}
          >
            {/* Real DRISHYA logo PNG as atmospheric watermark behind auth panel */}
            <div
              ref={apertureRef}
              aria-hidden="true"
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '420px',
                maxWidth: '110%',
                zIndex: 0,
                pointerEvents: 'none',
              }}
            >
              <img
                src="/logo/drishya-logo.png"
                alt=""
                style={{
                  width: '100%',
                  height: 'auto',
                  objectFit: 'contain',
                  opacity: 0.06,
                  filter: 'sepia(1) saturate(1.5) hue-rotate(-10deg)',
                  display: 'block',
                  userSelect: 'none',
                  pointerEvents: 'none',
                }}
                draggable={false}
              />
            </div>

            {/* Authentication Form */}
            <div style={{ position: 'relative', zIndex: 5, width: '100%', display: 'flex', justifyContent: 'center' }}>
              {isAuthenticated && user ? (
                <div
                  style={{
                    background: 'linear-gradient(180deg, #27180E 0%, #1A0E06 100%)',
                    border: '1px solid var(--border-rich, rgba(201, 154, 60, 0.35))',
                    borderRadius: '20px',
                    padding: '2.5rem',
                    maxWidth: '440px',
                    width: '100%',
                    textAlign: 'center',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8)',
                  }}
                >
                  <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🌿</div>
                  <h2
                    style={{
                      fontFamily: isHindiOrMarathi ? 'var(--font-devanagari-display)' : 'var(--font-display)',
                      fontSize: '1.5rem',
                      color: '#FBF6EA',
                      marginBottom: '0.5rem',
                    }}
                  >
                    {t('auth.welcome_back', { name: user.name })}
                  </h2>
                  <p style={{ color: 'var(--c-dust, #D8C7A3)', fontSize: '0.9rem', marginBottom: '1.8rem' }}>
                    {user.email}
                  </p>

                  <button
                    type="button"
                    id="btn-enter-studio"
                    onClick={() => navigate('/home')}
                    style={{
                      width: '100%',
                      minHeight: '50px',
                      padding: '0.75rem 1.5rem',
                      background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 60%, #8A5A2B 100%)',
                      border: 'none',
                      borderRadius: '10px',
                      color: '#140C07',
                      fontWeight: '700',
                      fontSize: '1.05rem',
                      cursor: 'pointer',
                      boxShadow: '0 8px 20px rgba(201, 154, 60, 0.35)',
                      marginBottom: '1rem',
                    }}
                  >
                    {t('auth.enter_studio')}
                  </button>

                  <button
                    type="button"
                    onClick={logout}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#E07A5F',
                      fontSize: '0.85rem',
                      cursor: 'pointer',
                      textDecoration: 'underline',
                    }}
                  >
                    {t('nav.logout')}
                  </button>
                </div>
              ) : (
                <AuthForm onAuthenticated={() => navigate('/home')} />
              )}
            </div>
          </div>
        </main>

        {/* Editorial Footer */}
        <footer
          style={{
            width: '100%',
            maxWidth: '1240px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            paddingTop: '1.5rem',
            borderTop: '1px solid rgba(201, 154, 60, 0.12)',
            fontSize: '0.78rem',
            color: 'var(--c-dusk, #6F5F52)',
            position: 'relative',
            zIndex: 10,
          }}
        >
          <span>DRISHYA • Deep Robust Intelligence for Sustainable Harvest & Yield Assessment</span>
          <span>{t('app.footer_credits')}</span>
        </footer>
      </div>
    </div>
  );
}
