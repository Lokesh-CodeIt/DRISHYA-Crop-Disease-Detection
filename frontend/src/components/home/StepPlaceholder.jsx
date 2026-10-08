/**
 * StepPlaceholder.jsx - Minimal Elegant Placeholder for Upcoming Workspaces
 *
 * Provides the required transitional hook for /check and /journal routes
 * without building full screens before their designated build steps.
 */

import React from 'react';
import { ArrowLeft, Camera, BookOpen, FileText } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';

export default function StepPlaceholder({ type = 'check', selectedCrop = null, diagnosisResult = null }) {
  const { navigate } = useAuth();
  const { t, language } = useLanguage();

  const isCheck = type === 'check';
  const isResult = type === 'result';
  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  const cropName = selectedCrop
    ? selectedCrop === 'turmeric'
      ? t('check.crop_turmeric')
      : t('check.crop_citrus')
    : null;

  return (
    <div
      style={{
        width: '100%',
        minHeight: 'calc(100vh - 65px)',
        backgroundColor: '#FBF6EA',
        padding: '3rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          maxWidth: '520px',
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
            margin: '0 auto 1.25rem',
            borderRadius: '50%',
            background: 'rgba(242, 193, 78, 0.22)',
            border: '1px solid rgba(201, 154, 60, 0.38)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#8A5A2B',
          }}
        >
        {isCheck ? <Camera size={30} /> : isResult ? <FileText size={30} /> : <BookOpen size={30} />}
        </div>

        {cropName && (
          <div
            style={{
              display: 'inline-block',
              background: 'rgba(201, 154, 60, 0.15)',
              border: '1px solid rgba(201, 154, 60, 0.3)',
              borderRadius: '9999px',
              padding: '0.3rem 0.85rem',
              color: '#8A5A2B',
              fontSize: '0.8rem',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: '0.85rem',
            }}
          >
            {cropName}
          </div>
        )}

        <h2
          style={{
            fontFamily: isHindiOrMarathi
              ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
              : 'var(--font-display, "Fraunces", Georgia, serif)',
            fontSize: '1.65rem',
            color: '#1C110A',
            fontWeight: '700',
            marginBottom: '0.65rem',
          }}
        >
          {isCheck
            ? t('home.placeholder_check_title')
            : isResult
            ? t('result.title')
            : t('home.placeholder_journal_title')}
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
          {isCheck
            ? t('home.placeholder_check_desc')
            : isResult
            ? t('analysis.processing')
            : t('home.placeholder_journal_desc')}
        </p>

        <button
          type="button"
          onClick={() => navigate('/home')}
          style={{
            minHeight: '48px',
            padding: '0.75rem 1.6rem',
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
          <ArrowLeft size={18} />
          <span>{t('home.back_to_home')}</span>
        </button>
      </div>
    </div>
  );
}
