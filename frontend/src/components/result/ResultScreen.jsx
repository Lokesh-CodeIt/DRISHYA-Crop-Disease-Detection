/**
 * ResultScreen.jsx - The DRISHYA Diagnosis & Insights Experience
 *
 * Implements ML Upgrade Step C:
 * 1. Warm daylight botanical journal aesthetic (parchment, ivory, antique gold, espresso, terracotta)
 * 2. Visual Hero: Large authentic uploaded leaf photograph, crop identity badge, clear finding headline
 * 3. Confidence Arc: Custom botanical circular/partial-ring SVG arc animated via GSAP,
 *    strictly consuming backend calibrated confidence (with fallback transparency)
 * 4. Prediction Breakdown: Stacked flowing botanical ribbons for top candidates with GSAP length transitions
 * 5. DRISHYA Insights: Signature product feature with Original ↔ Grad-CAM overlay toggle,
 *    authentic attention-region thumbnails (direct crop_base64), interactive click-to-focus inspection,
 *    and scientific disclaimer ("Model attention is not proof of causation")
 * 6. Truthful Actionable Guidance: Verified advisory content or truthful localized fallback (no invented chemicals)
 * 7. Technical Details: Secondary expandable drawer displaying real model metadata and calibration parameters
 * 8. SpeechSynthesis Listen and Web Share / Clipboard sharing with privacy safety
 * 9. Local UI Field Feedback ("Does this match what you see in the field?")
 * 10. Strict mobile responsive stacking (375px, 390px, 768px, 1024px, 1440px+) with zero horizontal overflow
 * 11. Full prefers-reduced-motion compliance
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft,
  Volume2,
  VolumeX,
  Share2,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Camera,
  Home,
  Check,
  BookOpen,
} from 'lucide-react';
import gsap from 'gsap';
import { useLanguage } from '../../context/LanguageContext';
import CropIdentity from '../brand/CropIdentity';
import ConfidenceArc from './ConfidenceArc';
import PredictionRibbons from './PredictionRibbons';
import DrishyaInsights from './DrishyaInsights';
import ConditionKnowledge from './ConditionKnowledge';

export default function ResultScreen({
  diagnosisPayload = null,
  onCheckAnother,
  onBackToHome,
}) {
  const { t, language, formatDate, formatTime, getConditionDisplayName } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  // Component state
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechUnavailable, setSpeechUnavailable] = useState(false);
  const [copiedToast, setCopiedToast] = useState(false);
  const [technicalOpen, setTechnicalOpen] = useState(false);
  const [feedbackChoice, setFeedbackChoice] = useState(null); // 'yes' | 'no' | null

  // GSAP animation refs
  const screenRef = useRef(null);
  const heroSectionRef = useRef(null);
  const metricsGridRef = useRef(null);
  const insightsSectionRef = useRef(null);
  const advisorySectionRef = useRef(null);
  const technicalSectionRef = useRef(null);

  // Parse diagnosis payload
  const response = diagnosisPayload?.diagnosisResponse;
  const prediction = response?.prediction;
  const calibration = response?.calibration;
  const explanation = response?.explanation;
  const advisory = response?.advisory;

  const hasValidPayload = Boolean(
    diagnosisPayload &&
    diagnosisPayload.imageObjectUrl &&
    response &&
    prediction &&
    typeof prediction.predicted_class === 'string'
  );

  // ─── GSAP Entrance Animations ─────────────────────────────────────────────
  useEffect(() => {
    if (!hasValidPayload || !screenRef.current) return;

    const prefersReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const ctx = gsap.context(() => {
      const cards = [
        heroSectionRef.current,
        metricsGridRef.current,
        insightsSectionRef.current,
        advisorySectionRef.current,
        technicalSectionRef.current,
      ].filter(Boolean);

      if (prefersReduced) {
        gsap.set(cards, { opacity: 1 });
        return;
      }

      gsap.set(cards, { opacity: 0, y: 18 });
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

      tl.to(cards, {
        opacity: 1,
        y: 0,
        duration: 0.5,
        stagger: 0.08,
      });
    }, screenRef);

    return () => ctx.revert();
  }, [hasValidPayload]);

  // Clean up speech synthesis on unmount
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // ─── STATE A: Missing or invalid payload (Direct access or refresh) ───────
  if (!hasValidPayload) {
    return (
      <div
        style={{
          width: '100%',
          minHeight: 'calc(100vh - 65px)',
          backgroundColor: '#FBF6EA',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2.5rem 1.5rem',
        }}
      >
        <div
          style={{
            maxWidth: '500px',
            width: '100%',
            background: '#FAF5EB',
            border: '1.5px solid rgba(201, 154, 60, 0.35)',
            borderRadius: '20px',
            padding: '2.5rem 2rem',
            textAlign: 'center',
            boxShadow: '0 12px 32px rgba(28, 17, 10, 0.06)',
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'rgba(201, 154, 60, 0.15)',
              border: '1px solid rgba(201, 154, 60, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem',
              color: '#8A5A2B',
            }}
          >
            <HelpCircle size={32} aria-hidden="true" />
          </div>

          <h2
            style={{
              fontFamily: isDevanagari
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.6rem',
              color: '#1C110A',
              marginBottom: '0.65rem',
            }}
          >
            {t('result.no_result_title')}
          </h2>

          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1rem',
              color: '#6F5F52',
              lineHeight: 1.55,
              marginBottom: '2rem',
            }}
          >
            {t('result.no_result_desc')}
          </p>

          <button
            type="button"
            id="btn-result-go-to-check"
            onClick={onCheckAnother}
            style={{
              minHeight: '48px',
              padding: '0.75rem 1.8rem',
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
            <Camera size={18} aria-hidden="true" />
            <span>{t('result.go_to_check')}</span>
          </button>
        </div>
      </div>
    );
  }

  // ─── STATE B: Real Diagnosis Findings ─────────────────────────────────────
  const crop = diagnosisPayload.crop || response.crop || 'turmeric';
  const cropDisplayName =
    crop === 'turmeric' ? t('check.crop_turmeric') : t('check.crop_citrus');

  const rawClass = prediction.predicted_class;
  const isRejected = Boolean(prediction.is_rejected || calibration?.is_uncertain);
  const isHealthy = !isRejected && rawClass.toLowerCase().trim() === 'healthy';
  const conditionDisplayName = getConditionDisplayName(crop, rawClass);

  // Formatted date and time
  const observationDate = new Date();
  const formattedDate = formatDate(observationDate, language);
  const formattedTime = formatTime(observationDate, language);

  // Calibrated vs Raw Confidence Resolution
  const isCalibrationActive = Boolean(calibration?.is_active);
  const calibratedConf = prediction.calibrated_confidence ?? calibration?.calibrated_confidence ?? null;
  const rawConf = prediction.confidence ?? calibration?.raw_confidence ?? 0.0;
  const activeConfidenceVal = isCalibrationActive && typeof calibratedConf === 'number'
    ? calibratedConf
    : rawConf;
  const activeConfidencePercent = Math.round(activeConfidenceVal * 100);

  // Headline & Status styling
  let headline = '';
  let statusBadgeText = '';
  let statusBadgeBg = '';
  let statusBadgeBorder = '';
  let statusBadgeColor = '';
  let statusIcon = null;

  if (isRejected) {
    headline = t('result.headline_uncertain');
    statusBadgeText = t('result.state_unsure');
    statusBadgeBg = 'rgba(162, 74, 43, 0.16)';
    statusBadgeBorder = 'rgba(162, 74, 43, 0.45)';
    statusBadgeColor = '#8F3819';
    statusIcon = <AlertTriangle size={16} aria-hidden="true" />;
  } else if (isHealthy) {
    headline = t('result.headline_healthy');
    statusBadgeText = t('result.state_healthy');
    statusBadgeBg = 'rgba(94, 107, 56, 0.15)';
    statusBadgeBorder = 'rgba(94, 107, 56, 0.4)';
    statusBadgeColor = '#3B5E2B';
    statusIcon = <CheckCircle2 size={16} aria-hidden="true" />;
  } else {
    headline = t('result.headline_condition', { condition: conditionDisplayName });
    statusBadgeText = conditionDisplayName;
    statusBadgeBg = 'rgba(162, 74, 43, 0.12)';
    statusBadgeBorder = 'rgba(162, 74, 43, 0.35)';
    statusBadgeColor = '#8F3819';
    statusIcon = <AlertTriangle size={16} aria-hidden="true" />;
  }

  // Explanation description
  let explanationDesc = '';
  if (isRejected) {
    explanationDesc = t('result.explanation_uncertain_desc');
  } else if (isHealthy) {
    explanationDesc = t('result.explanation_healthy_desc');
  } else {
    explanationDesc = t('result.explanation_condition_desc', { condition: conditionDisplayName });
  }

  // Advisory verification
  const hasVerifiedAdvisory = Boolean(
    advisory &&
    (
      (advisory.cultural_preventative_measures && advisory.cultural_preventative_measures.length > 0) ||
      (advisory.organic_biological_controls && advisory.organic_biological_controls.length > 0) ||
      (advisory.chemical_controls && advisory.chemical_controls.length > 0)
    )
  );

  // Model metadata transparently corresponding to registry.py
  const isTurmeric = crop === 'turmeric';
  const modelArchitecture = isTurmeric ? 'ConvNeXt-Tiny' : 'EfficientNetV2-S';
  const modelResolution = isTurmeric ? '224 × 224' : '384 × 384';
  const modelSeed = 42;
  const targetFeatureLayer = explanation?.target_layer || 'features.7';

  // ─── Listen (SpeechSynthesis) handler ──────────────────────────────────────
  const handleToggleListen = () => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setSpeechUnavailable(true);
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    window.speechSynthesis.cancel();

    // Spoken text includes: crop, finding, model confidence, and concise explanation
    const confidenceText = `${t('result.model_confidence')}: ${activeConfidencePercent} percent.`;
    const spokenText = `${cropDisplayName}. ${headline}. ${confidenceText} ${explanationDesc}`;
    const utterance = new SpeechSynthesisUtterance(spokenText);

    const langCodes = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' };
    utterance.lang = langCodes[language] || 'en-IN';
    utterance.rate = 0.95;

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => {
      setIsSpeaking(false);
      setSpeechUnavailable(true);
    };

    setIsSpeaking(true);
    setSpeechUnavailable(false);
    window.speechSynthesis.speak(utterance);
  };

  // ─── Share handler ────────────────────────────────────────────────────────
  const handleShare = async () => {
    const shareText = `DRISHYA: ${cropDisplayName} — ${headline}. ${t('result.model_confidence')}: ${activeConfidencePercent}%. (${formattedDate})`;

    if (typeof navigator !== 'undefined' && navigator.share) {
      try {
        await navigator.share({
          title: t('result.share_title'),
          text: shareText,
        });
        return;
      } catch (err) {
        if (err.name === 'AbortError') return;
      }
    }

    // Fallback: clipboard
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(shareText);
        setCopiedToast(true);
        setTimeout(() => setCopiedToast(false), 2500);
      } catch (e) {
        // Safe fallback
      }
    }
  };

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
      <div style={{ maxWidth: '980px', margin: '0 auto' }}>

        {/* Top Navigation Row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.5rem',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}
        >
          {/* Back to Home */}
          <button
            type="button"
            id="btn-result-back-home"
            onClick={onBackToHome}
            style={{
              minHeight: '48px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              background: 'none',
              border: 'none',
              color: '#6F5F52',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.9rem',
              fontWeight: '600',
              cursor: 'pointer',
              padding: '0.4rem 0.2rem',
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#3A2412')}
            onMouseLeave={(e) => (e.currentTarget.style.color = '#6F5F52')}
            aria-label={t('home.back_to_home')}
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>{t('home.back_to_home')}</span>
          </button>

          {/* Action Tools: Listen + Share */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {/* Listen Button */}
            <button
              type="button"
              id="btn-result-listen"
              onClick={handleToggleListen}
              style={{
                minHeight: '48px',
                padding: '0.5rem 1rem',
                background: isSpeaking ? 'rgba(201, 154, 60, 0.25)' : '#FAF5EB',
                border: '1.5px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                color: '#3A2412',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.88rem',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                transition: 'all 0.15s ease',
              }}
              aria-label={isSpeaking ? t('result.stop_listening') : t('result.listen_aria')}
              title={isSpeaking ? t('result.stop_listening') : t('result.listen')}
            >
              {isSpeaking ? (
                <>
                  <VolumeX size={17} color="#8A5A2B" aria-hidden="true" />
                  <span>{t('result.stop_listening')}</span>
                </>
              ) : (
                <>
                  <Volume2 size={17} color="#8A5A2B" aria-hidden="true" />
                  <span>{t('result.listen')}</span>
                </>
              )}
            </button>

            {/* Share Button */}
            <button
              type="button"
              id="btn-result-share"
              onClick={handleShare}
              style={{
                minHeight: '48px',
                padding: '0.5rem 1rem',
                background: '#FAF5EB',
                border: '1.5px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                color: '#3A2412',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.88rem',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                transition: 'all 0.15s ease',
              }}
              aria-label={t('result.share')}
              title={t('result.share')}
            >
              <Share2 size={16} color="#8A5A2B" aria-hidden="true" />
              <span>{t('result.share')}</span>
            </button>
          </div>
        </div>

        {/* Toast / Notification Feedbacks */}
        {copiedToast && (
          <div
            role="status"
            aria-live="polite"
            style={{
              padding: '0.65rem 1.1rem',
              background: '#23160E',
              color: '#F4EAD3',
              borderRadius: '8px',
              marginBottom: '1rem',
              fontSize: '0.9rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 6px 16px rgba(0, 0, 0, 0.15)',
            }}
          >
            <Check size={16} color="#F2C14E" aria-hidden="true" />
            <span>{t('result.share_copied')}</span>
          </div>
        )}

        {speechUnavailable && (
          <div
            role="alert"
            style={{
              padding: '0.65rem 1.1rem',
              background: 'rgba(201, 154, 60, 0.15)',
              border: '1px solid rgba(201, 154, 60, 0.35)',
              color: '#6F5F52',
              borderRadius: '8px',
              marginBottom: '1rem',
              fontSize: '0.88rem',
            }}
          >
            {t('result.listen_unavailable')}
          </div>
        )}

        {/* ─── 1. RESULT HERO: Leaf Photo + Headline + Finding ─────────────── */}
        <div
          ref={heroSectionRef}
          className="drishya-result-hero-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1.25fr',
            gap: '2rem',
            background: '#FAF5EB',
            border: '1.5px solid rgba(201, 154, 60, 0.35)',
            borderRadius: '24px',
            padding: '2rem',
            boxShadow: '0 12px 36px rgba(28, 17, 10, 0.05)',
            marginBottom: '1.75rem',
            alignItems: 'center',
          }}
        >
          {/* Left: Original Leaf Image (Visual Hero) */}
          <div
            style={{
              width: '100%',
              aspectRatio: '4 / 3',
              borderRadius: '16px',
              overflow: 'hidden',
              background: '#0D0704',
              border: '1.5px solid rgba(201, 154, 60, 0.3)',
              position: 'relative',
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
            }}
          >
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

            {/* Crop Badge Overlay */}
            <div
              style={{
                position: 'absolute',
                top: '0.75rem',
                left: '0.75rem',
                background: 'rgba(28, 17, 10, 0.85)',
                backdropFilter: 'blur(4px)',
                border: '1px solid rgba(201, 154, 60, 0.4)',
                borderRadius: '9999px',
                padding: '0.25rem 0.65rem 0.25rem 0.25rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                color: '#F4EAD3',
                fontSize: '0.8rem',
                fontWeight: '600',
              }}
            >
              <CropIdentity crop={crop} size={24} fontSize="0.8rem" style={{ color: '#F4EAD3' }} />
            </div>
          </div>

          {/* Right: Diagnosis Interpretation Headline */}
          <div>
            {/* Status Pill + Journal Confirmation */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                flexWrap: 'wrap',
                marginBottom: '0.75rem',
              }}
            >
              {/* Status badge */}
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  background: statusBadgeBg,
                  border: `1px solid ${statusBadgeBorder}`,
                  borderRadius: '9999px',
                  padding: '0.35rem 0.85rem',
                  color: statusBadgeColor,
                  fontSize: '0.82rem',
                  fontWeight: '700',
                  letterSpacing: '0.02em',
                }}
              >
                {statusIcon}
                <span>{statusBadgeText}</span>
              </div>

              {/* Journal confirmation badge (reflecting SQLite persistence) */}
              {response?.prediction_id && (
                <div
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    color: '#6F5F52',
                    fontSize: '0.8rem',
                    fontWeight: '500',
                  }}
                >
                  <BookOpen size={14} color="#8A5A2B" aria-hidden="true" />
                  <span>{t('result.saved_to_journal')}</span>
                </div>
              )}
            </div>

            {/* Headline */}
            <h1
              style={{
                fontFamily: isDevanagari
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: 'clamp(1.5rem, 2.5vw, 2.1rem)',
                fontWeight: '700',
                color: '#1C110A',
                lineHeight: 1.25,
                marginBottom: '0.85rem',
                letterSpacing: isDevanagari ? '0' : '-0.015em',
              }}
            >
              {headline}
            </h1>

            {/* Explanation description */}
            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '1rem',
                color: '#4A3728',
                lineHeight: 1.6,
                marginBottom: '1.25rem',
              }}
            >
              {explanationDesc}
            </p>

            {/* Observation timestamp */}
            <div
              style={{
                color: '#8A7768',
                fontSize: '0.85rem',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
              }}
            >
              <span>🕒</span>
              <span>
                {t('result.recorded_on', { date: formattedDate, time: formattedTime })}
              </span>
            </div>
          </div>
        </div>

        {/* ─── 2. METRICS ROW: Confidence Arc + Prediction Breakdown ───────── */}
        <div
          ref={metricsGridRef}
          className="drishya-metrics-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(280px, 1fr) 1.5fr',
            gap: '1.5rem',
            marginBottom: '1.75rem',
            alignItems: 'stretch',
          }}
        >
          {/* Custom Botanical Confidence Arc */}
          <ConfidenceArc
            calibratedConfidence={calibratedConf}
            rawConfidence={rawConf}
            isCalibrationActive={isCalibrationActive}
            isRejected={isRejected}
            rejectionThreshold={calibration?.rejection_threshold ?? 0.65}
          />

          {/* Stacked Flowing Ribbons Prediction Breakdown */}
          <PredictionRibbons
            crop={crop}
            predictedClass={rawClass}
            candidates={prediction.candidates || []}
            isCalibrationActive={isCalibrationActive}
          />
        </div>

        {/* ─── 3. SIGNATURE FEATURE: DRISHYA Insights ──────────────────────── */}
        <div ref={insightsSectionRef}>
          <DrishyaInsights
            imageObjectUrl={diagnosisPayload.imageObjectUrl}
            explanation={explanation}
          />
        </div>

        {/* ─── 4. CONDITION KNOWLEDGE & SAFE ADVISORY (STEP D) ─────────────── */}
        <div ref={advisorySectionRef}>
          <ConditionKnowledge
            knowledge={response?.knowledge}
            isRejected={isRejected}
            crop={crop}
            predictedClass={rawClass}
          />
        </div>

        {/* ─── 5. FIELD OBSERVATION FEEDBACK ───────────────────────────────── */}
        <div
          style={{
            background: '#FAF5EB',
            border: '1.5px solid rgba(201, 154, 60, 0.28)',
            borderRadius: '20px',
            padding: '1.5rem 1.75rem',
            marginBottom: '1.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <p style={{ fontWeight: '600', color: '#1C110A', fontSize: '0.95rem' }}>
              {t('result.feedback_prompt')}
            </p>
            {feedbackChoice && (
              <p style={{ color: '#3B5E2B', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                ✓ {t('result.feedback_thanks')}
              </p>
            )}
          </div>

          {!feedbackChoice && (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                type="button"
                id="btn-feedback-yes"
                onClick={() => setFeedbackChoice('yes')}
                style={{
                  minHeight: '44px',
                  padding: '0.45rem 1.1rem',
                  background: '#FBF6EA',
                  border: '1.5px solid rgba(201, 154, 60, 0.35)',
                  borderRadius: '8px',
                  color: '#3A2412',
                  fontWeight: '600',
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                }}
              >
                {t('result.feedback_yes')}
              </button>
              <button
                type="button"
                id="btn-feedback-no"
                onClick={() => setFeedbackChoice('no')}
                style={{
                  minHeight: '44px',
                  padding: '0.45rem 1.1rem',
                  background: '#FBF6EA',
                  border: '1.5px solid rgba(201, 154, 60, 0.35)',
                  borderRadius: '8px',
                  color: '#3A2412',
                  fontWeight: '600',
                  fontSize: '0.88rem',
                  cursor: 'pointer',
                }}
              >
                {t('result.feedback_no')}
              </button>
            </div>
          )}
        </div>

        {/* ─── 6. DETAILED ANALYSIS (Technical Transparency Drawer) ────────── */}
        <div
          ref={technicalSectionRef}
          style={{
            background: '#FAF5EB',
            border: '1.5px solid rgba(201, 154, 60, 0.28)',
            borderRadius: '20px',
            overflow: 'hidden',
            marginBottom: '2.5rem',
          }}
        >
          <button
            type="button"
            id="btn-toggle-detailed-analysis"
            onClick={() => setTechnicalOpen(!technicalOpen)}
            style={{
              width: '100%',
              minHeight: '52px',
              padding: '1rem 1.75rem',
              background: 'none',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              textAlign: 'left',
            }}
            aria-expanded={technicalOpen}
          >
            <div>
              <span
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.15rem',
                  fontWeight: '700',
                  color: '#1C110A',
                }}
              >
                {t('result.detailed_analysis')}
              </span>
            </div>
            {technicalOpen ? <ChevronUp size={20} color="#8A5A2B" /> : <ChevronDown size={20} color="#8A5A2B" />}
          </button>

          {technicalOpen && (
            <div
              style={{
                padding: '0 1.75rem 1.75rem',
                borderTop: '1px solid rgba(201, 154, 60, 0.2)',
                marginTop: '0.25rem',
              }}
            >
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: '1rem',
                  paddingTop: '1rem',
                }}
              >
                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_model')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>{modelArchitecture}</strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_seed')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>{modelSeed}</strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_input_size')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>{modelResolution}</strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_predicted_class')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>{rawClass}</strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_raw_probability')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {(rawConf * 100).toFixed(2)}%
                  </strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_calibrated_probability')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {isCalibrationActive && typeof calibratedConf === 'number'
                      ? `${(calibratedConf * 100).toFixed(2)}%`
                      : 'N/A (Inactive)'}
                  </strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_calibration')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {isCalibrationActive ? 'Active (Temperature Scaling)' : t('result.tech_calibration_inactive')}
                  </strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_temperature')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {calibration?.temperature_applied ?? 'N/A'}
                  </strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_uncertainty_threshold')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {calibration?.rejection_threshold ?? 0.65}
                  </strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_explanation_method')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {explanation?.method || 'Grad-CAM'}
                  </strong>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_target_layer')}
                  </span>
                  <code style={{ color: '#1C110A', fontSize: '0.88rem' }}>
                    {targetFeatureLayer}
                  </code>
                </div>

                <div>
                  <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    {t('result.tech_processing_time')}
                  </span>
                  <strong style={{ color: '#1C110A', fontSize: '0.92rem' }}>
                    {response.processing_time_ms ? `${response.processing_time_ms} ms` : 'N/A'}
                  </strong>
                </div>

                {response.image_sha256 && (
                  <div style={{ gridColumn: '1 / -1' }}>
                    <span style={{ display: 'block', color: '#8A7768', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                      {t('result.tech_image_sha')}
                    </span>
                    <code style={{ color: '#4A3728', fontSize: '0.84rem', wordBreak: 'break-all' }}>
                      {response.image_sha256}
                    </code>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* ─── 7. BOTTOM ACTIONS: Check another leaf + Home ────────────────── */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            flexWrap: 'wrap',
          }}
        >
          {/* Check Another Leaf (Primary Gold CTA) */}
          <button
            type="button"
            id="btn-result-check-another"
            onClick={onCheckAnother}
            style={{
              minHeight: '50px',
              padding: '0.75rem 2rem',
              background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
              border: 'none',
              borderRadius: '12px',
              color: '#140C07',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1.02rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.6rem',
              boxShadow: '0 4px 16px rgba(201, 154, 60, 0.4)',
              transition: 'transform 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateY(-1px)')}
            onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
          >
            <RefreshCw size={18} aria-hidden="true" />
            <span>{t('result.check_another')}</span>
          </button>

          {/* Back to Home */}
          <button
            type="button"
            id="btn-result-secondary-home"
            onClick={onBackToHome}
            style={{
              minHeight: '50px',
              padding: '0.75rem 1.8rem',
              background: '#FAF5EB',
              border: '1.5px solid rgba(201, 154, 60, 0.4)',
              borderRadius: '12px',
              color: '#3A2412',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <Home size={18} aria-hidden="true" />
            <span>{t('home.back_to_home')}</span>
          </button>
        </div>

      </div>

      {/* Responsive layout rule for Result Hero and Metrics Grid */}
      <style>{`
        @media (max-width: 768px) {
          .drishya-result-hero-grid {
            grid-template-columns: 1fr !important;
            gap: 1.5rem !important;
            padding: 1.5rem !important;
          }
          .drishya-metrics-grid {
            grid-template-columns: 1fr !important;
            gap: 1.25rem !important;
          }
        }
      `}</style>
    </div>
  );
}
