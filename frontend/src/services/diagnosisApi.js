/**
 * diagnosisApi.js - DRISHYA Leaf Diagnosis API Client
 *
 * Calls POST /api/v1/diagnose via multipart/form-data.
 * Uses HttpOnly cookie auth (credentials: 'include').
 * No JWT is stored in JS. No raw image bytes are persisted.
 */

const API_BASE = '/api/v1';

/**
 * Structured error for diagnosis failures
 */
export class DiagnosisApiError extends Error {
  constructor(message, status = 0, detail = null) {
    super(message);
    this.name = 'DiagnosisApiError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Submit a leaf image to the backend for explainable diagnosis.
 *
 * @param {Object} params
 * @param {File}   params.file     - Raw image File object from browser input
 * @param {string} params.crop     - 'turmeric' | 'citrus'
 * @param {string} params.language - 'en' | 'hi' | 'mr'
 * @returns {Promise<DiagnosisResponse>} Full backend DiagnosisResponse object
 * @throws {DiagnosisApiError}
 */
export async function submitLeafDiagnosis({ file, crop, language = 'en' }) {
  if (!file) {
    throw new DiagnosisApiError('No image file provided.', 0);
  }
  if (!crop || !['turmeric', 'citrus'].includes(crop)) {
    throw new DiagnosisApiError('Invalid crop type. Must be turmeric or citrus.', 0);
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('crop', crop);
  formData.append('language', language);

  try {
    const res = await fetch(`${API_BASE}/diagnose`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
      // Do NOT set Content-Type — browser sets multipart boundary automatically
    });

    // Authentication failure
    if (res.status === 401 || res.status === 403) {
      throw new DiagnosisApiError(
        'Your session has expired. Please sign in again.',
        res.status
      );
    }

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const detail = data?.detail || `Diagnosis request failed (HTTP ${res.status}).`;
      throw new DiagnosisApiError(detail, res.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof DiagnosisApiError) throw err;
    // Network / fetch failure
    throw new DiagnosisApiError(
      'Unable to reach the server. Check your connection and try again.',
      0,
      err
    );
  }
}
