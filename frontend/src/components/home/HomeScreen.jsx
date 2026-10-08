/**
 * HomeScreen.jsx - The Real DRISHYA Home Screen
 *
 * Implements:
 * - Thoughtful agricultural field companion aesthetic
 * - Primary headline: "Which leaf shall we look at today?"
 * - Supporting farmer-first copy
 * - Turmeric & Citrus botanical field journal selection tiles
 * - Recent Leaf Journal preview with real user-scoped history records
 * - Truthful field photography tips teaser
 * - Restrained GSAP entrance motion with prefers-reduced-motion respect
 */

import React, { useEffect, useRef } from 'react';
import { BookOpen, Info, ArrowRight } from 'lucide-react';
import gsap from 'gsap';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import CropTile from './CropTile';
import RecentJournalPreview from './RecentJournalPreview';
import PhotoTipsTeaser from './PhotoTipsTeaser';

export default function HomeScreen({ onSelectCrop }) {
  const { user, navigate } = useAuth();
  const { t, language } = useLanguage();

  const containerRef = useRef(null);
  const heroRef = useRef(null);
  const cropGridRef = useRef(null);
  const journalRef = useRef(null);
  const tipsRef = useRef(null);

  // GSAP Entrance Timeline
  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      gsap.set(
        [heroRef.current, cropGridRef.current, journalRef.current, tipsRef.current],
        { opacity: 1, y: 0, clearProps: 'all' }
      );
      return;
    }

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

      gsap.set([heroRef.current, cropGridRef.current, journalRef.current, tipsRef.current], {
        opacity: 0,
        y: 20,
      });

      tl.to(heroRef.current, { opacity: 1, y: 0, duration: 0.65 }, 0.1)
        .to(cropGridRef.current, { opacity: 1, y: 0, duration: 0.7 }, 0.25)
        .to(journalRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.45)
        .to(tipsRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.6);
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const handleCropSelection = (cropKey) => {
    if (onSelectCrop) {
      onSelectCrop(cropKey);
    } else {
      navigate(`/check?crop=${cropKey}`);
    }
  };

  const handleCheckLeafAction = () => {
    navigate('/check');
  };

  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  return (
    <div
      ref={containerRef}
      className="drishya-home-screen"
      style={{
        width: '100%',
        minHeight: 'calc(100vh - 65px)',
        backgroundColor: '#FBF6EA',
        color: '#1C110A',
        padding: '2.5rem 1.5rem 5rem',
      }}
    >
      <div
        style={{
          maxWidth: '1100px',
          margin: '0 auto',
        }}
      >
        {/* Main Hero Header */}
        <header
          ref={heroRef}
          style={{
            textAlign: 'center',
            marginBottom: '3rem',
            padding: '1rem 0',
          }}
        >
          {/* Concept Pill */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              background: 'rgba(201, 154, 60, 0.16)',
              border: '1px solid rgba(201, 154, 60, 0.35)',
              borderRadius: '9999px',
              padding: '0.35rem 0.95rem',
              color: '#8A5A2B',
              fontSize: '0.82rem',
              fontWeight: '600',
              marginBottom: '1.25rem',
              letterSpacing: '0.04em',
            }}
          >
            <span>🍃</span>
            <span>{t('auth.concept')}</span>
          </div>

          {/* Primary Heading */}
          <h1
            style={{
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: 'clamp(2.1rem, 4.2vw, 3.2rem)',
              fontWeight: '700',
              color: '#1C110A',
              lineHeight: isHindiOrMarathi ? 1.3 : 1.18,
              letterSpacing: isHindiOrMarathi ? '0' : '-0.02em',
              marginBottom: '0.9rem',
            }}
          >
            {t('home.hero_title')}
          </h1>

          {/* Supporting Copy */}
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: 'clamp(1.05rem, 1.8vw, 1.25rem)',
              color: '#4A3728',
              maxWidth: '640px',
              margin: '0 auto',
              lineHeight: 1.6,
            }}
          >
            {t('home.hero_subtitle')}
          </p>
        </header>

        {/* Botanical Crop Selection Grid */}
        <section
          ref={cropGridRef}
          aria-label={t('home.select_prompt')}
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '2rem',
            marginBottom: '3rem',
          }}
        >
          {/* 1. Turmeric Crop Tile */}
          <CropTile
            cropKey="turmeric"
            title={t('home.crop_turmeric_title')}
            scientificName="Curcuma longa L."
            description={t('home.crop_turmeric_desc')}
            actionText={t('home.crop_turmeric_action')}
            imageSrc="/logo/turmuric.jpg"
            onSelect={handleCropSelection}
          />

          {/* 2. Citrus Crop Tile */}
          <CropTile
            cropKey="citrus"
            title={t('home.crop_citrus_title')}
            scientificName="Citrus limon (L.)"
            description={t('home.crop_citrus_desc')}
            actionText={t('home.crop_citrus_action')}
            imageSrc="/logo/citrus.jpg"
            onSelect={handleCropSelection}
          />
        </section>

        {/* Recent Leaves Preview ("My Leaf Journal") */}
        <div ref={journalRef}>
          <RecentJournalPreview onCheckLeaf={handleCheckLeafAction} />
        </div>

        {/* Truthful Field Photography Tips Teaser */}
        <div ref={tipsRef}>
          <PhotoTipsTeaser />
        </div>

        {/* Field Resources & System Documentation */}
        <section
          aria-label="Field Resources & System Documentation"
          style={{
            margin: '1.5rem 0 3.5rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem',
          }}
        >
          {/* Field Guide Card */}
          <div
            style={{
              padding: '1.6rem',
              background: '#FFFDF9',
              border: '1.5px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '16px',
              boxShadow: '0 4px 16px rgba(28, 17, 10, 0.03)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: '#8A5A2B',
                  fontSize: '0.82rem',
                  fontWeight: '700',
                  marginBottom: '0.5rem',
                }}
              >
                <BookOpen size={16} />
                <span>FIELD KNOWLEDGE</span>
              </div>
              <h3
                style={{
                  fontFamily: isHindiOrMarathi
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.25rem',
                  color: '#1C110A',
                  fontWeight: '700',
                  margin: '0 0 0.45rem 0',
                }}
              >
                {t('guide.title')}
              </h3>
              <p
                style={{
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '0.92rem',
                  color: '#554232',
                  lineHeight: 1.5,
                  margin: '0 0 1.25rem 0',
                }}
              >
                {t('guide.subtitle')}
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate('/guide')}
              style={{
                minHeight: '44px',
                padding: '0.6rem 1.2rem',
                backgroundColor: '#FAF5EB',
                border: '1px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                color: '#8A5A2B',
                fontSize: '0.9rem',
                fontWeight: '700',
                cursor: 'pointer',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.45rem',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#F4EAD3';
                e.currentTarget.style.borderColor = '#8A5A2B';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#FAF5EB';
                e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.4)';
              }}
            >
              <span>{t('guide.title')}</span>
              <ArrowRight size={16} />
            </button>
          </div>

          {/* About DRISHYA Card */}
          <div
            style={{
              padding: '1.6rem',
              background: '#24160E',
              border: '1.5px solid rgba(201, 154, 60, 0.35)',
              borderRadius: '16px',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: '#F2C14E',
                  fontSize: '0.82rem',
                  fontWeight: '700',
                  marginBottom: '0.5rem',
                }}
              >
                <Info size={16} />
                <span>SYSTEM ARCHITECTURE</span>
              </div>
              <h3
                style={{
                  fontFamily: isHindiOrMarathi
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.25rem',
                  color: '#FAF4E6',
                  fontWeight: '700',
                  margin: '0 0 0.45rem 0',
                }}
              >
                {t('about.title')}
              </h3>
              <p
                style={{
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '0.92rem',
                  color: '#D8C7A3',
                  lineHeight: 1.5,
                  margin: '0 0 1.25rem 0',
                }}
              >
                {t('about.subtitle')}
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate('/about')}
              style={{
                minHeight: '44px',
                padding: '0.6rem 1.2rem',
                backgroundColor: 'rgba(201, 154, 60, 0.15)',
                border: '1px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                color: '#F2C14E',
                fontSize: '0.9rem',
                fontWeight: '700',
                cursor: 'pointer',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.45rem',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(201, 154, 60, 0.3)';
                e.currentTarget.style.borderColor = '#F2C14E';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(201, 154, 60, 0.15)';
                e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.4)';
              }}
            >
              <span>{t('about.title')}</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
