/**
 * historyApi.js - DRISHYA Prediction History & Journal Client
 *
 * Communicates with backend /api/v1/history endpoint using HttpOnly credentials.
 * Queries authenticated user's diagnosis records.
 */

const API_BASE = '/api/v1';

/**
 * Fetch paginated prediction history records for currently authenticated user
 * @param {{ limit?: number, offset?: number, crop?: string }} params
 * @returns {Promise<{ total: number, limit: number, offset: number, items: Array }>}
 */
export async function fetchPredictionHistory({ limit = 50, offset = 0, crop = null } = {}) {
  try {
    const queryParams = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    if (crop && crop !== 'all') {
      queryParams.append('crop', crop);
    }

    const res = await fetch(`${API_BASE}/history?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      credentials: 'include',
    });

    if (res.status === 401 || res.status === 403) {
      return { total: 0, limit, offset, items: [], unauthenticated: true };
    }

    if (!res.ok) {
      console.warn(`[DRISHYA historyApi] Request failed with status ${res.status}`);
      throw new Error(`Failed to fetch history (status ${res.status})`);
    }

    const data = await res.json();
    return data || { total: 0, limit, offset, items: [] };
  } catch (err) {
    console.warn('[DRISHYA historyApi] Error fetching history:', err);
    throw err;
  }
}

// Retain alias for existing callers
export const fetchRecentPredictions = fetchPredictionHistory;

/**
 * Fetch complete detail for a single prediction owned by current user
 * @param {number|string} id - Prediction history ID
 * @returns {Promise<Object>}
 */
export async function fetchPredictionDetail(id) {
  if (!id) throw new Error('Prediction ID is required');

  const res = await fetch(`${API_BASE}/history/${id}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch prediction detail (${res.status})`);
  }

  return await res.json();
}

/**
 * Delete a single prediction history record owned by current user
 * @param {number|string} id - Prediction history ID
 * @returns {Promise<{ deleted: boolean, id: number }>}
 */
export async function deletePrediction(id) {
  if (!id) throw new Error('Prediction ID is required');

  const res = await fetch(`${API_BASE}/history/${id}`, {
    method: 'DELETE',
    headers: {
      'Accept': 'application/json',
    },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error(`Failed to delete prediction record (${res.status})`);
  }

  return await res.json();
}
