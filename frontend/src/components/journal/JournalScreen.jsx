/**
 * JournalScreen.jsx - DRISHYA "My Leaf Journal" Experience
 *
 * Implements:
 * - Authentic agricultural field notebook aesthetic (parchment, ivory, espresso, antique gold, restrained moss)
 * - Strict user-scoped history fetched from GET /api/v1/history
 * - Chronological grouping by Month & Year (October 2026, September 2026...) with newest first
 * - Responsive localized dates (English, Hindi, Marathi) using Intl.DateTimeFormat
 * - Crop filter controls: All, Turmeric, Citrus
 * - Truthful image retention policy: original photos are NOT stored by backend.
 *   Shows elegant botanical field-record plate with condition glyph & typography.
 *   Never fabricates historical leaf photos or pretends raw images are permanently retained.
 * - In-memory active session continuity: if user just diagnosed a leaf in the active session,
 *   that photo can be displayed with an honest "Active session photograph" badge.
 * - Genuine backend result state mapping: Healthy, Condition detected, Unclear (rejection/uncertainty)
 * - Translated condition names via getConditionDisplayName(crop, predicted_class, t)
 * - Deletion of history entries via DELETE /api/v1/history/{id} with calm confirmation dialog
 * - Detailed entry drawer/modal with full diagnosis metadata and honest photo notice
 * - Calm editorial loading, error, and empty states
 * - GSAP motion respecting prefers-reduced-motion
 * - Accessible >= 48px touch targets, visible focus, aria-live announcements
 */

import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  BookOpen,
  Calendar,
  Clock,
  Filter,
  Trash2,
  ChevronRight,
  X,
  ArrowLeft,
  Camera,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileText,
  Info,
  Check,
} from 'lucide-react';
import gsap from 'gsap';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import CropIdentity from '../brand/CropIdentity';
import {
  fetchPredictionHistory,
  fetchPredictionDetail,
  deletePrediction,
} from '../../services/historyApi';

export default function JournalScreen({
  activeSessionDiagnosis = null,
  onCheckLeaf,
  onBackToHome,
}) {
  const { navigate } = useAuth();
  const { t, language, formatDate, formatTime, getConditionDisplayName } = useLanguage();
  const isDevanagari = language === 'hi' || language === 'mr';

  // Component state
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState('all'); // 'all' | 'turmeric' | 'citrus'

  // Delete modal state
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Detail view modal state
  const [detailRecord, setDetailRecord] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailData, setDetailData] = useState(null);

  // GSAP animation refs
  const pageContainerRef = useRef(null);
  const headerRef = useRef(null);
  const filtersRef = useRef(null);
  const contentRef = useRef(null);

  // Load history records from backend API
  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPredictionHistory({ limit: 100, offset: 0 });
      if (data?.unauthenticated) {
        navigate('/welcome');
        return;
      }
      setRecords(data?.items || []);
    } catch (err) {
      console.error('[DRISHYA Journal] Failed to load history:', err);
      setError(t('journal.error_loading'));
    } finally {
      setLoading(false);
    }
  }, [navigate, t]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  // Entrance animation with GSAP (respecting prefers-reduced-motion)
  useEffect(() => {
    if (loading || !pageContainerRef.current) return;

    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      gsap.set([headerRef.current, filtersRef.current, contentRef.current].filter(Boolean), {
        opacity: 1,
        y: 0,
        clearProps: 'all',
      });
      return;
    }

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });
      gsap.set([headerRef.current, filtersRef.current, contentRef.current].filter(Boolean), {
        opacity: 0,
        y: 16,
      });

      tl.to(headerRef.current, { opacity: 1, y: 0, duration: 0.45 }, 0.05)
        .to(filtersRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0.15)
        .to(contentRef.current, { opacity: 1, y: 0, duration: 0.45 }, 0.25);
    }, pageContainerRef);

    return () => ctx.revert();
  }, [loading]);

  // Toast auto-dismissal
  useEffect(() => {
    if (!toastMessage) return;
    const timer = setTimeout(() => {
      setToastMessage(null);
    }, 3200);
    return () => clearTimeout(timer);
  }, [toastMessage]);

  // Filter records by crop
  const filteredRecords = useMemo(() => {
    if (selectedCrop === 'all') return records;
    return records.filter((r) => (r.crop || '').toLowerCase() === selectedCrop);
  }, [records, selectedCrop]);

  // Counts for filter pills
  const counts = useMemo(() => {
    const total = records.length;
    const turmeric = records.filter((r) => (r.crop || '').toLowerCase() === 'turmeric').length;
    const citrus = records.filter((r) => (r.crop || '').toLowerCase() === 'citrus').length;
    return { total, turmeric, citrus };
  }, [records]);

  // Chronological Monthly Grouping (October 2026, September 2026, etc.)
  // Sorted newest first by created_at
  const groupedByMonth = useMemo(() => {
    const groups = new Map();

    // Sort newest first
    const sorted = [...filteredRecords].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    sorted.forEach((item) => {
      const dateObj = new Date(item.created_at);
      if (isNaN(dateObj.getTime())) return;

      // Group key: 'YYYY-MM' for stable chronological grouping
      const year = dateObj.getFullYear();
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      const groupKey = `${year}-${month}`;

      // Localized display label using Intl.DateTimeFormat via formatDate utility
      const displayLabel = formatDate(dateObj, { month: 'long', year: 'numeric' });

      if (!groups.has(groupKey)) {
        groups.set(groupKey, {
          key: groupKey,
          label: displayLabel,
          items: [],
        });
      }
      groups.get(groupKey).items.push(item);
    });

    // Return groups ordered newest month first
    return Array.from(groups.values()).sort((a, b) => b.key.localeCompare(a.key));
  }, [filteredRecords, formatDate]);

  // Handle open entry detail
  const handleOpenDetail = async (item) => {
    setDetailRecord(item);
    setDetailLoading(true);
    setDetailData(null);

    try {
      const fullData = await fetchPredictionDetail(item.id);
      setDetailData(fullData);
    } catch (err) {
      console.warn('[DRISHYA Journal] Failed to fetch record detail:', err);
      // Fallback: use item summary
      setDetailData(item);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCloseDetail = () => {
    setDetailRecord(null);
    setDetailData(null);
  };

  // Handle delete confirmation
  const handleInitiateDelete = (e, item) => {
    e.stopPropagation();
    setRecordToDelete(item);
  };

  const handleCancelDelete = () => {
    if (isDeleting) return;
    setRecordToDelete(null);
  };

  const handleConfirmDelete = async () => {
    if (!recordToDelete) return;
    setIsDeleting(true);

    try {
      await deletePrediction(recordToDelete.id);
      // Remove from state immediately upon confirmed backend response
      setRecords((prev) => prev.filter((r) => r.id !== recordToDelete.id));
      setToastMessage(t('journal.deleted_toast'));
      setRecordToDelete(null);

      // If deleted record is currently open in detail modal, close it
      if (detailRecord?.id === recordToDelete.id) {
        setDetailRecord(null);
        setDetailData(null);
      }
    } catch (err) {
      console.error('[DRISHYA Journal] Failed to delete record:', err);
      alert('Unable to delete journal entry. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  // Helper to check if item matches active in-memory session leaf photo
  const getSessionImageIfAvailable = (item) => {
    if (!activeSessionDiagnosis || !activeSessionDiagnosis.imageObjectUrl) {
      return null;
    }
    // Match by SHA-256 or prediction ID if available
    const sessionSha =
      activeSessionDiagnosis.diagnosisResponse?.prediction?.image_sha256;
    const sessionId = activeSessionDiagnosis.diagnosisResponse?.prediction?.id;

    if (
      (sessionId && sessionId === item.id) ||
      (sessionSha && item.image_sha256 && sessionSha === item.image_sha256)
    ) {
      return activeSessionDiagnosis.imageObjectUrl;
    }
    return null;
  };

  // Determine result state glyph & text
  const getResultState = (item) => {
    if (item.is_rejected) {
      return {
        label: t('journal.state_unsure'),
        type: 'unclear',
        color: '#B46E1B',
        bgColor: 'rgba(217, 131, 36, 0.14)',
        borderColor: 'rgba(217, 131, 36, 0.35)',
        icon: AlertTriangle,
      };
    }
    const rawClass = (item.predicted_class || '').toLowerCase();
    if (rawClass.includes('healthy')) {
      return {
        label: t('journal.state_healthy'),
        type: 'healthy',
        color: '#2D6A2E',
        bgColor: 'rgba(45, 106, 46, 0.14)',
        borderColor: 'rgba(45, 106, 46, 0.35)',
        icon: CheckCircle2,
      };
    }
    return {
      label: t('journal.state_likely'),
      type: 'condition',
      color: '#A24A2B',
      bgColor: 'rgba(162, 74, 43, 0.14)',
      borderColor: 'rgba(162, 74, 43, 0.35)',
      icon: AlertCircle,
    };
  };

  return (
    <div
      ref={pageContainerRef}
      className="drishya-journal-screen"
      style={{
        width: '100%',
        minHeight: 'calc(100vh - 65px)',
        backgroundColor: '#FBF6EA',
        color: '#1C110A',
        padding: '1.5rem 1rem 5rem',
      }}
    >
      <div
        style={{
          maxWidth: '1100px',
          margin: '0 auto',
        }}
      >
        {/* ── 1. Top Navigation & Header ───────────────────────────────── */}
        <header
          ref={headerRef}
          style={{
            marginBottom: '1.75rem',
            borderBottom: '1.5px solid rgba(201, 154, 60, 0.28)',
            paddingBottom: '1.25rem',
          }}
        >
          {/* Back Action & Breadcrumb */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem',
            }}
          >
            <button
              type="button"
              id="btn-journal-back-home"
              onClick={onBackToHome || (() => navigate('/home'))}
              aria-label={t('common.back')}
              style={{
                minHeight: '48px',
                padding: '0.5rem 1rem',
                background: 'rgba(58, 36, 18, 0.05)',
                border: '1px solid rgba(201, 154, 60, 0.3)',
                borderRadius: '9999px',
                color: '#6F5F52',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
                fontSize: '0.9rem',
                fontWeight: '600',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(58, 36, 18, 0.1)';
                e.currentTarget.style.color = '#1C110A';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(58, 36, 18, 0.05)';
                e.currentTarget.style.color = '#6F5F52';
              }}
            >
              <ArrowLeft size={16} aria-hidden="true" />
              <span>{t('common.back')}</span>
            </button>

            {/* Check a leaf CTA button */}
            <button
              type="button"
              id="btn-journal-check-leaf"
              onClick={onCheckLeaf || (() => navigate('/check'))}
              style={{
                minHeight: '48px',
                padding: '0.55rem 1.25rem',
                background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
                border: 'none',
                borderRadius: '10px',
                color: '#140C07',
                fontWeight: '700',
                fontSize: '0.95rem',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 14px rgba(201, 154, 60, 0.35)',
                transition: 'transform 0.2s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
              onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
            >
              <Camera size={18} aria-hidden="true" />
              <span>{t('journal.check_leaf_action')}</span>
            </button>
          </div>

          {/* Title & Editorial Subtitle */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem', flexWrap: 'wrap' }}>
            <h1
              id="journal-page-heading"
              style={{
                fontFamily: isDevanagari
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: 'clamp(2rem, 3.8vw, 2.75rem)',
                fontWeight: '700',
                color: '#1C110A',
                letterSpacing: isDevanagari ? '0' : '-0.02em',
                lineHeight: 1.2,
                margin: 0,
              }}
            >
              {t('journal.title')}
            </h1>

            {/* Record count badge */}
            {!loading && records.length > 0 && (
              <span
                style={{
                  fontSize: '0.85rem',
                  fontWeight: '600',
                  color: '#8A5A2B',
                  background: 'rgba(201, 154, 60, 0.15)',
                  padding: '0.2rem 0.65rem',
                  borderRadius: '9999px',
                  border: '1px solid rgba(201, 154, 60, 0.3)',
                }}
              >
                {records.length === 1
                  ? t('journal.records_count', { count: records.length })
                  : t('journal.records_count_plural', { count: records.length })}
              </span>
            )}
          </div>

          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '1.05rem',
              color: '#6F5F52',
              marginTop: '0.4rem',
              marginBottom: 0,
              maxWidth: '680px',
              lineHeight: 1.55,
            }}
          >
            {t('journal.subtitle')}
          </p>
        </header>

        {/* ── 2. Filter Controls (All / Turmeric / Citrus) ─────────────── */}
        <section
          ref={filtersRef}
          aria-label="Filter records by crop"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            flexWrap: 'wrap',
            marginBottom: '2rem',
          }}
        >
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontSize: '0.85rem',
              fontWeight: '600',
              color: '#8A5A2B',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginRight: '0.35rem',
            }}
          >
            <Filter size={14} aria-hidden="true" />
            <span>{t('check.selected_crop_label')}:</span>
          </span>

          {/* Filter: All */}
          <button
            type="button"
            id="btn-filter-all"
            onClick={() => setSelectedCrop('all')}
            aria-pressed={selectedCrop === 'all'}
            style={{
              minHeight: '48px',
              padding: '0.5rem 1.15rem',
              borderRadius: '9999px',
              cursor: 'pointer',
              fontSize: '0.92rem',
              fontWeight: selectedCrop === 'all' ? '700' : '500',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              border: selectedCrop === 'all' ? '1.5px solid #8A5A2B' : '1px solid rgba(201, 154, 60, 0.35)',
              background: selectedCrop === 'all' ? '#FAF5EB' : 'rgba(250, 245, 235, 0.6)',
              color: selectedCrop === 'all' ? '#1C110A' : '#6F5F52',
              boxShadow: selectedCrop === 'all' ? '0 2px 8px rgba(138, 90, 43, 0.15)' : 'none',
              transition: 'all 0.2s ease',
            }}
          >
            <span>{t('journal.filter_all')}</span>
            <span style={{ marginLeft: '0.4rem', opacity: 0.75, fontSize: '0.8rem' }}>
              ({counts.total})
            </span>
          </button>

          {/* Filter: Turmeric */}
          <button
            type="button"
            id="btn-filter-turmeric"
            onClick={() => setSelectedCrop('turmeric')}
            aria-pressed={selectedCrop === 'turmeric'}
            style={{
              minHeight: '48px',
              padding: '0.5rem 1.15rem 0.5rem 0.6rem',
              borderRadius: '9999px',
              cursor: 'pointer',
              fontSize: '0.92rem',
              fontWeight: selectedCrop === 'turmeric' ? '700' : '500',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              border: selectedCrop === 'turmeric' ? '1.5px solid #8A5A2B' : '1px solid rgba(201, 154, 60, 0.35)',
              background: selectedCrop === 'turmeric' ? '#FAF5EB' : 'rgba(250, 245, 235, 0.6)',
              color: selectedCrop === 'turmeric' ? '#8A5A2B' : '#6F5F52',
              boxShadow: selectedCrop === 'turmeric' ? '0 2px 8px rgba(138, 90, 43, 0.15)' : 'none',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            <CropIdentity crop="turmeric" size={22} showName={false} />
            <span>{t('journal.filter_turmeric')}</span>
            <span style={{ marginLeft: '0.25rem', opacity: 0.75, fontSize: '0.8rem' }}>
              ({counts.turmeric})
            </span>
          </button>

          {/* Filter: Citrus */}
          <button
            type="button"
            id="btn-filter-citrus"
            onClick={() => setSelectedCrop('citrus')}
            aria-pressed={selectedCrop === 'citrus'}
            style={{
              minHeight: '48px',
              padding: '0.5rem 1.15rem 0.5rem 0.6rem',
              borderRadius: '9999px',
              cursor: 'pointer',
              fontSize: '0.92rem',
              fontWeight: selectedCrop === 'citrus' ? '700' : '500',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              border: selectedCrop === 'citrus' ? '1.5px solid #5E6B38' : '1px solid rgba(201, 154, 60, 0.35)',
              background: selectedCrop === 'citrus' ? '#FAF5EB' : 'rgba(250, 245, 235, 0.6)',
              color: selectedCrop === 'citrus' ? '#3B4D1C' : '#6F5F52',
              boxShadow: selectedCrop === 'citrus' ? '0 2px 8px rgba(94, 107, 56, 0.15)' : 'none',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            <CropIdentity crop="citrus" size={22} showName={false} />
            <span>{t('journal.filter_citrus')}</span>
            <span style={{ marginLeft: '0.25rem', opacity: 0.75, fontSize: '0.8rem' }}>
              ({counts.citrus})
            </span>
          </button>
        </section>

        {/* ── 3. Main Content: Loading, Error, Empty, or Grouped Records ── */}
        <div ref={contentRef} id="journal-content-area">
          {/* Loading State */}
          {loading && (
            <div
              role="status"
              aria-live="polite"
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '1.25rem',
              }}
            >
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  style={{
                    background: '#FAF5EB',
                    border: '1px solid rgba(201, 154, 60, 0.25)',
                    borderRadius: '16px',
                    padding: '1.5rem',
                    minHeight: '190px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    opacity: 0.6,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div style={{ width: '80px', height: '22px', background: 'rgba(201, 154, 60, 0.2)', borderRadius: '9999px' }} />
                    <div style={{ width: '70px', height: '22px', background: 'rgba(201, 154, 60, 0.15)', borderRadius: '9999px' }} />
                  </div>
                  <div style={{ width: '65%', height: '24px', background: 'rgba(58, 36, 18, 0.12)', borderRadius: '6px', margin: '1rem 0' }} />
                  <div style={{ width: '45%', height: '16px', background: 'rgba(58, 36, 18, 0.08)', borderRadius: '4px' }} />
                </div>
              ))}
              <span className="sr-only" style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden' }}>
                {t('journal.loading')}
              </span>
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div
              role="alert"
              style={{
                background: '#FAF5EB',
                border: '1.5px solid rgba(162, 74, 43, 0.35)',
                borderRadius: '16px',
                padding: '2.5rem 1.5rem',
                textAlign: 'center',
                maxWidth: '520px',
                margin: '2rem auto',
              }}
            >
              <AlertCircle size={36} color="#A24A2B" style={{ margin: '0 auto 1rem' }} aria-hidden="true" />
              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.35rem',
                  color: '#1C110A',
                  marginBottom: '0.5rem',
                }}
              >
                {t('journal.error_loading')}
              </h2>
              <button
                type="button"
                id="btn-journal-retry"
                onClick={loadHistory}
                style={{
                  minHeight: '48px',
                  marginTop: '1.25rem',
                  padding: '0.65rem 1.4rem',
                  background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#140C07',
                  fontWeight: '700',
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                }}
              >
                <RefreshCw size={16} aria-hidden="true" />
                <span>{t('journal.retry')}</span>
              </button>
            </div>
          )}

          {/* Empty State: Zero total user records */}
          {!loading && !error && records.length === 0 && (
            <div
              style={{
                background: '#FAF5EB',
                border: '1.5px dashed rgba(201, 154, 60, 0.45)',
                borderRadius: '20px',
                padding: '3.5rem 2rem',
                textAlign: 'center',
                maxWidth: '560px',
                margin: '2.5rem auto',
                boxShadow: '0 8px 24px rgba(28, 17, 10, 0.04)',
              }}
            >
              <div
                style={{
                  width: '68px',
                  height: '68px',
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
                <BookOpen size={32} aria-hidden="true" />
              </div>

              <h2
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.65rem',
                  color: '#1C110A',
                  fontWeight: '700',
                  marginBottom: '0.65rem',
                }}
              >
                {t('journal.empty_title')}
              </h2>

              <p
                style={{
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '1rem',
                  color: '#6F5F52',
                  lineHeight: 1.6,
                  maxWidth: '460px',
                  margin: '0 auto 2rem',
                }}
              >
                {t('journal.empty_desc')}
              </p>

              <button
                type="button"
                id="btn-journal-empty-check"
                onClick={onCheckLeaf || (() => navigate('/check'))}
                style={{
                  minHeight: '48px',
                  padding: '0.75rem 1.8rem',
                  background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
                  border: 'none',
                  borderRadius: '10px',
                  color: '#140C07',
                  fontWeight: '700',
                  fontSize: '1rem',
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 6px 18px rgba(201, 154, 60, 0.35)',
                }}
              >
                <Camera size={18} aria-hidden="true" />
                <span>{t('journal.check_leaf_action')}</span>
              </button>
            </div>
          )}

          {/* Empty State: Filter has zero records */}
          {!loading && !error && records.length > 0 && filteredRecords.length === 0 && (
            <div
              style={{
                background: '#FAF5EB',
                border: '1px dashed rgba(201, 154, 60, 0.4)',
                borderRadius: '16px',
                padding: '3rem 2rem',
                textAlign: 'center',
                maxWidth: '500px',
                margin: '2rem auto',
              }}
            >
              <Info size={32} color="#8A5A2B" style={{ margin: '0 auto 0.75rem' }} aria-hidden="true" />
              <p
                style={{
                  fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                  fontSize: '1.05rem',
                  color: '#6F5F52',
                  marginBottom: '1.25rem',
                }}
              >
                {t('journal.no_crop_records')}
              </p>
              <button
                type="button"
                id="btn-reset-filter"
                onClick={() => setSelectedCrop('all')}
                style={{
                  minHeight: '48px',
                  padding: '0.55rem 1.25rem',
                  background: 'rgba(58, 36, 18, 0.08)',
                  border: '1px solid rgba(201, 154, 60, 0.35)',
                  borderRadius: '8px',
                  color: '#1C110A',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                {t('journal.filter_all')}
              </button>
            </div>
          )}

          {/* ── 4. Chronological Monthly Field Groups ──────────────────── */}
          {!loading && !error && groupedByMonth.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
              {groupedByMonth.map((group) => (
                <section
                  key={group.key}
                  className="drishya-journal-month-section"
                  aria-labelledby={`month-heading-${group.key}`}
                >
                  {/* Month / Year Section Divider & Header */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.85rem',
                      marginBottom: '1.25rem',
                    }}
                  >
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.45rem',
                        color: '#8A5A2B',
                      }}
                    >
                      <Calendar size={18} aria-hidden="true" />
                      <h2
                        id={`month-heading-${group.key}`}
                        style={{
                          fontFamily: isDevanagari
                            ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                            : 'var(--font-display, "Fraunces", Georgia, serif)',
                          fontSize: '1.35rem',
                          color: '#1C110A',
                          fontWeight: '700',
                          margin: 0,
                        }}
                      >
                        {group.label}
                      </h2>
                    </div>

                    <div
                      style={{
                        flex: 1,
                        height: '1px',
                        background: 'linear-gradient(90deg, rgba(201, 154, 60, 0.35) 0%, rgba(201, 154, 60, 0.05) 100%)',
                      }}
                    />

                    <span
                      style={{
                        fontSize: '0.8rem',
                        color: '#8A5A2B',
                        fontWeight: '600',
                      }}
                    >
                      {group.items.length}{' '}
                      {group.items.length === 1 ? t('journal.records_count', { count: 1 }) : ''}
                    </span>
                  </div>

                  {/* Field Cards Grid for this Month */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fill, minmax(310px, 1fr))',
                      gap: '1.25rem',
                    }}
                  >
                    {group.items.map((item) => {
                      const cropName =
                        item.crop === 'turmeric'
                          ? t('check.crop_turmeric')
                          : t('check.crop_citrus');
                      const conditionDisplayName = getConditionDisplayName(
                        item.crop,
                        item.predicted_class,
                        t
                      );
                      const stateInfo = getResultState(item);
                      const StateIcon = stateInfo.icon;
                      const sessionPhoto = getSessionImageIfAvailable(item);

                      return (
                        <article
                          key={item.id}
                          className="drishya-journal-card"
                          tabIndex={0}
                          role="button"
                          aria-label={`${cropName} - ${conditionDisplayName} - ${formatDate(item.created_at)}`}
                          onClick={() => handleOpenDetail(item)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              handleOpenDetail(item);
                            }
                          }}
                          style={{
                            background: '#FAF5EB',
                            border: '1.5px solid rgba(201, 154, 60, 0.32)',
                            borderRadius: '16px',
                            padding: '1.25rem',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            boxShadow: '0 6px 18px rgba(28, 17, 10, 0.04)',
                            cursor: 'pointer',
                            position: 'relative',
                            transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-3px)';
                            e.currentTarget.style.boxShadow = '0 12px 28px rgba(28, 17, 10, 0.08)';
                            e.currentTarget.style.borderColor = '#C99A3C';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 6px 18px rgba(28, 17, 10, 0.04)';
                            e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.32)';
                          }}
                        >
                          <div>
                            {/* Card Top Row: Crop Badge + Result State Pill + Delete Button */}
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                gap: '0.5rem',
                                marginBottom: '0.85rem',
                              }}
                            >
                              {/* Crop Identity Badge */}
                              <span
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  color: item.crop === 'turmeric' ? '#8A5A2B' : '#3E4D1D',
                                  background:
                                    item.crop === 'turmeric'
                                      ? 'rgba(201, 154, 60, 0.16)'
                                      : 'rgba(94, 107, 56, 0.16)',
                                  border:
                                    item.crop === 'turmeric'
                                      ? '1px solid rgba(201, 154, 60, 0.35)'
                                      : '1px solid rgba(94, 107, 56, 0.35)',
                                  padding: '0.15rem 0.55rem 0.15rem 0.2rem',
                                  borderRadius: '9999px',
                                }}
                              >
                                <CropIdentity
                                  crop={item.crop}
                                  size={20}
                                  fontSize="0.72rem"
                                  style={{ color: item.crop === 'turmeric' ? '#8A5A2B' : '#3E4D1D', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
                                />
                              </span>

                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                                {/* State Indicator Pill */}
                                <span
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '0.3rem',
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    color: stateInfo.color,
                                    background: stateInfo.bgColor,
                                    border: `1px solid ${stateInfo.borderColor}`,
                                    padding: '0.2rem 0.55rem',
                                    borderRadius: '9999px',
                                  }}
                                >
                                  <StateIcon size={12} aria-hidden="true" />
                                  <span>{stateInfo.label}</span>
                                </span>

                                {/* Delete Entry Action Button */}
                                <button
                                  type="button"
                                  aria-label={`${t('journal.delete')} - ${cropName} ${conditionDisplayName}`}
                                  title={t('journal.delete')}
                                  onClick={(e) => handleInitiateDelete(e, item)}
                                  style={{
                                    minWidth: '44px',
                                    minHeight: '44px',
                                    padding: 0,
                                    background: 'transparent',
                                    border: 'none',
                                    borderRadius: '8px',
                                    color: '#8A5A2B',
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    cursor: 'pointer',
                                    transition: 'color 0.15s ease, background 0.15s ease',
                                  }}
                                  onMouseEnter={(e) => {
                                    e.currentTarget.style.color = '#A24A2B';
                                    e.currentTarget.style.background = 'rgba(162, 74, 43, 0.1)';
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.color = '#8A5A2B';
                                    e.currentTarget.style.background = 'transparent';
                                  }}
                                >
                                  <Trash2 size={16} aria-hidden="true" />
                                </button>
                              </div>
                            </div>

                            {/* Botanical Field Visual Area */}
                            {sessionPhoto ? (
                              /* Genuine Active Session Continuity Photo */
                              <div
                                style={{
                                  position: 'relative',
                                  width: '100%',
                                  height: '110px',
                                  borderRadius: '10px',
                                  overflow: 'hidden',
                                  marginBottom: '0.85rem',
                                  border: '1px solid rgba(201, 154, 60, 0.3)',
                                  background: '#1C110A',
                                }}
                              >
                                <img
                                  src={sessionPhoto}
                                  alt={conditionDisplayName}
                                  style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                  }}
                                />
                                <span
                                  style={{
                                    position: 'absolute',
                                    bottom: '6px',
                                    right: '6px',
                                    fontSize: '0.65rem',
                                    background: 'rgba(28, 17, 10, 0.85)',
                                    color: '#F2C14E',
                                    padding: '0.15rem 0.45rem',
                                    borderRadius: '4px',
                                    fontWeight: '600',
                                  }}
                                >
                                  Current Session
                                </span>
                              </div>
                            ) : (
                              /* Truthful Botanical Field Note Insignia (No Fake Photos) */
                              <div
                                style={{
                                  width: '100%',
                                  height: '76px',
                                  borderRadius: '10px',
                                  background: 'linear-gradient(135deg, rgba(201, 154, 60, 0.1) 0%, rgba(138, 90, 43, 0.05) 100%)',
                                  border: '1px dashed rgba(201, 154, 60, 0.3)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  padding: '0.75rem 1rem',
                                  marginBottom: '0.85rem',
                                }}
                              >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                                  <div
                                    style={{
                                      width: '36px',
                                      height: '36px',
                                      borderRadius: '50%',
                                      background: item.crop === 'turmeric' ? 'rgba(201, 154, 60, 0.2)' : 'rgba(94, 107, 56, 0.2)',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      color: item.crop === 'turmeric' ? '#8A5A2B' : '#5E6B38',
                                    }}
                                  >
                                    <FileText size={18} aria-hidden="true" />
                                  </div>
                                  <div>
                                    <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#1C110A' }}>
                                      Field Diagnosis
                                    </div>
                                    <div style={{ fontSize: '0.72rem', color: '#6F5F52' }}>
                                      Diagnosis Record
                                    </div>
                                  </div>
                                </div>
                                <span
                                  style={{
                                    fontSize: '0.7rem',
                                    color: '#8A5A2B',
                                    fontWeight: '500',
                                    background: 'rgba(201, 154, 60, 0.12)',
                                    padding: '0.2rem 0.5rem',
                                    borderRadius: '4px',
                                  }}
                                >
                                  Photo not retained
                                </span>
                              </div>
                            )}

                            {/* Condition Headline */}
                            <h3
                              style={{
                                fontFamily: isDevanagari
                                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                                fontSize: '1.25rem',
                                fontWeight: '700',
                                color: '#1C110A',
                                lineHeight: 1.3,
                                margin: '0 0 0.5rem 0',
                              }}
                            >
                              {conditionDisplayName}
                            </h3>
                          </div>

                          {/* Card Footer: Date, Time & View Link */}
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              borderTop: '1px solid rgba(201, 154, 60, 0.2)',
                              paddingTop: '0.75rem',
                              marginTop: '0.75rem',
                              fontSize: '0.82rem',
                              color: '#6F5F52',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                                <Calendar size={13} aria-hidden="true" />
                                {formatDate(item.created_at)}
                              </span>
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                                <Clock size={13} aria-hidden="true" />
                                {formatTime(item.created_at)}
                              </span>
                            </div>

                            <span
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.15rem',
                                color: '#8A5A2B',
                                fontWeight: '600',
                                fontSize: '0.82rem',
                              }}
                            >
                              <ChevronRight size={16} aria-hidden="true" />
                            </span>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── 5. Delete Confirmation Modal ─────────────────────────────── */}
      {recordToDelete && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-modal-title"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 100,
            background: 'rgba(28, 17, 10, 0.65)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.25rem',
          }}
          onClick={handleCancelDelete}
        >
          <div
            style={{
              background: '#FAF5EB',
              border: '1.5px solid rgba(201, 154, 60, 0.45)',
              borderRadius: '20px',
              maxWidth: '460px',
              width: '100%',
              padding: '2rem 1.75rem',
              boxShadow: '0 20px 48px rgba(0, 0, 0, 0.3)',
              position: 'relative',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                width: '52px',
                height: '52px',
                borderRadius: '50%',
                background: 'rgba(162, 74, 43, 0.15)',
                border: '1px solid rgba(162, 74, 43, 0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#A24A2B',
                margin: '0 auto 1.25rem',
              }}
            >
              <Trash2 size={24} aria-hidden="true" />
            </div>

            <h3
              id="delete-modal-title"
              style={{
                fontFamily: isDevanagari
                  ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                  : 'var(--font-display, "Fraunces", Georgia, serif)',
                fontSize: '1.35rem',
                color: '#1C110A',
                textAlign: 'center',
                marginBottom: '0.65rem',
              }}
            >
              {t('journal.delete')}
            </h3>

            <p
              style={{
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                fontSize: '0.98rem',
                color: '#6F5F52',
                textAlign: 'center',
                lineHeight: 1.55,
                marginBottom: '1.5rem',
              }}
            >
              {t('journal.delete_confirm')}
            </p>

            {/* Target Entry Pill */}
            <div
              style={{
                background: 'rgba(201, 154, 60, 0.1)',
                border: '1px solid rgba(201, 154, 60, 0.25)',
                borderRadius: '10px',
                padding: '0.75rem 1rem',
                marginBottom: '1.75rem',
                textAlign: 'center',
              }}
            >
              <div style={{ fontWeight: '700', color: '#1C110A', fontSize: '1rem' }}>
                {getConditionDisplayName(recordToDelete.crop, recordToDelete.predicted_class, t)}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#8A5A2B', marginTop: '0.2rem' }}>
                {recordToDelete.crop === 'turmeric' ? t('check.crop_turmeric') : t('check.crop_citrus')} •{' '}
                {formatDate(recordToDelete.created_at)}
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                type="button"
                id="btn-cancel-delete"
                disabled={isDeleting}
                onClick={handleCancelDelete}
                style={{
                  flex: 1,
                  minHeight: '48px',
                  padding: '0.65rem 1rem',
                  background: 'rgba(58, 36, 18, 0.08)',
                  border: '1px solid rgba(201, 154, 60, 0.3)',
                  borderRadius: '10px',
                  color: '#1C110A',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                }}
              >
                {t('journal.delete_cancel')}
              </button>

              <button
                type="button"
                id="btn-confirm-delete"
                disabled={isDeleting}
                onClick={handleConfirmDelete}
                style={{
                  flex: 1,
                  minHeight: '48px',
                  padding: '0.65rem 1rem',
                  background: '#A24A2B',
                  border: 'none',
                  borderRadius: '10px',
                  color: '#FFFFFF',
                  fontWeight: '700',
                  fontSize: '0.95rem',
                  cursor: isDeleting ? 'wait' : 'pointer',
                  boxShadow: '0 4px 12px rgba(162, 74, 43, 0.35)',
                }}
              >
                {isDeleting ? t('journal.deleting') : t('journal.delete_button')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── 6. Detail View Modal / Drawer ───────────────────────────── */}
      {detailRecord && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="detail-modal-title"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 90,
            background: 'rgba(28, 17, 10, 0.65)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.25rem',
          }}
          onClick={handleCloseDetail}
        >
          <div
            style={{
              background: '#FAF5EB',
              border: '1.5px solid rgba(201, 154, 60, 0.45)',
              borderRadius: '20px',
              maxWidth: '560px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '2rem 1.75rem',
              boxShadow: '0 24px 50px rgba(0, 0, 0, 0.35)',
              position: 'relative',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              type="button"
              id="btn-close-detail"
              onClick={handleCloseDetail}
              aria-label={t('journal.close_detail')}
              style={{
                position: 'absolute',
                top: '1.25rem',
                right: '1.25rem',
                minWidth: '44px',
                minHeight: '44px',
                background: 'rgba(58, 36, 18, 0.08)',
                border: '1px solid rgba(201, 154, 60, 0.3)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#6F5F52',
                cursor: 'pointer',
              }}
            >
              <X size={18} aria-hidden="true" />
            </button>

            {/* Header: Crop & Condition */}
            <div style={{ marginBottom: '1.25rem' }}>
              <span
                style={{
                  fontSize: '0.78rem',
                  fontWeight: '700',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  color: detailRecord.crop === 'turmeric' ? '#8A5A2B' : '#3E4D1D',
                  background:
                    detailRecord.crop === 'turmeric'
                      ? 'rgba(201, 154, 60, 0.18)'
                      : 'rgba(94, 107, 56, 0.18)',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '9999px',
                }}
              >
                {detailRecord.crop === 'turmeric'
                  ? t('check.crop_turmeric')
                  : t('check.crop_citrus')}
              </span>

              <h2
                id="detail-modal-title"
                style={{
                  fontFamily: isDevanagari
                    ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                    : 'var(--font-display, "Fraunces", Georgia, serif)',
                  fontSize: '1.65rem',
                  color: '#1C110A',
                  fontWeight: '700',
                  lineHeight: 1.25,
                  margin: '0.65rem 0 0.35rem',
                }}
              >
                {getConditionDisplayName(detailRecord.crop, detailRecord.predicted_class, t)}
              </h2>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  fontSize: '0.85rem',
                  color: '#6F5F52',
                }}
              >
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Calendar size={14} aria-hidden="true" />
                  {formatDate(detailRecord.created_at)}
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Clock size={14} aria-hidden="true" />
                  {formatTime(detailRecord.created_at)}
                </span>
              </div>
            </div>

            {/* Truthful Image Policy Banner */}
            {getSessionImageIfAvailable(detailRecord) ? (
              <div
                style={{
                  width: '100%',
                  height: '180px',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  marginBottom: '1.25rem',
                  border: '1px solid rgba(201, 154, 60, 0.35)',
                }}
              >
                <img
                  src={getSessionImageIfAvailable(detailRecord)}
                  alt={getConditionDisplayName(detailRecord.crop, detailRecord.predicted_class, t)}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>
            ) : (
              <div
                style={{
                  background: 'rgba(201, 154, 60, 0.12)',
                  border: '1px dashed rgba(201, 154, 60, 0.4)',
                  borderRadius: '12px',
                  padding: '1rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem',
                  marginBottom: '1.25rem',
                }}
              >
                <Info size={18} color="#8A5A2B" style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
                <p
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.88rem',
                    color: '#6F5F52',
                    lineHeight: 1.5,
                    margin: 0,
                  }}
                >
                  {t('journal.photo_not_retained')}
                </p>
              </div>
            )}

            {/* Diagnosis State Badge */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.85rem 1rem',
                borderRadius: '12px',
                background: getResultState(detailRecord).bgColor,
                border: `1px solid ${getResultState(detailRecord).borderColor}`,
                marginBottom: '1.25rem',
              }}
            >
              {React.createElement(getResultState(detailRecord).icon, {
                size: 20,
                color: getResultState(detailRecord).color,
                'aria-hidden': 'true',
              })}
              <div>
                <div
                  style={{
                    fontWeight: '700',
                    fontSize: '0.95rem',
                    color: getResultState(detailRecord).color,
                  }}
                >
                  {getResultState(detailRecord).label}
                </div>
                <div style={{ fontSize: '0.82rem', color: '#6F5F52' }}>
                  {detailRecord.is_rejected
                    ? t('result.explanation_uncertain_desc')
                    : (detailRecord.predicted_class || '').toLowerCase().includes('healthy')
                    ? t('result.explanation_healthy_desc')
                    : t('result.explanation_condition_desc', {
                        condition: getConditionDisplayName(
                          detailRecord.crop,
                          detailRecord.predicted_class,
                          t
                        ),
                      })}
                </div>
              </div>
            </div>

            {/* Other possibilities (if available in detail) */}
            {detailData?.top_k && detailData.top_k.length > 1 && (
              <div style={{ marginBottom: '1.25rem' }}>
                <h4
                  style={{
                    fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                    fontSize: '0.9rem',
                    fontWeight: '700',
                    color: '#8A5A2B',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    marginBottom: '0.5rem',
                  }}
                >
                  {t('result.other_possibilities')}
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  {detailData.top_k.slice(1, 3).map((candidate, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '0.5rem 0.75rem',
                        background: 'rgba(58, 36, 18, 0.04)',
                        border: '1px solid rgba(201, 154, 60, 0.2)',
                        borderRadius: '8px',
                        fontSize: '0.85rem',
                        color: '#1C110A',
                        display: 'flex',
                        justifyContent: 'space-between',
                      }}
                    >
                      <span>
                        {getConditionDisplayName(detailRecord.crop, candidate.class_name, t)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Bottom Actions */}
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
              <button
                type="button"
                id="btn-detail-check-leaf"
                onClick={() => {
                  handleCloseDetail();
                  if (onCheckLeaf) onCheckLeaf();
                  else navigate(`/check?crop=${detailRecord.crop}`);
                }}
                style={{
                  flex: 1,
                  minHeight: '48px',
                  padding: '0.65rem 1rem',
                  background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
                  border: 'none',
                  borderRadius: '10px',
                  color: '#140C07',
                  fontWeight: '700',
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.45rem',
                  boxShadow: '0 4px 14px rgba(201, 154, 60, 0.35)',
                }}
              >
                <Camera size={16} aria-hidden="true" />
                <span>{t('result.check_another')}</span>
              </button>

              <button
                type="button"
                id="btn-detail-close"
                onClick={handleCloseDetail}
                style={{
                  minHeight: '48px',
                  padding: '0.65rem 1.25rem',
                  background: 'rgba(58, 36, 18, 0.08)',
                  border: '1px solid rgba(201, 154, 60, 0.3)',
                  borderRadius: '10px',
                  color: '#1C110A',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                }}
              >
                {t('journal.close_detail')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── 7. Notification Toast (aria-live) ────────────────────────── */}
      {toastMessage && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            zIndex: 110,
            background: '#1C110A',
            color: '#F4EAD3',
            border: '1px solid rgba(201, 154, 60, 0.45)',
            borderRadius: '10px',
            padding: '0.85rem 1.4rem',
            boxShadow: '0 10px 28px rgba(0, 0, 0, 0.35)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.65rem',
            fontSize: '0.92rem',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
          }}
        >
          <Check size={18} color="#F2C14E" aria-hidden="true" />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}
