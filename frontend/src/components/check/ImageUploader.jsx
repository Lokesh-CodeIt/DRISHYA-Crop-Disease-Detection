/**
 * ImageUploader.jsx - Drag-and-Drop + File Picker + Mobile Camera Input
 *
 * Implements:
 * - File input accepting image/* (JPEG, PNG, WebP) up to 20MB
 * - Drag-and-drop zone for desktop
 * - Mobile camera capture via accept="image/*" capture="environment"
 * - Client-side safety validation (file type, size, decodability)
 * - Calm editorial error display — no stack traces, no model internals
 *
 * No image conversion, no fake scanning overlays, no automatic crop validation.
 * The backend is the authoritative source of truth for diagnosis.
 */

import React, { useRef, useState, useCallback } from 'react';
import { Upload, Camera } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

// Safe client-side validation constants
const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB (generous above backend 15MB guideline)
const ACCEPTED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp'];
const ACCEPTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp'];

/**
 * Safely checks that the browser can decode this file as an image.
 * Revokes the object URL immediately after check.
 */
async function verifyImageDecodable(file) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(true);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(false);
    };
    img.src = url;
  });
}

export default function ImageUploader({
  onImageSelected,
  onValidationError,
  // Optional external refs — CheckLeafScreen passes these so retake/choose-another work
  fileInputRef: externalFileRef,
  cameraInputRef: externalCameraRef,
}) {
  const { t } = useLanguage();
  const internalFileRef = useRef(null);
  const internalCameraRef = useRef(null);
  // Use external refs if provided, else fall back to internal
  const fileInputRef = externalFileRef || internalFileRef;
  const cameraInputRef = externalCameraRef || internalCameraRef;
  const [isDragging, setIsDragging] = useState(false);
  const [validating, setValidating] = useState(false);

  const handleFile = useCallback(async (file) => {
    if (!file) return;

    // 1. File existence
    if (file.size === 0) {
      onValidationError(t('check.error_empty_file'));
      return;
    }

    // 2. MIME type check — primary guard
    const mimeOk = file.type
      ? ACCEPTED_MIME_TYPES.includes(file.type)
      : ACCEPTED_EXTENSIONS.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!mimeOk) {
      onValidationError(t('check.error_invalid_type'));
      return;
    }

    // 3. Size guard
    if (file.size > MAX_FILE_SIZE_BYTES) {
      onValidationError(t('check.error_file_too_large'));
      return;
    }

    // 4. Decode check — ensure browser can read the image data
    setValidating(true);
    const decodable = await verifyImageDecodable(file);
    setValidating(false);

    if (!decodable) {
      onValidationError(t('check.error_cannot_decode'));
      return;
    }

    // All checks passed — hand off to parent
    onImageSelected(file);
  }, [t, onImageSelected, onValidationError]);

  // Standard file picker
  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    // Reset input so same file can be re-selected after "Take another"
    e.target.value = '';
  };

  // Drag-and-drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* Hidden standard gallery/file picker */}
      <input
        ref={fileInputRef}
        type="file"
        id="leaf-file-input"
        accept="image/jpeg,image/png,image/webp"
        aria-label={t('check.choose_photo')}
        style={{ display: 'none' }}
        onChange={handleFileInputChange}
      />

      {/* Hidden camera capture input (mobile) */}
      <input
        ref={cameraInputRef}
        type="file"
        id="leaf-camera-input"
        accept="image/*"
        capture="environment"
        aria-label={t('check.take_photo')}
        style={{ display: 'none' }}
        onChange={handleFileInputChange}
      />

      {/* Drag-and-drop zone */}
      <div
        role="button"
        tabIndex={0}
        aria-label={t('check.drag_drop')}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        style={{
          border: `2px dashed ${isDragging ? '#C99A3C' : 'rgba(201, 154, 60, 0.4)'}`,
          borderRadius: '14px',
          padding: '2.5rem 1.5rem',
          background: isDragging
            ? 'rgba(201, 154, 60, 0.08)'
            : 'rgba(244, 234, 211, 0.35)',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'border-color 0.2s ease, background 0.2s ease',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <Upload
          size={36}
          color={isDragging ? '#C99A3C' : '#8A5A2B'}
          aria-hidden="true"
          style={{ transition: 'color 0.2s ease' }}
        />
        <div>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.95rem',
              color: '#3A2412',
              fontWeight: '600',
              marginBottom: '0.25rem',
            }}
          >
            {validating ? t('check.validating_image') : t('check.drag_drop')}
          </p>
          <p
            style={{
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              fontSize: '0.78rem',
              color: '#6F5F52',
            }}
          >
            {t('check.supported_formats')}
          </p>
        </div>
      </div>

      {/* Action row: Choose from Gallery + Take Photo */}
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        {/* Gallery / file picker */}
        <button
          type="button"
          id="btn-choose-photo"
          onClick={() => fileInputRef.current?.click()}
          disabled={validating}
          aria-label={t('check.choose_photo')}
          style={{
            flex: 1,
            minHeight: '48px',
            padding: '0.65rem 1rem',
            background: '#FAF5EB',
            border: '1.5px solid rgba(201, 154, 60, 0.4)',
            borderRadius: '10px',
            color: '#3A2412',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: '0.9rem',
            fontWeight: '600',
            cursor: validating ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            transition: 'background 0.15s ease, border-color 0.15s ease',
          }}
          onMouseEnter={(e) => {
            if (!validating) {
              e.currentTarget.style.background = '#F4EAD3';
              e.currentTarget.style.borderColor = '#C99A3C';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#FAF5EB';
            e.currentTarget.style.borderColor = 'rgba(201, 154, 60, 0.4)';
          }}
        >
          <Upload size={16} aria-hidden="true" />
          <span>{t('check.choose_photo')}</span>
        </button>

        {/* Camera (mobile-primary, still shows on desktop) */}
        <button
          type="button"
          id="btn-take-photo"
          onClick={() => cameraInputRef.current?.click()}
          disabled={validating}
          aria-label={t('check.take_photo')}
          style={{
            flex: 1,
            minHeight: '48px',
            padding: '0.65rem 1rem',
            background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 65%, #8A5A2B 100%)',
            border: 'none',
            borderRadius: '10px',
            color: '#140C07',
            fontFamily: 'var(--font-body, "Mukta", sans-serif)',
            fontSize: '0.9rem',
            fontWeight: '700',
            cursor: validating ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            boxShadow: '0 4px 12px rgba(201, 154, 60, 0.3)',
            opacity: validating ? 0.65 : 1,
            transition: 'filter 0.15s ease',
          }}
          onMouseEnter={(e) => {
            if (!validating) e.currentTarget.style.filter = 'brightness(1.06)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.filter = 'none';
          }}
        >
          <Camera size={16} aria-hidden="true" />
          <span>{t('check.take_photo')}</span>
        </button>
      </div>
    </div>
  );
}
