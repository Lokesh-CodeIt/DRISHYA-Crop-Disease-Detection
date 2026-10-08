/**
 * authApi.js - DRISHYA / LeafLens Authentication API Client
 *
 * Communicates with backend endpoints using HttpOnly cookies (credentials: 'include').
 * Authentication tokens are NEVER stored in localStorage.
 */

const API_BASE = '/api/v1/auth';

/**
 * Custom error wrapper for structured API responses
 */
export class AuthApiError extends Error {
  constructor(message, status = 500, detail = null) {
    super(message);
    this.name = 'AuthApiError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Register a new user account
 * @param {{ name: string, email: string, password: string, preferred_language?: string }} payload
 */
export async function registerUser({ name, email, password, preferred_language = 'en' }) {
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ name, email, password, preferred_language }),
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = data?.detail || 'Failed to register account.';
      throw new AuthApiError(msg, res.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof AuthApiError) throw err;
    throw new AuthApiError('Network error during registration.', 0, err);
  }
}

/**
 * Log in with email and password
 * Issues HttpOnly session cookie
 * @param {{ email: string, password: string }} payload
 */
export async function loginUser({ email, password }) {
  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = data?.detail || 'Invalid email or password.';
      throw new AuthApiError(msg, res.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof AuthApiError) throw err;
    throw new AuthApiError('Network error during login.', 0, err);
  }
}

/**
 * Fetch the currently authenticated user session
 * Validates HttpOnly cookie server-side
 */
export async function getCurrentUser() {
  try {
    const res = await fetch(`${API_BASE}/me`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      credentials: 'include',
    });

    if (res.status === 401 || res.status === 403) {
      return null;
    }

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      throw new AuthApiError(data?.detail || 'Failed to fetch current user.', res.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof AuthApiError) throw err;
    return null;
  }
}

/**
 * Log out current user session
 * Clears HttpOnly session cookie on backend
 */
export async function logoutUser() {
  try {
    const res = await fetch(`${API_BASE}/logout`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
      credentials: 'include',
    });

    const data = await res.json().catch(() => null);

    if (!res.ok && res.status !== 401) {
      throw new AuthApiError(data?.detail || 'Failed to log out cleanly.', res.status, data);
    }

    return true;
  } catch (err) {
    if (err instanceof AuthApiError) throw err;
    return true; // Still clear local state on client
  }
}

/**
 * Update authenticated user language preference
 * @param {{ preferred_language: 'en' | 'hi' | 'mr' }} payload
 */
export async function updateUserPreferences({ preferred_language }) {
  try {
    const res = await fetch(`${API_BASE}/me/preferences`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ preferred_language }),
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = data?.detail || 'Failed to update user preference.';
      throw new AuthApiError(msg, res.status, data);
    }

    return data;
  } catch (err) {
    if (err instanceof AuthApiError) throw err;
    throw new AuthApiError('Network error while updating preferences.', 0, err);
  }
}

