/**
 * RecentJournalPreview.jsx - DRISHYA Authentic Leaf Journal Preview
 *
 * Implements:
 * - Fetches authenticated user's recent records from /api/v1/history
 * - Shows strictly real metadata (crop, translated condition, date, state indicator)
 * - Zero fabricated image thumbnails (backend stores sha256, not raw images)
 * - Zero technical metrics (no raw confidence, no model seeds, no architectures)
 * - Graceful empty state ("Your first leaf will appear here.")
 */

import React, { useEffect, useState } from 'react';
import { BookOpen, Calendar, Clock, ChevronRight, Leaf } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';
import { fetchRecentPredictions } from '../../services/historyApi';
import CropIdentity from '../brand/CropIdentity';

export default function RecentJournalPreview({ onCheckLeaf }) {
  const { t, language, formatDate, formatTime, getConditionDisplayName } = useLanguage();
  const { navigate } = useAuth();

  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadRecent() {
      setLoading(true);
      try {
        const data = await fetchRecentPredictions({ limit: 4, offset: 0 });
        if (isMounted) {
          setRecords(data?.items || []);
        }
      } catch (err) {
        if (isMounted) setRecords([]);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRecent();
    return () => {
      isMounted = false;
    };
  }, []);

  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  return (
    <section
      className="drishya-journal-preview"
      style={{
        width: '100%',
        margin: '3rem 0 2rem',
      }}
      aria-labelledby="recent-journal-heading"
    >
      {/* Section Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem',
          marginBottom: '1.4rem',
          borderBottom: '1px solid rgba(201, 154, 60, 0.25)',
          paddingBottom: '0.75rem',
        }}
      >
        <div>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              color: '#8A5A2B',
              fontSize: '0.8rem',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: '0.25rem',
            }}
          >
            <BookOpen size={14} />
            <span>{t('home.recent_journal_title')}</span>
          </div>
          <h2
            id="recent-journal-heading"
            style={{
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.75rem',
              color: '#1C110A',
              fontWeight: '700',
            }}
          >
            {t('home.recent_journal_subtitle')}
          </h2>
        </div>

        {records.length > 0 && (
          <button
            type="button"
            onClick={() => navigate('/journal')}
            style={{
              background: 'none',
              border: 'none',
              color: '#8A5A2B',
              fontSize: '0.92rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              textDecoration: 'underline',
              textUnderlineOffset: '3px',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            }}
          >
            <span>{t('home.view_all_journal')}</span>
            <ChevronRight size={16} />
          </button>
        )}
      </div>

      {/* Loading Skeleton */}
      {loading ? (
        <div
          style={{
            padding: '2.5rem',
            textAlign: 'center',
            color: '#8A5A2B',
            background: '#FAF5EB',
            borderRadius: '16px',
            border: '1px dashed rgba(201, 154, 60, 0.35)',
            fontFamily: 'var(--font-body)',
          }}
        >
          <span>{t('common.loading')}</span>
        </div>
      ) : records.length === 0 ? (
        /* Empty State */
        <div
          style={{
            padding: '3rem 2rem',
            textAlign: 'center',
            background: '#FAF5EB',
            border: '1px dashed rgba(201, 154, 60, 0.4)',
            borderRadius: '16px',
            boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.02)',
          }}
        >
          <div
            style={{
              width: '56px',
              height: '56px',
              margin: '0 auto 1rem',
              borderRadius: '50%',
              background: 'rgba(242, 193, 78, 0.2)',
              border: '1px solid rgba(201, 154, 60, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#8A5A2B',
            }}
          >
            <Leaf size={26} />
          </div>
          <p
            style={{
              fontFamily: isHindiOrMarathi
                ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                : 'var(--font-display, "Fraunces", Georgia, serif)',
              fontSize: '1.2rem',
              color: '#3A2412',
              fontWeight: '600',
              marginBottom: '0.5rem',
            }}
          >
            {t('home.empty_journal')}
          </p>
          <p
            style={{
              color: '#6F5F52',
              fontSize: '0.92rem',
              maxWidth: '440px',
              margin: '0 auto 1.5rem',
              lineHeight: 1.5,
            }}
          >
            {t('journal.empty')}
          </p>
          <button
            type="button"
            onClick={onCheckLeaf}
            style={{
              minHeight: '48px',
              padding: '0.65rem 1.4rem',
              background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#140C07',
              fontWeight: '700',
              fontSize: '0.95rem',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(201, 154, 60, 0.3)',
            }}
          >
            {t('home.action_check_now')}
          </button>
        </div>
      ) : (
        /* Real History Items Grid */
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {records.map((item) => {
            const isHealthy = (item.predicted_class || '').toLowerCase().includes('healthy');
            const conditionLabel = getConditionDisplayName(item.crop, item.predicted_class);
            const cropLabel = item.crop === 'turmeric' ? t('check.crop_turmeric') : t('check.crop_citrus');

            return (
              <div
                key={item.id}
                role="button"
                tabIndex={0}
                onClick={() => navigate('/journal')}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    navigate('/journal');
                  }
                }}
                aria-label={`${cropLabel} - ${conditionLabel}`}
                style={{
                  background: '#FAF5EB',
                  border: '1px solid rgba(201, 154, 60, 0.3)',
                  borderRadius: '14px',
                  padding: '1.25rem 1.4rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 4px 12px rgba(28, 17, 10, 0.05)',
                  cursor: 'pointer',
                  transition: 'transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.borderColor = '#C99A3C';
                  e.currentTarget.style.boxShadow = '0 8px 20px rgba(28, 17, 10, 0.08)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.3)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(28, 17, 10, 0.05)';
                }}
              >
                <div>
                  {/* Top Badge: Crop & Condition Status */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '0.75rem',
                    }}
                  >
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        color: item.crop === 'turmeric' ? '#8A5A2B' : '#5E6B38',
                        background: item.crop === 'turmeric' ? 'rgba(201, 154, 60, 0.15)' : 'rgba(94, 107, 56, 0.15)',
                        padding: '0.15rem 0.5rem 0.15rem 0.2rem',
                        borderRadius: '9999px',
                      }}
                    >
                      <CropIdentity
                        crop={item.crop}
                        size={18}
                        fontSize="0.72rem"
                        style={{ color: item.crop === 'turmeric' ? '#8A5A2B' : '#5E6B38', fontWeight: 700 }}
                      />
                    </span>

                    {/* Simple botanical status indicator */}
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        color: isHealthy ? '#38662B' : '#A24A2B',
                      }}
                    >
                      <span
                        style={{
                          width: '7px',
                          height: '7px',
                          borderRadius: '50%',
                          backgroundColor: isHealthy ? '#5E6B38' : '#A24A2B',
                        }}
                      />
                      {isHealthy ? t('result.state_healthy') : t('result.state_likely')}
                    </span>
                  </div>

                  {/* Condition Name */}
                  <h3
                    style={{
                      fontFamily: isHindiOrMarathi
                        ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)'
                        : 'var(--font-display, "Fraunces", Georgia, serif)',
                      fontSize: '1.15rem',
                      color: '#1C110A',
                      fontWeight: '700',
                      lineHeight: 1.3,
                      marginBottom: '0.5rem',
                    }}
                  >
                    {conditionLabel}
                  </h3>
                </div>

                {/* Date & Time Metadata */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    color: '#6F5F52',
                    fontSize: '0.8rem',
                    borderTop: '1px solid rgba(201, 154, 60, 0.18)',
                    paddingTop: '0.75rem',
                    marginTop: '0.75rem',
                  }}
                >
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Calendar size={13} />
                    {formatDate(item.created_at)}
                  </span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Clock size={13} />
                    {formatTime(item.created_at)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
